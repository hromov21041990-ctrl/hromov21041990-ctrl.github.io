"""SEO metadata and markup from verified, visible business information."""
import json
import re
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

from lxml import html
from PIL import Image

ROOT = Path(__file__).resolve().parent
METADATA = {
    '/katalog/': ('Пеллетные котлы и горелки в Екатеринбурге — цены | PelletsGrupp', 'Котлы BIOTEP, FACI, Vulkan и СТАРТ, пеллетные горелки ZOTA. Сравните модели и комплектации. Подбор, доставка и монтаж в Екатеринбурге и Свердловской области.'),
    '/biotep/': ('Пеллетные котлы BIOTEP в Екатеринбурге — цены | PelletsGrupp', 'Пеллетные котлы BIOTEP 18, 25, 32 и 77: характеристики, цены и документы. Подбор оборудования, монтаж и сервис в Екатеринбурге и Свердловской области.'),
    '/faci/': ('Пеллетные котлы FACI в Екатеринбурге — цены | PelletsGrupp', 'Котлы FACI: модели, мощность, комплектации и бункеры. Цены, характеристики, подбор, доставка и монтаж в Екатеринбурге и Свердловской области.'),
    '/start/': ('Пеллетные котлы СТАРТ в Екатеринбурге — цены | PelletsGrupp', 'Автоматические пеллетные котлы СТАРТ серии GR: модели, комплектации, бункеры и цены. Подбор, доставка и монтаж в Екатеринбурге и Свердловской области.'),
    '/pustayastranitsa/': ('Монтаж пеллетных котлов — примеры работ | PelletsGrupp', 'Выполненные работы PelletsGrupp: установка котлов BIOTEP, отопления и дымоходов. Фотографии и описание объектов, подбор решения для вашего дома.'),
    '/pustayastranitsa_qspm/': ('Сервис пеллетных котлов — примеры работ | PelletsGrupp', 'Примеры работ по обслуживанию пеллетных котлов: чистка, проверка узлов и профилактика неисправностей. Сервис PelletsGrupp в Екатеринбурге.'),
    '/pustayastranitsa_qewx/': ('Согласие на обработку персональных данных | PelletsGrupp', 'Согласие на обработку персональных данных ООО «ПЕЛЛЕТС ГРУПП». Условия обработки данных и порядок отзыва согласия.'),
    '/dostavka/': ('Доставка пеллет по Екатеринбургу и области | PelletsGrupp', 'Доставка пеллет в мешках и биг-бэгах, самовывоз в Екатеринбурге. Зоны и способы доставки, расчёт стоимости для адресов Свердловской области.'),
    '/o-nas/': ('О компании PelletsGrupp — отопление в Екатеринбурге', 'PelletsGrupp: поставка пеллет, подбор котлов, монтаж, сервис и ремонт. Комплексное отопление для домов и бизнеса Екатеринбурга и Свердловской области.'),
    '/remont-kotla/': ('Ремонт пеллетных котлов в Екатеринбурге | PelletsGrupp', 'Диагностика и ремонт пеллетных котлов, проверка узлов и автоматики. Обратитесь в PelletsGrupp для согласования работ и выезда в Екатеринбурге и области.'),
}

def metadata(path, title, description):
    return METADATA.get(path, (title, description))

@lru_cache(maxsize=None)
def image_size(src):
    if not src.startswith('/assets/'):
        return None
    try:
        with Image.open(ROOT / urlparse(src).path.lstrip('/')) as image:
            return image.size
    except (OSError, ValueError):
        return None

def prepare_body(path, body):
    """Reserve raster image space without changing the surrounding markup."""
    def size_image(match):
        tag = match.group()
        src = re.search(r'\bsrc="([^"]+)"', tag)
        size = image_size(src.group(1)) if src else None
        if size:
            for name, value in zip(('width', 'height'), size):
                if not re.search(r'\b'+name+r'=', tag):
                    tag = tag[:-1] + f' {name}="{value}">'
        return tag
    body = re.sub(r'<img\b[^>]*>', size_image, body)
    if path == '/':
        # The first main image is the visible hero, not a below-the-fold card.
        body = re.sub(r'<img\b', '<img fetchpriority="high" decoding="async"', body, count=1)
    return body

def structured_data(path, body, schema, origin):
    business_id = origin + '/#business'
    nodes = []
    if path in ('/', '/kontakty/'):
        nodes.append({
            '@type':'LocalBusiness', '@id':business_id,
            'name':'PelletsGrupp', 'legalName':'ООО «ПЕЛЛЕТС ГРУПП»',
            'url':origin+'/', 'telephone':'+73433455225', 'email':'office@pelletsgrupp.ru',
            'image':origin+'/assets/pelletsgrupp-logo.png',
            'address':{'@type':'PostalAddress','streetAddress':'ул. Лукиных, д. 1, оф. 4','addressLocality':'Екатеринбург','addressRegion':'Свердловская область','addressCountry':'RU'},
            'areaServed':['Екатеринбург','Свердловская область'],
            'openingHoursSpecification':{'@type':'OpeningHoursSpecification','dayOfWeek':['Monday','Tuesday','Wednesday','Thursday','Friday'],'opens':'09:00','closes':'18:00'},
        })
    if path == '/':
        nodes.append({'@type':'WebSite','@id':origin+'/#website','url':origin+'/','name':'PelletsGrupp','inLanguage':'ru','publisher':{'@id':business_id}})
    if schema and not (path == '/' and schema.get('@type') == 'Organization'):
        original = dict(schema)
        original.pop('@context', None)
        if original.get('@type') == 'Service':
            original['provider'] = {'@type':'LocalBusiness','@id':business_id,'name':'PelletsGrupp'}
        nodes.extend(original.get('@graph', [original]))
    doc = html.fromstring('<div>'+body+'</div>')
    breadcrumbs = doc.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," crumbs ")]')
    if breadcrumbs:
        items = []
        for link in breadcrumbs[0].xpath('.//a[@href]'):
            href = link.get('href')
            if href.startswith('/'):
                items.append({'@type':'ListItem','position':len(items)+1,'name':' '.join(link.text_content().split()),'item':origin+href})
        h1 = doc.xpath('//h1')
        if h1 and (not items or items[-1]['item'] != origin+path):
            items.append({'@type':'ListItem','position':len(items)+1,'name':' '.join(h1[0].text_content().split()),'item':origin+path})
        if len(items)>1:
            nodes.append({'@type':'BreadcrumbList','itemListElement':items})
    return {'@context':'https://schema.org','@graph':nodes} if nodes else None
