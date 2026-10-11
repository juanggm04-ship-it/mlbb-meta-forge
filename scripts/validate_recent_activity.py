from pathlib import Path
import re,sys

HOME=Path('index.html')
PRIVACY=Path('privacy.html')
CORE=[Path('index.html'),Path('roster/index.html'),Path('explore/index.html'),Path('trends/index.html'),Path('compare/index.html'),Path('my-meta/index.html')]
STATS=sorted(Path('stats/heroes').glob('*/index.html'))
EDITORIAL=sorted(Path('heroes').glob('*/index.html'))
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

need(HOME.exists(),'Homepage missing')
need(PRIVACY.exists(),'Privacy page missing')
need(len(STATS)==133,f'Expected 133 live hero pages, got {len(STATS)}')
need(len(EDITORIAL)==34,f'Expected 34 editorial hero pages, got {len(EDITORIAL)}')

if HOME.exists():
    home=HOME.read_text(encoding='utf-8')
    for token,msg in [
        ('id="mfResumePanel"','Resume panel missing'),
        ('id="mfResumeList"','Resume list missing'),
        ('id="mfResumeClear"','Resume clear control missing'),
        ('Continuar donde lo dejaste','Resume title missing'),
        ('máximo 8 destinos recientes','Local retention limit disclosure missing'),
        ('id="mf-recent-activity-style"','Resume style missing')]:
        need(token in home,msg)
    hub=home.find('id="homeProductHub"');resume=home.find('id="mfResumePanel"')
    need(hub!=-1 and resume>hub,'Resume panel must follow the homepage decision hub')

for path in CORE+STATS+EDITORIAL:
    if not path.exists():
        errors.append(f'Recent activity target missing: {path}')
        continue
    text=path.read_text(encoding='utf-8')
    need(text.count('id="mf-recent-activity-runtime"')==1,f'Expected one recent activity runtime on {path}')
    m=re.search(r'<script id="mf-recent-activity-runtime">(.*?)</script>',text,re.S)
    if not m: continue
    runtime=m.group(1)
    for token,msg in [
        ("KEY='mf_recent_activity_v1'",'local activity key missing'),
        ('LIMIT=8','history limit guard missing'),
        ('localStorage','localStorage runtime missing'),
        ('safeRoute','internal route guard missing'),
        ("addEventListener('pagehide',record",'pagehide refresh missing')]:
        need(token in runtime,f'{msg} on {path}')
    need('fetch(' not in runtime,f'Recent activity must not send network requests on {path}')

if HOME.exists():
    runtime=re.search(r'<script id="mf-recent-activity-runtime">(.*?)</script>',HOME.read_text(encoding='utf-8'),re.S)
    if runtime:
        need('.slice(0,3)' in runtime.group(1),'Homepage resume panel must show at most 3 recent destinations')
        need("localStorage.removeItem(KEY)" in runtime.group(1),'User must be able to clear recent activity')

if PRIVACY.exists():
    privacy=PRIVACY.read_text(encoding='utf-8')
    need('historial reciente para “Continuar donde lo dejaste”' in privacy,'Privacy page does not disclose recent-activity local storage')
    need('no se envía a un servidor propio de Meta Forge' in privacy,'Privacy local-only disclosure missing')

if errors:
    print('RECENT ACTIVITY VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print(f'Recent activity validation passed: core={len(CORE)}; live_heroes={len(STATS)}; editorial_heroes={len(EDITORIAL)}; history_limit=8; homepage_limit=3; local-only; clearable; no network requests.')
