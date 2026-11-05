"""Commercial landing page for the established /kotly/ search route."""


BRANDS = (
    ("BIOTEP", "/biotep/", "Автоматические котлы для частных домов и небольших объектов."),
    ("FACI", "/faci/", "Линейка мощностей и комплектаций для бытовых и промышленных задач."),
    ("СТАРТ", "/start/", "Котлы серии GR с выбором мощности и объёма топливного бункера."),
    ("Вулкан", "/vulkan/", "Серии автоматических котлов для домов, бизнеса и производственных объектов."),
)


def boiler_products(products):
    return [
        product for product in products
        if product.get("product_type") not in ("biotep_spare", "vulkan_spare", "start_spare")
        and product["brand"] != "ZOTA"
    ]


def featured_products(products):
    boilers = boiler_products(products)
    featured = []
    for brand, _, _ in BRANDS:
        featured.extend([product for product in boilers if product["brand"] == brand][:2])
    return featured


def model_count(count):
    if count % 10 == 1 and count % 100 != 11:
        word = "модель"
    elif count % 10 in (2, 3, 4) and count % 100 not in (12, 13, 14):
        word = "модели"
    else:
        word = "моделей"
    return f"{count} {word}"


def page(products, card):
    boilers = boiler_products(products)
    featured = featured_products(products)
    hero_image = next(product for product in boilers if product["brand"] == "BIOTEP")["images"][0]
    brand_cards = []
    for brand, route, description in BRANDS:
        count = sum(product["brand"] == brand for product in boilers)
        brand_cards.append(
            f'<a class="tile boiler-brand" href="{route}">'
            f'<span class="badge">{model_count(count)} в каталоге</span>'
            f'<h3>{brand}</h3><p>{description}</p>'
            '<span class="text-link">Смотреть модели →</span></a>'
        )
    return f'''
<div class="wrap"><section class="hero boiler-hero"><div><span class="eyebrow">Оборудование для автономного отопления</span><h1>Пеллетные котлы в Екатеринбурге</h1><p class="lead">Автоматические пеллетные котлы BIOTEP, FACI, СТАРТ и Vulkan для дома, бизнеса и производственных объектов. Поможем рассчитать мощность, подобрать комплектацию и организовать доставку по Свердловской области.</p><div class="actions"><a class="btn" href="#models">Посмотреть модели →</a><a class="btn light" href="/otoplenie/">Монтаж котла</a></div><div class="proof"><span><b>01</b> Расчёт мощности</span><span><b>02</b> Подбор комплектации</span><span><b>03</b> Монтаж и сервис</span></div></div><div class="photo"><img src="{hero_image}" alt="Автоматический пеллетный котёл из каталога PelletsGrupp" loading="eager"><div class="stamp"><strong>{model_count(len(boilers))}</strong>Цены и характеристики в карточках оборудования</div></div></section></div>
<section class="section white"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Марки оборудования</span><h2>Котлы в каталоге PelletsGrupp</h2></div><a href="/katalog/">Весь каталог оборудования →</a></div><div class="grid boiler-brands">{''.join(brand_cards)}</div></div></section>
<section class="section"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Подбор без лишнего запаса</span><h2>Что учитываем при выборе котла</h2></div></div><div class="grid boiler-factors"><article class="service"><div class="num">01 / МОЩНОСТЬ</div><h3>Теплопотери объекта</h3><p>Учитываем площадь, утепление, высоту помещений, вентиляцию и режим эксплуатации. Мощность подбирается по расчёту, а не только по площади.</p></article><article class="service"><div class="num">02 / АВТОМАТИКА</div><h3>Режим работы</h3><p>Сравниваем возможности управления, авторозжига и очистки с тем, как часто владелец сможет контролировать котельную.</p></article><article class="service"><div class="num">03 / ТОПЛИВО</div><h3>Бункер и подача</h3><p>Объём бункера и расход зависят от мощности, нагрузки и качества пеллет. Сразу планируем место хранения топлива.</p></article><article class="service"><div class="num">04 / ЭКСПЛУАТАЦИЯ</div><h3>Монтаж и обслуживание</h3><p>Проверяем требования к дымоходу, обвязке и доступу к узлам, чтобы котёл было удобно чистить и обслуживать.</p></article></div></div></section>
<section class="section white" id="models"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Цены и комплектации</span><h2>Модели пеллетных котлов</h2></div><a href="/katalog/">Все котлы и горелки →</a></div><div class="grid products">{''.join(card(product) for product in featured)}</div><div class="boiler-catalog-link"><p>Не нашли подходящую мощность? В полном каталоге доступны остальные модели и варианты комплектации.</p><a class="btn light" href="/katalog/">Открыть полный каталог →</a></div></div></section>
<section class="section"><div class="wrap boiler-support"><div><span class="eyebrow">Оборудование под ключ</span><h2>От подбора до сезонного обслуживания</h2><p>Пеллетный котёл рассматриваем вместе с системой отопления, дымоходом, топливом и будущим сервисом. Так можно заранее согласовать состав работ и избежать несовместимых решений.</p></div><div class="grid"><a class="tile" href="/otoplenie/"><h3>Монтаж отопления</h3><p>Проектирование, установка котла и дымохода, обвязка и пусконаладка.</p><span class="text-link">Условия монтажа →</span></a><a class="tile" href="/pellety/"><h3>Топливные пеллеты</h3><p>Белые и серые гранулы в мешках и биг-бэгах, самовывоз и доставка.</p><span class="text-link">Цены на пеллеты →</span></a><a class="tile" href="/servisiremont/"><h3>Сервис и ремонт</h3><p>Чистка, диагностика, настройка автоматики и помощь в эксплуатации.</p><span class="text-link">Перейти к сервису →</span></a></div></div></section>
<section class="section white"><div class="wrap boiler-faq"><span class="eyebrow">Ответы перед покупкой</span><h2>Частые вопросы о пеллетных котлах</h2><details><summary>Как подобрать мощность пеллетного котла?</summary><p>Нужен расчёт теплопотерь здания с учётом утепления, окон, высоты помещений, вентиляции, горячего водоснабжения и режима проживания. Подбор только по площади может дать недостаточную или избыточную мощность.</p></details><details><summary>От чего зависит цена котла?</summary><p>От марки, мощности, автоматики, варианта исполнения и объёма бункера. Доставка, монтаж, дымоход и обвязка рассчитываются отдельно после уточнения объекта.</p></details><details><summary>Как часто нужно загружать пеллеты?</summary><p>Интервал зависит от объёма бункера, мощности котла, тепловой нагрузки и качества топлива. Ожидаемый расход и подходящий объём бункера рассчитываем при подборе.</p></details><details><summary>Есть ли доставка по Свердловской области?</summary><p>Да, оборудование и топливо доставляем по Екатеринбургу и Свердловской области. Стоимость и способ разгрузки согласовываются для конкретного адреса.</p></details></div></section>
'''
