"""ZOTA pellet-burner catalogue presentation."""
from html import escape
from pathlib import PurePosixPath

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
    body += f'<div class="wrap"><div class="page-head"><span class="eyebrow">Каталог ZOTA</span><h1>{e(title)}</h1><p class="lead">{e(lead)}</p></div>{tabs(selected)}'
    if selected:
        subset = [p for p in items if p["zota_category"] == selected]
        body += f'<p class="fine">{count_label(len(subset))}</p><div class="grid products">' + "".join(card(p) for p in subset) + '</div>'
    else:
        body += '<div class="filters"><input id="search" aria-label="Поиск товара ZOTA" placeholder="Название, артикул производителя или внутренний артикул"></div>'
        body += f'<p class="fine" id="count">{count_label(len(items))}</p><div class="grid products">' + "".join(card(p) for p in items) + '</div><div id="empty" class="empty" hidden>По вашему запросу ничего не найдено.</div>'
    return body + '</div>'


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
