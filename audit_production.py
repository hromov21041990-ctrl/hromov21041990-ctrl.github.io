from pathlib import Path
from urllib.parse import urlparse, unquote

from lxml import html


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
ORIGIN = "https://pelletsgrupp.ru"
errors = []
html_files = list(DIST.rglob("*.html"))

for file in html_files:
    source = file.read_text()
    document = html.fromstring(source)
    relative = file.relative_to(DIST)

    if "chatgpt.site" in source:
        errors.append((str(relative), "test-host reference"))
    if "noindex" in source.lower():
        errors.append((str(relative), "noindex in production"))
    if "Тестовая версия переноса" in source:
        errors.append((str(relative), "test banner in production"))
    if "08:00" in source or "08.00" in source:
        errors.append((str(relative), "old working hours"))
    if "+7 (930)" in source or "226-0-228" in source:
        errors.append((str(relative), "retired service phone"))
    for claim in (
        "собственное производство топлива",
        "собственное производство</",
        "является производителем пеллетов",
        "PelletsGrupp производит цилиндрические гранулы",
        "Компания PelletsGrupp производит и продает древесные пеллеты",
        "Мы производим пеллеты из чистой хвойной древесины",
        "На собственном производстве мы выпускаем",
    ):
        if claim.lower() in source.lower():
            errors.append((str(relative), f"incorrect production claim: {claim}"))

    canonical = document.xpath('//link[@rel="canonical"]/@href')
    if len(canonical) != 1 or not canonical[0].startswith(ORIGIN + "/"):
        errors.append((str(relative), "invalid canonical"))

    for value in document.xpath('//@href|//@src'):
        if not value.startswith("/") or value.startswith("//"):
            continue
        path = unquote(urlparse(value).path)
        local = DIST / path.lstrip("/")
        if not local.is_file() and not (local / "index.html").is_file():
            errors.append((str(relative), f"broken local URL: {value}"))

robots = (DIST / "robots.txt").read_text()
if "Allow: /" not in robots or ORIGIN + "/sitemap.xml" not in robots:
    errors.append(("robots.txt", "production indexing is not enabled"))
if (DIST / "CNAME").read_text().strip() != "pelletsgrupp.ru":
    errors.append(("CNAME", "custom domain is not configured"))
if not (DIST / ".nojekyll").exists():
    errors.append((".nojekyll", "GitHub Pages marker is missing"))

sitemap = (DIST / "sitemap.xml").read_text()
if "chatgpt.site" in sitemap or ORIGIN not in sitemap:
    errors.append(("sitemap.xml", "invalid production origin"))

if errors:
    raise SystemExit("Production audit failed:\n" + "\n".join(f"- {path}: {message}" for path, message in errors))

print(f"Production audit passed: {len(html_files)} HTML files, custom domain {ORIGIN}, indexing enabled.")
