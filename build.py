import json,os,re,shutil,hashlib,html as esc
from pathlib import Path
from urllib.parse import urlparse
from lxml import html,etree
from seo import metadata as seo_metadata, prepare_body, structured_data
from vulkan import SERIES as VULKAN_SERIES, catalog_body as vulkan_catalog, breadcrumbs as vulkan_crumbs, product_facts as vulkan_facts, documents as vulkan_documents
from catalog_identity import prepare_catalog
from faci import breadcrumbs as faci_crumbs, facts as faci_facts, documents as faci_documents, intro as faci_intro, configuration_views as faci_views, specifications as faci_specs
from start import breadcrumbs as start_crumbs, facts as start_facts, documents as start_documents, intro as start_intro, configuration_views as start_views, specifications as start_specs
from zota import CATEGORIES as ZOTA_CATEGORIES, catalog_body as zota_catalog, breadcrumbs as zota_crumbs, facts as zota_facts, documents as zota_documents
from biotep import breadcrumbs as biotep_crumbs, facts as biotep_facts, documents as biotep_documents, intro as biotep_intro
from biotep_spares import CATEGORIES as BIOTEP_SPARE_CATEGORIES, catalog_body as biotep_spares_catalog, breadcrumbs as biotep_spares_crumbs, facts as biotep_spares_facts
from vulkan_spares import CATEGORIES as VULKAN_SPARE_CATEGORIES, catalog_body as vulkan_spares_catalog, breadcrumbs as vulkan_spares_crumbs, facts as vulkan_spares_facts
ROOT=Path(__file__).resolve().parent;DIST=ROOT/'dist'
if DIST.exists():shutil.rmtree(DIST)
DIST.mkdir(exist_ok=True)
PAGES=json.loads((ROOT/'data/pages.json').read_text());PRODUCTS,PELLET_TYPES=prepare_catalog();SITE=json.loads((ROOT/'data/site.json').read_text())
SEO_REDIRECTS=json.loads((ROOT/'data/seo-redirects.json').read_text())
ORIGIN=os.environ.get('SITE_ORIGIN','https://pelletsgrupp-migration.hromov-aa.chatgpt.site').rstrip('/');PREVIEW=os.environ.get('PRODUCTION','0')!='1'
JS_VERSION=hashlib.sha256((ROOT/'site.js').read_bytes()).hexdigest()[:12]
def e(s):return esc.escape(str(s),quote=True)
def normalize_business_claims(s):
 s=re.sub(r'<p>Sed feugiat porttitor nunc, non dignissim ipsum vestibulum in\..*?vel odio\.</p>','',s,flags=re.S)
 replacements={
  'производство высококачественных пеллет':'поставку качественных пеллет',
  'Производство, оборудование и сервис под ключ':'Топливо, оборудование и сервис под ключ',
  'Производство и офис':'Офис и поставки',
  'является производителем пеллетов':'поставляет топливные пеллеты',
  'а также является производителем пеллетов':'а также поставляет топливные пеллеты',
  'PelletsGrupp производит цилиндрические гранулы':'PelletsGrupp поставляет цилиндрические гранулы',
  'Компания PelletsGrupp производит и продает древесные пеллеты':'Компания PelletsGrupp закупает у производителей и продаёт древесные пеллеты',
  'Мы выпускаем от 700 до 900 тонн пеллет в месяц, предлагая':'Предлагаем',
  'Пеллеты PelletsGrupp производятся из хвойного сырья':'Пеллеты в ассортименте PelletsGrupp изготовлены из хвойного сырья',
  'купить топливные пеллеты у производителя':'купить топливные пеллеты в PelletsGrupp',
  'купить топливные пеллеты напрямую у производителя':'купить топливные пеллеты в PelletsGrupp',
  'Мы производим пеллеты из чистой хвойной древесины':'Мы поставляем пеллеты из хвойного сырья',
  'На собственном производстве мы выпускаем 700–900 тонн топливных гранул в месяц.':'Мы закупаем топливные гранулы у производителей и поставляем их для частных домов, котельных и предприятий.',
  'Производство пеллет премиум-качества':'Поставка пеллет для дома и бизнеса',
  'собственное производство':'поставка топлива',
 }
 for old,new in replacements.items():s=s.replace(old,new)
 return s
def normalize_phone(s):
 s=re.sub(r'\+7[\s\u00a0]*\(930\)[\s\u00a0]*316[-–]18[-–]55','+7 (343) 345-52-25',s)
 return re.sub(r'\+7[\s\u00a0]*\(343\)[\s\u00a0]*226[-–]0?2?[-–]28','+7 (343) 345-52-25',s)
def plain(s):
 s=normalize_business_claims(s)
 try:return normalize_business_claims(normalize_phone(' '.join(html.fromstring('<div>'+s+'</div>').text_content().split())))
 except:return normalize_business_claims(normalize_phone(s))
