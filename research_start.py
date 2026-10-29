"""Build an auditable START pellet-boiler snapshot from saved manufacturer pages."""
import argparse
import hashlib
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

from lxml import html

BASE = "https://www.kotel74.ru"
PAGES = [
    ("start20.html", "start-20-gr", "Пеллетный котел СТАРТ-20-GR"),
    ("start30.html", "start-30-gr", "Пеллетный котел СТАРТ-30-GR"),
    ("start30v2.html", "start-30-gr-v2", "Пеллетный котел СТАРТ-30-GR-V2"),
    ("start35.html", "start-35-gr", "Пеллетный котел СТАРТ-35-GR"),
    ("start50.html", "start-50-gr", "Пеллетный котел СТАРТ-50-GR"),
    ("start100.html", "start-100-gr", "Пеллетный котел СТАРТ-100-GR"),
    ("start100right.html", "start-100-gr-right", "Пеллетный котел СТАРТ-100-GR с правым бункером"),
    ("start100ash.html", "start-100-gr-ash", "Пеллетный котел СТАРТ-100-GR с автозолоудалением"),
    ("start150.html", "start-150-gr-max", "Пеллетный котел СТАРТ-100-GR-MAX, 150 кВт"),
]
AREA = {
    "start-20-gr": "50–200 м²", "start-30-gr": "100–300 м²",
    "start-30-gr-v2": "100–300 м²", "start-35-gr": "100–350 м²",
    "start-50-gr": "200–500 м²", "start-100-gr": "300–1000 м²",
    "start-100-gr-right": "300–1000 м²", "start-100-gr-ash": "300–1000 м²",
    "start-150-gr-max": "300–1500 м²",
}


def clean(value):
    return " ".join(value.replace("\xa0", " ").split())


def amount(value):
    return int(re.sub(r"\D", "", value))


def absolute(url):
    return urllib.parse.urljoin(BASE, url)


def download(url, directory):
    encoded = urllib.parse.quote(absolute(url), safe=":/%?=&")
    request = urllib.request.Request(encoded, headers={"User-Agent": "PelletsGrupp catalogue research"})
    data = urllib.request.urlopen(request, timeout=45).read()
    digest = hashlib.sha256(data).hexdigest()
    suffix = Path(urllib.parse.urlparse(url).path).suffix.lower() or ".bin"
    target = directory / f"{digest[:20]}{suffix}"
    target.write_bytes(data)
    return {"source_url": absolute(url), "local_path": str(target), "sha256": digest}


