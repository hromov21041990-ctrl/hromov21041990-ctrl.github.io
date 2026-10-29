"""Import the checked manufacturer snapshot; keep existing product identities."""
import json,hashlib,re,sys
from pathlib import Path
from PIL import Image,ImageOps

ROOT=Path(__file__).resolve().parent
SOURCE=Path(sys.argv[1]).resolve()
from vulkan import SERIES
raw=json.loads((SOURCE/'catalog.json').read_text())
existing=json.loads((ROOT/'data/products.json').read_text())
existing_vulkan={p['path'].strip('/').rsplit('/',1)[-1]:p for p in existing if p['brand']=='Вулкан'}
expected={key:count for key,_,count in SERIES}
assert len(raw)==64
assert {key:sum(p['series']==key for p in raw) for key in expected}==expected
assets=ROOT/'assets/vulkan';assets.mkdir(exist_ok=True)
image_cache={}
new=[]
for row in raw:
    slug=row['slug'];previous=existing_vulkan.get(slug,{})
    images=[]
    for src in row['images']:
        local=SOURCE/src['local_image'];assert local.is_file(),local
        checksum=src['sha256'];name=checksum[:20]+'.webp'
        if checksum not in image_cache:
            with Image.open(local) as image:
                image=ImageOps.exif_transpose(image)
                image.thumbnail((1400,1400))
                if image.mode not in ('RGB','RGBA'):image=image.convert('RGBA')
                image.save(assets/name,'WEBP',quality=88,method=6)
            image_cache[checksum]='/assets/vulkan/'+name
        if image_cache[checksum] not in images:images.append(image_cache[checksum])
    specs={k:str(v) for k,v in row.get('site_specifications',row['specifications']).items() if str(v).strip()}
    if not specs:
        specs={k:str(v) for k,v in row.get('basic_specifications',{}).items() if str(v).strip()}
    notes=row.get('warnings',[])
    conflicts=row.get('conflicts',[])
    # Areas flagged by the manufacturer audit must not become confident website facts.
    uncertain_area=any(c.get('field')=='heating_area_m2' for c in conflicts)
    if uncertain_area:
        for k in list(specs):
            if 'площад' in k.lower():specs[k]='Уточняется при подборе'
    for k in list(specs):
        if 'мощность' in k.lower() and k.endswith('кВт') and not re.fullmatch(r'\d+(?:[,.]\d+)?',specs[k]):
            if not specs[k].strip():specs[k]='Уточняется при подборе'
    if row['series']=='optimum-uni-max' and row.get('power_kw') is None:
        specs['Мощность, кВт']='Уточняется при подборе'
    description=row['description']
    if uncertain_area:
        description=re.sub(r'Заявленная производителем отапливаемая площадь[^.]*\.\s*','',description)
    p={'id':previous.get('id',hashlib.sha256(('Vulkan:'+slug).encode()).hexdigest()[:12]),'name':'Автоматический котёл '+row['title'],'brand':'Вулкан','display_brand':'Vulkan','power':row.get('power_kw'),'path':previous.get('path','/katalog/item/'+slug+'/'),'legacy_price':previous.get('legacy_price'),'price':row['price'],'images':images,'unit':'штука','source':row['source_url'],'manufacturer_title':row['title'],'checked_at':'2026-10-21','specs':specs,'variants':[],'series':row['series'],'series_name':row['series_name'],'description':description,'documents':row['documents'],'facts_to_confirm':notes,'source_availability':row.get('source_availability'),'our_availability':None}
    assert p['price']>0 and images
    if previous.get('sku'):p['sku']=previous['sku']
    new.append(p)
others=[p for p in existing if p['brand']!='Вулкан']
products=others+new
assert len(products)==81 and len({p['id'] for p in products})==81 and len({p['path'] for p in products})==81
assert all(p['path'] in {n['path'] for n in new} for p in existing if p['brand']=='Вулкан')
(ROOT/'data/products.json').write_text(json.dumps(products,ensure_ascii=False,indent=2)+'\n')
audit={'checked_at':'2026-10-21','manufacturer':'https://kras-kotel.ru/','total':64,'series_counts':expected,'source_snapshot':[{k:r.get(k) for k in ['slug','title','series','source_url','price','price_source','specifications','basic_specifications','main_fuel','reserve_fuel','documents','warnings','conflicts','field_provenance']} for r in raw]}
(ROOT/'data/vulkan-source.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
print('Imported',len(new),'Vulkan models;',len(image_cache),'unique photos;',len(others),'other products preserved')