page_ids={p['ID']:p['path'] for p in PAGES};paths={p['path'] for p in PAGES};paths|={p['path'] for p in PRODUCTS}
for f in SITE.get('folders',{}).values():
 if f.get('INDEX_ID') in page_ids:page_ids[f['INDEX_ID']]='/'+f['CODE'].strip('/')+'/'
def rewrite(href):
 m=re.match(r'page:#landing(\d+)',href or '')
 if m:return page_ids.get(m.group(1),'/katalog/')
 if href.startswith('tel:'):return 'tel:+73433455225'
 if href.startswith('mailto:#'):return 'mailto:office@pelletsgrupp.ru'
 if href.startswith(('https://pelletsgrupp.ru','http://pelletsgrupp.ru')):return urlparse(href).path or '/'
 return href
allowed={'p','br','strong','b','em','i','ul','ol','li','a','span','h2','h3','h4','table','tbody','thead','tr','td','th','blockquote'}
def rich(s):
 s=normalize_business_claims(normalize_phone(s))
 root=html.fromstring('<div>'+s+'</div>')
 for node in list(root.iterdescendants()):
  if node.tag in ('script','style','iframe','form'):node.drop_tree();continue
  if node.tag not in allowed:node.drop_tag();continue
  href=node.get('href');node.attrib.clear()
  if node.tag=='a' and href:
   href=rewrite(href)
   if href.startswith(('/','https://','http://','tel:','mailto:','#')):node.set('href',href)
 return (root.text or '')+''.join(html.tostring(c,encoding='unicode') for c in root)
logo='<span class="brand-logo"><img src="/assets/pelletsgrupp-logo.png" alt="PelletsGrupp"></span>'
head='''<header><div class="wrap"><div class="topline"><span>Екатеринбург · доставка по Свердловской области</span><span>Пн–Пт, 09:00–18:00</span></div><div class="nav"><a class="brand brand-image" href="/" aria-label="PelletsGrupp — главная">'''+logo+'''</a><button class="menu" aria-label="Открыть меню" aria-expanded="false">Меню</button><nav aria-label="Главная навигация"><a href="/pellety/">Пеллеты</a><a href="/katalog/">Котлы и горелки</a><a href="/servisiremont/">Сервис</a><a href="/blog/">Блог</a><a href="/kontakty/">Контакты</a></nav><a class="phone" href="tel:+73433455225">+7 (343) 345-52-25</a></div></div></header>'''
foot='''<footer><div class="wrap"><div class="footgrid"><div><a class="brand brand-image footer-logo" href="/" aria-label="PelletsGrupp — главная">'''+logo+'''</a><p>Пеллетное отопление с подбором оборудования,<br>поставкой топлива и сервисным сопровождением.</p></div><nav><a href="/katalog/">Каталог оборудования</a><a href="/pellety/">Пеллеты</a><a href="/dostavka/">Доставка</a><a href="/servisiremont/">Сервис и ремонт</a><a href="/blog/">Полезные статьи</a><a href="/o-nas/">О компании</a></nav><div><a class="phone" style="display:block" href="tel:+73433455225">+7 (343) 345-52-25</a><p><a href="mailto:office@pelletsgrupp.ru">office@pelletsgrupp.ru</a><br>Екатеринбург, ул. Лукиных, 1, оф. 4</p><a class="text-link" href="/kontakty/">Все контакты</a></div></div><div class="legal">© PelletsGrupp. ООО «ПЕЛЛЕТС ГРУПП», ИНН 6678134556. <a href="/soglasie-na-obrabotku-personalnyh-dannyh/">Обработка персональных данных</a></div></div></footer><a class="mobile-call" href="tel:+73433455225" aria-label="Позвонить">☎</a>'''
foot=foot.replace('/soglasie-na-obrabotku-personalnyh-dannyh/','/pustayastranitsa_qewx/')
head=head.replace('<a href="/servisiremont/">Сервис</a>','<a href="/otoplenie/">Монтаж</a><a href="/servisiremont/">Сервис</a>')
foot=foot.replace('<a href="/servisiremont/">Сервис и ремонт</a>','<a href="/otoplenie/">Монтаж отопления</a><a href="/servisiremont/">Сервис и ремонт</a>')
head=prepare_body('',head)
foot=prepare_body('',foot)
written={}
def write(path,title,body,desc='',schema=None):
 out=DIST/path.strip('/')/'index.html' if path!='/' else DIST/'index.html';out.parent.mkdir(parents=True,exist_ok=True)
 title,desc=seo_metadata(path,title,desc)
 body=prepare_body(path,body)
 original_schema=schema
 schema=structured_data(path,body,schema,ORIGIN)
 desc=normalize_business_claims((desc or f'{title}. Пеллетное отопление, оборудование, топливо, монтаж и сервис PelletsGrupp в Екатеринбурге.').strip())
 robots='<meta name="robots" content="noindex,nofollow">' if PREVIEW else '<meta name="robots" content="noindex,follow">' if path=='/404/' else ''
 note='<div class="testnote">Тестовая версия переноса · заявки по телефону</div>' if PREVIEW else ''
 ld='<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('</','<\\/')+'</script>' if schema else ''
 extra_style='<link rel="stylesheet" href="/vulkan.css">' if path.startswith('/vulkan/') or (original_schema and original_schema.get('category','').startswith('Vulkan ')) else ''
 out.write_text(f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(desc)}">{robots}<link rel="canonical" href="{e(ORIGIN+path)}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website"><meta property="og:url" content="{e(ORIGIN+path)}"><meta property="og:site_name" content="PelletsGrupp"><link rel="stylesheet" href="/site.css">{extra_style}{ld}<script src="/site.js?v={JS_VERSION}" defer></script></head><body>{note}{head}<main>{body}</main>{foot}</body></html>');written[path]=title
