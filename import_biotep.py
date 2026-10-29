"""Import the audited BIOTEP pellet-boiler catalogue snapshot."""
import json
from pathlib import Path

from catalog_identity import prepare_catalog, save_json

ROOT = Path(__file__).resolve().parent


def main():
    source = json.loads((ROOT / "data/biotep-source.json").read_text())
    rows = source["source_snapshot"]
    assert [row["model"] for row in rows] == ["18", "25", "32", "77"]

    products = json.loads((ROOT / "data/products.json").read_text())
    previous = {str(p["power"]): p for p in products if p["brand"] == "BIOTEP"}
    assert set(previous) == {"18", "25", "32", "77"}
    imported = []

    for row in rows:
        prior = previous[row["model"]]
        imported.append({
            **prior,
            "name": row["name"],
            "power": row["power_kw"],
            "power_label": row["power_label"],
            "price": row["price"],
            "source": row["source_url"],
            "manufacturer_title": row["manufacturer_title"],
            "checked_at": row["checked_at"],
            "specs": row["specifications"],
            "description": row["description"],
            "advantages": row["advantages"],
            "documents": row["documents"],
            "support_source": source["support_url"],
        })

    other = [p for p in products if p["brand"] != "BIOTEP"]
    save_json(ROOT / "data/products.json", imported + other)
    prepare_catalog()
    print(f"Imported {len(imported)} BIOTEP cards; retained {len(other)} other products.")


if __name__ == "__main__":
    main()
