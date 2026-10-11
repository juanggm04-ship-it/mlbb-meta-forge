"""Validate public snapshot signals and delivery of shared responsive styles."""
from html.parser import HTMLParser
from pathlib import Path
import json

class Home(HTMLParser):
    def __init__(self):
        super().__init__();self.signals={};self.current=None;self.ids=[];self.styles=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.append(a['id'])
        if tag=='link' and a.get('id')=='mf-product-design':self.styles.append(a.get('href'))
        if tag=='a' and a.get('data-signal'):
            self.current=a['data-signal'];self.signals[self.current]={'key':a.get('data-hero-key'),'href':a.get('href'),'text':''}
    def handle_data(self,data):
        if self.current:self.signals[self.current]['text']+=data
    def handle_endtag(self,tag):
        if tag=='a':self.current=None

page=Path('index.html').read_text(encoding='utf-8')
home=Home();home.feed(page)
assert len(home.ids)==len(set(home.ids)), 'Homepage contains duplicate control IDs'
assert set(home.signals)=={'wr','ban','pick'}, 'Homepage must expose the three snapshot signals'
live=json.loads(Path('data/live-meta.json').read_text())
by_key={h['key']:h for h in live['heroes']}
for metric,signal in home.signals.items():
    row=by_key[signal['key']]
    assert row[metric]==max(h[metric] for h in live['heroes']),f'Wrong {metric} leader'
    assert f'{row[metric]:.2f}%' in signal['text'],f'Stale {metric} display'
    assert Path(signal['href'],'index.html').exists(),f'Broken {metric} hero link'
assert live['source_updated'] in page, 'Homepage must disclose source measurement time'
assert 'setTimeout(openProfile,650)' not in page, 'Personalization must not block a first visit'
assert './assets/product-design.css' in Path('sw.js').read_text(), 'Design stylesheet must be precached for offline use'
paths=[Path('index.html'),Path('roster/index.html'),Path('explore/index.html'),Path('trends/index.html'),Path('compare/index.html'),Path('my-meta/index.html'),Path('methodology.html')]+list(Path('stats/heroes').glob('*/index.html'))
for path in paths:
    parser=Home();parser.feed(path.read_text(encoding='utf-8'))
    assert len(parser.styles)==1,f'Expected one product stylesheet on {path}'
    assert (path.parent/parser.styles[0]).resolve()==Path('assets/product-design.css').resolve(),f'Wrong stylesheet URL on {path}'
print(f'Product design validation passed: canonical leaders and measurement date, unique IDs, optional profile, shared stylesheet on {len(paths)} pages, offline precache')
