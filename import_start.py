"""Import the audited automatic START pellet-boiler category."""
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageOps

from catalog_identity import prepare_catalog, save_json

ROOT = Path(__file__).resolve().parent


def main(source):
    rows = json.loads((source / "catalog.json").read_text())
    expected = [
        "start-20-gr", "start-30-gr", "start-30-gr-v2", "start-35-gr",
        "start-50-gr", "start-100-gr", "start-100-gr-right",
        "start-100-gr-ash", "start-150-gr-max",
    ]
    assert len(rows) == 9 and [row["slug"] for row in rows] == expected
    assert sum(len(row["bunkers"]) for row in rows) == 25

    products = json.loads((ROOT / "data/products.json").read_text())
    previous = {p["path"].strip("/").rsplit("/", 1)[-1]: p for p in products if p["brand"] == "СТАРТ"}
    assets = ROOT / "assets/start"
    assets.mkdir(parents=True, exist_ok=True)
    image_cache = {}
    imported = []

    for row in rows:
        slug = row["slug"]
        prior = previous.get(slug, {})
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
                image_cache[checksum] = "/assets/start/" + target.name
            if image_cache[checksum] not in images:
                images.append(image_cache[checksum])

        old_variants = {v["name"]: v for v in prior.get("variants", [])}
        old_bunkers = {b.get("capacity_l"): b for b in prior.get("bunkers", [])}
        variant = {"name": "Базовая комплектация", "price": row["price"], "includes": row["includes"]}
        if old_variants.get(variant["name"], {}).get("option_id"):
            variant["option_id"] = old_variants[variant["name"]]["option_id"]
        bunkers = []
        for source_bunker in row["bunkers"]:
            old = old_bunkers.get(source_bunker["capacity_l"], {})
            bunker = {k: source_bunker[k] for k in ["name", "capacity_l", "extra"]}
            if source_bunker.get("source_status"):
                bunker["source_status"] = source_bunker["source_status"]
            if old.get("option_id"):
                bunker["option_id"] = old["option_id"]
            bunkers.append(bunker)

        specs = {
            "Артикул производителя": row["manufacturer_article"],
            "Площадь отопления по данным производителя": row["heating_area"],
            **row["specifications"],
        }
        product = {
            "id": prior.get("id", hashlib.sha256(("START:" + slug).encode()).hexdigest()[:12]),
            "name": row["name"], "brand": "СТАРТ", "display_brand": "START",
            "power": row["power_kw"], "power_label": row["power_label"],
            "path": prior.get("path", "/katalog/item/" + slug + "/"),
            "legacy_price": prior.get("legacy_price"), "price": row["price"],
            "images": images, "unit": "штука", "source": row["source_url"],
            "manufacturer_title": row["manufacturer_title"],
            "manufacturer_article": row["manufacturer_article"],
            "checked_at": row["checked_at"], "specs": specs,
            "variants": [variant], "bunkers": bunkers,
            "bunker_fixed": len(bunkers) == 1, "description": row["description"],
            "documents": row["documents"], "source_availability": row["source_availability"],
            "our_availability": None, "automatic_pellet": True,
        }
        if prior.get("sku"):
            product["sku"] = prior["sku"]
        imported.append(product)

    other = [p for p in products if p["brand"] != "СТАРТ"]
    save_json(ROOT / "data/products.json", other + imported)
    prepare_catalog()
    snapshot = []
    for row in rows:
        item = {k: row.get(k) for k in [
            "slug", "name", "manufacturer_title", "manufacturer_article", "source_url",
            "category_url", "checked_at", "price", "power_kw", "power_label",
            "heating_area", "source_availability", "specifications", "bunkers",
            "includes", "description", "documents",
        ]}
        item["images"] = [{"source_url": image["source_url"], "sha256": image["sha256"]} for image in row["images"]]
        snapshot.append(item)
    save_json(ROOT / "data/start-source.json", {
        "checked_at": "2026-10-22", "category_url": "https://www.kotel74.ru/kotly/pelletny",
        "scope": "Only the nine automatic pellet-boiler cards in the manufacturer's pellet category",
        "models": 9, "configurations": 25, "source_snapshot": snapshot,
    })
    print(f"Imported {len(imported)} START cards and {sum(len(p['bunkers']) for p in imported)} configurations; retained {len(other)} other products.")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
