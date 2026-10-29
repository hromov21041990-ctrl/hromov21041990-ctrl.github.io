"""Import only the audited FACI pellet category, retaining all existing identities."""
import hashlib
import json
import re
import sys
from pathlib import Path
from PIL import Image, ImageOps
from catalog_identity import prepare_catalog, save_json

ROOT=Path(__file__).resolve().parent

def volume(name):
    value=float(re.search(r'\d+(?:[.,]\d+)?',name).group().replace(',','.'))
    return round(value*1000) if re.search(r'м\s*[3³]',name) else round(value)

def main(source):
    raw=json.loads((source/'catalog.json').read_text())
    expected=['GT','15','20','26','34','42','51','78','105','130','215','258','386','455','645','761','1000','1500']
    assert len(raw)==18 and {r['model'] for r in raw}==set(expected)
    rows={r['model']:r for r in raw}
    products=json.loads((ROOT/'data/products.json').read_text())
    previous={p['name'].split('FACI ')[-1]:p for p in products if p['brand']=='FACI'}
    assets=ROOT/'assets/faci';assets.mkdir(parents=True,exist_ok=True)
    result=[]
    for model in expected:
        row=rows[model];prior=previous.get(model,{})
        assert '/catalog/pelletnye-kotly/' in row['source_url']
        images=[]
        for photo in row['images']:
            path=Path(photo['local_path']);checksum=hashlib.sha256(path.read_bytes()).hexdigest()
            assert checksum==photo['sha256']
            target=assets/(checksum[:20]+'.webp')
            with Image.open(path) as image:
                image=ImageOps.exif_transpose(image).convert('RGBA')
                image.thumbnail((1400,1400))
                background=Image.new('RGBA',image.size,'white')
                image=Image.alpha_composite(background,image).convert('RGB')
                image.save(target,'WEBP',quality=88,method=6)
            url='/assets/faci/'+target.name
            if url not in images:images.append(url)
        variants=[];bunkers=[]
        old_variants={x['name']:x for x in prior.get('variants',[])}
        old_bunkers={volume(x['name']):x for x in prior.get('bunkers',[])}
        for v in row['variants']:
            option={k:v[k] for k in ['name','price','includes']}
            if old_variants.get(v['name'],{}).get('option_id'):option['option_id']=old_variants[v['name']]['option_id']
            variants.append(option)
        for b in row['bunkers']:
            capacity=volume(b['name']);old=old_bunkers.get(capacity,{})
            option={'name':old.get('name',b['name']),'extra':b['extra'],'capacity_l':capacity}
            if old.get('option_id'):option['option_id']=old['option_id']
            bunkers.append(option)
        assert variants and bunkers and images
        assert len({volume(b['name']) for b in bunkers})==len(bunkers)
        p={'id':prior.get('id',hashlib.sha256(('FACI:'+model).encode()).hexdigest()[:12]),'name':prior.get('name','Пеллетный котел FACI '+model),'brand':'FACI','power':None if row.get('power_min_kw') is not None else row['power_kw'],'power_label':row['power_label'],'path':prior.get('path','/katalog/item/faci-'+model.lower()+'/'),'legacy_price':prior.get('legacy_price'),'price':variants[0]['price'],'images':images,'unit':'штука','source':row['source_url'],'manufacturer_title':row['title'],'checked_at':row['checked_at'],'specs':row['specifications'],'variants':variants,'bunkers':bunkers,'bunker_fixed':all(b.get('fixed',False) for b in row['bunkers']),'description':row['description'],'documents':row['documents'],'facts_to_confirm':[],'our_availability':None}
        if prior.get('sku'):p['sku']=prior['sku']
        result.append(p)
    assert sum(len(p['variants']) for p in result)==51
    assert sum(len(p['variants'])*len(p['bunkers']) for p in result)==129
    others=[p for p in products if p['brand']!='FACI']
    save_json(ROOT/'data/products.json',others+result)
    prepare_catalog()
    save_json(ROOT/'data/faci-source.json',{'checked_at':'2026-10-21','category_url':'https://facirus.ru/catalog/pelletnye-kotly/','models':18,'standard_configurations':129,'scope':'Pellet boilers and standard bunkers only; external DI STRADA accessories excluded','source_snapshot':[{k:r.get(k) for k in ['model','title','source_url','category_url','power_kw','power_min_kw','power_label','bunker_l','price','price_kind','variants','bunkers','external_bunkers','specifications','description','documents','warnings','conflicts','images','layout_options']} for r in raw]})
    print('Imported 18 FACI pellet models and 129 configurations; retained',len(others),'other models.')

if __name__=='__main__':main(Path(sys.argv[1]).resolve())
