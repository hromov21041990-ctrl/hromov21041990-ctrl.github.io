import json,subprocess
from pathlib import Path
from urllib.parse import urlparse,unquote
from lxml import html
ROOT=Path(__file__).resolve().parent;DIST=ROOT/'dist';errors=[];count=0
for f in DIST.rglob('*.html'):
 doc=html.fromstring(f.read_text());count+=1
 if not doc.xpath('//html[@lang="ru"]'):errors.append((str(f),'missing Russian document language'))
 if len(doc.xpath('//h1'))!=1:errors.append((str(f),'expected one h1'))
 for url in doc.xpath('//@href|//@src'):
  if not url.startswith('/') or url.startswith('//'):continue
  path=unquote(urlparse(url).path);local=DIST/path.lstrip('/')
  if not local.is_file() and not (local/'index.html').is_file():errors.append((str(f),url))
 if 'Ð' in doc.text_content() or 'Ñ' in doc.text_content():errors.append((str(f),'text encoding problem'))
products=json.loads((ROOT/'data/products.json').read_text())
assert len(products)==338
assert len({p['path'] for p in products})==338
assert len({p['id'] for p in products})==338
for p in products:
 assert p['images'],p['name']
 if p['brand']=='FACI':
  assert p['variants'] and p['bunkers'],p['name']
 if p['brand']=='СТАРТ':
  assert p['variants'] and p['bunkers'] and p['automatic_pellet'],p['name']
 if p['price'] is not None:assert p['price']>0,p['name']
biotep=[p for p in products if p['brand']=='BIOTEP' and p.get('product_type')!='biotep_spare']
biotep_source=json.loads((ROOT/'data/biotep-source.json').read_text())
source_biotep={row['source_url']:row for row in biotep_source['source_snapshot']}
assert len(biotep)==4 and len(source_biotep)==4
assert [p['sku'] for p in biotep]==['PG-000001','PG-000002','PG-000003','PG-000004']
for p in biotep:
 original=source_biotep[p['source']]
 assert p['price']==original['price'] and p['power']==original['power_kw']
 assert p['power_label']==original['power_label'] and p['specs']==original['specifications']
 assert p['description']==original['description'] and p['advantages']==original['advantages']
 assert p['documents']==original['documents'] and len(p['documents'])>=6
 page=html.fromstring((DIST/p['path'].strip('/')/'index.html').read_text())
 text_content=page.text_content()
 assert original['description'] in text_content
 assert len(page.xpath('//a[contains(@class,"document-card")]'))==len(p['documents'])
 assert 'Основные возможности' in text_content and 'Паспорта, схемы и сервисные материалы' in text_content
biotep77=next(p for p in biotep if p['power']==77)
assert biotep77['specs']['Диапазон мощности']=='18–77 кВт'
assert biotep77['specs']['Площадь отопления']=='150–1100 м²'
assert biotep77['specs']['КПД']=='более 90%'
biotep_index=html.fromstring((DIST/'biotep'/'index.html').read_text())
assert len(biotep_index.xpath('//article[@data-product]'))==4
assert 'официальные паспорта' in biotep_index.text_content()
biotep_spares=[p for p in products if p.get('product_type')=='biotep_spare']
biotep_spares_source=json.loads((ROOT/'data/biotep-spares-source.json').read_text())
assert len(biotep_spares)==83 and all(p['brand']=='BIOTEP' for p in biotep_spares)
assert [p['sku'] for p in biotep_spares][0]=='PG-000261'
assert [p['sku'] for p in biotep_spares][-1]=='PG-000343'
assert len({p['sku'] for p in biotep_spares})==83
assert all(p['price']>0 for p in biotep_spares)
assert len(biotep_spares_source['items'])==83
assert biotep_spares_source['excluded_without_rrp']==[{'page':4,'manufacturer_article':'5627','name':'BD-77-92-001 Экран','note':'Экран для чаши BIOTEP 77C','reason':'В прайсе не указана РРЦ'}]
image_import=biotep_spares_source['image_import']
assert image_import['products_with_photos']==74 and image_import['products_without_photos']==9
assert image_import['photo_files']==77 and len(image_import['without_photos'])==9
assert sum(p['images']!=['/assets/biotep-spares.svg'] for p in biotep_spares)==74
assert sum(len(p['images']) for p in biotep_spares if p['images']!=['/assets/biotep-spares.svg'])==77
for p in biotep_spares:
 for image in p['images']:
  assert (ROOT/image.lstrip('/')).is_file(),(p['sku'],image)