def money(n):
 if n is None:return 'Цена по запросу'
 value=float(n)
 text=f'{int(value):,}' if value.is_integer() else f'{value:,.2f}'
 return text.replace(',','\u202f').replace('.',',')+' ₽'
def card(p):
 image=p['images'][0] if p['images'] else '/assets/archive-40177.webp'
 badge=p.get('display_brand',p['brand'])+(' · '+p['series_name'] if p.get('series_name') else '')
 meta='Комплектация на выбор' if p.get('variants') else 'Подбор, доставка и сервис'
 if p.get('series'):
  facts=[]
  if p.get('power') is not None:facts.append(f'{p["power"]:g} кВт')
  bunker=p.get('specs',{}).get('Ёмкость бункера, л')
  if bunker:facts.append('Бункер '+bunker+' л')
  meta=' · '.join(facts) or 'Мощность уточняется при подборе'
 elif p['brand']=='FACI' and p.get('power_label'):
  meta=p['power_label']+' · базовый бункер '+p['specs'].get('Емкость бункера','уточняется')
 elif p['brand']=='СТАРТ':
  meta=p['power_label']+' · '+p['specs'].get('Площадь отопления по данным производителя','площадь уточняется')
 elif p['brand']=='ZOTA':
  meta=p['zota_category_label']+(' · '+str(p['power'])+' кВт' if p.get('power') else '')+' · арт. '+p['manufacturer_article']
 elif p.get('product_type')=='biotep_spare':
  meta=p['biotep_spare_category_label']+(' · код '+p['manufacturer_article'] if p.get('manufacturer_article') else '')
 elif p.get('product_type')=='vulkan_spare':
  meta=p['vulkan_spare_category_label']
 attrs=f' data-series="{e(p.get("series",""))}" data-price="{p["price"] if p["price"] is not None else ""}" data-power="{p.get("power") if p.get("power") is not None else ""}" data-search="{e(p["name"]+" "+p["brand"]+" "+p["sku"]+" "+" ".join(o["sku"] for o in p.get("offers",[])))}"'
 return f'<article class="card" data-product="{p["id"]}" data-name="{e(p["name"])}" data-brand="{e(p["brand"])}"{attrs}><a class="image" href="{p["path"]}"><img src="{image}" alt="{e(p["name"])}" loading="lazy" decoding="async"></a><div class="card-body"><span class="badge">{e(badge)}'+(' · наш флагман' if p['brand']=='BIOTEP' and p.get('product_type')!='biotep_spare' else '')+f'</span><h3><a href="{p["path"]}">{e(p["name"])}</a></h3><div class="meta">{e(meta)}</div><p class="sku-line">Артикул: <span>{e(p["sku"])}</span></p><div class="price">{("от " if p.get("variants") else "")+money(p["price"])}</div><a class="btn light" href="{p["path"]}">Выбрать модель →</a></div></article>'
