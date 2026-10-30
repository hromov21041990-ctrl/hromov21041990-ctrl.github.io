"""Validate the generated production sitemap and search-facing markup."""
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from lxml import etree, html

ROOT = Path(__file__).resolve().parent
DIST = ROOT/'dist'
ORIGIN = 'https://pelletsgrupp.ru'
urls = etree.parse(str(DIST/'sitemap.xml')).xpath('//*[local-name()="loc"]/text()')
assert len(urls)==len(set(urls)), 'Duplicate sitemap URLs'
titles, descriptions = [], []
product_count = breadcrumb_count = image_count = 0
for url in urls:
    assert url.startswith(ORIGIN+'/'), url
    path = urlparse(url).path
    file = DIST/path.strip('/')/'index.html'
    assert file.is_file(), url
    doc = html.fromstring(file.read_text())
    assert doc.xpath('//link[@rel="canonical"]/@href') == [url], url
    assert not doc.xpath('//meta[@http-equiv="refresh"]'), url
    assert not any('noindex' in x.lower() for x in doc.xpath('//meta[@name="robots"]/@content')), url
    title = doc.xpath('string(//title)')
    description = doc.xpath('//meta[@name="description"]/@content')
    assert title and 'Пустой шаблон' not in title, url
    assert len(description)==1 and description[0].strip(), url
    titles.append(title); descriptions.extend(description)
    assert len(doc.xpath('//h1'))==1, url
    assert 'Sed feugiat' not in doc.text_content(), url
    assert doc.xpath('//meta[@property="og:url"]/@content')==[url], url
    nodes=[]
    for raw in doc.xpath('//script[@type="application/ld+json"]/text()'):
        value=json.loads(raw)
        nodes.extend(value.get('@graph',[value]))
    for node in nodes:
        if node.get('@type')=='Product':
            product_count+=1
            assert node.get('sku') and node.get('name'), url
            if node.get('offers'):
                assert node['offers']['price']>0, url
        if node.get('@type')=='BreadcrumbList':
            breadcrumb_count+=1
            items=node['itemListElement']
            assert [i['position'] for i in items]==list(range(1,len(items)+1)), url
            assert items[-1]['item']==url, url
            for item in items:
                assert item['name'] and item['item'].startswith(ORIGIN+'/'), url
                assert (DIST/urlparse(item['item']).path.strip('/')/'index.html').is_file(), item
    for image in doc.xpath('//img[starts-with(@src,"/assets/")]'):
        if urlparse(image.get('src')).path.endswith('.svg'):continue
        image_count+=1
        assert int(image.get('width','0'))>0 and int(image.get('height','0'))>0, url
assert not [t for t,n in Counter(titles).items() if n>1], 'Duplicate indexable titles'
assert not [d for d,n in Counter(descriptions).items() if n>1], 'Duplicate indexable descriptions'
assert product_count==340, product_count  # 338 equipment/parts + 2 pellet products
for path in ('/', '/kontakty/'):
    doc=html.fromstring((DIST/path.strip('/')/'index.html').read_text())
    nodes=json.loads(doc.xpath('//script[@type="application/ld+json"]/text()')[0])['@graph']
    business=next(n for n in nodes if n['@type']=='LocalBusiness')
    assert business['telephone']=='+73433455225'
    assert business['address']['addressLocality']=='Екатеринбург'
    assert business['openingHoursSpecification']['opens']=='09:00'
redirects=json.loads((ROOT/'data/seo-redirects.json').read_text())
for old,target in redirects.items():
    doc=html.fromstring((DIST/old.strip('/')/'index.html').read_text())
    assert doc.xpath('//link[@rel="canonical"]/@href')==[ORIGIN+target], old
    assert doc.xpath('//meta[@http-equiv="refresh"]/@content')==['0; url='+target], old
    assert ORIGIN+old not in urls, old
for path in ('404.html','404/index.html'):
    doc=html.fromstring((DIST/path).read_text())
    assert any('noindex' in x for x in doc.xpath('//meta[@name="robots"]/@content')),path
home=html.fromstring((DIST/'index.html').read_text())
assert 'Екатеринбурге' in home.xpath('string(//h1)')
assert home.xpath('//main//img[@fetchpriority="high"]')
catalog=html.fromstring((DIST/'katalog'/'index.html').read_text())
assert catalog.xpath('//*[@id="empty-clear"]')
for path in ('/dostavka/','/o-nas/'):
    assert home.xpath(f'//footer//a[@href="{path}"]'), path
blog=html.fromstring((DIST/'blog'/'index.html').read_text())
assert blog.xpath('//a[@href="/preimushhestva-pelletnykh-otopitelnykh-kotlov/"]')
source_js=(ROOT/'site.js').read_text()
for token in ('normalizeSearch','replaceAll(\'ё\',\'е\')','window.addEventListener(\'pageshow\'','requestAnimationFrame(filter)'):
    assert token in source_js, token
print(f'SEO verification passed: {len(urls)} canonical sitemap URLs, unique metadata, {product_count} Product nodes, {breadcrumb_count} BreadcrumbList nodes, {image_count} raster images with dimensions, {len(redirects)} legacy URL fallbacks, noindex 404.')
