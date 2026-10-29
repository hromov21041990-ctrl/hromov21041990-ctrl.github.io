"""Import Vulkan spare parts from the manufacturer RRP price list dated 15.06.2026."""

import json
from pathlib import Path

from catalog_identity import prepare_catalog
from vulkan_spares import CATEGORIES


ROOT = Path(__file__).resolve().parent
SOURCE_PATH = ROOT / "data/vulkan-spares-source.json"
PRODUCTS_PATH = ROOT / "data/products.json"
SOURCE_DATE = "2026-06-15"
SOURCE_TITLE = "Прайс КК2 от 15.06.2026 — Вулкан. Дил"
SOURCE_URL = "https://kras-kotel.ru/katalog/"
PLACEHOLDER = "/assets/vulkan-spares.svg"
CATEGORY_LABELS = {key: label for key, label, _ in CATEGORIES}


def product_from_source(item):
    sku = item["sku"]
    name = item["name"]
    note = item.get("note", "").strip()
    summary = note or "Совместимость и состав поставки уточняются по модели и мощности котла."
    return {
        "id": "vulkan-spare-" + sku.lower(),
        "name": name,
        "brand": "Вулкан",
        "display_brand": "Vulkan",
        "power": None,
        "path": f'/katalog/item/vulkan-zip-{sku[3:]}/',
        "legacy_price": None,
        "price": item["price"],
        "images": item.get("images") or [PLACEHOLDER],
        "unit": "штука",
        "source": SOURCE_URL,
        "manufacturer_title": name,
        "manufacturer_article": "",
        "checked_at": SOURCE_DATE,
        "specs": {
            "Раздел": CATEGORY_LABELS[item["category_key"]],
            "Совместимость и примечание": summary,
            "Страна производства": item.get("country") or "Россия",
            "РРЦ производителя": f'{item["price"]:,}'.replace(",", " ") + " руб.",
            "Источник цены": SOURCE_TITLE,
        },
        "variants": [],
        "bunkers": [],
        "description": f'{name}. {summary} Цена на сайте указана по РРЦ производителя.',
        "summary": summary,
        "documents": [],
        "source_availability": None,
        "our_availability": None,
        "product_type": "vulkan_spare",
        "vulkan_spare_category": item["category_key"],
        "vulkan_spare_category_label": CATEGORY_LABELS[item["category_key"]],
        "price_type": "РРЦ производителя",
        "price_list": SOURCE_TITLE,
        "price_list_page": item["page"],
        "sku": sku,
    }


def main():
    source = json.loads(SOURCE_PATH.read_text())
    items = sorted(source["items"], key=lambda item: int(item["sku"][3:]))
    products = json.loads(PRODUCTS_PATH.read_text())
    products = [product for product in products if product.get("product_type") != "vulkan_spare"]
    products.extend(product_from_source(item) for item in items)
    PRODUCTS_PATH.write_text(json.dumps(products, ensure_ascii=False, indent=2) + "\n")
    products, _ = prepare_catalog()
    imported = [product for product in products if product.get("product_type") == "vulkan_spare"]
    assert len(imported) == 126
    assert imported[0]["sku"] == "PG-000344"
    assert imported[-1]["sku"] == "PG-000469"
    print(json.dumps({"imported": len(imported), "first_sku": imported[0]["sku"], "last_sku": imported[-1]["sku"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
