"""Vulkan spare parts catalogue presentation."""

from html import escape


CATEGORIES = [
    ("automatic-options", "Опции автоматических котлов", "opcii-avtomaticheskih-kotlov"),
    ("bunkers-ash", "Бункеры и зольники", "bunkery-i-zolniki"),
    ("cleaning-firebox", "Комплекты чистки и топочная часть", "chistka-i-topochnaya-chast"),
    ("ash-fuel-feed", "Золоудаление и подача топлива", "zoloudalenie-i-podacha-topliva"),
    ("burners", "Горелки", "gorelki"),
    ("augers-drives", "Шнеки и приводы", "shneki-i-privody"),
    ("fans", "Вентиляторы", "ventilyatory"),
    ("automation", "Автоматика", "avtomatika"),
    ("semi-auto-parts", "Комплектующие полуавтоматических котлов", "komplektuyushchie-poluavtomaticheskih-kotlov"),
    ("semi-auto-automation", "Автоматика полуавтоматических котлов", "avtomatika-poluavtomaticheskih-kotlov"),
]


def e(value):
    return escape(str(value), quote=True)


def catalog_body(products, card, selected=None):
    members = [product for product in products if product.get("product_type") == "vulkan_spare"]
    if selected:
        members = [product for product in members if product["vulkan_spare_category"] == selected]
    label = next((name for key, name, _ in CATEGORIES if key == selected), "Запчасти и комплектующие Vulkan")
    category_tabs = '<div class="brand-tabs"><a class="' + ("active" if not selected else "") + '" href="/vulkan/zapchasti/">Все запчасти</a>' + ''.join(
        '<a class="' + ("active" if selected == key else "") + '" href="/vulkan/zapchasti/' + route + '/">' + e(name) + '</a>'
        for key, name, route in CATEGORIES
    ) + '</div>'
    return (
        '<div class="wrap crumbs"><a href="/">Главная</a> / <a href="/katalog/">Котлы и горелки</a> / '
        '<a href="/vulkan/">Vulkan</a> / ' + e(label) + '</div>'
        '<div class="wrap"><div class="page-head"><span class="eyebrow">Vulkan · запасные части</span><h1>' + e(label) + '</h1>'
        '<p class="lead">Запасные части, горелки и дополнительное оборудование для котлов Vulkan. Цены указаны по РРЦ производителя из прайса от 15 июня 2026 года.</p></div>'
        '<div class="brand-tabs"><a href="/vulkan/">Котлы Vulkan</a><a class="active" href="/vulkan/zapchasti/">Запчасти Vulkan</a></div>'
        + category_tabs
        + '<div class="filters"><input id="search" aria-label="Поиск запчасти Vulkan" placeholder="Название или внутренний артикул"></div>'
        '<p class="fine" id="count">' + str(len(members)) + ' товаров</p><div class="grid products">' + ''.join(card(product) for product in members) + '</div>'
        '<div id="empty" class="empty" hidden>По вашему запросу ничего не найдено.</div></div>'
    )


def breadcrumbs(product):
    return (
        '<div class="wrap crumbs"><a href="/">Главная</a> / <a href="/katalog/">Котлы и горелки</a> / '
        '<a href="/vulkan/">Vulkan</a> / <a href="/vulkan/zapchasti/">Запчасти</a> / ' + e(product["name"]) + '</div>'
    )


def facts(product):
    return (
        '<section class="section white"><div class="wrap biotep-description"><span class="eyebrow">Запасная часть Vulkan</span>'
        '<h2>Назначение и подбор</h2><p>' + e(product["summary"]) + '</p><div class="biotep-feature-grid">'
        '<article class="tile"><h3>Раздел</h3><p>' + e(product["vulkan_spare_category_label"]) + '</p></article>'
        '<article class="tile"><h3>Артикул PelletsGrupp</h3><p>' + e(product["sku"]) + '</p></article>'
        '<article class="tile"><h3>Цена</h3><p>РРЦ производителя</p></article>'
        '<article class="tile"><h3>Подбор</h3><p>Проверим совместимость с моделью и мощностью котла.</p></article>'
        '</div></div></section>'
    )
