import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


CATEGORIES = [
    {
        "key": "bojlery",
        "label": "Бойлеры косвенного нагрева",
        "source": ("Бойлеры косвенного нагрева", "Косвенники из нержавейки"),
        "description": "Эмалированные и нержавеющие бойлеры для приготовления горячей воды от котла.",
    },
    {
        "key": "teploakkumulyatory",
        "label": "Теплоаккумуляторы",
        "source": ("Теплоаккумуляторы",),
        "description": "Буферные ёмкости для устойчивой и экономичной работы системы отопления.",
    },
    {
        "key": "teploakkumulyatory-gvs",
        "label": "Теплоаккумуляторы с ГВС",
        "source": ("Теплоаккумуляторы с ГВС",),
        "description": "Баки с контуром горячего водоснабжения для отопления и приготовления воды.",
    },
    {
        "key": "baki-elektronagreva",
        "label": "Баки электронагрева",
        "source": ("Баки Электронагрева",),
        "description": "Ёмкости для нагрева воды электрическими ТЭНами.",
    },
    {
        "key": "holodoakkumulyatory",
        "label": "Холодоаккумуляторы",
        "source": ("Холодоаккумуляторы",),
        "description": "Накопительные ёмкости для систем охлаждения и кондиционирования.",
    },
    {
        "key": "teny-i-anody",
        "label": "ТЭНы и аноды",
        "source": ("ТЭНы для баков", "Магниевые аноды", "Титановые аноды и комплектующие"),
        "description": "ТЭНы, магниевые и титановые аноды, а также комплектующие для баков.",
    },
]


PREFIXES = {
    "Бойлеры косвенного нагрева": "Бойлер косвенного нагрева",
    "ТЭНы для баков": "ТЭН",
    "Теплоаккумуляторы": "Теплоаккумулятор",
    "Теплоаккумуляторы с ГВС": "Теплоаккумулятор с ГВС",
    "Косвенники из нержавейки": "Бойлер косвенного нагрева из нержавеющей стали",
    "Баки Электронагрева": "Бак электронагрева",
    "Холодоаккумуляторы": "Холодоаккумулятор",
}


IMAGES_BY_SERIES = {
    "P": ["/assets/stank/p.webp"],
    "P-2": ["/assets/stank/p-2.webp"],
    "P easy": ["/assets/stank/p-easy.webp"],
    "P Turbo": ["/assets/stank/p-turbo.webp"],
    "PWL": ["/assets/stank/pwl-pwr.webp"],
    "PWR": ["/assets/stank/pwl-pwr.webp"],
    "Магниевые аноды": ["/assets/stank/magnesium-anodes.webp"],
    "Титановые аноды и комплектующие": ["/assets/stank/titanium-kit.webp"],
    "AT": ["/assets/stank/at.webp", "/assets/stank/at-alt.webp"],
    "AT Prestige": ["/assets/stank/at-prestige.webp"],
    "ET": ["/assets/stank/at-alt.webp"],
    "FLAT": ["/assets/stank/flat.webp"],
    "SS": ["/assets/stank/ss.webp"],
    "HFWT": ["/assets/stank/hfwt.webp"],
    "HFWT DUO": ["/assets/stank/hfwt-duo.webp"],
    "FRESH": ["/assets/stank/fresh.webp"],
    "SOLAR SS": ["/assets/stank/solar-ss.webp"],
    "SOLAR SS DUO": ["/assets/stank/solar-ss-duo.webp"],
    "SS-HP": ["/assets/stank/ss-hp.webp"],
    "AT ETRO": ["/assets/stank/atro.webp"],
    "AT ETRO MONO": ["/assets/stank/atro-mono.webp"],
    "SS ETRO": ["/assets/stank/atro.webp"],
    "SS ETRO MONO": ["/assets/stank/atro-mono.webp"],
    "ATP ETRO": ["/assets/stank/atp-etro.webp"],
    "ATP ETRO MONO": ["/assets/stank/atp-etro-mono.webp"],
    "CT": ["/assets/stank/ct.webp"],
    "SS CT": ["/assets/stank/ss-ct.webp"],
}


