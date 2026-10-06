from pathlib import Path

p=Path('index.html')
html=p.read_text(encoding='utf-8')
if 'id="mfOnboarding"' in html:
    print('Onboarding already injected')
    raise SystemExit

css='''<style>
.profile-strip{margin-top:14px;padding:17px 18px;border:1px solid #2a3b58;border-radius:18px;background:linear-gradient(145deg,#0b1322,#15172a)}
.profile-strip[hidden]{display:none}.profile-head{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}.profile-head h4{margin:3px 0;font-size:18px}.profile-head p{margin:0;color:#8392ad;font-size:11px}.profile-edit{border:1px solid #344662;background:#101a2c;color:#dce8f8;border-radius:10px;padding:8px 10px;cursor:pointer;font-size:11px}.profile-picks{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-top:12px}.profile-pick{display:block;padding:11px;border:1px solid #263752;border-radius:12px;background:#0c1422;color:#dfe9f8;text-decoration:none}.profile-pick b{display:block;font-size:12px}.profile-pick span{display:block;margin-top:3px;color:#8291aa;font-size:10px}.profile-role{display:inline-flex;margin-top:8px;padding:6px 9px;border:1px solid #46e6ff55;border-radius:999px;color:#46e6ff;font-size:10px;font-weight:800}.onboarding{border:1px solid #33445f;border-radius:22px;background:#0b1220;color:#edf4ff;padding:0;max-width:720px;width:calc(100% - 28px);box-shadow:0 24px 80px #000a}.onboarding::backdrop{background:#03060bcc;backdrop-filter:blur(6px)}.onboarding-inner{padding:24px}.onboarding h2{margin:4px 0 8px;font-size:28px}.onboarding p{color:#91a0ba;line-height:1.5}.onboard-step{margin-top:18px}.onboard-step h3{font-size:13px;margin:0 0 10px}.role-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}.role-btn{border:1px solid #30415d;background:#10192a;color:#dce8f8;border-radius:12px;padding:11px 6px;cursor:pointer;font-size:11px;font-weight:800}.role-btn.active{background:#46e6ff;color:#07111d;border-color:#46e6ff}.hero-select-search{width:100%;box-sizing:border-box;border:1px solid #30415d;background:#0a111e;color:#eef5ff;border-radius:11px;padding:10px 12px}.hero-choice-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:9px;max-height:240px;overflow:auto}.hero-choice{border:1px solid #293a55;background:#0d1625;color:#dfe9f8;border-radius:10px;padding:9px;cursor:pointer;text-align:left;font-size:11px}.hero-choice.active{border-color:#8b5cff;background:#18142c}.onboard-actions{display:flex;justify-content:space-between;gap:10px;align-items:center;margin-top:18px;flex-wrap:wrap}.onboard-primary,.onboard-skip{border-radius:11px;padding:10px 13px;cursor:pointer;font-weight:800}.onboard-primary{border:0;background:linear-gradient(135deg,#46e6ff,#8b5cff);color:#07101c}.onboard-skip{border:1px solid #34455f;background:#10192a;color:#cdd9eb}.onboard-count{font-size:11px;color:#8392ac}@media(max-width:700px){.profile-picks,.hero-choice-grid{grid-template-columns:1fr 1fr}.role-grid{grid-template-columns:repeat(3,1fr)}}
</style>'''
html=html.replace('</head>',css+'</head>')

profile='''<section id="personalProfile" class="profile-strip" hidden aria-labelledby="personalProfileTitle"><div class="profile-head"><div><small>FOR YOU</small><h4 id="personalProfileTitle">Tu meta personal</h4><p id="personalProfileSub"></p></div><button id="editProfile" class="profile-edit" type="button">Editar preferencias</button></div><span id="personalRole" class="profile-role"></span><div id="personalPicks" class="profile-picks"></div></section>'''
anchor='id="watchlistPanel"'
pos=html.find(anchor)
if pos!=-1:
    html=html[:pos-9]+profile+html[pos-9:]
else:
    html=html.replace('</main>',profile+'</main>',1)

modal='''<dialog id="mfOnboarding" class="onboarding"><div class="onboarding-inner"><small>PERSONALIZA META FORGE</small><h2>Haz que la portada juegue en tu línea</h2><p>Elige tu rol principal y entre 3 y 5 héroes favoritos. Todo se guarda únicamente en este navegador.</p><div class="onboard-step"><h3>1. Tu rol principal</h3><div id="roleGrid" class="role-grid"><button class="role-btn" data-role="Jungle" type="button">Jungle</button><button class="role-btn" data-role="EXP" type="button">EXP</button><button class="role-btn" data-role="Mid" type="button">Mid</button><button class="role-btn" data-role="Gold" type="button">Gold</button><button class="role-btn" data-role="Roam" type="button">Roam</button></div></div><div class="onboard-step"><h3>2. Tus héroes favoritos</h3><input id="onboardHeroSearch" class="hero-select-search" type="search" placeholder="Buscar héroe…" autocomplete="off"><div id="heroChoiceGrid" class="hero-choice-grid"></div></div><div class="onboard-actions"><div><button id="skipOnboarding" class="onboard-skip" type="button">Ahora no</button></div><div><span id="onboardCount" class="onboard-count">0/5 seleccionados</span> <button id="saveOnboarding" class="onboard-primary" type="button">Guardar</button></div></div></div></dialog>'''
html=html.replace('</body>',modal+'</body>')