expected_spare_counts={'automation':11,'airflow':5,'auger':20,'ignition':6,'burner':4,'body':15,'insulation':7,'tubes':3,'seals':4,'wires':8}
assert {key:sum(p['biotep_spare_category']==key for p in biotep_spares) for key in expected_spare_counts}==expected_spare_counts
spares_index=html.fromstring((DIST/'biotep'/'zapchasti'/'index.html').read_text())
assert len(spares_index.xpath('//article[@data-product]'))==83
assert spares_index.xpath('//*[@id="count"]/text()')==['83 товаров']
from biotep_spares import CATEGORIES as BIOTEP_SPARE_CATEGORIES
for key,label,route in BIOTEP_SPARE_CATEGORIES:
 page=html.fromstring((DIST/'biotep'/'zapchasti'/route/'index.html').read_text())
 assert len(page.xpath('//article[@data-product]'))==expected_spare_counts[key]
 assert label in page.xpath('//h1')[0].text_content()
for p in biotep_spares:
 page=html.fromstring((DIST/p['path'].strip('/')/'index.html').read_text())
 assert p['biotep_spare_category_label'] in page.text_content()
 assert 'РРЦ производителя с НДС' in page.text_content()
faci15=next(p for p in products if p['name']=='Пеллетный котел FACI 15')
# Check manufacturer reference combinations rather than implementation details.
assert faci15['variants'][0]['price']+faci15['bunkers'][1]['extra']==399600
assert faci15['variants'][2]['price']+faci15['bunkers'][2]['extra']==656640
faci=[p for p in products if p['brand']=='FACI']
faci_source=json.loads((ROOT/'data/faci-source.json').read_text())
assert len(faci)==18 and sum(len(p['offers']) for p in faci)==129
source_faci={r['source_url']:r for r in faci_source['source_snapshot']}
assert len(source_faci)==18
for p in faci:
 original=source_faci[p['source']]
 assert p['price']==original['price'] and p['specs']==original['specifications'],p['name']
 assert [{k:v[k] for k in ['name','price','includes']} for v in p['variants']]==[{k:v[k] for k in ['name','price','includes']} for v in original['variants']],p['name']
 assert [b['extra'] for b in p['bunkers']]==[b['extra'] for b in original['bunkers']],p['name']
 assert p['description'] and p['documents'] and len(p['images'])>=1
gt=next(p for p in faci if p['name'].endswith(' GT'))
assert gt['power'] is None and gt['power_label']=='10-40 кВт'
assert [v['name'] for v in next(p for p in faci if p['name'].endswith(' 1500'))['variants']]==['Base','Classico']
assert next(p for p in faci if p['name'].endswith(' 1000'))['bunkers'][0]['capacity_l']==2000
assert next(p for p in faci if p['name'].endswith(' 1500'))['bunkers'][0]['capacity_l']==2500
from faci import configuration_views
for p in faci:
 views=configuration_views(p)
 variants={v['option_id']:v for v in p['variants']}
 bunkers={b['option_id']:b for b in p['bunkers']}
 for offer in p['offers']:
  v=variants[offer['variant_id']];b=bunkers[offer['bunker_id']];view=views[offer['sku']]
  assert view['specs']['Комплектация']==v['name'] and view['specs']['Артикул']==offer['sku']
  assert view['specs']['Емкость бункера']==str(b['capacity_l'])+' л'
  assert v['name'] in view['description'] and str(b['capacity_l'])+' л' in view['description']
  for feature in ['Автоподжиг','Автоочистка теплообменника','Автозолоудаление']:
   assert view['specs'][feature]==('Входит в комплектацию' if feature in v['includes'] else 'Не входит в комплектацию')
 page=html.fromstring((DIST/p['path'].strip('/')/'index.html').read_text())
 payload=json.loads(page.xpath('//script[@id="product-data"]')[0].text)
 assert payload['configuration_views']==views and page.xpath('//*[@id="configuration-description"]') and page.xpath('//*[@id="configuration-specs"]')
