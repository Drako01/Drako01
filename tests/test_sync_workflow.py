"""Offline regression checks for the scheduled sync's branch lifecycle."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / '.github/workflows/sync-open-vsx-profile.yml').read_text(encoding='utf-8')
BASH = 'C:/Program Files/Git/bin/bash.exe' if os.name == 'nt' else shutil.which('bash')


def step_script(name):
    section = WORKFLOW.split(f'- name: {name}\n', 1)[1]
    block = section.split('        run: |\n', 1)[1]
    lines = []
    for line in block.splitlines():
        if line and not line.startswith('          '):
            break
        lines.append(line[10:])
    return '\n'.join(lines) + '\n'


@unittest.skipUnless(BASH and shutil.which('jq'), 'Requires Bash and jq, as provided by the CI runner')
class SyncWorkflowTest(unittest.TestCase):
    def test_pending_pr_detection(self):
        """Execute the real workflow query against representative API responses."""
        cases = [
            ([], ''),
            ([{'number': 15, 'headRefName': 'automation/open-vsx-profile-sync'}], '15'),
            ([{'number': 21, 'headRefName': 'automation/open-vsx-profile-sync-123-1'}], '21'),
            ([{'number': 22, 'headRefName': 'feat/unrelated'}], ''),
            ([{'number': 22, 'headRefName': 'feat/unrelated'},
              {'number': 21, 'headRefName': 'automation/open-vsx-profile-sync-123-2'}], '21'),
        ]
        mock = '''
gh() {
  [[ "$1 $2" == "pr list" ]] || return 90
  while (( $# )); do
    if [[ "$1" == "--jq" ]]; then
      shift
      printf '%s' "$TEST_PRS" | jq -r "$1"
      return
    fi
    shift
  done
  return 91
}
'''
        script = mock + step_script('Do not duplicate a pending automated PR')
        for prs, expected in cases:
            with self.subTest(prs=prs), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / 'output'
                summary = Path(directory) / 'summary'
                env = dict(os.environ, TEST_PRS=json.dumps(prs), GITHUB_REPOSITORY='test/profile',
                           GITHUB_OUTPUT=output.as_posix(), GITHUB_STEP_SUMMARY=summary.as_posix())
                result = subprocess.run([BASH, '-e', '-o', 'pipefail'], input=script, text=True,
                                        env=env, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(output.exists(), bool(expected))
                if expected:
                    self.assertIn('exists=true', output.read_text())
                    self.assertIn(f'PR #{expected}', summary.read_text())

    def test_branch_names_differ_across_runs_and_retries(self):
        script = step_script('Create validated PR and squash-merge via GitHub branch protection')
        assignment = re.search(r'^branch=.*$', script, re.MULTILINE).group()
        branches = []
        for run, attempt in [('100', '1'), ('100', '2'), ('101', '1')]:
            env = dict(os.environ, GITHUB_RUN_ID=run, GITHUB_RUN_ATTEMPT=attempt)
            result = subprocess.run([BASH, '-eu'], input=assignment + '\nprintf "%s" "$branch"',
                                    text=True, env=env, check=True, capture_output=True)
            branches.append(result.stdout)
        self.assertEqual(len(set(branches)), 3)
        for branch in branches:
            self.assertNotEqual(branch, 'automation/open-vsx-profile-sync')
            self.assertFalse(branch.startswith('automation/open-vsx-profile-sync/'))
            subprocess.run(['git', 'check-ref-format', '--branch', branch],
                           check=True, capture_output=True)

    def test_protected_automerge_outcomes(self):
        """Pending approval is successful queueing; API/SHA failures remain errors."""
        sha = 'a' * 40
        cases = [
            ('pending', {'headRefOid': sha, 'mergedAt': None, 'autoMergeRequest': {}}, 0, 0, 0),
            ('merged', {'headRefOid': sha, 'mergedAt': '2026-11-14T18:00:00Z',
                        'autoMergeRequest': None}, 0, 0, 0),
            ('missing', {'headRefOid': sha, 'mergedAt': None, 'autoMergeRequest': None}, 0, 0, 1),
            ('denied', {'headRefOid': sha}, 1, 0, 1),
            ('changed', {'headRefOid': 'b' * 40}, 0, 0, 1),
            ('api_error', {}, 0, 1, 1),
        ]
        mock = '''
gh() {
  case "$1 $2" in
    "pr merge")
      printf '%s\\n' "$@" > "$TEST_MERGE_ARGS"
      return "$TEST_MERGE_EXIT"
      ;;
    "pr view")
      [[ "$TEST_READ_EXIT" == 0 ]] || return "$TEST_READ_EXIT"
      while (( $# )); do
        if [[ "$1" == "--jq" ]]; then
          shift
          printf '%s' "$TEST_PR_JSON" | jq -r "$1"
          return
        fi
        shift
      done
      return 91
      ;;
    *) return 90 ;;
  esac
}
source "$TEST_SCRIPT" 21 "$TEST_SHA"
'''
        for name, metadata, merge_exit, read_exit, expected_exit in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                summary = Path(directory) / 'summary'
                merge_args = Path(directory) / 'merge_args'
                env = dict(os.environ, TEST_PR_JSON=json.dumps(metadata),
                           TEST_MERGE_EXIT=str(merge_exit), TEST_READ_EXIT=str(read_exit),
                           TEST_MERGE_ARGS=merge_args.as_posix(), TEST_SHA=sha,
                           TEST_SCRIPT=(ROOT / 'scripts/request_gallery_automerge.sh').as_posix(),
                           GITHUB_REPOSITORY='test/profile', GITHUB_STEP_SUMMARY=summary.as_posix())
                result = subprocess.run([BASH, '-e', '-o', 'pipefail'], input=mock, text=True,
                                        env=env, capture_output=True)
                self.assertEqual(result.returncode, expected_exit, result.stderr + result.stdout)
                if name in ('changed', 'api_error'):
                    self.assertFalse(merge_args.exists())
                else:
                    args = merge_args.read_text().splitlines()
                    self.assertIn('--auto', args)
                    self.assertIn('--squash', args)
                    self.assertNotIn('--admin', args)
                    self.assertEqual(args[args.index('--match-head-commit') + 1], sha)
                if name == 'pending':
                    self.assertIn('awaiting required approvals/checks', summary.read_text())
                    self.assertNotIn('squash-merged', summary.read_text())
                elif name == 'merged':
                    self.assertIn('squash-merged', summary.read_text())
                else:
                    self.assertFalse(summary.exists())


if __name__ == '__main__':
    unittest.main()
