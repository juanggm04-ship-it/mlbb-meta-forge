from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import sys

ROOT=Path('.').resolve()
PROJECT_PREFIX='/mlbb-meta-forge/'
class Links(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=True); self.hrefs=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()!='a': return
        d=dict(attrs); href=d.get('href')
        if href: self.hrefs.append(href)

errors=[]; pages=0; links=0
for page in Path('.').rglob('*.html'):
    if '.git' in page.parts: continue
    parser=Links()
    try: parser.feed(page.read_text(encoding='utf-8'))
    except Exception as exc:
        errors.append(f'HTML parse failed {page}: {exc}'); continue
    pages+=1
    for href in parser.hrefs:
        if href.startswith(('#','mailto:','tel:','javascript:','data:','blob:','//')): continue
        parts=urlsplit(href)
        if parts.scheme or parts.netloc: continue
        raw=unquote(parts.path)
        if not raw: continue
        if raw.startswith('/'):
            if raw.startswith(PROJECT_PREFIX): raw=raw[len(PROJECT_PREFIX):]
            else: continue
            target=ROOT/raw
        else:
            target=(page.parent/raw).resolve()
        try: target.relative_to(ROOT)
        except ValueError:
            errors.append(f'Link escapes project: {page} -> {href}'); continue
        if raw.endswith('/') or target.is_dir(): target=target/'index.html'
        links+=1
        if not target.exists():
            errors.append(f'Broken internal link: {page} -> {href} (expected {target.relative_to(ROOT)})')
if pages<170: errors.append(f'Internal-link audit coverage unexpectedly low: {pages} pages')
if errors:
    print('INTERNAL LINK VALIDATION FAILED')
    for e in errors[:100]: print('- '+e)
    if len(errors)>100: print(f'- ... and {len(errors)-100} more')
    sys.exit(1)
print(f'Internal-link validation passed: pages={pages}; resolvable local anchors checked={links}; no missing static targets.')
