"""Refresh only exactly matched supplier products; retain last good values on failure."""
import json,re,datetime,urllib.request,copy,concurrent.futures
from pathlib import Path
from urllib.parse import urljoin
from lxml import html
ROOT=Path(__file__).resolve().parent
def text(el):return ' '.join(el.text_content().split())
def amount(s):
 value=float(re.sub(r'[^0-9,.]','',s).replace(',','.'))
 if not 100<=value<=10000000:raise ValueError('Price outside the accepted range')
 return round(value)
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'PelletsGrupp catalog updater; office@pelletsgrupp.ru'})
 return html.fromstring(urllib.request.urlopen(req,timeout=30).read())
def faci_catalog():
 doc=fetch('https://facirus.ru/catalog/pelletnye-kotly/');result={}
 for el in doc.xpath('//div[contains(concat(" ",@class," ")," product ")]'):
  titles=el.xpath('.//a[@class="title"]')
  if not titles:continue
  name=text(titles[0]);labels=[text(x) for x in el.xpath('.//div[@class="kolection"]/label')];boxes=el.xpath('.//div[contains(@class,"priceBox")]')
  variants=[]
  for i,box in enumerate(boxes):
   if i>=len(labels) and len(boxes)!=1:raise ValueError('Unrecognized FACI configuration layout')
   desc=box.xpath('./div')[0];inc=[t.strip() for t in desc.itertext() if t.strip() and 'Комплектация' not in t]
   variants.append({'name':labels[i] if labels else 'Ottima','price':amount(box.get('data-price')),'includes':inc})
  if not variants:raise ValueError('Missing FACI price')
  bunkers=[]
  for x in el.xpath('.//div[@class="bunkers"]//input[not(@data-main)]'):
   extra=int(x.get('data-price'))
   if not 0<=extra<=2000000:raise ValueError('Invalid bunker supplement')
   bunkers.append({'name':text(x.getparent()),'extra':extra})
  result[name]={'variants':variants,'bunkers':bunkers,'price':variants[0]['price']}
 return result
def biotep_catalog():
 doc=fetch('https://bio-tep.ru/catalog/');result={}
 for h in doc.xpath('//h2'):
  m=re.fullmatch(r'BIOTEP\s+(18|25|32|77)',text(h))
  if not m:continue
  node=h
  for _ in range(5):
   s=text(node);price=re.search(r'РРЦ\s*[–—-]?\s*([\d\s]+)\s*руб',s)
   if price:
    result[int(m.group(1))]=amount(price.group(1));break
   node=node.getparent()
 return result
def start_catalog():
 category='https://www.kotel74.ru/kotly/pelletny';doc=fetch(category)
 urls=[]
 for href in doc.xpath('//a[contains(@href,"/kotly/pelletny/") and contains(@href,"-detail")]/@href'):
  url=urljoin(category,href)
  if url not in urls:urls.append(url)
 if len(urls)!=9:raise ValueError('START category composition changed')
 def one(url):
  detail=fetch(url);prices=detail.xpath('//span[contains(concat(" ",normalize-space(@class)," ")," PricesalesPrice ")]')
  if not prices:raise ValueError('Missing START price: '+url)
  bunkers=[]
  for option in detail.xpath('//li[contains(translate(@title,"БУНКЕР","бункер"),"бункер")]'):
   capacity=int(re.search(r'\d+',option.get('title')).group());entry={'name':str(capacity)+' л','capacity_l':capacity,'extra':int(option.get('data-price','0'))}
   if 'proddisable' in option.get('class',''):entry['source_status']='Временно недоступен для выбора у производителя'
   bunkers.append(entry)
  return url,{'price':amount(text(prices[-1])),'bunkers':bunkers}
 result={}
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
  for url,data in pool.map(one,urls):result[url]=data
 return result
def zota_catalog():
 category_urls=[
  'https://dk-zota.ru/products/gorelki','https://dk-zota.ru/products/bunker',
  'https://dk-zota.ru/products/mehanizm-podachi','https://dk-zota.ru/products/adapter',
  'https://dk-zota.ru/products/adapter?page=2','https://dk-zota.ru/products/otboynik',
  'https://dk-zota.ru/products/avtomatika-dlya-gorelok',
 ]
 urls=[]
 for category in category_urls:
  doc=fetch(category)
  for href in doc.xpath('//a[starts-with(@href,"/product/")]/@href'):
   url=urljoin(category,href)
   if url not in urls:urls.append(url)
 if len(urls)!=34:raise ValueError('ZOTA category composition changed')
 def one(url):
  detail=fetch(url);heading=detail.xpath('//h1');article=detail.xpath('string(//*[@itemprop="sku"]/@content)');price=detail.xpath('string(//*[@itemprop="price"]/@content)')
  if len(heading)!=1 or not article or not price:raise ValueError('Missing ZOTA identity or price: '+url)
  return url,{'name':text(heading[0]),'manufacturer_article':article,'price':amount(price)}
 result={}
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for url,data in pool.map(one,urls):result[url]=data
 return result