base=configuration_views(faci15)[faci15['offers'][0]['sku']]
large=configuration_views(faci15)[faci15['offers'][-1]['sku']]
assert base['specs']['Вес']=='285 кг' and 'Уточняется' in large['specs']['Вес']
assert '500 л' in base['description'] and '2000 л' in large['description'] and '500 л' not in large['description']
assert configuration_views(gt)[gt['sku']]['specs']['Очистка котла']=='Механическая, с помощью рычага'
from start import configuration_views as start_views
start=[p for p in products if p['brand']=='СТАРТ']
start_source=json.loads((ROOT/'data/start-source.json').read_text())
source_start={row['source_url']:row for row in start_source['source_snapshot']}
assert len(start)==9 and sum(len(p['offers']) for p in start)==25 and len(source_start)==9
for p in start:
 original=source_start[p['source']]
 assert p['price']==original['price'] and p['manufacturer_article']==original['manufacturer_article']
 assert p['power']==original['power_kw'] and p['power_label']==original['power_label']
 assert [(b['name'],b['capacity_l'],b['extra']) for b in p['bunkers']]==[(b['name'],b['capacity_l'],b['extra']) for b in original['bunkers']]
 assert all(p['specs'][k]==v for k,v in original['specifications'].items())
 assert p['documents']==original['documents'] and p['images']
 views=start_views(p);page=html.fromstring((DIST/p['path'].strip('/')/'index.html').read_text())
 payload=json.loads(page.xpath('//script[@id="product-data"]')[0].text)
 assert payload['configuration_views']==views and page.xpath('//*[@id="configuration-description"]') and page.xpath('//*[@id="configuration-specs"]')
 for offer in p['offers']:
  view=views[offer['sku']]
  assert view['specs']['Внутренний артикул']==offer['sku']
  bunker=next(b for b in p['bunkers'] if b['option_id']==offer['bunker_id'])
  assert view['specs']['Выбранный бункер']==str(bunker['capacity_l'])+' л'
assert next(p for p in start if p['path'].endswith('start-100-gr-ash/'))['specs']['Наличие автоматического шнекового золоудаления']=='да'
from zota import CATEGORIES as ZOTA_CATEGORIES
zota=[p for p in products if p['brand']=='ZOTA']
zota_source=json.loads((ROOT/'data/zota-source.json').read_text())
source_zota={row['source_url']:row for row in zota_source['source_snapshot']}
assert len(zota)==34 and len(source_zota)==34
assert {key:sum(p['zota_category']==key for p in zota) for key in zota_source['category_counts']}==zota_source['category_counts']
assert len({p['manufacturer_article'] for p in zota})==34
assert len({p['sku'] for p in zota})==34
for p in zota:
 original=source_zota[p['source']]
 assert p['price']==original['price'] and p['manufacturer_article']==original['manufacturer_article']
 assert all(p['specs'][key]==value for key,value in original['specifications'].items())
 assert p['documents']==original['documents'] and p['images'] and p['description']
 page=html.fromstring((DIST/p['path'].strip('/')/'index.html').read_text())
 assert page.xpath('//*[@id="product-sku"]/text()')==[p['sku']]
 assert p['manufacturer_article'] in page.text_content()
for key,label,_,route in ZOTA_CATEGORIES:
 page=html.fromstring((DIST/'zota'/route/'index.html').read_text())
 assert len(page.xpath('//article[@data-product]'))==zota_source['category_counts'][key]
 assert label in page.xpath('//h1')[0].text_content()
zota_index=html.fromstring((DIST/'zota'/'index.html').read_text())
assert len(zota_index.xpath('//article[@data-product]'))==34
assert zota_index.xpath('//*[@id="count"]/text()')==['34 товара']
assert zota_index.xpath('//*[@id="search"]')
fox25=next(p for p in zota if p['manufacturer_article']=='ZF4938004025')
assert fox25['price']==87500 and fox25['sku']=='PG-000227' and fox25['path']=='/katalog/item/zota-fox-25/'
assert len(fox25['specs'])>=20 and len(fox25['documents'])==2
from vulkan import SERIES
vulkan=[p for p in products if p['brand']=='Вулкан' and p.get('product_type')!='vulkan_spare']
assert len(vulkan)==64
audit=json.loads((ROOT/'data/vulkan-source.json').read_text())
source={p['slug']:p for p in audit['source_snapshot']}
for key,label,expected in SERIES:
 members=[p for p in vulkan if p['series']==key]
 assert len(members)==expected,(key,len(members))
 page=html.fromstring((DIST/'vulkan'/key/'index.html').read_text())
 assert len(page.xpath('//article[@data-product]'))==expected,key
 assert label in page.xpath('//h1')[0].text_content(),key
