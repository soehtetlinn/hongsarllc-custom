# Pyidaungsu fonts for PDF reports

Source TTF files (used to generate base64-embedded CSS):

- `Pyidaungsu-2.5.3_Regular.ttf`
- `Pyidaungsu-2.5.3_Bold.ttf`

## How it works

wkhtmltopdf cannot load fonts via URL paths like `/hongsar_reports/static/src/fonts/...`
because it runs as an isolated process without access to Odoo's web server.

The solution is to embed fonts as base64 data URIs in `report_fonts.css`.

## Regenerating the CSS

If you update the font files, run:

```bash
python generate_font_css.py
```

This will regenerate `static/src/css/report_fonts.css` with the new base64-encoded fonts.
