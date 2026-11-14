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


if __name__ == '__main__':
    unittest.main()