for p in vulkan:
 slug=p['path'].strip('/').rsplit('/',1)[-1]
 assert p['price']==source[slug]['price'],p['name']
 assert p['manufacturer_title']==source[slug]['title'],p['name']
 assert p['documents'],p['name']
 assert p['images'],p['name']
 page=html.fromstring((DIST/p['path'].strip('/')/'index.html').read_text())
 schema=json.loads(page.xpath('//script[@type="application/ld+json"]')[0].text)
 assert schema['offers']['price']==p['price'],p['name']
 if source[slug].get('conflicts'):
  assert any('Уточняется' in v for k,v in p['specs'].items() if 'площад' in k.lower()),p['name']
 if p['series']=='optimum-uni-max':
  assert p['power'] is None and p['specs']['Мощность, кВт']=='Уточняется при подборе',p['name']
vulkan_spares=[p for p in products if p.get('product_type')=='vulkan_spare']
vulkan_spares_source=json.loads((ROOT/'data/vulkan-spares-source.json').read_text())
assert len(vulkan_spares)==126 and all(p['brand']=='Вулкан' for p in vulkan_spares)
assert [p['sku'] for p in vulkan_spares][0]=='PG-000344'
assert [p['sku'] for p in vulkan_spares][-1]=='PG-000469'
assert len({p['sku'] for p in vulkan_spares})==126
assert all(p['price']>0 for p in vulkan_spares)
assert len(vulkan_spares_source['items'])==126
vulkan_image_import=vulkan_spares_source['image_import']
assert vulkan_image_import['products_with_photos']==26
assert vulkan_image_import['products_without_photos']==100
assert vulkan_image_import['photo_files']==3
assert sum(p['images']!=['/assets/vulkan-spares.svg'] for p in vulkan_spares)==26
assert len({image for p in vulkan_spares for image in p['images'] if image!='/assets/vulkan-spares.svg'})==3
for p in vulkan_spares:
 for image in p['images']:
  assert (ROOT/image.lstrip('/')).is_file(),(p['sku'],image)
expected_vulkan_spare_counts={'automatic-options':5,'bunkers-ash':28,'cleaning-firebox':7,'ash-fuel-feed':17,'burners':10,'augers-drives':21,'fans':12,'automation':9,'semi-auto-parts':8,'semi-auto-automation':9}
assert {key:sum(p['vulkan_spare_category']==key for p in vulkan_spares) for key in expected_vulkan_spare_counts}==expected_vulkan_spare_counts
vulkan_spares_index=html.fromstring((DIST/'vulkan'/'zapchasti'/'index.html').read_text())
assert len(vulkan_spares_index.xpath('//article[@data-product]'))==126
assert vulkan_spares_index.xpath('//*[@id="count"]/text()')==['126 товаров']
from vulkan_spares import CATEGORIES as VULKAN_SPARE_CATEGORIES
for key,label,route in VULKAN_SPARE_CATEGORIES:
 page=html.fromstring((DIST/'vulkan'/'zapchasti'/route/'index.html').read_text())
 assert len(page.xpath('//article[@data-product]'))==expected_vulkan_spare_counts[key]
 assert label in page.xpath('//h1')[0].text_content()
for p in vulkan_spares:
 page=html.fromstring((DIST/p['path'].strip('/')/'index.html').read_text())
 assert p['vulkan_spare_category_label'] in page.text_content()
 assert 'РРЦ производителя' in page.text_content()
source_vulkan_spares={item['sku']:item for item in vulkan_spares_source['items']}
for p in vulkan_spares:
 item=source_vulkan_spares[p['sku']]
 assert p['name']==item['name'] and p['price']==item['price'] and p['price_list_page']==item['page']
