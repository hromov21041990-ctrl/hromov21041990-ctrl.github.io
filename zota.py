"""ZOTA pellet-burner catalogue presentation."""
from html import escape
from pathlib import PurePosixPath
from catalog_nav import brand_tabs

CATEGORIES = [
    ("gorelki", "Пеллетные горелки", "Горелки FOX G2 и RAY G2 с контроллером C-Line PBA.", "gorelki"),
    ("bunker", "Бункеры", "Основные бункеры и дополнительные секции для увеличения объёма.", "bunkery"),
    ("mehanizm-podachi", "Механизм подачи", "Шнековый механизм подачи для горелок FOX и RAY.", "mehanizm-podachi"),
    ("adapter", "Адаптеры", "Адаптеры для установки горелок на конкретные модели котлов.", "adaptery"),
    ("otboynik", "Отбойники", "Отбойники топки для совместимых котлов и горелок.", "otboiniki"),
    ("avtomatika-dlya-gorelok", "Автоматика для горелок", "Дополнительные элементы управления горелкой.", "avtomatika"),
]


def e(value):
    return escape(str(value), quote=True)


def category(product):
    return next(item for item in CATEGORIES if item[0] == product["zota_category"])


def category_path(key):
    return "/zota/" + next(item[3] for item in CATEGORIES if item[0] == key) + "/"


def count_label(count):
    if count % 10 == 1 and count % 100 != 11:
        word = "товар"
    elif count % 10 in (2, 3, 4) and count % 100 not in (12, 13, 14):
        word = "товара"
    else:
        word = "товаров"
    return f"{count} {word}"


def rubles(value):
    return f"{int(value):,}".replace(",", " ") + " ₽"


def burner_landing(items):
    rows = []
    for product in items:
        specs = product["specs"]
        rows.append(
            '<tr><th scope="row"><a href="' + e(product["path"]) + '">' + e(product["name"].split(" (", 1)[0]) + '</a></th>'
            '<td>' + e(specs["Мощность, кВт"]) + ' кВт</td>'
            '<td>' + e(specs["Система самоочистки лотка горелки"]) + '</td>'
            '<td>' + e(rubles(product["price"])) + '</td></tr>'
        )
    return '''
<section class="section"><div class="wrap burner-intro"><div><span class="eyebrow">Сравнение моделей</span><h2>FOX G2 или RAY G2</h2><p>В каталоге представлены приставные горелки ZOTA мощностью 25 и 43 кВт. Все три позиции комплектуются контроллером C-Line PBA; бункер, механизм подачи и адаптер подбираются под котёл и условия монтажа.</p></div><div class="table-scroll"><table class="specs burner-comparison"><thead><tr><th>Модель</th><th>Мощность</th><th>Очистка лотка</th><th>Цена</th></tr></thead><tbody>''' + "".join(rows) + '''</tbody></table></div></div></section>
<section class="section white"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Комплект для автоматической подачи</span><h2>Что подобрать вместе с горелкой</h2></div></div><div class="grid burner-accessories"><a class="tile" href="/zota/bunkery/"><h3>Бункер для пеллет</h3><p>Объём выбирают по доступному месту, мощности и желаемому интервалу между загрузками.</p><span class="text-link">Выбрать бункер →</span></a><a class="tile" href="/zota/mehanizm-podachi/"><h3>Механизм подачи</h3><p>Шнек подаёт топливо из бункера в горелку. Совместимость проверяется для выбранной серии.</p><span class="text-link">Механизм подачи →</span></a><a class="tile" href="/zota/adaptery/"><h3>Адаптер для котла</h3><p>Адаптер выбирают по модели и мощности котла; до заказа нужно сверить монтажные размеры.</p><span class="text-link">Подобрать адаптер →</span></a></div></div></section>
<section class="section"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Проверка до покупки</span><h2>Как выбрать пеллетную горелку</h2></div></div><div class="grid burner-factors"><article class="service"><div class="num">01 / МОЩНОСТЬ</div><h3>Тепловая нагрузка</h3><p>Мощность горелки сопоставляют с теплопотерями объекта и допустимым диапазоном мощности котла.</p></article><article class="service"><div class="num">02 / СОВМЕСТИМОСТЬ</div><h3>Конструкция котла</h3><p>Проверяют топочную дверцу, посадочные размеры, требования производителя и возможность установки адаптера.</p></article><article class="service"><div class="num">03 / ТОПЛИВО</div><h3>Пеллеты 6–8 мм</h3><p>Для моделей FOX G2 и RAY G2 производитель указывает пеллеты диаметром 6–8 мм. Качество топлива влияет на режим очистки и обслуживание.</p></article></div><p class="burner-service-link">Перед установкой важно оценить котельную, дымоход и обвязку. Посмотрите условия <a href="/otoplenie/">монтажа отопления</a> и варианты <a href="/pellety/">топливных пеллет</a>.</p></div></section>
<section class="section white"><div class="wrap burner-faq"><span class="eyebrow">Ответы перед заказом</span><h2>Частые вопросы о горелках ZOTA</h2><details><summary>Что входит в показанную цену?</summary><p>В карточках представлены горелки FOX G2 и RAY G2 с контроллером C-Line PBA. Точный состав позиции указан в названии и характеристиках; бункер, механизм подачи и адаптер выбираются отдельно.</p></details><details><summary>Можно ли установить горелку на любой твердотопливный котёл?</summary><p>Нет, совместимость нужно проверять для конкретной модели котла. Имеют значение конструкция топки, мощность, посадочные размеры, требования производителя и подходящий адаптер.</p></details><details><summary>Чем отличаются FOX G2 и RAY G2?</summary><p>В представленном каталоге FOX G2 доступна на 25 и 43 кВт с механической кочергой очистки. RAY G2 25 кВт использует подвижный лоток с ножом-отбойником. Остальные характеристики следует сравнить в карточках моделей.</p></details><details><summary>Какие пеллеты подходят?</summary><p>Для этих серий производитель указывает гранулы диаметром 6–8 мм. Перед закупкой топлива необходимо сверить паспорт выбранной модели и требования к качеству пеллет.</p></details></div></section>
'''


