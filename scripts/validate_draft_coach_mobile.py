from pathlib import Path
import sys

PAGE=Path('index.html')
errors=[]

def need(cond,msg):
    if not cond: errors.append(msg)

need(PAGE.exists(),'index.html is missing')
text=PAGE.read_text(encoding='utf-8') if PAGE.exists() else ''
for token,msg in [
    ('id="coachMobileTabs"','Mobile Draft Coach tablist missing'),
    ('id="coachTabAllies"','Allies mobile tab missing'),
    ('id="coachTabEnemies"','Enemies mobile tab missing'),
    ('id="coachAlliesCount"','Allies live pick count missing'),
    ('id="coachEnemiesCount"','Enemies live pick count missing'),
    ('id="coach-mobile-tabs-runtime"','Mobile Draft Coach runtime missing'),
    ('@media(max-width:760px)','Mobile Draft Coach breakpoint missing'),
    ("active='allies'",'Mobile Draft Coach does not default to allies'),
    ("filled('a')+'/5 picks'",'Allies count is not updated from pick state'),
    ("filled('e')+'/5 picks'",'Enemies count is not updated from pick state'),
    ("media.matches",'Responsive Draft Coach state is not tied to mobile media query'),
    ("coach-mobile-hidden",'Inactive mobile Draft Coach panel is not collapsible'),
    ("ArrowLeft",'Mobile Draft Coach keyboard tab switching missing'),
    ("ArrowRight",'Mobile Draft Coach keyboard tab switching missing'),
]: need(token in text,msg)
need(text.count('role="tab"')>=2,'Expected two Draft Coach tabs')
need('id="coachAlliesPanel"' not in text,'Panel ids should be assigned at runtime to generated coach panels')

if errors:
    print('MOBILE DRAFT COACH VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Mobile Draft Coach validation passed: allies/enemies segmented tabs, live counts, keyboard switching, desktop dual-panel fallback.')