def cta():return '<section class="section"><div class="wrap"><div class="cta"><div><h2>Подберём отопление для вашего дома</h2><p>Обсудим оборудование, топливо и обслуживание.</p></div><a class="btn lime" href="/kontakty/">Связаться со специалистом →</a></div></div></section>'
def crumbs(title):return f'<div class="wrap crumbs"><a href="/">Главная</a> / {e(title)}</div>'
def tiles(items):return '<div class="grid">'+''.join(f'<a class="tile" href="{p["path"]}"><span class="badge">Полезно знать</span><h3>{e(p["TITLE"])}</h3><span class="text-link">Читать статью →</span></a>' for p in items)+'</div>'
brands=['BIOTEP','FACI','Вулкан','СТАРТ','ZOTA'];brandroutes={'BIOTEP':'/biotep/','FACI':'/faci/','Вулкан':'/vulkan/','СТАРТ':'/start/','ZOTA':'/zota/'}
articles=[p for p in PAGES if p['PUBLIC']=='Y' and (len(p['TITLE'])>45 or p['path']=='/preimushhestva-pelletnykh-otopitelnykh-kotlov/') and p['ID']!='123']
home=f'''<div class="wrap"><section class="hero"><div><div class="eyebrow">PelletsGrupp · пеллетное отопление</div><h1>Пеллетное отопление<br>в Екатеринбурге</h1><p class="lead">Пеллетные котлы, поставка топлива, монтаж и сервис. Подберём систему отопления для вашего дома в Екатеринбурге и Свердловской области.</p><div class="actions"><a class="btn" href="/katalog/">Подобрать котёл →</a><a class="btn light" href="/pellety/">Заказать пеллеты</a></div><div class="proof"><span><b>01</b> Подбор оборудования</span><span><b>02</b> Доставка топлива</span><span><b>03</b> Сервис и ремонт</span></div></div><div class="photo"><img src="{SITE['home']}" alt="Котельное оборудование PelletsGrupp"><div class="stamp"><strong>BIOTEP</strong>Наш флагман для отопления дома</div></div></section></div><section class="section white"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Оборудование с поддержкой</span><h2>Пеллетные котлы BIOTEP</h2></div><a href="/biotep/">Вся линейка →</a></div><div class="grid products">{''.join(card(p) for p in PRODUCTS if p['brand']=='BIOTEP' and p.get('product_type')!='biotep_spare')}</div></div></section><section class="section"><div class="wrap"><div class="section-head"><div><span class="eyebrow">От топлива до обслуживания</span><h2>Одна компания. Полный цикл.</h2></div></div><div class="grid cycle-grid"><div class="service"><div class="num">01 / ТОПЛИВО</div><h3>Древесные пеллеты</h3><p>Белые и серые пеллеты. Фасовка в мешки и биг-бэги, розничные и оптовые поставки.</p><a class="text-link" href="/pellety/">Выбрать топливо →</a></div><div class="service"><div class="num">02 / ОБОРУДОВАНИЕ</div><h3>Котлы и горелки</h3><p>BIOTEP, FACI, Вулкан, СТАРТ и горелки ZOTA. Подбор модели и комплектации под ваш объект.</p><a class="text-link" href="/katalog/">Открыть каталог →</a></div><div class="service"><div class="num">03 / МОНТАЖ</div><h3>Монтаж отопления</h3><p>Установка котла, системы отопления и дымохода. Подбор материалов, сборка и пусконаладка оборудования.</p><a class="text-link" href="/otoplenie/">Подробнее о монтаже →</a></div><div class="service"><div class="num">04 / СЕРВИС</div><h3>Обслуживание и ремонт</h3><p>Сезонная чистка, настройка автоматики и помощь в эксплуатации пеллетного котла.</p><a class="text-link" href="/servisiremont/">Узнать об услугах →</a></div></div></div></section><section class="section white"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Помогаем разобраться</span><h2>Об отоплении — по делу</h2></div><a href="/blog/">Все статьи →</a></div>{tiles(articles[-3:])}</div></section>'''+cta()
from installation import home_block, page as installation_page
home_marker='<section class="section white"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Помогаем разобраться</span>'
assert home_marker in home
home=home.replace(home_marker,home_block()+home_marker,1)
write('/','Пеллетные котлы и пеллеты в Екатеринбурге — PelletsGrupp',home,'Продажа пеллетных котлов BIOTEP, FACI, Вулкан, СТАРТ, горелок ZOTA. Пеллеты, монтаж, сервис и ремонт в Екатеринбурге.',{'@context':'https://schema.org','@type':'Organization','name':'PelletsGrupp','url':ORIGIN,'telephone':'+73433455225','email':'office@pelletsgrupp.ru'})
write('/otoplenie/','Монтаж отопления, котлов и дымоходов в Екатеринбурге — PelletsGrupp',installation_page(),'Монтаж пеллетных котлов, систем отопления и дымоходов в Екатеринбурге. Подбор оборудования, проектирование, пусконаладка и шеф-монтаж.',{'@context':'https://schema.org','@type':'Service','serviceType':'Монтаж пеллетных котлов, отопления и дымоходов','provider':{'@type':'Organization','name':'PelletsGrupp','telephone':'+73433455225'},'areaServed':['Екатеринбург','Свердловская область'],'url':ORIGIN+'/otoplenie/'})
def catalog(path,title,brand=None):
 prods=[p for p in PRODUCTS if p.get('product_type') not in ('biotep_spare','vulkan_spare') and (not brand or p['brand']==brand)]
 lead=biotep_intro() if brand=='BIOTEP' else faci_intro() if brand=='FACI' else start_intro() if brand=='СТАРТ' else 'Подберём оборудование и комплектацию. Организуем доставку и сервис.'
 tabs='<div class="brand-tabs"><a href="/katalog/">Все марки</a>'+''.join(f'<a class="{"active" if brand==b else ""}" href="{brandroutes[b]}">{e(b)}</a>' for b in brands)+'</div>'
 filters='<div class="filters"><input id="search" aria-label="Поиск модели" placeholder="Название модели или артикул">'+('' if brand else '<select id="brand-filter" aria-label="Марка"><option value="">Все марки</option>'+''.join(f'<option>{b}</option>' for b in brands)+'</select>')+'</div>'
 section_tabs='<div class="brand-tabs"><a class="active" href="/biotep/">Котлы BIOTEP</a><a href="/biotep/zapchasti/">Запчасти BIOTEP</a></div>' if brand=='BIOTEP' else ''
 body=crumbs(title)+f'<div class="wrap"><div class="page-head"><span class="eyebrow">Каталог PelletsGrupp</span><h1>{e(title)}</h1><p class="lead">{e(lead)}</p></div>{tabs}{section_tabs}{filters}<p class="fine" id="count">{len(prods)} товаров</p><div class="grid products">'+''.join(card(p) for p in prods)+'</div><div id="empty" class="empty" hidden><p>По вашему запросу ничего не найдено. Проверьте название или артикул.</p><div class="actions"><button type="button" class="btn light" id="empty-clear">Показать все товары</button><a class="btn" href="/kontakty/">Помочь с подбором →</a></div></div></div>'+cta()
 write(path,title+' — PelletsGrupp',body,'Каталог пеллетного отопления: модели, комплектации и цены. Подбор оборудования, доставка и сервис в Екатеринбурге.')
