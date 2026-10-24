# FORGE website

Static site: 5 pages x 2 languages (English at `/`, Arabic at `/ar/`) + 2 live demos.

## Before launch (edit the top of build.py)
- SITE_URL      your real domain (used for canonical, hreflang, sitemap, social previews)
- EMAIL         company email
- WHATSAPP      digits only, e.g. 201001234567  (enables the WhatsApp buttons)
- FORM_ENDPOINT a form service URL (e.g. Formspree). Empty = opens the visitor's email app.
Then run:  python3 build.py   (needs Python 3 + cairosvg; output goes to ./dist)

## Preview locally
cd dist && python3 -m http.server 8000   ->  http://localhost:8000
(Opening index.html by double-click will not follow folder links; use a server or deploy.)

## Deploy
Upload the contents of dist/ to Netlify, Cloudflare Pages, GitHub Pages or any static host.
404.html is used automatically by most of them.

## Edit content
All copy (English + Arabic) is in content.py. Styles: assets/css/site.css. Demos: demos/*/index.html.
Logos are copied from the Brand Kit at build time (see KIT path in build.py).