def product_from_page(path, slug, public_name, output):
    root = html.parse(str(path)).getroot()
    page_text = clean(root.text_content())
    source_url = root.xpath("string(//link[@rel='canonical']/@href)")
    title = clean(root.xpath("//h1")[0].text_content())
    price_nodes = root.xpath("//span[contains(concat(' ',normalize-space(@class),' '),' PricesalesPrice ')]")
    price = amount(clean(price_nodes[-1].text_content()))
    article_match = re.search(r"Артикул:\s*([^\s]+)", page_text)
    availability_match = re.search(r"Остаток:\s*\d+\s*•\s*(В наличии|Под заказ)", page_text)

    characteristic_tables = [table for table in root.xpath("//table") if "Характеристика" in clean(table.text_content())]
    assert len(characteristic_tables) == 1, (slug, len(characteristic_tables))
    specs = {}
    for row in characteristic_tables[0].xpath(".//tr[position()>1]"):
        cells = row.xpath("./td")
        if len(cells) != 2:
            continue
        key = clean(" ".join(cells[0].itertext()))
        value = clean(" ".join(cells[1].itertext()))
        if key.startswith("Габаритные размеры"):
            numbers = re.findall(r"\d+", value)
            if len(numbers) >= 3:
                value = " × ".join(numbers[:3]) + " мм (В × Ш × Г)"
        if key and value:
            specs[key] = value

    images = []
    for src in root.xpath("//img[contains(concat(' ',normalize-space(@class),' '),' slider-item-image ')]/@data-src"):
        if src in [item[0] for item in images]:
            continue
        downloaded = download(src, output / "images")
        images.append((src, downloaded))

    docs = []
    seen_docs = set()
    for link in root.xpath("//a[strong[contains(normalize-space(.),'СКАЧАТЬ')]]"):
        url = absolute(link.get("href"))
        if url in seen_docs:
            continue
        seen_docs.add(url)
        text = clean(link.getparent().text_content())
        doc_title = re.sub(r"^\d+\.\s*", "", text).replace("СКАЧАТЬ", "").strip()
        docs.append({"title": doc_title, "url": url})

    bunkers = []
    for option in root.xpath("//li[contains(translate(@title,'БУНКЕР','бункер'),'бункер')]"):
        bunker_name = clean(option.get("title"))
        capacity = int(re.search(r"\d+", bunker_name).group())
        entry = {"name": f"{capacity} л", "capacity_l": capacity, "extra": int(option.get("data-price", "0"))}
        if "proddisable" in option.get("class", ""):
            entry["source_status"] = "Временно недоступен для выбора у производителя"
        bunkers.append(entry)
    if not bunkers:
        capacity = int(re.search(r"\d+", specs["Объем бункера пеллет, литров"]).group())
        bunkers = [{"name": f"{capacity} л", "capacity_l": capacity, "extra": 0}]

    power_range = specs["Номинальная тепловая мощность, кВт"]
    power_values = [int(value) for value in re.findall(r"\d+", power_range)]
    power = power_values[-1]
    includes = [
        "Теплообменник и теплоизоляционные панели",
        "Шнековый механизм с ретортной горелкой",
        "Вентилятор",
        "Цифровой контроллер Термокуб С10",
        "Зольный ящик",
        "Пластины-турбулизаторы",
        "Инструкция по эксплуатации",
    ]
    if "Мощность электрокотла, кВт" in specs:
        includes.insert(4, "Встроенный электрокотел: " + specs["Мощность электрокотла, кВт"])
    if "золоудаления" in public_name:
        includes.insert(4, "Автоматическое шнековое золоудаление")

    description = (
        f"Автоматический пеллетный котёл {title.replace('Пеллетный котел ', '')} мощностью {power_range.replace('настраивается ', '')} кВт. "
        f"По данным производителя рассчитан на отопление площади {AREA[slug]}. "
        f"Котёл оснащён ретортной горелкой, жёстким шнеком и контроллером Термокуб С10; "
        "поддерживает управление насосом отопления, комнатный термостат и подключение GSM-модуля."
    )
    return {
        "slug": slug, "name": public_name, "manufacturer_title": title,
        "manufacturer_article": article_match.group(1) if article_match else None,
        "source_url": source_url, "category_url": BASE + "/kotly/pelletny",
        "checked_at": "2026-10-22", "price": price, "power_kw": power,
        "power_label": power_range.replace("настраивается ", "") + " кВт", "heating_area": AREA[slug],
        "source_availability": availability_match.group(1) if availability_match else None,
        "specifications": specs, "bunkers": bunkers, "includes": includes,
        "description": description, "documents": docs,
        "images": [item[1] for item in images],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("html_directory", type=Path)
    parser.add_argument("output_directory", type=Path)
    args = parser.parse_args()
    args.output_directory.mkdir(parents=True, exist_ok=True)
    (args.output_directory / "images").mkdir(exist_ok=True)
    products = []
    for filename, slug, name in PAGES:
        products.append(product_from_page(args.html_directory / filename, slug, name, args.output_directory))
    assert len(products) == 9
    assert sum(len(p["bunkers"]) for p in products) == 25
    assert len({p["source_url"] for p in products}) == 9
    (args.output_directory / "catalog.json").write_text(json.dumps(products, ensure_ascii=False, indent=2) + "\n")
    print(f"Captured {len(products)} START models, {sum(len(p['bunkers']) for p in products)} configurations and {sum(len(p['images']) for p in products)} gallery files.")


if __name__ == "__main__":
    main()
