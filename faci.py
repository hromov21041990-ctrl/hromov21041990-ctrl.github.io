"""FACI pellet boiler facts, documents and catalogue navigation."""
from html import escape
import re

def e(value):return escape(str(value),quote=True)

def breadcrumbs(product):
    return '<div class="wrap crumbs"><a href="/">Главная</a> / <a href="/katalog/">Котлы и горелки</a> / <a href="/faci/">FACI</a> / '+e(product.get('manufacturer_title',product['name']))+'</div>'

def configuration_views(product):
    """Render facts only from the selected manufacturer's equipment and bunker data."""
    variants={v['option_id']:v for v in product['variants']}
    bunkers={b['option_id']:b for b in product['bunkers']}
    base_capacity=int(re.search(r'\d+',product['specs']['Емкость бункера']).group())
    views={}
    for offer in product['offers']:
        variant=variants[offer['variant_id']];bunker=bunkers[offer['bunker_id']]
        capacity=str(bunker['capacity_l'])+' л'
        includes=variant['includes']
        specs={'Комплектация':variant['name'],'Артикул':offer['sku']}
        for key,value in product['specs'].items():
            if 'емкость бункера' in key.lower().replace('ё','е'):
                value=capacity
            elif bunker['capacity_l']!=base_capacity and (key.lower().startswith('габариты') or key.lower().startswith('вес')):
                value='Уточняется для бункера '+capacity
            specs[key]=value
        for feature in ['Автоподжиг','Автоочистка теплообменника','Автозолоудаление']:
            specs[feature]='Входит в комплектацию' if feature in includes else 'Не входит в комплектацию'
        if 'Очистка котла с помощью рычага' in includes:
            specs['Очистка котла']='Механическая, с помощью рычага'
        description=product['name']+'. Мощность: '+product['power_label']+'. Комплектация '+variant['name']+', бункер '+capacity+'. '
        description+='Оснащение: '+', '.join(feature[0].lower()+feature[1:] for feature in includes)+'. '
        if product['specs'].get('Вид топлива'):description+='Топливо: '+product['specs']['Вид топлива']+'.'
        views[offer['sku']]={'description':description,'specs':specs,'summary':variant['name']+' · бункер '+capacity}
    return views

def specifications(product,view):
    return '<table class="specs" id="configuration-specs"><tbody>'+''.join('<tr><th scope="row">'+e(k)+'</th><td>'+e(v)+'</td></tr>' for k,v in view['specs'].items())+'</tbody></table>'

def facts(product):
    view=configuration_views(product)[product['offers'][0]['sku']]
    description=view['description']
    if not description:return ''
    body='<section class="section white"><div class="wrap"><h2>Описание выбранной комплектации</h2><p id="configuration-description">'+e(description)+'</p>'
    for warning in product.get('facts_to_confirm',[]):
        body+='<p class="fine">'+e(warning)+'</p>'
    return body+'</div></section>'

def documents(product):
    docs=product.get('documents',[])
    if not docs:return ''
    return '<section class="section"><div class="wrap"><h2>Документы производителя</h2><div class="actions">'+''.join('<a class="btn light" href="'+e(d['url'])+'" target="_blank" rel="noopener">'+e(d['title'])+' →</a>' for d in docs)+'</div></div></section>'

def intro():
    return 'Пеллетные котлы FACI и FACI GT. Выберите мощность, комплектацию и бункер: цена и артикул обновятся в карточке модели. Поможем с подбором, доставкой и монтажом.'