catalog('/katalog/','Котлы и горелки')
for b in brands:
 if b not in ('Вулкан','ZOTA'):catalog(brandroutes[b],'Пеллетные котлы '+b,b)
write('/vulkan/','Автоматические котлы Vulkan — серии и цены | PelletsGrupp',vulkan_catalog(PRODUCTS,card)+cta(),'64 модели автоматических котлов Vulkan: Boss, Eko, Eko-Max, Max-Duo и Optimum. Характеристики, фотографии, цены и подбор оборудования.')
for series in VULKAN_SERIES:
 key,label,_=series
 write('/vulkan/'+key+'/',f'Котлы Vulkan {label} — модели и цены | PelletsGrupp',vulkan_catalog(PRODUCTS,card,series)+cta(),f'Автоматические котлы Vulkan {label}: модели, цены, характеристики и фотографии. Подбор, доставка и монтаж в Екатеринбурге.')
write('/zota/','Пеллетные горелки и комплектующие ZOTA — цены | PelletsGrupp',zota_catalog(PRODUCTS,card)+cta(),'Пеллетные горелки ZOTA FOX G2 и RAY G2, бункеры, механизмы подачи, адаптеры, отбойники и автоматика. Цены, характеристики и документы.')
for key,label,_,route in ZOTA_CATEGORIES:
 write('/zota/'+route+'/',f'{label} ZOTA — цены | PelletsGrupp',zota_catalog(PRODUCTS,card,key)+cta(),f'{label} ZOTA для пеллетных горелок: актуальные цены, фотографии, описание и подбор совместимости.')
write('/biotep/zapchasti/','Запчасти BIOTEP — РРЦ и подбор | PelletsGrupp',biotep_spares_catalog(PRODUCTS,card)+cta(),'Оригинальные запчасти для пеллетных котлов BIOTEP: автоматика, вентиляторы, шнеки, розжиг, горелка, уплотнения и комплект проводов. РРЦ производителя с НДС.')
for key,label,route in BIOTEP_SPARE_CATEGORIES:
 write('/biotep/zapchasti/'+route+'/',f'{label} для котлов BIOTEP — РРЦ | PelletsGrupp',biotep_spares_catalog(PRODUCTS,card,key)+cta(),f'{label} для котлов BIOTEP: РРЦ производителя с НДС, внутренние артикулы и подбор совместимости.')
write('/vulkan/zapchasti/','Запчасти Vulkan — РРЦ и подбор | PelletsGrupp',vulkan_spares_catalog(PRODUCTS,card)+cta(),'Запчасти, горелки, бункеры, шнеки, приводы, автоматика и дополнительное оборудование для котлов Vulkan. РРЦ производителя.')
for key,label,route in VULKAN_SPARE_CATEGORIES:
 write('/vulkan/zapchasti/'+route+'/',f'{label} для котлов Vulkan — РРЦ | PelletsGrupp',vulkan_spares_catalog(PRODUCTS,card,key)+cta(),f'{label} для котлов Vulkan: РРЦ производителя, внутренние артикулы и подбор совместимости.')
