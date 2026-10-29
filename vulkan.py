"""Vulkan series navigation and product facts within the existing storefront."""
from html import escape

SERIES=[('boss','Boss',13),('eko','Eko',9),('eko-max','Eko-Max',5),('max-duo','Max-Duo',5),('optimum-ultra','Optimum-Ultra',6),('optimum-ultra-pro','Optimum-Ultra-Pro',7),('optimum-uni','Optimum-Uni',8),('optimum-uni-max','Optimum-Uni-Max',6),('optimum-uni-pro','Optimum-Uni-Pro',5)]

def e(value):return escape(str(value),quote=True)
def series_url(key):return '/vulkan/'+key+'/'
def plural(n,words):return words[2] if 11<=n%100<=14 else words[0] if n%10==1 else words[1] if 2<=n%10<=4 else words[2]
def money(n):return f'{n:,}'.replace(',','\u202f')+' ₽'
def breadcrumbs(product=None,series=None):
    links='<a href="/">Главная</a> / <a href="/katalog/">Котлы и горелки</a>'
    if product or series:links+=' / <a href="/vulkan/">Vulkan</a>'
    else:links+=' / Vulkan'
    if product:
        links+=f' / <a href="{series_url(product["series"])}">{e(product["series_name"])}</a> / {e(product["manufacturer_title"])}'
    elif series:links+=' / '+e(series[1])
    return '<div class="wrap crumbs">'+links+'</div>'

def catalog_body(products,card,series=None):
    all_products=[p for p in products if p['brand']=='Вулкан' and p.get('product_type')!='vulkan_spare']
    selected=[p for p in all_products if not series or p['series']==series[0]]
    title='Автоматические котлы Vulkan'+(' '+series[1] if series else '')
    lead='Выберите модель по мощности, топливу и комплектации. Поможем с подбором, доставкой и монтажом.'
    body=breadcrumbs(series=series)+f'<div class="wrap vulkan-catalog"><div class="page-head"><span class="eyebrow">Vulkan · каталог оборудования</span><h1>{e(title)}</h1><p class="lead">{lead}</p></div>'
    body+='<div class="brand-tabs"><a class="active" href="/vulkan/">Котлы Vulkan</a><a href="/vulkan/zapchasti/">Запчасти Vulkan</a></div>'
    if not series:
        body+='<div class="section-head vulkan-section-head"><h2>Серии котлов</h2><span class="fine">9 серий · 64 модели</span></div><div class="series-grid">'
        for key,label,expected in SERIES:
            items=[p for p in all_products if p['series']==key]
            assert len(items)==expected,(key,len(items),expected)
            representative=items[0]
            count=len(items)
            body+=f'<a class="series-card" href="{series_url(key)}"><div class="series-image"><img src="{e(representative["images"][0])}" alt="{e(representative["manufacturer_title"])} — серия {e(label)}" loading="lazy" width="300" height="220"></div><div class="series-copy"><span class="badge">Vulkan</span><h2>{e(label)}</h2><p>{count} {plural(count,["модель","модели","моделей"])}</p><strong>от {money(min(p["price"] for p in items))}</strong><span class="text-link">Смотреть серию →</span></div></a>'
        body+='</div><div class="section-head vulkan-section-head" id="models"><h2>Все модели Vulkan</h2></div>'
    else:
        body+='<nav class="series-pills" aria-label="Серии Vulkan"><a href="/vulkan/">Все серии</a>'
        for key,label,_ in SERIES:
            active=' class="active" aria-current="page"' if key==series[0] else ''
            body+=f'<a{active} href="{series_url(key)}">{e(label)}</a>'
        body+='</nav>'
    body+='<div class="filters vulkan-filters"><label><span>Модель или артикул</span><input id="search" type="search" aria-label="Модель или артикул" placeholder="Boss 16 или PG-000001" autocomplete="off"></label>'
    if not series:
        body+='<label><span>Серия</span><select id="series-filter" aria-label="Серия"><option value="">Все серии</option>'+''.join(f'<option value="{key}">{e(label)}</option>' for key,label,_ in SERIES)+'</select></label>'
    body+='<label><span>Сортировка</span><select id="sort" aria-label="Сортировка"><option value="default">По порядку в каталоге</option><option value="price-asc">Сначала дешевле</option><option value="price-desc">Сначала дороже</option><option value="power-asc">По мощности</option></select></label><button type="button" class="btn light" id="clear-filters">Сбросить</button></div>'
    body+=f'<p class="fine" id="count" data-noun="models" aria-live="polite">{len(selected)} {plural(len(selected),["модель","модели","моделей"])}</p><div class="grid products vulkan-products">'+''.join(card(p) for p in selected)+'</div><div id="empty" class="empty" hidden>Таких моделей не найдено. Измените запрос или сбросьте фильтры.</div>'
    body+='<p class="fine catalog-note">Цены сверены с каталогом производителя 21.10.2026. Наличие и состав поставки уточняются перед заказом.</p></div>'
    return body

def product_facts(product):
    description=product.get('description','')
    body='<section class="section white"><div class="wrap"><h2>О модели</h2><p class="model-description">'+e(description)+'</p>'
    if product.get('facts_to_confirm'):
        body+='<p class="fine">Часть характеристик требует уточнения при подборе. Свяжитесь с нами, чтобы проверить исполнение для вашего объекта.</p>'
    body+='</div></section>'
    return body

def documents(product):
    docs=product.get('documents',[])
    if not docs:return ''
    return '<section class="section"><div class="wrap"><h2>Документы производителя</h2><div class="document-links">'+''.join(f'<a class="btn light" href="{e(d["url"])}" target="_blank" rel="noopener">{e(d["title"])} · PDF ↗</a>' for d in docs)+'</div></div></section>'
