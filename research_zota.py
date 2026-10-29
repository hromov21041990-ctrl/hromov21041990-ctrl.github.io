"""Build an auditable ZOTA burner and accessory snapshot from saved official pages."""
import argparse
import hashlib
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

from lxml import html, etree

BASE = "https://dk-zota.ru"
CATEGORIES = [
    ("gorelki.html", "gorelki", "Пеллетные горелки"),
    ("bunker.html", "bunker", "Бункер"),
    ("mehanizm.html", "mehanizm-podachi", "Механизм подачи"),
    ("adapter.html", "adapter", "Адаптер"),
    ("adapter-page2.html", "adapter", "Адаптер"),
    ("otboynik.html", "otboynik", "Отбойник"),
    ("avtomatika.html", "avtomatika-dlya-gorelok", "Автоматика для горелок"),
]


def clean(value):
    return " ".join((value or "").replace("\xa0", " ").split())


def absolute(url):
    return urllib.parse.urljoin(BASE, url)


def slug_from_url(url):
    return urllib.parse.urlparse(url).path.rstrip("/").rsplit("/", 1)[-1]


def amount(value):
    return int(re.sub(r"\D", "", str(value)))


def download(url, directory):
    request = urllib.request.Request(url, headers={"User-Agent": "PelletsGrupp catalogue research"})
    data = urllib.request.urlopen(request, timeout=45).read()
    digest = hashlib.sha256(data).hexdigest()
    suffix = Path(urllib.parse.urlparse(url).path).suffix.lower() or ".bin"
    target = directory / f"{digest[:20]}{suffix}"
    target.write_bytes(data)
    return {"source_url": url, "local_path": str(target), "sha256": digest}


def script_context(root):
    scripts = [node.text for node in root.xpath("//script[not(@src)]") if node.text and "window.__NUXT__=" in node.text]
    assert len(scripts) == 1
    script = scripts[0]
    match = re.match(r"window\.__NUXT__=\(function\(([^)]*)\)\{return ", script)
    assert match
    names = [name.strip() for name in match.group(1).split(",") if name.strip()]
    tail = re.search(r"\}\((.*)\)\);\s*$", script, re.S)
    assert tail
    values = json.loads("[" + tail.group(1) + "]")
    return script, dict(zip(names, values))


def balanced(text, start, opening="[", closing="]"):
    assert text[start] == opening
    depth = 0
    quoted = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise ValueError("Unbalanced embedded catalogue data")


def objects_in_array(value):
    objects = []
    depth = 0
    quoted = False
    escaped = False
    start = None
    for index, char in enumerate(value):
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char == "{":
            if depth == 0:
                start = index
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0 and start is not None:
                objects.append(value[start:index + 1])
    return objects


def all_objects(value):
    objects = []
    stack = []
    quoted = False
    escaped = False
    for index, char in enumerate(value):
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char == "{":
            stack.append(index)
        elif char == "}" and stack:
            start = stack.pop()
            objects.append(value[start:index + 1])
    return objects


def embedded_value(obj, key, variables):
    match = re.search(r"(?:^|[,{])" + re.escape(key) + r":(\"(?:\\.|[^\"])*\"|-?\d+(?:\.\d+)?|true|false|null|[A-Za-z_$][\w$]*)", obj)
    if not match:
        return None
    token = match.group(1)
    if token.startswith('"'):
        return json.loads(token)
    if token in variables:
        return variables[token]
    if token == "null":
        return None
    if token in ("true", "false"):
        return token == "true"
    return float(token) if "." in token else int(token)


def embedded_specs(script, variables):
    marker = "tabs:{specifications:"
    pos = script.index(marker) + len(marker)
    raw = balanced(script, pos)
    specs = {}
    for obj in objects_in_array(raw):
        title = embedded_value(obj, "title", variables)
        value = embedded_value(obj, "value", variables)
        if title and value not in (None, ""):
            specs[clean(str(title))] = clean(str(value))
    return specs


def embedded_files(script, variables):
    marker = ",files:"
    pos = script.index(marker) + len(marker)
    raw = balanced(script, pos)
    docs = []
    for obj in all_objects(raw):
        title = embedded_value(obj, "title", variables)
        link = embedded_value(obj, "link", variables)
        if title and link and "data:[" not in obj:
            docs.append({"title": clean(title), "url": absolute(link)})
    return docs