for p in PRODUCTS:
 images=p['images'];gallery=f'<div class="gallery"><img id="main-image" src="{images[0]}" alt="{e(p["name"])}">' if images else '<div class="gallery"><p>Фотография уточняется</p>'
 gallery+='<div class="thumbs">'+''.join(f'<button data-src="{src}" data-alt="{e(p["name"])}" aria-label="Фото {i+1}"><img src="{src}" alt="" loading="lazy"></button>' for i,src in enumerate(images))+'</div></div>'
 conf=''
 if p['variants']:
  conf='<label for="variant">Комплектация</label><select id="variant">'+''.join(f'<option value="{i}">{e(v["name"])}</option>' for i,v in enumerate(p['variants']))+'</select>' if len(p['variants'])>1 else '<p>Комплектация: <strong>'+e(p['variants'][0]['name'])+'</strong></p>'
  conf+=('<label for="bunker">Объём бункера</label><select id="bunker">'+''.join(f'<option value="{i}">{e(b["name"])}</option>' for i,b in enumerate(p['bunkers']))+'</select>') if len(p['bunkers'])>1 else '<p>Штатный бункер: <strong>'+e(p['bunkers'][0]['name'])+'</strong></p>'
  conf+='<ul class="includes" id="includes"></ul>'
 specs='<table class="specs"><tbody>'+''.join(f'<tr><th scope="row">{e(k)}</th><td>{e(v)}</td></tr>' for k,v in p['specs'].items())+'</tbody></table>'
 view_data=dict(p)
 if p['brand']=='FACI':
  view_data['configuration_views']=faci_views(p)
  specs=faci_specs(p,view_data['configuration_views'][p['offers'][0]['sku']])
 if p['brand']=='СТАРТ':
  view_data['configuration_views']=start_views(p)
  specs=start_specs(view_data['configuration_views'][p['offers'][0]['sku']])
 data=json.dumps(view_data,ensure_ascii=False).replace('</','<\\/')
 is_biotep_spare=p.get('product_type')=='biotep_spare'
 is_vulkan_spare=p.get('product_type')=='vulkan_spare'
 is_spare=is_biotep_spare or is_vulkan_spare
 breadcrumb=biotep_spares_crumbs(p) if is_biotep_spare else vulkan_spares_crumbs(p) if is_vulkan_spare else vulkan_crumbs(product=p) if p.get('series') else biotep_crumbs(p) if p['brand']=='BIOTEP' else faci_crumbs(p) if p['brand']=='FACI' else start_crumbs(p) if p['brand']=='СТАРТ' else zota_crumbs(p) if p['brand']=='ZOTA' else crumbs(p['name'])
 detail_intro=biotep_spares_facts(p) if is_biotep_spare else vulkan_spares_facts(p) if is_vulkan_spare else vulkan_facts(p) if p.get('series') else biotep_facts(p) if p['brand']=='BIOTEP' else faci_facts(p) if p['brand']=='FACI' else start_facts(p) if p['brand']=='СТАРТ' else zota_facts(p,rich) if p['brand']=='ZOTA' else ''
 detail_docs='' if is_spare else vulkan_documents(p) if p.get('series') else biotep_documents(p) if p['brand']=='BIOTEP' else faci_documents(p) if p['brand']=='FACI' else start_documents(p) if p['brand']=='СТАРТ' else zota_documents(p) if p['brand']=='ZOTA' else ''
 body=breadcrumb+f'<section class="section"><div class="wrap detail">{gallery}<div class="buybox"><span class="badge">{e(p.get("display_brand",p["brand"]))}'+(' · флагман PelletsGrupp' if p['brand']=='BIOTEP' and not is_spare else '')+f'</span><h1>{e(p["name"])}</h1><p class="sku-line">Артикул: <span id="product-sku">{e(p["sku"])}</span></p><p class="fine">Подбор, доставка и сервисное сопровождение</p>{conf}<div id="chosen-price" class="bigprice">{money(p["price"])}</div><p class="fine">'+('Цена сверена с источником '+p['checked_at']+'. Наличие уточняется при заказе.' if p['checked_at'] else 'Актуальная цена и комплектация уточняются у специалиста.')+f'</p><div class="actions"><a class="btn" href="tel:+73433455225">Позвонить: +7 (343) 345-52-25</a></div><p class="fine">Назовите специалисту модель, артикул и выбранную комплектацию.</p><button class="btn light" id="copy-quote">Скопировать выбранную модель</button><p id="copy-status" class="fine" aria-live="polite"></p></div></div></section>'+detail_intro+f'<section class="section white"><div class="wrap"><h2>Характеристики</h2>{specs if p["specs"] else "<p>Подробные характеристики уточним при подборе оборудования.</p>"}<p class="fine"><a href="{e(p["source"])}" target="_blank" rel="noopener">Источник данных →</a></p></div></section>'+detail_docs+f'<script type="application/json" id="product-data">{data}</script>'+cta()
 schema={'@context':'https://schema.org','@type':'Product','sku':p['sku'],'name':p['name'],'brand':{'@type':'Brand','name':p.get('display_brand',p['brand'])},'url':ORIGIN+p['path']}
 if p.get('series'):schema['category']='Vulkan '+p['series_name']
 if p['brand']=='ZOTA':schema['category']='ZOTA · '+p['zota_category_label'];schema['mpn']=p['manufacturer_article']
 if is_spare:
  schema['category']=('Запчасти BIOTEP · '+p['biotep_spare_category_label']) if is_biotep_spare else ('Запчасти Vulkan · '+p['vulkan_spare_category_label'])
  if p.get('manufacturer_article'):schema['mpn']=p['manufacturer_article']
 if images:schema['image']=[ORIGIN+i for i in images]
 if p['price'] is not None:schema['offers']={'@type':'Offer','priceCurrency':'RUB','price':p['price'],'url':ORIGIN+p['path']}
 write(p['path'],p['name']+' — цена и подбор | PelletsGrupp',body,p['name']+'. Комплектация, цена и характеристики. Подбор, доставка и сервис в Екатеринбурге.',schema)
