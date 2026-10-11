from pathlib import Path
import re

STYLE='''<style id="mf-accessibility-style">.mf-skip-link{position:fixed;left:12px;top:12px;z-index:100000;transform:translateY(-160%);padding:10px 13px;border-radius:10px;background:#55e6ff;color:#061019;font:900 11px/1 system-ui;text-decoration:none;box-shadow:0 10px 30px #0007}.mf-skip-link:focus{transform:translateY(0)}:focus-visible{outline:2px solid #58e7ff!important;outline-offset:3px!important}</style>'''
count=0
for path in Path('.').rglob('*.html'):
    if '.git' in path.parts: continue
    text=path.read_text(encoding='utf-8')
    if '<main' not in text or 'id="mf-accessibility-style"' in text: continue
    m=re.search(r'<main\b([^>]*)>',text,re.I)
    if not m: continue
    attrs=m.group(1)
    idm=re.search(r'\bid=["\']([^"\']+)["\']',attrs,re.I)
    target=idm.group(1) if idm else 'main-content'
    if not idm:
        original=m.group(0)
        replacement=original[:-1]+' id="main-content">'
        text=text[:m.start()]+replacement+text[m.end():]
    skip=f'<a class="mf-skip-link" href="#{target}">Saltar al contenido</a>'
    body=re.search(r'<body\b[^>]*>',text,re.I)
    if not body: continue
    text=text[:body.end()]+skip+text[body.end():]
    text=text.replace('</head>',STYLE+'</head>',1)
    path.write_text(text,encoding='utf-8')
    count+=1
print(f'Accessibility shell injected into {count} HTML pages with main content')
