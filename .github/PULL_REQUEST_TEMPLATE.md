# Pull request

## Resumen

<!-- Qué cambia y por qué. -->

## Contexto

<!-- Pedido, issue o problema que resuelve. -->

## Tipo de cambio

- [ ] Feature
- [ ] Bugfix
- [ ] UI/UX
- [ ] Documentación
- [ ] Mantenimiento
- [ ] Tests o automatización

## Alcance

<!-- Archivos y comportamiento afectados. -->

## Impacto funcional

- [ ] Afecta el perfil público
- [ ] Mantiene los enlaces y secciones existentes
- [ ] Modifica la automatización de la galería

## Validación realizada

- [ ] `git diff --check`
- [ ] Markdown revisado con el linter disponible; detallar avisos pendientes
- [ ] SVG parseados como XML y referencias locales comprobadas, si aplica
- [ ] `python -m unittest discover -s tests -p 'test_sync_open_vsx.py' -v`
- [ ] Vista renderizada revisada en GitHub, si aplica

<!-- Resultados reales y limitaciones. No marcar checks pendientes. -->

## Evidencia visual

<!-- Imagen, captura o ruta del recurso. Indicar si falta revisión visual. -->

## Backend, datos y contratos

- [ ] No modifica backend, bases de datos ni contratos de API

## Variables, secretos y configuración

- [ ] No requiere nuevas variables de entorno
- [ ] No modifica secretos ni credenciales
- [ ] No incluye archivos `.env`

## Seguridad y privacidad

- [ ] No expone secretos ni información privada
- [ ] Enlaces externos revisados
- [ ] SVG sin scripts ni recursos externos

## Media y archivos

- [ ] Rutas nuevas o modificadas comprobadas
- [ ] Imágenes con texto alternativo descriptivo
- [ ] Recursos existentes conservados

## Performance, accesibilidad y SEO

<!-- Tamaño de recursos, legibilidad y texto alternativo cuando corresponda. -->

## Deploy

- [ ] Se publica con el README del perfil al integrar en `main`
- [ ] No requiere migraciones ni configuración adicional

## Riesgos y rollback

<!-- Dependencias externas, limitaciones y cómo revertir el cambio. -->

## Guía para reviewer

<!-- Archivos o decisiones que requieren atención. -->

## Checklist final

- [ ] Revisé el diff completo
- [ ] No quedan archivos temporales ni datos de prueba
- [ ] Los textos visibles están revisados
- [ ] La evidencia distingue checks ejecutados de verificaciones pendientes
- [ ] El PR está listo para review