skip={'87','89','91','93','95','97','107','109','111','113','123','125','127','129','131','133','135','153','159','155','157','161','175'}
from pellets import page as pellets_page
from service_page import page as service_page
from maintenance_page import page as maintenance_page
from service_pro_page import page as service_pro_page
write('/tekhnicheskoe-obsluzhivanie-kotla/','Техническое обслуживание пеллетных котлов — PelletsGrupp',maintenance_page(),'Сезонное ТО пеллетных котлов: чистка горелки, шнека, теплообменника, дымохода и камеры сгорания, диагностика датчиков и настройка автоматики.',{'@context':'https://schema.org','@type':'Service','serviceType':'Техническое обслуживание пеллетных котлов','provider':{'@type':'Organization','name':'PelletsGrupp'},'areaServed':'Екатеринбург и Свердловская область','url':ORIGIN+'/tekhnicheskoe-obsluzhivanie-kotla/'})
write('/servis-pro/','Сервис PRO для пеллетных котлов — тарифы | PelletsGrupp',service_pro_page(),'Программа сезонного обслуживания пеллетных котлов для физических и юридических лиц: тарифы, состав работ, плановые и аварийные выезды.',{'@context':'https://schema.org','@type':'Service','serviceType':'Программа сезонного обслуживания пеллетных котлов «Сервис PRO»','provider':{'@type':'Organization','name':'PelletsGrupp','telephone':'+73433455225'},'areaServed':'Екатеринбург и Свердловская область','url':ORIGIN+'/servis-pro/'})
write('/servisiremont/','Сервис и ремонт пеллетных котлов в Екатеринбурге — PelletsGrupp',service_page(),'Техническое обслуживание от 5 000 ₽, ремонт от 7 500 ₽, программа «Сервис PRO» от 12 000 ₽. Сезонная чистка, диагностика и настройка пеллетных котлов.',{'@context':'https://schema.org','@type':'Service','serviceType':'Сервис и ремонт пеллетных котлов','provider':{'@type':'Organization','name':'PelletsGrupp','telephone':'+73433455225'},'areaServed':'Екатеринбург и Свердловская область','url':ORIGIN+'/servisiremont/'})
pellets_source=next(p for p in PAGES if p['path']=='/pellety/')
pellets_sections=[]
for sec in pellets_source['sections'][9:]:
 if 'form' in sec['code']:continue
 parts=[]
 for title in sec['titles']:
  if plain(title):parts.append('<h2>'+e(plain(title))+'</h2>')
 for text in sec['texts']:
  if plain(text):parts.append(rich(text))
 if parts:pellets_sections.append('<section>'+''.join(parts)+'</section>')
pellets_extra='<section class="section"><div class="wrap"><article class="article">'+''.join(pellets_sections)+'</article></div></section>'
write('/pellety/','Топливные пеллеты в Екатеринбурге — цены и доставка | PelletsGrupp',pellets_page(pellets_extra),'Серые пеллеты — 12 000 ₽/т, белые — 17 000 ₽/т. Мешки по 30 кг и биг-бэги по 1 т, самовывоз в Екатеринбурге и доставка. Поставки для дома и бизнеса.',{'@context':'https://schema.org','@graph':[{'@type':'Product','sku':p['sku'],'name':p['name'],'image':ORIGIN+p['image'],'brand':{'@type':'Brand','name':'PelletsGrupp'},'offers':{'@type':'Offer','price':p['price'],'priceCurrency':'RUB','url':ORIGIN+'/pellety/','description':'Цена за тонну, доставка отдельно'}} for p in PELLET_TYPES]})
for p in PAGES:
 path=p['path']
 if p['PUBLIC']!='Y' or p['ACTIVE']!='Y' or p['ID'] in skip or path in written or path=='/kotly_rxdg/' or path in SEO_REDIRECTS:continue
 # Layout fragments and blank templates have no independent public content.
 if p['TITLE'].startswith('Область') or p['TITLE']=='Пустой шаблон':continue
 if p['ID']=='199':write(path,'Блог о пеллетном отоплении — PelletsGrupp',crumbs('Блог')+'<div class="wrap"><div class="page-head"><span class="eyebrow">Полезные материалы</span><h1>Разбираемся в отоплении</h1></div>'+tiles(articles)+'</div>');continue
 seen=set();sections=[]
 for sec in p['sections']:
  if 'form' in sec['code'] or 'menu' in sec['code']:continue
  parts=[]
  for t in sec['titles']:
   tx=plain(t)
   if tx and tx!=p['TITLE'] and tx not in seen:parts.append('<h2>'+e(tx)+'</h2>');seen.add(tx)
  for text in sec['texts']:
   tx=plain(text)
   if tx and tx not in seen:parts.append(rich(text));seen.add(tx)
  if parts:
   for im in sec['images'][:3]:parts.append(f'<img src="{im["src"]}" alt="{e(im["alt"] or p["TITLE"])}" loading="lazy">')
   sections.append('<section>'+''.join(parts)+'</section>')
 seo=p.get('ADDITIONAL_FIELDS',{});title=seo.get('METAMAIN_TITLE') or p['TITLE']+' — PelletsGrupp';desc=seo.get('METAMAIN_DESCRIPTION') or ''
 body=crumbs(p['TITLE'])+f'<div class="wrap"><div class="page-head"><h1>{e(p["TITLE"])}</h1></div><article class="article">'+''.join(sections)+'</article></div>'+cta()
 write(path,title,body,desc)