# Existing non-Vulkan products and the nine migrated Vulkan identities must survive the import.
baseline=json.loads(subprocess.check_output(['git','show','HEAD:data/products.json'],cwd=ROOT,text=True))
def without_identity(value):
 if isinstance(value,dict):return {k:without_identity(v) for k,v in value.items() if k not in ['sku','option_id','offers']}
 if isinstance(value,list):return [without_identity(v) for v in value]
 return value
assert [p for p in products if p['brand'] not in ('BIOTEP','FACI','СТАРТ','ZOTA') and p.get('product_type')!='vulkan_spare']==[p for p in baseline if p['brand'] not in ('BIOTEP','FACI','СТАРТ','ZOTA') and p.get('product_type')!='vulkan_spare']
current={p['id']:p for p in products}
for prior in baseline:
 if prior['brand']=='ZOTA':continue
 assert current[prior['id']]['path']==prior['path'] and current[prior['id']]['sku']==prior['sku']
 if prior['brand']!='СТАРТ':
  assert sorted(current[prior['id']].get('offers',[]),key=lambda x:x['sku'])==sorted(prior.get('offers',[]),key=lambda x:x['sku'])
for prior in [p for p in baseline if p['brand']=='Вулкан' and p.get('product_type')!='vulkan_spare']:
 current=next(p for p in vulkan if p['path']==prior['path'])
 assert current['id']==prior['id']
for prior in [p for p in baseline if p['brand']=='СТАРТ']:
 current=next(p for p in start if p['path']==prior['path'])
 assert current['id']==prior['id'] and current['sku']==prior['sku']
from catalog_identity import assign_skus,export_rows
import copy
pellets=json.loads((ROOT/'data/pellets.json').read_text())
registry=json.loads((ROOT/'data/sku-registry.json').read_text())
rows=export_rows(products,pellets)
assert len(rows)==467 and len({r['sku'] for r in rows})==467
assert len({p['sku'] for p in products+pellets})==340
previous_registry=json.loads(subprocess.check_output(['git','show','HEAD:data/sku-registry.json'],cwd=ROOT,text=True))
assert all(registry['entries'].get(k)==v for k,v in previous_registry['entries'].items())
assert registry['entries']['equipment:1d2371411a14']=='PG-000072' and registry['entries']['equipment:c0aeee1f4222']=='PG-000073'
assert not {'1d2371411a14','c0aeee1f4222'} & {p['id'] for p in products}
for p in products:
 page=html.fromstring((DIST/p['path'].strip('/')/'index.html').read_text())
 assert page.xpath('//*[@id="product-sku"]/text()')==[p['sku']]
 schema=json.loads(page.xpath('//script[@type="application/ld+json"]')[0].text)
 assert schema['sku']==p['sku']
# Renaming, repricing and reordering must preserve identities, including FACI choices.
trial=copy.deepcopy(products);fuel=copy.deepcopy(pellets);reg=copy.deepcopy(registry)
trial.reverse()
for p in trial:
 p['name']+=' renamed';p['price']=1
 p['variants'].reverse()
 if p.get('bunkers'):p['bunkers'].reverse()
assign_skus(trial,fuel,reg)
assert reg==registry
before={p['id']:p for p in products}
for p in trial:
 assert p['sku']==before[p['id']]['sku']
 assert sorted(p.get('offers',[]),key=lambda x:x['sku'])==sorted(before[p['id']].get('offers',[]),key=lambda x:x['sku'])
# A retired number stays reserved; a new product receives the next unused number.
retired=trial.pop()
trial.append({'id':'identity-verification-only','name':'New model','variants':[]})
assign_skus(trial,fuel,reg)
assert reg['entries']['equipment:'+retired['id']]==retired['sku']
assert trial[-1]['sku']==f'PG-{registry["next_number"]:06d}'
if errors:
 print(errors[:20]);raise SystemExit(1)
print('Verified',count,'HTML files, local links/assets, 338 product routes, 4 BIOTEP boilers with descriptions and documents, 83 BIOTEP spare parts in 10 groups with 77 source photos for 74 products, 18 FACI models, 129 FACI configurations, 9 START models, 25 START configurations, 34 ZOTA products in 6 supplier groups, 126 Vulkan spare parts in 10 groups with 3 source photos used for 26 products, 467 active unique articles, 64 Vulkan source prices and preserved identities.')
