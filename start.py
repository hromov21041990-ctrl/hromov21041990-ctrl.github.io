"""START automatic pellet-boiler catalogue content."""
from html import escape
from pathlib import PurePosixPath


def e(value):
    return escape(str(value), quote=True)


def breadcrumbs(product):
    return '<div class="wrap crumbs"><a href="/">Главная</a> / <a href="/katalog/">Котлы и горелки</a> / <a href="/start/">START</a> / ' + e(product["manufacturer_title"]) + '</div>'


def configuration_views(product):
    variants = {v["option_id"]: v for v in product["variants"]}
    bunkers = {b["option_id"]: b for b in product["bunkers"]}
    views = {}
    for offer in product["offers"]:
        variant = variants[offer["variant_id"]]
        bunker = bunkers[offer["bunker_id"]]
        capacity = f'{bunker["capacity_l"]} л'
        specs = {
            "Комплектация": variant["name"],
            "Внутренний артикул": offer["sku"],
        }
        for key, value in product["specs"].items():
            if key.lower().startswith("объем бункера"):
                value = capacity
            specs[key] = value
        specs["Выбранный бункер"] = capacity
        specs["Доплата за бункер"] = "Без доплаты" if bunker["extra"] == 0 else f'{bunker["extra"]:,}'.replace(",", "\u202f") + " ₽"
        if bunker.get("source_status"):
            specs["Статус бункера у производителя"] = bunker["source_status"]
        description = product["description"] + f' Выбран бункер объёмом {capacity}.'
        if product["path"].endswith("start-100-gr-right/"):
            description += " Бункер расположен справа относительно фронтальной стороны котла."
        if product["path"].endswith("start-100-gr-ash/"):
            description += " Исполнение оснащено автоматическим шнековым золоудалением и внешним зольным ящиком."
        views[offer["sku"]] = {"description": description, "specs": specs, "summary": variant["name"] + " · бункер " + capacity}
    return views


def specifications(view):
    return '<table class="specs" id="configuration-specs"><tbody>' + ''.join(
        '<tr><th scope="row">' + e(key) + '</th><td>' + e(value) + '</td></tr>' for key, value in view["specs"].items()
    ) + '</tbody></table>'


def facts(product):
    view = configuration_views(product)[product["offers"][0]["sku"]]
    specs = product["specs"]
    cards = [
        ("Подача топлива", specs.get("Шнек подачи топлива", "Жёсткий шнековый механизм") + ". " + specs.get("Тип горелки", "Ретортная горелка") + "."),
        ("Автоматика", specs.get("Автоматика", "Контроллер Термокуб С10") + ". Управление насосом отопления и подключение комнатного термостата предусмотрены."),
        ("Топливо", specs.get("Основное топливо", "Пеллеты") + ". Резервный автоматический режим: " + specs.get("Резервное топливо для автоматического режима", "уточняется") + "."),
        ("Защита", "Защита от перегрева, обратного огня, заклинивания шнека, образования конденсата и размораживания по данным производителя."),
    ]
    return '<section class="section white"><div class="wrap"><h2>Полное описание выбранного исполнения</h2><p id="configuration-description">' + e(view["description"]) + '</p><div class="start-feature-grid">' + ''.join(
        '<article class="tile"><h3>' + e(title) + '</h3><p>' + e(text) + '</p></article>' for title, text in cards
    ) + '</div></div></section>'


def documents(product):
    docs = product.get("documents", [])
    if not docs:
        return ""
    links = []
    for doc in docs:
        suffix = PurePosixPath(doc["url"].split("?", 1)[0]).suffix.upper().lstrip(".") or "ФАЙЛ"
        links.append('<a class="document-card" href="' + e(doc["url"]) + '" target="_blank" rel="noopener"><span>' + e(suffix) + '</span><strong>' + e(doc["title"]) + '</strong><small>Открыть документ производителя ↗</small></a>')
    return '<section class="section"><div class="wrap"><h2>Документы и чертежи производителя</h2><div class="document-grid">' + ''.join(links) + '</div></div></section>'


def intro():
    return "Все автоматические пеллетные котлы START из актуального раздела производителя: 9 исполнений мощностью от 20 до 150 кВт. В карточках доступны характеристики, варианты штатного бункера, внутренние артикулы, инструкции, декларации и чертежи."
