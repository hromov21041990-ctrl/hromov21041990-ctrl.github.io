"""BIOTEP pellet-boiler catalogue presentation."""
from html import escape


def e(value):
    return escape(str(value), quote=True)


def breadcrumbs(product):
    return '<div class="wrap crumbs"><a href="/">Главная</a> / <a href="/katalog/">Котлы и горелки</a> / <a href="/biotep/">BIOTEP</a> / ' + e(product["manufacturer_title"]) + '</div>'


def facts(product):
    specs = product["specs"]
    cards = [
        ("Автоматическая работа", "Розжиг, подача топлива, поддержание мощности и остановка выполняются автоматикой котла."),
        ("Адаптация к условиям", "Система управления распознаёт теплотворность пеллет и особенности дымохода."),
        ("Запас топлива", "Встроенный бункер: " + specs["Встроенный бункер"] + "."),
        ("Горячая вода", "Подключение бойлера горячего водоснабжения предусмотрено производителем."),
    ]
    advantages = ''.join('<li>' + e(item) + '</li>' for item in product["advantages"])
    return '<section class="section white"><div class="wrap biotep-description"><span class="eyebrow">Описание производителя</span><h2>О модели</h2><p>' + e(product["description"]) + '</p><div class="biotep-feature-grid">' + ''.join(
        '<article class="tile"><h3>' + e(title) + '</h3><p>' + e(text) + '</p></article>' for title, text in cards
    ) + '</div><div class="biotep-advantages"><h2>Основные возможности</h2><ul>' + advantages + '</ul></div></div></section>'


def documents(product):
    links = []
    for document in product.get("documents", []):
        links.append('<a class="document-card" href="' + e(document["url"]) + '" target="_blank" rel="noopener"><span>' + e(document.get("type", "PDF")) + '</span><strong>' + e(document["title"]) + '</strong><small>Открыть официальный документ ↗</small></a>')
    if not links:
        return ""
    return '<section class="section"><div class="wrap"><span class="eyebrow">Библиотека BIOTEP</span><h2>Паспорта, схемы и сервисные материалы</h2><p class="lead biotep-doc-lead">Документы открываются из официальной библиотеки производителя.</p><div class="document-grid">' + ''.join(links) + '</div><p class="fine biotep-support-link"><a href="' + e(product["support_source"]) + '" target="_blank" rel="noopener">Все инструкции на сайте BIOTEP →</a></p></div></section>'


def intro():
    return "Четыре автоматических пеллетных котла из актуальной линейки производителя: описание, полные характеристики, официальные паспорта, схемы подключения и сервисные материалы."
