"""Import BIOTEP spare parts from the manufacturer RRP price list dated 12.02.2026."""

import hashlib
import json
import re
import sys
from pathlib import Path

from catalog_identity import prepare_catalog

ROOT = Path(__file__).resolve().parent
SOURCE_DATE = "2026-02-12"
SOURCE_TITLE = "ЗИП опт март 2026"
SOURCE_URL = "https://bio-tep.ru/"
GENERIC_IMAGE = "/assets/biotep-spares.svg"

CATEGORIES = {
    "automation": "Автоматика и датчики",
    "airflow": "Вентиляторы и воздуховоды",
    "auger": "Шнеки и приводы",
    "ignition": "Система розжига",
    "burner": "Горелка и дымоудаление",
    "body": "Турбуляторы и детали корпуса",
    "insulation": "Теплоизоляция",
    "tubes": "ПВХ-трубки",
    "seals": "Уплотнения",
    "wires": "Комплект проводов",
}

# page, manufacturer code, product name, note, RRP incl. VAT, category
RAW_ITEMS = [
    (1, "4002", "Контроллер управления котлом", "Для всех моделей BIOTEP; отличается прошивка.", 31680, "automation"),
    (1, "4003", "Дисплей пеллетного котла с проводом", "Для всех моделей BIOTEP.", 4320, "automation"),
    (1, "4918", "Вентилятор наддува SOHON AC230V/50Hz 35W", "FAN1, с трубкой Вентури для BD-N27C5; вход d97 мм, выход d60 мм; применяется с октября 2022 года.", 17280, "airflow"),
    (1, "5037", "Воздухозаборник d97 (BD-N-09-11)", "Для вентилятора SOHON, d97, BIOTEP 32.", 837.12, "airflow"),
    (1, "4814", "Воздухозаборник d51 мм", "Для вентилятора TRIAL, вход d51 мм, BD27C5.", 2400, "airflow"),
    (1, "5739", "Воздуховод BD-N-09-A2M", "Приёмный патрубок после вентилятора наддува для BIOTEP 25/32; отверстие для ТЭН под зажим.", 2688, "airflow"),
    (1, "4005", "Вентилятор дымоудаления центробежный SIT", "FAN2; сопротивление обмотки 28-32 Ом; BIOTEP 18/25/32.", 26880, "airflow"),
    (1, "4015", "Насос циркуляционный", "PMP, 50/70/100 Вт, 50 л/мин, H-6 м; BIOTEP 18/25/32.", 7680, "automation"),
    (1, "4006", "Датчик давления управляющий (прессостат) Huba Control", "UPRS1, дифференциальный датчик давления; BIOTEP 18/25/32.", 14507.52, "automation"),
    (1, "4399", "Реле давления безопасности Huba Control", "SCP / UPRS2, защита открытой дверки; BIOTEP 18/25/32.", 7680, "automation"),
    (1, "4879", "Трубка Вентури", "Датчик потока на вентиляторе наддува FAN1 SOHON; BIOTEP 18/25/32.", 1152, "automation"),
    (1, "5038", "Трубка Вентури узкая", "Датчик потока для BIOTEP 77; также для замены Вентури на TRIAL с доработкой посадки.", 1152, "automation"),
    (1, "4920", "Мотор-редуктор шнека AC230V/50Hz 7,0 RPM с кожухом и проводом", "FED1; обмотка 1425-1430 Ом; BIOTEP 18/25/32.", 9600, "auger"),
    (1, "5099", "Мотор-редуктор AC230V/50Hz 7,0 RPM", "Без провода и кожуха.", 8064, "auger"),
    (1, "5040", "Шнек для BIOTEP 32/25", "Посадка под вал привода d=8,0 мм.", 3504, "auger"),
    (2, "5217", "Опора шнека с буфером BIOTEP 32/25", "Опора шнека с буфером.", 672, "auger"),
    (2, "5041", "Шнек для BIOTEP 32/25 в сборе", "Втулки, шайбы и монтажная пластина; выпуск после октября 2022 года.", 5515.20, "auger"),
    (2, "5039", "Шнек для BIOTEP 32/25 в сборе с приводом", "Втулки, шайбы, монтажная пластина, мотор-редуктор и провод.", 15360, "auger"),
    (2, "5728", "Шнек для BIOTEP 18", "Посадка под вал привода d=8,0 мм.", 3504, "auger"),
    (2, "5729", "Шнек для BIOTEP 18 в сборе", "Втулки, шайбы и монтажная пластина; посадка под вал d=8,0 мм.", 5515.20, "auger"),
    (2, "5916", "Шнек для BIOTEP 77", "Посадка под вал привода d=8,0 мм.", 3504, "auger"),
    (2, "4862", "Шнек для BIOTEP 77 в сборе", "Втулки, шайбы и монтажная пластина.", 5515.20, "auger"),
    (2, "5218", "Опора шнека с буфером для BD-27C5", "Выпуск до октября 2022 года.", 672, "auger"),
    (2, "4712", "Шнек для BD-27C5 (dв=8,5 мм)", "Выпуск до октября 2022 года; посадка под вал d=8,5 мм.", 3532.80, "auger"),
    (2, "4036", "Шнек для BD-27C5 (dв=8,5 мм) в сборе", "Выпуск до октября 2022 года; втулки, шайбы и монтажная пластина.", 4416, "auger"),
    (2, "4713", "Шнек для BD-C15L (dв=8,5 мм)", "Выпуск до октября 2022 года; сварной узел без втулок, шайб и монтажной пластины.", 3532.80, "auger"),
    (2, "4037", "Шнек для BD-C15L (dв=8,5 мм) в сборе", "Выпуск до октября 2022 года; втулки, шайбы и монтажная пластина.", 4416, "auger"),
    (2, "4011", "ТЭН розжига керамический под зажим", "CND, керамика 112x11 мм; сопротивление 80-90 Ом.", 4704, "ignition"),
    (2, "5982", "ТЭН розжига кварцевый", "Для BIOTEP 18/25/32/77, установка под зажим.", 6336, "ignition"),
    (2, "4529", "Трубка ТЭНа BD-21-09-14 для BIOTEP 32/25", "Для центрирования ТЭН под зажим.", 288, "ignition"),
    (2, "4730", "Трубка ТЭНа 325-04-065 для BIOTEP 18", "Для центрирования ТЭН под зажим.", 288, "ignition"),
    (2, "6264", "Трубка ТЭНа BD-77-29-003 для BIOTEP 77", "Для центрирования ТЭН под зажим.", 288, "ignition"),
    (2, "4919", "ТЭН розжига керамический с резьбой", "Для котлов до 2019 года; керамика 112x11 мм, втулка 3/8, сопротивление 80-90 Ом.", 4704, "ignition"),
    (3, "4883", "Датчик температуры дымовых газов", "TC1, термопара.", 3360, "automation"),
    (3, "4884", "Датчик температуры в камере сгорания", "TC2, термопара.", 3360, "automation"),
    (3, "4525", "Датчик температуры воды", "T1/T2, обратка и подача.", 1440, "automation"),
    (3, "4008", "Термостат электрический капиллярный предохранительный IMIT", "SCT / STB, выключатель по высокой температуре.", 3206.40, "automation"),
    (3, "4250", "Пластина крепления платы", "Основа крепления контроллера BIOTEP 32/25.", 480, "body"),
    (3, "4014", "Чашка горелки с уплотнителем", "Чашка горелки в комплекте с уплотнителем.", 6912, "burner"),
    (3, "4764", "Корпус горелки для котла BIOTEP 32/25", "Корпус горелки.", 11040, "burner"),
    (3, "4332", "Чаша горелки BD C25-04-A6 из нержавеющей стали", "Нержавеющая сталь 4 мм; для BIOTEP 18.", 6400.32, "burner"),
    (3, "5736", "Проставка дымососа BD-N-02-10", "Для разворота дымохода влево; L=120 мм, d136 мм.", 5088, "burner"),
    (3, "4381", "Рамка турбуляторов BD-N-12-A1", "Для BIOTEP 32/25.", 5088, "body"),
    (3, "4808", "Рычаг турбуляторов BD-N-12-A2", "Два рычага на рамку.", 1344, "body"),
    (3, "4247", "Болт M8x20 DIN933, класс прочности 10.9", "Два болта на ось.", 7.20, "body"),
    (3, "4754", "Ось турбуляторов BD-N-12-07", "Для котла BD-N27C5.", 1776, "body"),
    (3, "4873", "Ручка для котла BD-N27C5", "Для BIOTEP 32/25.", 1104, "body"),
    (3, "4364", "Ручка цилиндрическая M10x80, бакелит", "Для BIOTEP 32/25.", 701.76, "body"),
    (3, "4052", "Турбулятор BD-N-12-09", "30 штук на котёл BIOTEP 32.", 441.60, "body"),
    (3, "4400", "Ножка BD-N-03-A2", "Резьба M12.", 552, "body"),
    (3, "4075", "Резиновый амортизатор мотора шнека", "Буфер крышки багажника.", 552, "auger"),
    (3, "4039", "Втулка нижняя BD-N-15-51", "На шнек снизу.", 468.48, "auger"),
    (4, "4048", "Шайба нижняя BD-N-15-57", "На шнек снизу.", 72, "auger"),
    (4, "4040", "Втулка верхняя BD-N-15-52", "На шнек сверху.", 468.48, "auger"),
    (4, "4049", "Шайба верхняя BD-N-15-58", "На шнек сверху.", 72, "auger"),
    (4, "5092", "Теплоизоляция крышки теплообменника 27C5", "Вермикулит, для 27C5.", 2400, "insulation"),
    (4, "5088", "Защита вермикулита крышки теплообменника", "Металл, для BD-27C5.", 2196.48, "insulation"),
    (4, "5093", "Теплоизоляция дверки топки", "Вермикулит, для 27C5 и BD21.", 2400, "insulation"),
    (4, "5089", "Защита вермикулита дверки топки", "Металл, для 27C5 и BD21.", 2196.48, "insulation"),
    (4, "5094", "Теплоизоляция дверки теплообменника 27C5", "Вермикулит, для BD-27C5.", 2400, "insulation"),
    (4, "5096", "Теплоизоляция дверки теплообменника BD21", "Вермикулит, нижняя, для BD21.", 2400, "insulation"),
    (4, "5095", "Теплоизоляция верхней крышки теплообменника BD21", "Вермикулит, верхняя, для BD21.", 2400, "insulation"),
    (4, "4124", "Кожух защиты FAN1 BD-N-25-01", "Устанавливается над FAN1.", 288, "body"),
    (4, "4055", "Кронштейн управляющего прессостата BD-N-25-02", "Крепление чёрного прессостата Huba Control.", 288, "body"),
    (4, "4789", "Кронштейн реле давления BD-N-13-15", "Крепление серого реле безопасности Huba Control.", 288, "body"),
    (4, "5208", "Щиток задний BD-N-13-21M", "Экран защиты электроники.", 2400, "body"),
    (4, "5209", "Кожух дисплея BD-N-14-12", "Устанавливается внутри бункера.", 480, "body"),
    (4, "5181", "Бункер верхний BD-N-14-20", "Бордовый для BIOTEP 32; 910x650x300 мм, 9 кг.", 6000, "body"),
    (4, "5051", "Комплект ПВХ-трубок и соединителей", "Полный комплект.", 960, "tubes"),
    (5, "5207", "Трубка прессостата", "Контроль атмосферного давления.", 96, "tubes"),
    (5, "4177", "Т-образные разделители для силиконовых трубок 6 мм", "Комплект, пара.", 480, "tubes"),
    (5, "5180", "Уплотнитель чашки горелки BD27C5", "Шнур керамический квадратный 8x8 мм.", 1440, "seals"),
    (5, "", "Уплотнитель дверцы теплообменника", "Уплотнитель дверцы теплообменника.", 1440, "seals"),
    (5, "6156", "Уплотнитель дверцы топки", "Уплотнитель дверцы топки.", 1440, "seals"),
    (5, "6157", "Уплотнитель крышки теплообменника", "Уплотнитель крышки теплообменника.", 1440, "seals"),
    (5, "5204", "Кабель дисплея", "Кабель дисплея котла BIOTEP.", 480, "wires"),
    (5, "5043", "Провод вентилятора наддува FAN1", "Провод вентилятора наддува.", 480, "wires"),
    (5, "5045", "Провод дымососа FAN2", "Провод вентилятора дымоудаления.", 480, "wires"),
    (5, "5042", "Провод реле давления", "Провод реле давления.", 480, "wires"),
    (5, "5210", "Кабель прессостата Huba", "Кабель прессостата Huba Control.", 480, "wires"),
    (5, "5046", "Провод датчика безопасности IMIT", "Провод датчика безопасности IMIT.", 480, "wires"),
    (5, "5044", "Провод мотор-редуктора", "Провод мотор-редуктора шнека.", 480, "wires"),
    (5, "5047", "Провод насоса", "Провод циркуляционного насоса.", 480, "wires"),
]

