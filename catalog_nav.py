"""Shared manufacturer navigation for equipment catalogue pages."""
from html import escape

BRANDS = (
    ("BIOTEP", "/biotep/"),
    ("FACI", "/faci/"),
    ("Вулкан", "/vulkan/"),
    ("СТАРТ", "/start/"),
    ("ZOTA", "/zota/"),
)


def brand_tabs(active=None):
    links = ['<a href="/katalog/">Все марки</a>']
    for label, path in BRANDS:
        current = ' class="active" aria-current="page"' if label == active else ""
        links.append(f'<a{current} href="{path}">{escape(label)}</a>')
    return '<nav class="brand-tabs catalogue-brand-tabs" aria-label="Марки котлов и горелок">' + "".join(links) + "</nav>"
