"""Catalogue presentation for START boiler spares."""
import html
CATEGORIES=[
 ('seals','Уплотнения и расходники','uplotneniya-i-raskhodniki'),
 ('heat_exchange','Турбулизаторы и чистка','turbulizatory-i-chistka'),
 ('sensors','Датчики и автоматика','datchiki-i-avtomatika'),
 ('body','Дверки, ручки и стекло','dverki-ruchki-i-steklo'),
 ('auger','Шнеки и приводы','shneki-i-privody'),
 ('bunkers','Топливные бункеры','bunkery'),
]
def e(v): return html.escape(str(v),quote=True)
def catalog_body(products,card,selected=None):
 members=[p for p in products if p.get('product_type')=='start_spare' and (not selected or p['start_spare_category']==selected)]
 label=next((v for k,v,_ in CATEGORIES if k==selected),'Запчасти для котлов СТАРТ')
 tabs='<div class="brand-tabs"><a class="'+('active' if not selected else '')+'" href="/start/zapchasti/">Все позиции</a>'+''.join('<a class="'+('active' if selected==k else '')+'" href="/start/zapchasti/'+route+'/">'+e(v)+'</a>' for k,v,route in CATEGORIES)+'</div>'
 return ('<div class="wrap crumbs"><a href="/">Главная</a> / <a href="/katalog/">Котлы и горелки</a> / <a href="/start/">СТАРТ</a> / '+e(label)+'</div>'
 '<div class="wrap"><div class="page-head"><span class="eyebrow">Запчасти и комплектующие</span><h1>'+e(label)+'</h1><p class="lead">Запасные части и расходные материалы для пеллетных котлов СТАРТ. Цены сверены с сайтом производителя 5 ноября 2026 года. Совместимость уточним по модели и году выпуска котла.</p></div>'
 '<div class="brand-tabs"><a href="/start/">Котлы СТАРТ</a><a class="active" href="/start/zapchasti/">Запчасти СТАРТ</a></div>'+tabs+
 '<div class="actions"><a class="btn light" href="/downloads/zapchasti-start-1c.xlsx" download>Скачать XLSX для 1С</a><a class="btn light" href="/downloads/prajs-pelletsgrupp.xlsx" download>Общая таблица цен</a></div>'
 '<div class="filters"><input id="search" aria-label="Поиск запчасти" placeholder="Название или артикул"></div><p class="fine" id="count">'+str(len(members))+' товаров</p><div class="grid products">'+''.join(card(p) for p in members)+'</div><div id="empty" class="empty" hidden>По вашему запросу ничего не найдено.</div></div>')
def breadcrumbs(p):
 return '<div class="wrap crumbs"><a href="/">Главная</a> / <a href="/start/">СТАРТ</a> / <a href="/start/zapchasti/">Запчасти</a> / '+e(p['name'])+'</div>'
def facts(p):
 return ('<section class="section white"><div class="wrap biotep-description"><span class="eyebrow">Запчасти СТАРТ</span><h2>Назначение и совместимость</h2><p>'+e(p['summary'])+'</p><div class="biotep-feature-grid">'
 '<article class="tile"><h3>Раздел</h3><p>'+e(p['start_spare_category_label'])+'</p></article><article class="tile"><h3>Наличие у производителя</h3><p>'+e(p['source_availability'])+'</p></article><article class="tile"><h3>Цена</h3><p>Цена производителя</p></article><article class="tile"><h3>Подбор</h3><p>Проверим совместимость по модели и году выпуска котла.</p></article></div></div></section>')