def tabs(active=None):
    links = ['<a class="' + ("active" if active is None else "") + '" href="/zota/">Все товары</a>']
    for key, label, _, route in CATEGORIES:
        cls = "active" if key == active else ""
        links.append(f'<a class="{cls}" href="/zota/{route}/">{e(label)}</a>')
    return '<nav class="brand-tabs zota-tabs" aria-label="Разделы ZOTA">' + "".join(links) + "</nav>"


def catalog_body(products, card, selected=None):
    items = [p for p in products if p["brand"] == "ZOTA"]
    selected_meta = next((item for item in CATEGORIES if item[0] == selected), None)
    title = selected_meta[1] + " ZOTA" if selected_meta else "Пеллетные горелки и комплектующие ZOTA"
    lead = selected_meta[2] if selected_meta else "Каталог повторяет структуру производителя: пеллетные горелки, бункеры, механизм подачи, адаптеры, отбойники и автоматика. Для каждой позиции указан отдельный внутренний артикул для 1С."
    body = '<div class="wrap crumbs"><a href="/">Главная</a> / <a href="/katalog/">Котлы и горелки</a> / ' + (e(title) if selected is None else '<a href="/zota/">ZOTA</a> / ' + e(selected_meta[1])) + '</div>'
    body += f'<div class="wrap"><div class="page-head"><span class="eyebrow">Каталог ZOTA</span><h1>{e(title)}</h1><p class="lead">{e(lead)}</p></div>{brand_tabs("ZOTA")}{tabs(selected)}'
    extra = ""
    if selected:
        subset = [p for p in items if p["zota_category"] == selected]
        product_classes = "grid products burner-products" if selected == "gorelki" else "grid products"
        body += f'<p class="fine">{count_label(len(subset))}</p><div class="{product_classes}">' + "".join(card(p) for p in subset) + '</div>'
        if selected == "gorelki":
            extra = burner_landing(subset)
    else:
        body += '<div class="filters"><input id="search" aria-label="Поиск товара ZOTA" placeholder="Название, артикул производителя или внутренний артикул"></div>'
        body += f'<p class="fine" id="count">{count_label(len(items))}</p><div class="grid products">' + "".join(card(p) for p in items) + '</div><div id="empty" class="empty" hidden>По вашему запросу ничего не найдено.</div>'
    return body + '</div>' + extra


def breadcrumbs(product):
    _, label, _, _ = category(product)
    return '<div class="wrap crumbs"><a href="/">Главная</a> / <a href="/katalog/">Котлы и горелки</a> / <a href="/zota/">ZOTA</a> / <a href="' + category_path(product["zota_category"]) + '">' + e(label) + '</a> / ' + e(product["name"]) + '</div>'


def facts(product, rich):
    description = rich(product.get("description") or "")
    if not description:
        description = '<p>' + e(product.get("summary") or "Оригинальная продукция ZOTA.") + '</p>'
    return '<section class="section white"><div class="wrap zota-description"><span class="eyebrow">Описание производителя</span><h2>О товаре</h2>' + description + '</div></section>'


def documents(product):
    docs = product.get("documents", [])
    if not docs:
        return ""
    links = []
    for doc in docs:
        suffix = PurePosixPath(doc["url"].split("?", 1)[0]).suffix.upper().lstrip(".") or "ФАЙЛ"
        links.append('<a class="document-card" href="' + e(doc["url"]) + '" target="_blank" rel="noopener"><span>' + e(suffix) + '</span><strong>' + e(doc["title"]) + '</strong><small>Открыть документ производителя ↗</small></a>')
    return '<section class="section"><div class="wrap"><h2>Документы производителя</h2><div class="document-grid">' + "".join(links) + '</div></div></section>'
