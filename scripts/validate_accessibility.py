from pathlib import Path
import re,sys

errors=[]; checked=0
for path in Path('.').rglob('*.html'):
    if '.git' in path.parts: continue
    text=path.read_text(encoding='utf-8')
    if '<main' not in text: continue
    checked+=1
    if 'id="mf-accessibility-style"' not in text: errors.append(f'Accessibility style missing: {path}')
    m=re.search(r'<a class="mf-skip-link" href="#([^"]+)">Saltar al contenido</a>',text)
    if not m: errors.append(f'Skip link missing: {path}'); continue
    target=m.group(1)
    if not re.search(rf'\bid=["\']{re.escape(target)}["\']',text): errors.append(f'Skip target #{target} missing: {path}')
    if ':focus-visible' not in text: errors.append(f'Visible focus rule missing: {path}')
if checked<170: errors.append(f'Accessibility coverage unexpectedly low: {checked} pages')
if errors:
    print('ACCESSIBILITY VALIDATION FAILED')
    for e in errors[:80]: print('- '+e)
    if len(errors)>80: print(f'- ... and {len(errors)-80} more')
    sys.exit(1)
print(f'Accessibility validation passed: skip-to-content + visible keyboard focus on {checked} pages with main content.')
