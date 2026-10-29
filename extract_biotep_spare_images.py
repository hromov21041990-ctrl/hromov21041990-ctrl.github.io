"""Extract BIOTEP spare-part photos from the supplier PDF and attach them to products."""

import argparse
import json
import shutil
from collections import defaultdict
from pathlib import Path

import pdfplumber


ROOT = Path(__file__).resolve().parent
SOURCE_PATH = ROOT / "data/biotep-spares-source.json"
PRODUCTS_PATH = ROOT / "data/products.json"
ASSET_DIR = ROOT / "assets/biotep-spares"
PLACEHOLDER = "/assets/biotep-spares.svg"


def row_targets(page, source_rows, excluded_rows):
    words = page.extract_words(x_tolerance=1, y_tolerance=2, keep_blank_chars=False)
    code_tops = {}
    for word in words:
        text = word["text"].strip()
        if word["x0"] < 90 and text.isdigit() and 3 <= len(text) <= 5:
            code_tops[text] = float(word["top"])

    targets = []
    for row in source_rows:
        code = row["manufacturer_article"]
        if code:
            if code not in code_tops:
                raise RuntimeError(f"Не найден код {code} на странице {row['page']}")
            targets.append({"top": code_tops[code], "row": row})
    for row in excluded_rows:
        code = row["manufacturer_article"]
        if code in code_tops:
            targets.append({"top": code_tops[code], "row": None})

    no_code = [row for row in source_rows if not row["manufacturer_article"]]
    if no_code:
        ordered = sorted(targets, key=lambda item: item["top"])
        for row in no_code:
            # The only no-code line in this price list sits between 5180 and 6156.
            before = code_tops.get("5180")
            after = code_tops.get("6156")
            if before is None or after is None:
                raise RuntimeError("Не удалось определить строку позиции без кода")
            targets.append({"top": (before + after) / 2, "row": row})
    return sorted(targets, key=lambda item: item["top"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path, help="Исходный прайс-лист BIOTEP в PDF")
    args = parser.parse_args()
    if not args.pdf.is_file():
        raise SystemExit(f"PDF не найден: {args.pdf}")

    source = json.loads(SOURCE_PATH.read_text())
    products = json.loads(PRODUCTS_PATH.read_text())
    items = source["items"]
    excluded = source.get("excluded_without_rrp", [])
    by_identity = {
        (product.get("manufacturer_article", ""), product["name"]): product
        for product in products
        if product.get("product_type") == "biotep_spare"
    }

    if ASSET_DIR.exists():
        shutil.rmtree(ASSET_DIR)
    ASSET_DIR.mkdir(parents=True)
    mapped = defaultdict(list)

    with pdfplumber.open(args.pdf) as document:
        if len(document.pages) != 5:
            raise RuntimeError(f"Ожидалось 5 страниц, найдено {len(document.pages)}")
        for page_number, page in enumerate(document.pages, 1):
            page_rows = [row for row in items if row["page"] == page_number]
            page_excluded = [row for row in excluded if row["page"] == page_number]
            targets = row_targets(page, page_rows, page_excluded)
            for image in page.images:
                if image["top"] < 0:
                    continue
                expected_text_top = float(image["top"]) + 18.54
                target = min(targets, key=lambda item: abs(item["top"] - expected_text_top))
                if abs(target["top"] - expected_text_top) > 8 or target["row"] is None:
                    continue
                stream = image["stream"]
                raw = stream.get_rawdata()
                if not raw.startswith(b"\xff\xd8"):
                    raise RuntimeError(f"Неподдерживаемое изображение на странице {page_number}")
                row = target["row"]
                identity = (row["manufacturer_article"], row["name"])
                index = len(mapped[identity]) + 1
                stem = row["manufacturer_article"] or "uplotnitel-dvercy-teploobmennika"
                filename = f"{stem}-{index}.jpg"
                (ASSET_DIR / filename).write_bytes(raw)
                mapped[identity].append(f"/assets/biotep-spares/{filename}")

    spare_products = [product for product in products if product.get("product_type") == "biotep_spare"]
    missing = []
    for row in items:
        identity = (row["manufacturer_article"], row["name"])
        if identity not in by_identity:
            raise RuntimeError(f"Не найдена карточка товара: {identity}")
        images = mapped.get(identity, [])
        by_identity[identity]["images"] = images or [PLACEHOLDER]
        row["images"] = images
        if not images:
            missing.append({"manufacturer_article": row["manufacturer_article"], "name": row["name"]})

    if len(spare_products) != 83:
        raise RuntimeError(f"Ожидалось 83 карточки ЗИП, найдено {len(spare_products)}")
    PRODUCTS_PATH.write_text(json.dumps(products, ensure_ascii=False, indent=2) + "\n")
    source["image_import"] = {
        "source": "Фотографии извлечены из товарных строк исходного PDF",
        "products_with_photos": sum(bool(row.get("images")) for row in items),
        "products_without_photos": len(missing),
        "photo_files": sum(len(row.get("images", [])) for row in items),
        "without_photos": missing,
    }
    SOURCE_PATH.write_text(json.dumps(source, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(source["image_import"], ensure_ascii=False))


if __name__ == "__main__":
    main()