def _images(item):
    if item["series"] == "ТЭНы для баков":
        return ["/assets/stank/ten-small.webp" if item["name"].startswith(("2 ", "3 ")) else "/assets/stank/ten-large.webp"]
    return IMAGES_BY_SERIES.get(item["series"], ["/assets/stank/at.webp"])


def _product_name(item):
    if item["category"] in ("Магниевые аноды", "Титановые аноды и комплектующие"):
        return f'S-TANK {item["name"]}'
    return f'{PREFIXES.get(item["category"], "Оборудование")} S-TANK {item["name"]}'


def _option(entry):
    label = entry.get("label", "")
    if "магниев" in label.lower():
        return "С магниевым анодом", "MG"
    if "титанов" in label.lower():
        return "С титановым анодом", "TI"
    return "", ""


def _category(item):
    return next(category for category in CATEGORIES if item["category"] in category["source"])


def load_products():
    source = json.loads((ROOT / "data" / "stank_catalog.json").read_text())
    products = []
    for index, item in enumerate(source["items"], start=506):
        category = _category(item)
        internal = f"PG-{index:06d}"
        offers = []
        for entry in item["rrpColumns"]:
            option_name, suffix = _option(entry)
            price = round(entry["value"]) if isinstance(entry.get("value"), (int, float)) else None
            offers.append({
                "name": option_name,
                "article": f"{internal}-{suffix}" if suffix else internal,
                "price": price,
            })
        numeric_prices = [offer["price"] for offer in offers if offer["price"] is not None]
        products.append({
            **item,
            "internal_article": internal,
            "full_name": _product_name(item),
            "path": f'/santehnika/s-tank/{item["slug"]}/',
            "category_key": category["key"],
            "category_label": category["label"],
            "category_path": f'/santehnika/{category["key"]}/',
            "offers": offers,
            "price": min(numeric_prices) if numeric_prices else None,
            "images": _images(item),
        })
    return products


PRODUCTS = load_products()


def category_counts():
    return {
        category["key"]: sum(product["category_key"] == category["key"] for product in PRODUCTS)
        for category in CATEGORIES
    }


def card(product, esc, money):
    price_prefix = "от " if len(product["offers"]) > 1 and product["price"] is not None else ""
    facts = []
    if product.get("volume") is not None:
        facts.append(f'{product["volume"]} л')
    if product.get("power") is not None:
        facts.append(f'{product["power"]} кВт')
    meta = " · ".join(facts) or product["category_label"]
    search = " ".join((product["full_name"], product["internal_article"], product["supplierArticle"], product["series"], product["category_label"]))
    return f'''<article class="card stank-card" data-product="{esc(product["internal_article"])}" data-name="{esc(product["full_name"])}" data-brand="S-TANK" data-series="{esc(product["series"])}" data-price="{product["price"] if product["price"] is not None else ""}" data-search="{esc(search)}">
<a class="image" href="{product["path"]}" aria-label="{esc(product["full_name"])}"><img src="{product["images"][0]}" alt="{esc(product["full_name"])}" loading="lazy" decoding="async"></a>
<div class="card-body"><span class="badge">S‑TANK · {esc(product["series"])}</span><h3><a href="{product["path"]}">{esc(product["full_name"])}</a></h3><div class="meta">{esc(meta)} · арт. производителя {esc(product["supplierArticle"])}</div><p class="sku-line">Внутренний артикул: <span>{esc(product["internal_article"])}</span></p><div class="price">{price_prefix}{money(product["price"])}</div><a class="btn light" href="{product["path"]}">Подробнее →</a></div></article>'''


def category_tiles(esc):
    counts = category_counts()
    return "".join(
        f'''<a class="tile plumbing-tile" href="/santehnika/{category["key"]}/"><span class="badge">{counts[category["key"]]} товаров</span><h2>{esc(category["label"])}</h2><p>{esc(category["description"])}</p><span class="text-link">Открыть каталог →</span></a>'''
        for category in CATEGORIES
    )