def listing_rows(directory):
    rows = []
    seen = set()
    for filename, key, label in CATEGORIES:
        root = html.parse(str(directory / filename)).getroot()
        for link in root.xpath('//a[starts-with(@href,"/product/")]'):
            url = absolute(link.get("href"))
            if url in seen:
                continue
            seen.add(url)
            card = link
            while card is not None and card.tag != "article":
                card = card.getparent()
            assert card is not None
            price = card.xpath('.//*[@itemprop="price"]/@content')
            article = card.xpath('.//*[@itemprop="sku"]/@content')
            title = card.xpath('.//*[@itemprop="name"]/@content')
            rows.append({
                "source_url": url, "slug": slug_from_url(url), "category": key,
                "category_label": label, "listing_price": amount(price[0]),
                "manufacturer_article": article[0], "listing_title": clean(title[0]),
            })
    return rows


def product_from_page(row, path, output):
    root = html.parse(str(path)).getroot()
    source_url = root.xpath("string(//link[@rel='canonical']/@href)") or row["source_url"]
    title = clean(root.xpath("//h1")[0].text_content())
    article = root.xpath('string(//*[@itemprop="sku"]/@content)')
    price = amount(root.xpath('string(//*[@itemprop="price"]/@content)'))
    page_text = clean(root.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," product ")]')[0].text_content())
    stock = re.search(r"В наличии:\s*(.+?)(?:Описание|Характеристики|Файлы|$)", page_text)
    summary = root.xpath('string(//*[@itemprop="description"]/@content)')
    description_node = root.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," rich-text ")]')
    description = ""
    if description_node:
        description = (description_node[0].text or "") + "".join(etree.tostring(child, encoding="unicode") for child in description_node[0])
        description = re.sub(r"^\s*<h4>\s*<strong>Описание</strong>\s*</h4>", "", description, flags=re.I)
    script, variables = script_context(root)
    specs = embedded_specs(script, variables)
    documents = embedded_files(script, variables)
    image_urls = []
    for image in root.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," product ")]//img[contains(@src,"/entries/")]/@src'):
        image = absolute(image)
        if image not in image_urls:
            image_urls.append(image)
    images = [download(url, output / "images") for url in image_urls]
    assert source_url.rstrip("/") == row["source_url"].rstrip("/")
    assert title == row["listing_title"] and article == row["manufacturer_article"]
    assert price == row["listing_price"]
    return {
        **row, "name": title, "source_url": source_url, "checked_at": "2026-10-22",
        "price": price, "source_availability": clean(stock.group(1)) if stock else None,
        "summary": clean(summary), "description": description, "specifications": specs,
        "documents": documents, "images": images,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("html_directory", type=Path)
    parser.add_argument("output_directory", type=Path)
    args = parser.parse_args()
    args.output_directory.mkdir(parents=True, exist_ok=True)
    (args.output_directory / "images").mkdir(exist_ok=True)
    rows = listing_rows(args.html_directory)
    products = []
    for row in rows:
        page = args.html_directory / "products" / (row["slug"] + ".html")
        products.append(product_from_page(row, page, args.output_directory))
        print(f'{len(products):02d}/{len(rows)} {row["category"]}: {row["listing_title"]}')
    expected = {"gorelki": 3, "bunker": 8, "mehanizm-podachi": 1, "adapter": 17, "otboynik": 4, "avtomatika-dlya-gorelok": 1}
    actual = {key: sum(row["category"] == key for row in products) for key in expected}
    assert len(products) == 34 and actual == expected, actual
    assert len({row["source_url"] for row in products}) == len(products)
    assert len({row["manufacturer_article"] for row in products}) == len(products)
    assert all(row["images"] for row in products)
    (args.output_directory / "catalog.json").write_text(json.dumps(products, ensure_ascii=False, indent=2) + "\n")
    print(f"Captured {len(products)} ZOTA products, {sum(len(p['images']) for p in products)} gallery files and {sum(len(p['documents']) for p in products)} document links.")


if __name__ == "__main__":
    main()