EXCLUDED = [
    {"page": 4, "manufacturer_article": "5627", "name": "BD-77-92-001 Экран", "note": "Экран для чаши BIOTEP 77C", "reason": "В прайсе не указана РРЦ"}
]


def stable_id(code, name):
    if code:
        return f"biotep-spare-{code}"
    digest = hashlib.sha1(name.encode("utf-8")).hexdigest()[:10]
    return f"biotep-spare-no-code-{digest}"


def slug(code, name):
    if code:
        return f"biotep-zip-{code}"
    return "biotep-zip-uplotnitel-dvercy-teploobmennika"


def products_from_source(items):
    result = []
    for item in items:
        code = item["manufacturer_article"]
        name = item["name"]
        result.append({
            "id": stable_id(code, name),
            "name": name,
            "brand": "BIOTEP",
            "display_brand": "BIOTEP",
            "power": None,
            "path": f"/katalog/item/{slug(code, name)}/",
            "legacy_price": None,
            "price": item["rrp"],
            "images": item.get("images") or [item.get("image") or GENERIC_IMAGE],
            "unit": "штука",
            "source": SOURCE_URL,
            "manufacturer_title": name,
            "manufacturer_article": code,
            "checked_at": SOURCE_DATE,
            "specs": {
                "Код производителя": code or "Не указан в прайсе",
                "Раздел": CATEGORIES[item["category"]],
                "Совместимость и примечание": item["note"],
                "РРЦ с НДС": f'{item["rrp"]:,.2f}'.replace(",", " ").replace(".00", "") + " руб.",
            },
            "variants": [],
            "bunkers": [],
            "description": f'{name}. {item["note"]} Цена на сайте указана по РРЦ производителя с НДС.',
            "summary": item["note"],
            "documents": [],
            "source_availability": None,
            "our_availability": None,
            "product_type": "biotep_spare",
            "biotep_spare_category": item["category"],
            "biotep_spare_category_label": CATEGORIES[item["category"]],
            "price_type": "РРЦ производителя с НДС",
            "price_list": SOURCE_TITLE,
            "price_list_page": item["page"],
        })
    return result


