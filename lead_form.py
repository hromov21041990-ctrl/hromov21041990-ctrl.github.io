"""PelletsGrupp contact form and its linked personal data documents."""

from html import escape
from urllib.parse import urlencode


PRIVACY_PATH = '/politika-obrabotki-personalnyh-dannyh/'
CONSENT_PATH = '/soglasie-na-obrabotku-zayavki/'
FORM_URL = 'https://forms.yandex.ru/u/6afc135fba5f02d501bffb66'
TOPIC_FIELD = 'answer_dropdown_9008994231354092'
COMMENT_FIELD = 'answer_long_text_9008994231405088'
BOILER_TOPIC = '9008994231354102'
LEAD_TOPICS = {
    '/': None,
    '/kotly/': BOILER_TOPIC,
    '/kotly-15-kvt/': BOILER_TOPIC,
    '/kotly-20-kvt/': BOILER_TOPIC,
    '/kotly-22-kvt/': BOILER_TOPIC,
    '/biotep/': BOILER_TOPIC,
    '/faci/': BOILER_TOPIC,
    '/otoplenie/': '1794976625154',
    '/servisiremont/': '1794976625490',
}


def lead_section(origin, path, model=None):
    params = {'lead_source': origin + path}
    topic = BOILER_TOPIC if model else LEAD_TOPICS.get(path)
    if topic:
        params[TOPIC_FIELD] = topic
    if model:
        params[COMMENT_FIELD] = f'Модель котла: {model}'
    direct_url = FORM_URL + '?' + urlencode(params)
    frame_url = FORM_URL + '?' + urlencode({'iframe': '1', 'theme': 'light', **params})
    return f'''<section id="zayavka" class="section lead-section" aria-label="Оставить заявку">
      <div class="wrap lead-layout">
        <div class="lead-intro">
          <h2>Позвонить специалисту</h2>
          <a href="tel:+73433455225">+7 (343) 345-52-25</a>
          <p class="fine">Пн–Пт, 09:00–18:00 по Екатеринбургу</p>
        </div>
        <div class="lead-card">
          <iframe class="lead-frame ym-hide-content" title="Форма PelletsGrupp «Оставить заявку»"
            src="{escape(frame_url)}" name="ya-form-6afc135fba5f02d501bffb66" loading="lazy"
            referrerpolicy="origin"></iframe>
          <p class="lead-fallback fine">Если форма не загрузилась, <a href="{escape(direct_url)}"
            target="_blank" rel="noopener">откройте её в новой вкладке</a> или позвоните нам.</p>
        </div>
      </div>
    </section>'''


def legal_page(title, text):
    return f'''<section class="section"><div class="wrap">
      <div class="page-head"><h1>{title}</h1></div>
      <article class="article">{text}</article>
    </div></section>'''


LEGAL_PAGES = {
    PRIVACY_PATH: (
        'Политика обработки персональных данных при приёме заявок',
        '''<p>Политика применяется к заявкам, которые посетители отправляют через форму
        «Оставить заявку» на сайте pelletsgrupp.ru.</p>
        <h2>Оператор и контакты</h2>
        <p>ООО «ПЕЛЛЕТС ГРУПП», ИНН 6678134556, ОГРН 1236600075910.
        Почта для запросов по обработке данных — <a href="mailto:office@pelletsgrupp.ru">office@pelletsgrupp.ru</a>.</p>
        <h2>Данные и цель обработки</h2>
        <p>Компания получает имя, номер телефона, выбранную тему и комментарий, если вы его оставили,
        а также адрес страницы, время отправки и отметку о согласии. Данные используются
        для обработки заявки, обратной связи и консультации по указанной теме.
        Основание обработки — отдельное согласие, которое посетитель даёт в форме.</p>
        <h2>Приём и доступ к заявкам</h2>
        <p>Заявки принимает сервис <a href="https://yandex.ru/legal/forms_termsofuse/">Яндекс Формы</a>.
        Ответы сохраняются в закрытом разделе формы. Уведомления поступают на корпоративную почту
        PelletsGrupp. Доступ к обращениям предоставляется тем, кто обрабатывает заявки.
        Имя, телефон и комментарий из формы не используются в целях веб-аналитики.</p>
        <h2>Сроки обработки и права посетителя</h2>
        <p>Данные обрабатываются до достижения цели обработки или отзыва согласия.
        После этого обработка прекращается, а данные удаляются в сроки, установленные законом,
        если у компании нет иного законного основания для их обработки.</p>
        <p>Чтобы получить сведения об обработке, уточнить данные, потребовать прекращения обработки
        или отозвать согласие, напишите на <a href="mailto:office@pelletsgrupp.ru">office@pelletsgrupp.ru</a>.
        Укажите номер телефона, указанный в заявке, и суть запроса.</p>''',
    ),
    CONSENT_PATH: (
        'Согласие на обработку персональных данных при отправке заявки',
        '''<p>Отмечая поле согласия в форме «Оставить заявку», я даю ООО «ПЕЛЛЕТС ГРУПП»
        (ИНН 6678134556, ОГРН 1236600075910) согласие на обработку моего имени, телефона,
        выбранной темы и сведений, которые я указываю в комментарии, а также страницы
        и времени отправки и отметки о согласии. Цель обработки — принять мою заявку,
        связаться со мной и проконсультировать по теме обращения.</p>
        <p>Согласие включает сбор, запись, систематизацию, хранение, уточнение, извлечение,
        использование, блокирование и удаление данных с использованием средств автоматизации
        и без них. Для приёма и хранения ответов компания использует Яндекс Формы,
        а для получения уведомлений — корпоративную почту.</p>
        <p>Согласие действует до достижения указанной цели или его отзыва. Отозвать согласие
        можно письмом на <a href="mailto:office@pelletsgrupp.ru">office@pelletsgrupp.ru</a>.</p>''',
    ),
}