contacts=crumbs('Контакты')+'<div class="wrap"><div class="page-head"><span class="eyebrow">Всегда на связи</span><h1>Контакты PelletsGrupp в Екатеринбурге</h1></div><div class="contact-grid"><div class="tile"><h2>Продажи и консультации</h2><p><a href="tel:+73433455225">+7 (343) 345-52-25</a><br><a href="mailto:office@pelletsgrupp.ru">office@pelletsgrupp.ru</a></p><p>Пн–Пт, 09:00–18:00</p><a class="btn" href="tel:+73433455225">Позвонить: +7 (343) 345-52-25</a></div><div class="tile"><h2>Офис в Екатеринбурге</h2><p>ул. Лукиных, д. 1, оф. 4</p><p>ООО «ПЕЛЛЕТС ГРУПП»<br>ИНН 6678134556<br>ОГРН 1236600075910</p><p class="fine">Перед визитом согласуйте время по телефону.</p></div></div></div>'
write('/kontakty/','Контакты PelletsGrupp — Екатеринбург',contacts,'Телефон, email и адрес PelletsGrupp в Екатеринбурге. Подбор котлов, поставка пеллет, сервис и ремонт.')
# Retain aliases referenced in exported pages, while excluding retired brands from navigation.
aliases={'/kotly/':'/katalog/','/kotly-i-gorelki/':'/katalog/','/kotly_rxdg/':'/katalog/','/katalog/katalog/':'/katalog/'}
# Confirmed old search-result URLs; static redirects until an HTTP redirect layer is available.
aliases.update(SEO_REDIRECTS)
assert all(target in written for target in aliases.values())
for p in PAGES:
 if p['path'] not in written and p['PUBLIC']=='Y':aliases[p['path']]='/katalog/'
for path,target in aliases.items():
 if path in written:continue
 source_page=next((p for p in PAGES if p['path']==path),None)
 legacy_title=(source_page or {}).get('TITLE') or written.get(target,'Каталог оборудования')
 write(path,legacy_title+' — PelletsGrupp',crumbs('Каталог')+f'<section class="section"><div class="wrap"><h1>{e(legacy_title)}</h1><p>Актуальная информация представлена в общем каталоге PelletsGrupp.</p><a class="btn" href="{target}">Перейти в каталог →</a></div></section>',f'{legacy_title}. Актуальный каталог оборудования PelletsGrupp.')
 alias_file=DIST/path.strip('/')/'index.html'
 alias_html=alias_file.read_text()
 alias_html=alias_html.replace(f'<link rel="canonical" href="{e(ORIGIN+path)}">',f'<link rel="canonical" href="{e(ORIGIN+target)}"><meta http-equiv="refresh" content="0; url={e(target)}">',1)
 alias_file.write_text(alias_html)
# Rewrite archived internal URLs only after all final routes are known.
for file in DIST.rglob('*.html'):
 s=file.read_text()
 def fix(m):
  href=m.group(1)
  if href.startswith('/') and not href.startswith('/assets/'):
   parsed=urlparse(href)
   if parsed.path not in written and not parsed.path.endswith(('.css','.js')):return 'href="/katalog/"'
  return m.group(0)
 s=re.sub(r'href="([^"]+)"',fix,s)
 file.write_text('\n'.join(line.rstrip() for line in s.splitlines()))
for name in ['site.css','site.js','vulkan.css']:shutil.copy(ROOT/name,DIST/name)
shutil.copytree(ROOT/'assets',DIST/'assets',dirs_exist_ok=True)
for verification in ROOT.glob('yandex_*.html'):
 shutil.copy(verification,DIST/verification.name)
(DIST/'robots.txt').write_text('User-agent: *\nDisallow: /\n' if PREVIEW else 'User-agent: *\nAllow: /\nSitemap: '+ORIGIN+'/sitemap.xml\n')
(DIST/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+e(ORIGIN+p)+'</loc></url>' for p in written if p not in aliases)+'</urlset>')
if not PREVIEW:
 (DIST/'CNAME').write_text('pelletsgrupp.ru\n')
 (DIST/'.nojekyll').write_text('')
(ROOT/'data/routes.json').write_text(json.dumps(written,ensure_ascii=False,indent=2))
write('/404/','Страница не найдена — PelletsGrupp','<section class="section"><div class="wrap"><h1>Страница не найдена</h1><p>Воспользуйтесь каталогом или свяжитесь с нами.</p><a class="btn" href="/katalog/">Открыть каталог</a></div></section>')
shutil.copy(DIST/'404/index.html',DIST/'404.html')
print('Built',len(written),'routes;',len(PRODUCTS),'products; preview noindex:',PREVIEW)