def refresh():
 path=ROOT/'data/products.json';products=json.loads(path.read_text());today=datetime.datetime.now(datetime.timezone.utc).isoformat();errors=[];updated=[];pending=[];faci={};biotep={};start={};zota={}
 for name,fn in [('FACI',faci_catalog),('BIOTEP',biotep_catalog),('СТАРТ',start_catalog),('ZOTA',zota_catalog)]:
  try:
   result=fn()
   if not result:raise ValueError('No matching products')
   if name=='FACI':faci=result
   elif name=='BIOTEP':biotep=result
   elif name=='СТАРТ':start=result
   else:zota=result
  except Exception as ex:errors.append({'brand':name,'error':str(ex)[:180]})
 for p in products:
  candidate=copy.deepcopy(p)
  try:
   if p['brand']=='FACI':
    name='Автоматический котел FACI GT' if p['name'].endswith('GT') else p['name']
    if name not in faci:raise ValueError('Exact FACI model not found; previous price retained')
    data=copy.deepcopy(faci[name])
    if not data['bunkers'] and p.get('bunker_fixed'):data['bunkers']=copy.deepcopy(p['bunkers'])
    if set(v['name'] for v in data['variants'])!=set(v['name'] for v in p['variants']):raise ValueError('Configuration change requires review')
    if set(v['name'] for v in data['bunkers'])!=set(v['name'] for v in p['bunkers']):raise ValueError('Bunker change requires review')
    for field in ['variants','bunkers']:
     previous={x['name']:x for x in p[field]}
     for option in data[field]:
      if previous[option['name']].get('option_id'):option['option_id']=previous[option['name']]['option_id']
      if previous[option['name']].get('capacity_l'):option['capacity_l']=previous[option['name']]['capacity_l']
    candidate.update(data)
   elif p['brand']=='BIOTEP':
    if p['power'] not in biotep:raise ValueError('Exact BIOTEP model not found')
    candidate['price']=biotep[p['power']]
   elif p['brand']=='СТАРТ':
    if p['source'] not in start:raise ValueError('Exact START model not found')
    data=start[p['source']];candidate['price']=data['price'];candidate['variants'][0]['price']=data['price']
    if data['bunkers']:
     previous={b['capacity_l']:b for b in p['bunkers']}
     if set(previous)!=set(b['capacity_l'] for b in data['bunkers']):raise ValueError('START bunker options changed; review required')
     refreshed=[]
     for source_bunker in data['bunkers']:
      bunker=copy.deepcopy(previous[source_bunker['capacity_l']]);bunker['name']=source_bunker['name'];bunker['extra']=source_bunker['extra']
      if source_bunker.get('source_status'):bunker['source_status']=source_bunker['source_status']
      else:bunker.pop('source_status',None)
      refreshed.append(bunker)
     candidate['bunkers']=refreshed
   elif p['brand']=='Вулкан':
    doc=fetch(p['source']);heading=doc.xpath('//h1')
    expected=p.get('manufacturer_title','Vulkan Eko '+str(p['power']))
    if not heading or text(heading[0])!=expected:raise ValueError('Vulkan model mismatch')
    prices=doc.xpath('//*[contains(concat(" ",@class," ")," product__price ")]//*[@itemprop="price"]')
    if len(prices)!=1:raise ValueError('Vulkan price selector changed')
    candidate['price']=amount(prices[0].get('content') or text(prices[0]))
   elif p['brand']=='ZOTA':
    if p['source'] not in zota:raise ValueError('Exact ZOTA product is no longer in the supplier category')
    data=zota[p['source']]
    if data['manufacturer_article']!=p['manufacturer_article'] or data['name']!=p['manufacturer_title']:raise ValueError('ZOTA identity changed; review required')
    candidate['price']=data['price']
   else:pending.append({'model':p['name'],'reason':'No automatic price source configured'});continue
   if p['price'] and not .7<=candidate['price']/p['price']<=1.3:raise ValueError('Price change above 30% requires review')
   candidate['checked_at']=today[:10];p.clear();p.update(candidate);updated.append(p['name'])
  except Exception as ex:errors.append({'model':p['name'],'error':str(ex)[:180]})
 known={('Автоматический котел FACI GT' if p['name'].endswith('GT') else p['name']) for p in products if p['brand']=='FACI'}
 pending.extend({'model':name,'reason':'New FACI model requires owner review'} for name in faci if name not in known)
 known_start={p['source'] for p in products if p['brand']=='СТАРТ'}
 pending.extend({'model':url,'reason':'New START model requires owner review'} for url in start if url not in known_start)
 known_zota={p['source'] for p in products if p['brand']=='ZOTA'}
 pending.extend({'model':url,'reason':'New ZOTA burner or accessory requires owner review'} for url in zota if url not in known_zota)
 tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(products,ensure_ascii=False,indent=2));tmp.replace(path)
 report={'checked_at':today,'updated':updated,'errors':errors,'pending_review':pending};(ROOT/'data/sync-status.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
 if errors:print('Some sources failed; last verified values have been retained.')
if __name__=='__main__':refresh()
