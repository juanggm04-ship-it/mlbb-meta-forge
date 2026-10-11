from pathlib import Path
import json, sys

TARGETS=[Path('index.html'),Path('roster/index.html'),Path('trends/index.html'),Path('compare/index.html'),Path('my-meta/index.html')]
INFO=Path('data/build-info.json')
RELEASE=Path('data/product-release.json')
PRIVACY=Path('privacy.html')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
for p in TARGETS+[INFO,RELEASE,PRIVACY]:need(p.exists(),f'Missing update-beacon dependency: {p}')
if INFO.exists() and RELEASE.exists():
    info=json.loads(INFO.read_text(encoding='utf-8'))
    release=json.loads(RELEASE.read_text(encoding='utf-8'))
    product=info.get('product_release') or {}
    need(product.get('release_id')==release.get('release_id'),'build-info product release id mismatch')
    need(product.get('title')==release.get('title'),'build-info product release title mismatch')
    need(bool(product.get('release_id')),'build-info lacks stable product release id')
for p in TARGETS:
    if not p.exists():continue
    text=p.read_text(encoding='utf-8')
    for token,msg in [
        ('id="mfUpdateBeacon"',f'Update beacon missing on {p}'),
        ('id="mf-update-beacon-runtime"',f'Update beacon runtime missing on {p}'),
        ("KEY='mf_seen_updates_v1'",f'Local seen-state key missing on {p}'),
        ('releaseChanged=prev.release_id!==current.release_id',f'Release comparison missing on {p}'),
        ('sourceChanged=prev.source_updated!==current.source_updated',f'Source measurement comparison missing on {p}'),
        ('patchChanged=prev.patch!==current.patch',f'Patch comparison missing on {p}'),
        ('if(!prev||prev.schema!==1){save(current);return}',f'First-visit quiet initialization missing on {p}'),
        ("dataLink.href=PREFIX+'trends/'",f'Data-change route missing on {p}'),
        ("productLink.href=PREFIX+'status/'",f'Product-change route missing on {p}'),
        ('Marcar novedades como vistas',f'Accessible dismiss label missing on {p}'),
    ]:need(token in text,msg)
    need('prev.fetched_at' not in text and 'current.fetched_at' not in text,f'Fetched-at must not trigger update beacon on {p}')
privacy=PRIVACY.read_text(encoding='utf-8') if PRIVACY.exists() else ''
need('estado de novedades que ya marcaste como vistas' in privacy,'Privacy page does not disclose local update seen-state')
need('no se envía a un servidor propio de Meta Forge' in privacy,'Privacy local-only disclosure missing')
if errors:
    print('UPDATE BEACON VALIDATION FAILED')
    for e in errors:print('- '+e)
    sys.exit(1)
print('Update beacon validation passed: 5 surfaces, first visit quiet, release/source/patch only, fetched_at ignored, local-only seen state disclosed.')
