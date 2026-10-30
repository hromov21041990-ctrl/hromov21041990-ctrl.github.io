document.querySelector('.menu')?.addEventListener('click',e=>{const n=document.querySelector('.nav nav');const open=n.classList.toggle('open');e.currentTarget.setAttribute('aria-expanded',String(open));});
const money=n=>new Intl.NumberFormat('ru-RU').format(n)+' ₽';
const plural=(n,forms)=>n%100>=11&&n%100<=14?forms[2]:n%10===1?forms[0]:n%10>=2&&n%10<=4?forms[1]:forms[2];
const trackGoal=(name,params={})=>{if(typeof window.ym==='function')window.ym(91165337,'reachGoal',name,{page:location.pathname,...params});};
document.addEventListener('click',event=>{const link=event.target.closest('a[href]');if(!link)return;const href=link.getAttribute('href')||'';if(href.startsWith('tel:'))trackGoal('phone_click');else if(href.startsWith('mailto:'))trackGoal('email_click');else if(href==='/kontakty/'&&link.classList.contains('btn'))trackGoal('contact_cta_click');else if(link.closest('[data-product]'))trackGoal('catalog_product_click',{product:link.closest('[data-product]').dataset.product});});
const normalizeSearch=value=>{
  let text=String(value||'').toLocaleLowerCase('ru-RU').replaceAll('ё','е').replace(/[^a-zа-я0-9]+/g,' ').trim();
  for(const [source,target] of [['био теп','biotep'],['биотеп','biotep'],['фачи','faci'],['вулкан','vulkan'],['зота','zota'],['старт','start']])text=text.replaceAll(source,target);
  return text;
};
const filter=()=>{const q=normalizeSearch(document.querySelector('#search')?.value);const brand=document.querySelector('#brand-filter')?.value||'';const series=document.querySelector('#series-filter')?.value||'';let count=0;const cards=[...document.querySelectorAll('[data-product]')];cards.forEach((el,i)=>{if(!el.dataset.order)el.dataset.order=String(i);const haystack=normalizeSearch(el.dataset.search||el.dataset.name);const yes=haystack.includes(q)&&(!brand||el.dataset.brand===brand)&&(!series||el.dataset.series===series);el.hidden=!yes;if(yes)count++;});const sort=document.querySelector('#sort')?.value;const numeric=(el,key)=>el.dataset[key]!==''&&Number.isFinite(Number(el.dataset[key]))?Number(el.dataset[key]):Infinity;if(sort){const ordered=[...cards].sort((a,b)=>sort==='price-asc'?numeric(a,'price')-numeric(b,'price'):sort==='price-desc'?numeric(b,'price')-numeric(a,'price'):sort==='power-asc'?numeric(a,'power')-numeric(b,'power'):Number(a.dataset.order)-Number(b.dataset.order));const grid=document.querySelector('.vulkan-products');if(grid)ordered.forEach(el=>grid.appendChild(el));}const empty=document.querySelector('#empty');if(empty)empty.hidden=count>0;const countEl=document.querySelector('#count');if(countEl)countEl.textContent=count+' '+plural(count,countEl.dataset.noun==='models'?['модель','модели','моделей']:['товар','товара','товаров']);};
document.querySelector('#search')?.addEventListener('input',filter);document.querySelector('#brand-filter')?.addEventListener('change',filter);
document.querySelector('#series-filter')?.addEventListener('change',filter);document.querySelector('#sort')?.addEventListener('change',filter);
const clearFilters=()=>{for(const id of ['search','brand-filter','series-filter']){const el=document.getElementById(id);if(el)el.value='';}const sort=document.querySelector('#sort');if(sort)sort.value='default';filter();};
document.querySelector('#clear-filters')?.addEventListener('click',clearFilters);
document.querySelector('#empty-clear')?.addEventListener('click',clearFilters);
if(document.querySelector('[data-product]'))filter();
window.addEventListener('pageshow',()=>requestAnimationFrame(filter));
document.querySelectorAll('.thumbs button').forEach(b=>b.addEventListener('click',()=>{const image=document.querySelector('#main-image');image.src=b.dataset.src;image.alt=b.dataset.alt||image.alt;}));
const updateConfigurationFacts=(product,sku)=>{
  const view=product.configuration_views?.[sku];
  if(!view)return;
  const description=document.querySelector('#configuration-description');
  if(description)description.textContent=view.description;
  const body=document.querySelector('#configuration-specs tbody');
  if(body)body.replaceChildren(...Object.entries(view.specs).map(([label,value])=>{
    const row=document.createElement('tr');
    const heading=document.createElement('th');heading.scope='row';heading.textContent=label;
    const cell=document.createElement('td');cell.textContent=value;
    row.append(heading,cell);return row;
  }));
};
if(document.querySelector('#product-data')){const p=JSON.parse(document.querySelector('#product-data').textContent);const update=()=>{const v=p.variants[Number(document.querySelector('#variant')?.value||0)];const bunker=p.bunkers?.[Number(document.querySelector('#bunker')?.value||0)];const price=v?v.price+(bunker?.extra||0):p.price;document.querySelector('#chosen-price').textContent=price===null?'Цена по запросу':money(price);const inc=document.querySelector('#includes');if(inc&&v){inc.replaceChildren(...v.includes.map(text=>{const li=document.createElement('li');li.textContent=text;return li;}));}const offer=p.offers?.find(o=>o.variant_id===v?.option_id&&o.bunker_id===bunker?.option_id);const sku=offer?.sku||p.sku;document.querySelector('#product-sku').textContent=sku;updateConfigurationFacts(p,sku);const selection=p.name+'\nАртикул: '+sku+(v?'\nКомплектация: '+v.name:'')+(bunker?'\nБункер: '+bunker.name:'')+'\nЦена: '+(price===null?'Уточнить':money(price));document.querySelector('#copy-quote').dataset.text=selection;};document.querySelector('#variant')?.addEventListener('change',update);document.querySelector('#bunker')?.addEventListener('change',update);document.querySelector('#copy-quote')?.addEventListener('click',async e=>{trackGoal('quote_copy',{product:p.id});try{await navigator.clipboard.writeText(e.currentTarget.dataset.text);e.currentTarget.textContent='Выбор скопирован';}catch{document.querySelector('#copy-status').textContent=e.currentTarget.dataset.text;}});update();}