def main():
    previous_source = json.loads((ROOT / "data/biotep-spares-source.json").read_text()) if (ROOT / "data/biotep-spares-source.json").exists() else {}
    previous_images = {
        (row.get("manufacturer_article", ""), row["name"]): row.get("images", [])
        for row in previous_source.get("items", [])
    }
    rows = [
        {"page": page, "manufacturer_article": code, "name": name, "note": note, "rrp": price, "category": category}
        for page, code, name, note, price, category in RAW_ITEMS
    ]
    for row in rows:
        images = previous_images.get((row["manufacturer_article"], row["name"]), [])
        if images:
            row["images"] = images
    assert len(rows) == 83
    assert len({(row["manufacturer_article"], row["name"]) for row in rows}) == 83
    assert all(row["rrp"] > 0 for row in rows)

    source = {
        "source_title": SOURCE_TITLE,
        "effective_date": SOURCE_DATE,
        "source_file_pages": 5,
        "price_rule": "РРЦ с НДС (КАТАЛОГ)",
        "items": rows,
        "excluded_without_rrp": EXCLUDED,
    }
    if previous_source.get("image_import"):
        source["image_import"] = previous_source["image_import"]
    (ROOT / "data/biotep-spares-source.json").write_text(json.dumps(source, ensure_ascii=False, indent=2) + "\n")

    path = ROOT / "data/products.json"
    products = json.loads(path.read_text())
    products = [product for product in products if product.get("product_type") != "biotep_spare"]
    products.extend(products_from_source(rows))
    path.write_text(json.dumps(products, ensure_ascii=False, indent=2) + "\n")
    products, _ = prepare_catalog()
    imported = [product for product in products if product.get("product_type") == "biotep_spare"]
    assert len(imported) == 83
    print(json.dumps({"imported": len(imported), "first_sku": imported[0]["sku"], "last_sku": imported[-1]["sku"], "excluded_without_rrp": len(EXCLUDED)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
