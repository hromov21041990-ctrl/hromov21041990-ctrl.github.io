"""BIOTEP spare parts catalogue presentation."""

import html


CATEGORIES = [
    ("automation", "Автоматика и датчики", "avtomatika-i-datchiki"),
    ("airflow", "Вентиляторы и воздуховоды", "ventilyatory-i-vozduhovody"),
    ("auger", "Шнеки и приводы", "shneki-i-privody"),
    ("ignition", "Система розжига", "sistema-rozzhiga"),
    ("burner", "Горелка и дымоудаление", "gorelka-i-dymoudalenie"),
    ("body", "Турбуляторы и детали корпуса", "turbulyatory-i-korpus"),
    ("insulation", "Теплоизоляция", "teploizolyaciya"),
    ("tubes", "ПВХ-трубки", "pvh-trubki"),
    ("seals", "Уплотнения", "uplotneniya"),
    ("wires", "Комплект проводов", "provoda"),
]


def e(value):
    return html.escape(str(value), quote=True)


def catalog_body(products, card, selected=None):
    members = [product for product in products if product.get("product_type") == "biotep_spare"]
    if selected:
        members = [product for product in members if product["biotep_spare_category"] == selected]
    label = next((label for key, label, _ in CATEGORIES if key == selected), "Запчасти для котлов BIOTEP")
    tabs = '<div class="brand-tabs"><a class="' + ("active" if not selected else "") + '" href="/biotep/zapchasti/">Все запчасти</a>' + ''.join(
        '<a class="' + ("active" if selected == key else "") + '" href="/biotep/zapchasti/' + route + '/">' + e(name) + '</a>'
        for key, name, route in CATEGORIES
    ) + '</div>'
    return (
        '<div class="wrap crumbs"><a href="/">Главная</a> / <a href="/katalog/">Котлы и горелки</a> / '
        '<a href="/biotep/">BIOTEP</a> / ' + e(label) + '</div>'
        '<div class="wrap"><div class="page-head"><span class="eyebrow">Сервис и ремонт BIOTEP</span><h1>' + e(label) + '</h1>'
        '<p class="lead">Оригинальные запасные части для котлов BIOTEP. Цены указаны по РРЦ производителя с НДС из прайса, действующего с 12 февраля 2026 года.</p></div>'
        '<div class="brand-tabs"><a href="/biotep/">Котлы BIOTEP</a><a class="active" href="/biotep/zapchasti/">Запчасти BIOTEP</a></div>'
        + tabs +
        '<div class="filters"><input id="search" aria-label="Поиск запчасти" placeholder="Название, внутренний артикул или код производителя"></div>'
        '<p class="fine" id="count">' + str(len(members)) + ' товаров</p><div class="grid products">' + ''.join(card(product) for product in members) + '</div>'
        '<div id="empty" class="empty" hidden>По вашему запросу ничего не найдено.</div></div>'
    )


def breadcrumbs(product):
    return (
        '<div class="wrap crumbs"><a href="/">Главная</a> / <a href="/katalog/">Котлы и горелки</a> / '
        '<a href="/biotep/">BIOTEP</a> / <a href="/biotep/zapchasti/">Запчасти</a> / ' + e(product["name"]) + '</div>'
    )


def facts(product):
    code = product.get("manufacturer_article") or "не указан в прайсе"
    return (
        '<section class="section white"><div class="wrap biotep-description"><span class="eyebrow">Запасная часть BIOTEP</span>'
        '<h2>Назначение и совместимость</h2><p>' + e(product["summary"]) + '</p><div class="biotep-feature-grid">'
        '<article class="tile"><h3>Код производителя</h3><p>' + e(code) + '</p></article>'
        '<article class="tile"><h3>Раздел</h3><p>' + e(product["biotep_spare_category_label"]) + '</p></article>'
        '<article class="tile"><h3>Цена</h3><p>РРЦ производителя с НДС</p></article>'
        '<article class="tile"><h3>Подбор</h3><p>Проверим совместимость по модели и году выпуска котла.</p></article>'
        '</div></div></section>'
    )