def catalog_body(products, esc, money, title, lead, active_key=None):
    tabs = '<div class="brand-tabs stank-tabs"><a class="{}" href="/santehnika/">Все категории</a>{}</div>'.format(
        "active" if active_key is None else "",
        "".join(
            f'<a class="{"active" if active_key == category["key"] else ""}" href="/santehnika/{category["key"]}/">{esc(category["label"])}</a>'
            for category in CATEGORIES
        ),
    )
    return f'''<div class="wrap"><div class="page-head plumbing-head"><span class="eyebrow">S‑TANK · сантехника</span><h1>{esc(title)}</h1><p class="lead">{esc(lead)}</p></div>{tabs}<div class="filters"><input id="search" aria-label="Поиск товара S-TANK" placeholder="Название, серия или артикул"></div><p class="fine" id="count">{len(products)} товаров</p><div class="grid products stank-products">{"".join(card(product, esc, money) for product in products)}</div><div id="empty" class="empty" hidden>По вашему запросу ничего не найдено.</div></div>'''


def breadcrumb(product, esc):
    return f'''<div class="wrap crumbs"><a href="/">Главная</a> / <a href="/santehnika/">Сантехника</a> / <a href="{product["category_path"]}">{esc(product["category_label"])}</a> / {esc(product["name"])}</div>'''


def product_body(product, esc, money):
    thumbnails = "".join(
        f'<button data-src="{source}" data-alt="{esc(product["full_name"])} — фото {index + 1}" aria-label="Фото {index + 1}"><img src="{source}" alt="" loading="lazy"></button>'
        for index, source in enumerate(product["images"])
    )
    visual = f'''<div class="gallery stank-gallery"><img id="main-image" src="{product["images"][0]}" alt="{esc(product["full_name"])}"><div class="thumbs">{thumbnails}</div><p class="fine">Изображение серии из прайса производителя. Внешний вид конкретного объёма может отличаться.</p></div>'''
    if len(product["offers"]) > 1:
        options = "".join(
            f'<option value="{index}">{esc(offer["name"])} — {money(offer["price"])}</option>'
            for index, offer in enumerate(product["offers"])
        )
        selector = f'<label for="stank-option">Комплектация</label><select id="stank-option">{options}</select>'
    else:
        selector = ""
    selected = product["offers"][0] if product["offers"] else {"article": product["internal_article"], "price": product["price"]}
    buybox = f'''<div class="buybox"><span class="badge">S‑TANK · {esc(product["category_label"])}</span><h1>{esc(product["full_name"])}</h1><p class="sku-line">Внутренний артикул: <span id="product-sku">{esc(selected["article"])}</span></p><p class="fine">Артикул производителя: {esc(product["supplierArticle"])}</p>{selector}<div id="chosen-price" class="bigprice">{money(selected["price"])}</div><p class="fine">РРЦ по прайсу S‑TANK от 06.11.2026. Наличие и срок поставки уточняются при заказе.</p><div class="actions"><a class="btn" href="tel:+73433455225">Позвонить: +7 (343) 345-52-25</a></div><p class="fine">Назовите специалисту внутренний артикул или артикул производителя.</p><button class="btn light" id="stank-copy-quote">Скопировать выбранную модель</button><p id="copy-status" class="fine" aria-live="polite"></p></div>'''
    rows = [
        ("Бренд", "S-TANK"),
        ("Категория", product["category_label"]),
        ("Серия", product["series"]),
        ("Артикул производителя", product["supplierArticle"]),
        ("Объём, л", product.get("volume")),
        ("Мощность, кВт", product.get("power")),
        ("Площадь теплообменника, м²", product.get("area")),
        ("Размер, мм", product.get("dimensions")),
        ("Вес, кг", product.get("weight")),
    ]
    specs = '<table class="specs"><tbody>' + "".join(
        f'<tr><th scope="row">{esc(label)}</th><td>{esc(value)}</td></tr>'
        for label, value in rows if value not in (None, "")
    ) + '</tbody></table>'
    data = json.dumps({"name": product["full_name"], "offers": product["offers"]}, ensure_ascii=False).replace("</", "<\\/")
    return f'''{breadcrumb(product, esc)}<section class="section"><div class="wrap detail">{visual}{buybox}</div></section><section class="section white"><div class="wrap stank-description"><span class="eyebrow">Описание производителя</span><h2>О модели</h2><p>{esc(product["description"])}</p></div></section><section class="section"><div class="wrap"><h2>Характеристики</h2>{specs}</div></section><script type="application/json" id="stank-product-data">{data}</script>'''
