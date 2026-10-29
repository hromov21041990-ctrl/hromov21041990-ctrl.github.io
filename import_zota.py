"""Import the audited ZOTA pellet-burner and accessory catalogue."""
import hashlib
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

from catalog_identity import prepare_catalog, save_json

ROOT = Path(__file__).resolve().parent
EXPECTED = {
    "gorelki": 3,
    "bunker": 8,
    "mehanizm-podachi": 1,
    "adapter": 17,
    "otboynik": 4,
    "avtomatika-dlya-gorelok": 1,
}
SPECIAL_PATHS = {
    "ZF4938004025": "/katalog/item/zota-fox-25/",
    "ZF4938004043": "/katalog/item/zota-fox-43/",
    "RY4938002025": "/katalog/item/zota-ray-g2-25/",
}


def local_path(row):
    if row["manufacturer_article"] in SPECIAL_PATHS:
        return SPECIAL_PATHS[row["manufacturer_article"]]
    return "/katalog/item/zota-" + row["slug"] + "/"


def fallback_description(row):
    if row["category"] == "mehanizm-podachi":
        return "<p>Механизм подачи для пеллетных горелок ZOTA FOX и RAY с фиксацией шнека. Совместимость и комплект поставки уточняются при подборе.</p>"
    if row["category"] == "otboynik":
        return "<p>Отбойник топки для установки горелок ZOTA FOX или RAY на указанную в наименовании модель котла. Перед заказом проверим совместимость с исполнением и годом выпуска котла.</p>"
    return "<p>Оригинальная комплектующая для пеллетных горелок ZOTA. Совместимость с конкретной горелкой и котлом проверим перед заказом.</p>"


def main(source):
    rows = json.loads((source / "catalog.json").read_text())
    actual = {key: sum(row["category"] == key for row in rows) for key in EXPECTED}
    assert len(rows) == 34 and actual == EXPECTED, actual
    assert len({row["manufacturer_article"] for row in rows}) == len(rows)

    products = json.loads((ROOT / "data/products.json").read_text())
    previous = {p.get("manufacturer_article"): p for p in products if p["brand"] == "ZOTA" and p.get("manufacturer_article")}
    assets = ROOT / "assets/zota"
    assets.mkdir(parents=True, exist_ok=True)
    image_cache = {}
    imported = []

    for row in rows:
        article = row["manufacturer_article"]
        prior = previous.get(article, {})
        images = []
        for photo in row["images"]:
            local = Path(photo["local_path"])
            checksum = hashlib.sha256(local.read_bytes()).hexdigest()
            assert checksum == photo["sha256"]
            if checksum not in image_cache:
                target = assets / (checksum[:20] + ".webp")
                with Image.open(local) as image:
                    image = ImageOps.exif_transpose(image).convert("RGBA")
                    image.thumbnail((1600, 1600))
                    background = Image.new("RGBA", image.size, "white")
                    Image.alpha_composite(background, image).convert("RGB").save(target, "WEBP", quality=88, method=6)
                image_cache[checksum] = "/assets/zota/" + target.name
            if image_cache[checksum] not in images:
                images.append(image_cache[checksum])
        power_value = row["specifications"].get("Мощность, кВт")
        power_match = re.search(r"\d+(?:[.,]\d+)?", power_value or "")
        power = float(power_match.group().replace(",", ".")) if power_match else None
        if power is not None and power.is_integer():
            power = int(power)
        specs = {
            "Артикул производителя": article,
            "Раздел производителя": row["category_label"],
            **row["specifications"],
        }
        product = {
            "id": prior.get("id", hashlib.sha256(("ZOTA:" + article).encode()).hexdigest()[:12]),
            "name": row["name"], "brand": "ZOTA", "display_brand": "ZOTA",
            "power": power, "path": prior.get("path", local_path(row)),
            "legacy_price": prior.get("legacy_price"), "price": row["price"],
            "images": images, "unit": "штука", "source": row["source_url"],
            "manufacturer_title": row["name"], "manufacturer_article": article,
            "checked_at": row["checked_at"], "specs": specs, "variants": [],
            "description": row["description"] or fallback_description(row),
            "summary": row["summary"], "documents": row["documents"],
            "source_availability": row["source_availability"], "our_availability": None,
            "zota_category": row["category"], "zota_category_label": row["category_label"],
            "automatic_pellet": row["category"] == "gorelki",
        }
        if prior.get("sku"):
            product["sku"] = prior["sku"]
        imported.append(product)

    other = [p for p in products if p["brand"] != "ZOTA"]
    save_json(ROOT / "data/products.json", other + imported)
    prepare_catalog()
    snapshot = []
    for row in rows:
        item = {key: row.get(key) for key in [
            "slug", "name", "manufacturer_article", "source_url", "category",
            "category_label", "checked_at", "price", "source_availability", "summary",
            "description", "specifications", "documents",
        ]}
        item["images"] = [{"source_url": image["source_url"], "sha256": image["sha256"]} for image in row["images"]]
        snapshot.append(item)
    save_json(ROOT / "data/zota-source.json", {
        "checked_at": "2026-10-22",
        "category_url": "https://dk-zota.ru/catalog/pelletnye-gorelki",
        "scope": "All pellet burners and the five related accessory groups shown by the supplier",
        "category_counts": EXPECTED,
        "products": len(snapshot),
        "source_snapshot": snapshot,
    })
    print(f"Imported {len(imported)} ZOTA cards in {len(EXPECTED)} supplier groups; retained {len(other)} other products.")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
