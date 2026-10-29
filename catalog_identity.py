"""Permanent internal article numbers. The registry is append-only, including retired items."""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ORIGIN = 'https://pelletsgrupp-migration.hromov-aa.chatgpt.site'

def save_json(path, value):
    text = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if not path.exists() or path.read_text() != text:
        path.write_text(text)

def assign_skus(products, pellets, registry):
    entries = registry.setdefault('entries', {})
    options = registry.setdefault('option_ids', {})
    used = list(entries.values())
    if len(used) != len(set(used)) or any(not re.fullmatch(r'PG-\d{6}', s) for s in used):
        raise ValueError('Invalid or duplicate SKU in the permanent registry')
    registry['next_number'] = max(registry.get('next_number', 1), max([int(s[3:]) + 1 for s in used] or [1]))

    def reserve(key):
        if key not in entries:
            number = registry['next_number']
            if number > 999999:
                raise ValueError('Internal article number range exhausted')
            entries[key] = f'PG-{number:06d}'
            registry['next_number'] += 1
        return entries[key]

    for kind, items in [('equipment', products), ('pellets', pellets)]:
        for p in items:
            key = kind + ':' + p['id']
            sku = reserve(key)
            if p.get('sku') and p['sku'] != sku:
                raise ValueError('Attempt to change assigned SKU: ' + key)
            p['sku'] = sku
            if not p.get('variants'):
                continue
            option_map = options.setdefault(key, {'variants': {}, 'bunkers': {}})
            for field, prefix in [('variants', 'v'), ('bunkers', 'b')]:
                known = option_map[field]
                for item in p[field]:
                    if item.get('option_id'):
                        if item['name'] in known and known[item['name']] != item['option_id']:
                            raise ValueError('Configuration identity mismatch')
                        known[item['name']] = item['option_id']
                    elif item['name'] in known:
                        item['option_id'] = known[item['name']]
                    else:
                        n = max([int(v[1:]) for v in known.values()] or [0]) + 1
                        item['option_id'] = known[item['name']] = f'{prefix}{n:03d}'
            # Remember which configuration initially received the product's main SKU.
            default = registry.setdefault('default_offers', {}).setdefault(key, [p['variants'][0]['option_id'], p['bunkers'][0]['option_id']])
            p['offers'] = []
            for v in p['variants']:
                for b in p['bunkers']:
                    ids = [v['option_id'], b['option_id']]
                    offer_sku = sku if ids == default else reserve(key + ':' + ':'.join(ids))
                    p['offers'].append({'variant_id': ids[0], 'bunker_id': ids[1], 'sku': offer_sku})
    return registry

def prepare_catalog():
    products = json.loads((ROOT / 'data/products.json').read_text())
    pellets = json.loads((ROOT / 'data/pellets.json').read_text())
    path = ROOT / 'data/sku-registry.json'
    registry = json.loads(path.read_text()) if path.exists() else {'format': 'PG-000001', 'next_number': 1, 'entries': {}}
    assign_skus(products, pellets, registry)
    save_json(path, registry)
    save_json(ROOT / 'data/products.json', products)
    save_json(ROOT / 'data/pellets.json', pellets)
    return products, pellets

def export_rows(products, pellets):
    rows = []
    for p in products:
        variants = {v['option_id']: v for v in p.get('variants', [])}
        bunkers = {b['option_id']: b for b in p.get('bunkers', [])}
        for offer in p.get('offers') or [{'sku': p['sku']}]:
            v = variants.get(offer.get('variant_id'))
            b = bunkers.get(offer.get('bunker_id'))
            configuration = (v['name'] + '; бункер ' + b['name']) if v else ''
            rows.append({'sku': offer['sku'], 'name': p['name'] + (' — ' + configuration if configuration else ''), 'brand': p.get('display_brand', p['brand']), 'model': p['name'], 'configuration': configuration, 'unit': p['unit'], 'price': v['price'] + b['extra'] if v else p['price'], 'site_id': p['id'], 'url': ORIGIN + p['path'], 'source': p['source'], 'code_1c': '', 'guid_1c': ''})
    for p in pellets:
        rows.append({'sku': p['sku'], 'name': p['name'], 'brand': 'PelletsGrupp', 'model': p['name'], 'configuration': '', 'unit': 'тонна', 'price': p['price'], 'site_id': p['id'], 'url': ORIGIN + '/pellety/#' + p['id'], 'source': ORIGIN + '/pellety/', 'code_1c': '', 'guid_1c': ''})
    assert len({r['sku'] for r in rows}) == len(rows)
    return rows

if __name__ == '__main__':
    import sys
    products, pellets = prepare_catalog()
    rows = export_rows(products, pellets)
    if len(sys.argv) > 1:
        output = Path(sys.argv[1]); output.mkdir(parents=True, exist_ok=True)
        save_json(output / 'catalog-1c.json', rows)
        headers = ['Артикул', 'Наименование', 'Бренд', 'Модель', 'Комплектация', 'Единица', 'Цена сайта, руб.', 'ID сайта', 'Страница товара', 'Источник', 'Код 1С', 'GUID 1С']
        with (output / 'artikuly-1c.csv').open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter=';'); writer.writerow(headers)
            writer.writerows(list(r.values()) for r in rows)
    print(f'{len(products) + len(pellets)} product cards; {len(rows)} unique articles including configurations.')