js=r'''<script>
(()=>{
const PROFILE='mf_profile_v1',WATCH='mf_watchlist_v1';
const dlg=document.getElementById('mfOnboarding'),grid=document.getElementById('heroChoiceGrid'),search=document.getElementById('onboardHeroSearch'),count=document.getElementById('onboardCount');
if(!dlg||!grid)return;
const read=(k,f)=>{try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(f))}catch{return f}};
const slug=n=>n.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/&/g,'and').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const heroes=(window.DATA?.heroes||((typeof DATA!=='undefined'&&DATA?.heroes)?DATA.heroes:[]));
let role=null,selected=[];
function currentProfile(){const p=read(PROFILE,null);return p&&typeof p==='object'?p:null}
function setRole(v){role=v;document.querySelectorAll('.role-btn').forEach(b=>b.classList.toggle('active',b.dataset.role===v))}
function toggleHero(name){if(selected.includes(name))selected=selected.filter(x=>x!==name);else if(selected.length<5)selected=[...selected,name];renderChoices()}
function renderChoices(){const q=(search.value||'').toLowerCase().trim();const list=heroes.filter(h=>!q||h.name.toLowerCase().includes(q)).slice(0,45);grid.innerHTML=list.map(h=>`<button class="hero-choice ${selected.includes(h.name)?'active':''}" data-hero="${h.name.replace(/"/g,'&quot;')}" type="button"><b>${h.name}</b><br><span>${h.lane||''} · ${Number.isFinite(h.wr)?h.wr.toFixed(2)+'% WR':'—'}</span></button>`).join('');grid.querySelectorAll('[data-hero]').forEach(b=>b.onclick=()=>toggleHero(b.dataset.hero));count.textContent=`${selected.length}/5 seleccionados`}
function openProfile(){const p=currentProfile();role=p?.role||null;selected=Array.isArray(p?.heroes)?p.heroes.slice(0,5):[];setRole(role);renderChoices();dlg.showModal()}
function renderProfile(){const p=currentProfile(),box=document.getElementById('personalProfile');if(!box||!p||p.skipped){if(box)box.hidden=true;return}box.hidden=false;document.getElementById('personalRole').textContent=p.role||'Sin rol';document.getElementById('personalProfileSub').textContent=`Recomendaciones rápidas para ${p.role||'tu rol'} y tus héroes seguidos.`;const candidates=heroes.filter(h=>h.lane===p.role).sort((a,b)=>(b.wr??-1)-(a.wr??-1)).slice(0,3);document.getElementById('personalPicks').innerHTML=candidates.map(h=>`<a class="profile-pick" href="heroes/${slug(h.name)}/"><b>${h.name}</b><span>${Number.isFinite(h.wr)?h.wr.toFixed(2)+'% WR':'—'} · ${Number.isFinite(h.ban)?h.ban.toFixed(2)+'% ban':'—'}</span></a>`).join('')||'<div class="watch-empty">Aún no hay suficientes datos para este rol.</div>'}
document.querySelectorAll('.role-btn').forEach(b=>b.onclick=()=>setRole(b.dataset.role));search.addEventListener('input',renderChoices);
document.getElementById('saveOnboarding').onclick=()=>{if(!role){document.querySelector('.role-grid')?.animate([{opacity:.5},{opacity:1}],{duration:240});return}if(selected.length<3){count.textContent='Elige al menos 3 héroes';return}localStorage.setItem(PROFILE,JSON.stringify({role,heroes:selected,updatedAt:Date.now()}));const watch=read(WATCH,[]);localStorage.setItem(WATCH,JSON.stringify([...new Set([...(Array.isArray(watch)?watch:[]),...selected])]));dlg.close();renderProfile();window.MFWatchlist?.render?.()};
document.getElementById('skipOnboarding').onclick=()=>{localStorage.setItem(PROFILE,JSON.stringify({skipped:true,updatedAt:Date.now()}));dlg.close()};
document.getElementById('editProfile')?.addEventListener('click',openProfile);
renderProfile();
const initial=currentProfile();if(!initial)setTimeout(openProfile,650);
})();
</script>'''
html=html.replace('</body>',js+'</body>')
p.write_text(html,encoding='utf-8')
print('Injected personalized onboarding and profile strip')
