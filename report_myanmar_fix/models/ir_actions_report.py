# -*- coding: utf-8 -*-
"""
Fix Myanmar/Burmese PDF rendering by using WeasyPrint instead of wkhtmltopdf.

wkhtmltopdf has a known bug with Myanmar Unicode text - it cannot properly
handle complex text shaping (HarfBuzz), causing characters to be reordered
incorrectly.

WeasyPrint has proper HarfBuzz support and renders Myanmar Unicode correctly.
"""
import io
import logging
import re

import lxml.html
from lxml import etree

from odoo import api, models
from odoo.addons.base.models.ir_actions_report import _split_table
from odoo.http import request

_logger = logging.getLogger(__name__)

# Overall PDF body font size (px). Reduced ~2px below typical Odoo report (~13px).
REPORT_FONT_SIZE_PX = 11

# Myanmar script Unicode range (U+1000 - U+109F) plus extensions
_MYANMAR_PATTERN = re.compile(r'[\u1000-\u109F\uAA60-\uAA7F\uA9E0-\uA9FF]')


def _has_myanmar_text(text):
    """Check if text contains Myanmar characters."""
    return bool(_MYANMAR_PATTERN.search(text)) if text else False


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _get_weasyprint_base_url(self):
        """Get base URL for WeasyPrint to resolve relative paths."""
        if request:
            return request.httprequest.host_url
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return base_url or 'http://localhost:8069'

    def _weasyprint_subst_header_footer(self, header_html, footer_html, page_index):
        """
        Mimic wkhtmltopdf minimal_layout subst(): keep only header/footer child
        at page_index inside the containers (one per printed document in batch).
        """
        def _select_child(container_id, html_str):
            if not html_str:
                return html_str
            try:
                root = lxml.html.fromstring(html_str)
            except etree.ParserError:
                return html_str
            for el in root.xpath(f'//*[@id="{container_id}"]'):
                children = list(el)
                if children and page_index < len(children):
                    keep = children[page_index]
                    el.clear()
                    el.append(keep)
            return lxml.html.tostring(root, encoding='unicode', method='html')

        h = _select_child('minimal_layout_report_headers', header_html)
        f = _select_child('minimal_layout_report_footers', footer_html)
        return h, f

    def _sanitize_html_for_weasyprint(self, html_string):
        """
        Odoo minimal_layout uses <html style="height: 0"> and body overflow-hidden
        for wkhtmltopdf. WeasyPrint clips long documents (missing order lines, etc.).
        """
        if not html_string:
            return html_string
        try:
            doc = lxml.html.fromstring(html_string, parser=lxml.html.HTMLParser(encoding='utf-8'))
        except etree.ParserError:
            return html_string

        for node in doc.xpath('//html'):
            style = (node.get('style') or '').strip()
            if style:
                style = re.sub(r'height\s*:\s*0\s*;?', '', style, flags=re.IGNORECASE)
                style = re.sub(r';\s*;', ';', style).strip(' ;')
                if style:
                    node.set('style', style)
                elif 'style' in node.attrib:
                    del node.attrib['style']

        for node in doc.xpath('//body'):
            classes = [c for c in (node.get('class') or '').split() if c and c != 'overflow-hidden']
            node.set('class', ' '.join(classes))
            existing = node.get('style') or ''
            extra = 'min-height: auto !important; overflow: visible !important; height: auto !important;'
            node.set('style', f'{existing}; {extra}' if existing else extra)

        for node in doc.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " container ")]'):
            existing = node.get('style') or ''
            if 'overflow' not in existing.lower():
                node.set('style', f'{existing}; overflow: visible !important'.strip('; '))

        return lxml.html.tostring(doc, encoding='unicode', method='html', doctype='<!DOCTYPE html>')

    def _merge_header_footer_into_body(self, body, header=None, footer=None):
        """Insert Odoo PDF header/footer for WeasyPrint (running elements on every page)."""
        header_content = ''
        footer_content = ''

        if header:
            match = re.search(r'<body[^>]*>(.*?)</body>', header, re.DOTALL | re.IGNORECASE)
            if match:
                header_content = match.group(1).strip()
            else:
                # Some layouts provide header/footer HTML fragments without <body> tags.
                # In that case, inject the full fragment as-is.
                header_content = header.strip()

        if footer:
            match = re.search(r'<body[^>]*>(.*?)</body>', footer, re.DOTALL | re.IGNORECASE)
            if match:
                footer_content = match.group(1).strip()
            else:
                footer_content = footer.strip()

        if header_content:
            def _after_open_body(m):
                return (
                    m.group(1)
                    + '<div class="o_weasy_running_header">'
                    + '<div class="o_weasy_running_inset">'
                    + header_content
                    + '</div></div>'
                )

            body = re.sub(r'(<body[^>]*>)', _after_open_body, body, count=1, flags=re.IGNORECASE)

        if footer_content:
            def _after_open_body_for_footer(m):
                return (
                    m.group(1)
                    + '<div class="o_weasy_running_footer">'
                    + '<div class="o_weasy_running_inset">'
                    + footer_content
                    + '</div></div>'
                )

            # For running elements, placing footer at end of body may make it available only on
            # trailing pages in WeasyPrint. Inject right after <body> so it applies to all pages.
            body = re.sub(r'(<body[^>]*>)', _after_open_body_for_footer, body, count=1, flags=re.IGNORECASE)

        return body, bool(header_content), bool(footer_content)

    def _weasyprint_margins_mm(
            self, paperformat_id, specific_paperformat_args,
            has_running_header=False, has_running_footer=False):
        """Match Odoo wkhtmltopdf margins; left/right forced equal (max of both) for even gutters."""
        args = specific_paperformat_args or {}
        mt = float(args.get('data-report-margin-top') or (paperformat_id.margin_top if paperformat_id else 40))
        mb = float(args.get('data-report-margin-bottom') or (paperformat_id.margin_bottom if paperformat_id else 20))
        ml = float(paperformat_id.margin_left if paperformat_id else 7)
        mr = float(paperformat_id.margin_right if paperformat_id else 7)
        mlr = max(ml, mr)
        # Running header/footer paint in @page margin boxes (not duplicated in body).
        if has_running_header:
            # Cap Odoo's large default top margin; header height ~22–28mm is enough.
            mt = min(mt, 26.0) + 2.0
        if has_running_footer:
            mb = min(mb, 18.0) + 2.0
        return mt, mb, mlr

    def _weasyprint_page_size_css(self, paperformat_id, landscape):
        fmt = (paperformat_id.format if paperformat_id and paperformat_id.format else None) or 'A4'
        if fmt == 'custom' and paperformat_id and paperformat_id.page_width and paperformat_id.page_height:
            size = f'{paperformat_id.page_width}mm {paperformat_id.page_height}mm'
            return f'{size} landscape' if landscape else size
        if landscape:
            return f'{fmt} landscape'
        return fmt

    def _build_weasyprint_stylesheet_string(
            self,
            paperformat_id,
            specific_paperformat_args,
            landscape,
            has_running_header,
            has_running_footer,
    ):
        mt, mb, mlr = self._weasyprint_margins_mm(
            paperformat_id, specific_paperformat_args, has_running_header, has_running_footer)
        size = self._weasyprint_page_size_css(paperformat_id, landscape)

        # Running header/footer: repeats on every page (WeasyPrint / CSS GCPM)
        page_extra = []
        if has_running_header:
            page_extra.append('''
            @top-center {
                content: element(weasy-doc-header);
                vertical-align: top;
                text-align: left;
                padding: 3px 6mm 1mm 6mm;
                margin: 0;
                width: 100%;
            }''')
        if has_running_footer:
            page_extra.append('''
            @bottom-center {
                content: element(weasy-doc-footer);
                vertical-align: top;
                padding: 4mm 6mm 1.5mm 6mm;
                margin: 0;
                width: 100%;
            }''')

        page_rule = f'''
            @page {{
                size: {size};
                margin: {mt}mm {mlr}mm {mb}mm {mlr}mm;
                {''.join(page_extra)}
            }}
        '''

        running_css = []
        if has_running_header:
            running_css.append('''
            .o_weasy_running_header {
                position: running(weasy-doc-header);
                width: 100%;
                box-sizing: border-box;
                overflow: visible !important;
                line-height: 1.3 !important;
            }
            ''')
        if has_running_footer:
            running_css.append('''
            .o_weasy_running_footer {
                position: running(weasy-doc-footer);
                width: 100%;
                box-sizing: border-box;
                overflow: visible !important;
                line-height: 1.55 !important;
            }
            ''')

        base = f'''
            {page_rule}
            {''.join(running_css)}
            html {{
                height: auto !important;
                min-height: 0 !important;
            }}
            body, html {{
                overflow: visible !important;
            }}
            /* Same horizontal inset as body + room for tall glyphs */
            .o_weasy_running_header .o_weasy_running_inset {{
                padding: 5px 11mm 0.5mm 11mm;
                box-sizing: border-box !important;
                overflow: visible !important;
            }}
            .o_weasy_running_footer .o_weasy_running_inset {{
                padding: 0.5mm 11mm 0.5mm 11mm;
                box-sizing: border-box !important;
                overflow: visible !important;
            }}
            /* Footer only: reduce bottom inset further to avoid blank trailing pages */
            .o_weasy_running_footer .o_weasy_running_inset {{
                padding-bottom: 0.8mm !important;
            }}
            /* Bootstrap .row uses negative side margins; in WeasyPrint margin boxes that pulls
               content past the clip rect and chops the first/last columns (boxed layout headers). */
            .o_weasy_running_header .row,
            .o_weasy_running_footer .row {{
                margin-left: 0 !important;
                margin-right: 0 !important;
                --bs-gutter-x: 0.75rem;
            }}
            .o_weasy_running_header .header,
            .o_weasy_running_header .header .d-flex,
            .o_weasy_running_header .header [class*="col-"],
            .o_weasy_running_footer .footer,
            .o_weasy_running_footer .o_footer_content {{
                overflow: visible !important;
            }}
            /* WeasyPrint + position:running can collapse flex columns so company logos paint at 0×0 */
            .o_weasy_running_header img,
            .o_weasy_running_footer img {{
                flex-shrink: 0 !important;
                min-width: 0.5mm !important;
                min-height: 8mm !important;
                height: auto !important;
                width: auto !important;
                object-fit: contain !important;
                box-sizing: content-box !important;
                display: block !important;
            }}
            .o_weasy_running_header [class*="col-"]:first-child,
            .o_weasy_running_header .header .d-flex > :first-child {{
                flex-shrink: 0 !important;
                min-width: min-content !important;
            }}
            /* Letterhead: company block left-aligned like standard documents (Odoo boxed/bubble use text-end + space-between) */
            .o_weasy_running_header .text-end,
            .o_weasy_running_header [name="company_address"].text-end {{
                text-align: left !important;
            }}
            .o_weasy_running_header .float-end {{
                float: none !important;
            }}
            .o_weasy_running_header .header .row {{
                flex-direction: column !important;
                align-items: flex-start !important;
            }}
            .o_weasy_running_header .header .row > [class*="col-"] {{
                width: 100% !important;
                max-width: 100% !important;
                flex: 0 0 auto !important;
            }}
            .o_weasy_running_header .header .row > [class*="offset-"] {{
                margin-left: 0 !important;
            }}
            .o_weasy_running_header .header .d-flex.justify-content-between,
            .o_weasy_running_header .o_folder_company_info.d-flex.justify-content-between,
            .o_weasy_running_header .d-flex.justify-content-between.align-items-center {{
                justify-content: flex-start !important;
                align-items: flex-start !important;
                gap: 0.75rem !important;
            }}
            /* Recipient / customer block: Odoo uses col-5 ms-auto which pushes address to the right in PDF */
            body.o_body_pdf .address.row div[name="address"] {{
                margin-left: 0 !important;
                margin-inline-start: 0 !important;
                align-self: flex-start !important;
            }}
            body.o_body_pdf .address.row {{
                justify-content: flex-start !important;
                margin-top: 0 !important;
                margin-bottom: 2mm !important;
                padding-bottom: 0 !important;
            }}
            body.o_body_pdf .address.row div[name="address"],
            body.o_body_pdf .address.row div[name="information_block"] {{
                margin-bottom: 0 !important;
                padding-bottom: 0 !important;
                line-height: 1.25 !important;
            }}
            body.o_body_pdf .address.row address,
            body.o_body_pdf .address.row address div,
            body.o_body_pdf .address.row address span {{
                margin: 0 !important;
                padding: 0 !important;
                line-height: 1.25 !important;
            }}
            /* Compact company letterhead (logo + company address) */
            .o_weasy_running_header .mb8,
            .o_weasy_running_header .mb4,
            .o_weasy_running_header .mb-4 {{
                margin-bottom: 0 !important;
            }}
            .o_weasy_running_header .header {{
                margin-bottom: 0 !important;
                padding-bottom: 0 !important;
            }}
            .o_weasy_running_header .header .row {{
                margin-bottom: 0 !important;
                gap: 0.25rem !important;
            }}
            .o_weasy_running_header [name="company_address"],
            .o_weasy_running_header [name="company_address"] ul,
            .o_weasy_running_header [name="company_address"] li,
            .o_weasy_running_header [name="company_address"] span,
            .o_weasy_running_header [name="company_address"] div {{
                margin-top: 0 !important;
                margin-bottom: 0 !important;
                padding-top: 0 !important;
                padding-bottom: 0 !important;
                line-height: 1.25 !important;
            }}
            .o_weasy_running_header address {{
                margin: 0 !important;
                line-height: 1.25 !important;
            }}
            .o_weasy_running_header .o_company_logo_big {{
                margin-bottom: 0 !important;
            }}
            body.o_body_pdf #informations {{
                margin-bottom: 2mm !important;
                display: flex !important;
                flex-wrap: wrap !important;
                align-items: flex-start !important;
                gap: 0 2mm !important;
            }}
            /* Order date, customer, salesperson: one row, equal width (33% each) */
            body.o_body_pdf #informations [name="informations_date"] {{
                order: 2 !important;
            }}
            body.o_body_pdf #informations [name="informations_customer"] {{
                order: 3 !important;
            }}
            body.o_body_pdf #informations [name="informations_salesperson"] {{
                order: 4 !important;
            }}
            body.o_body_pdf #informations [name="informations_date"],
            body.o_body_pdf #informations [name="informations_customer"],
            body.o_body_pdf #informations [name="informations_salesperson"] {{
                flex: 1 1 33.33% !important;
                width: 33.33% !important;
                max-width: 33.33% !important;
                min-width: 0 !important;
                box-sizing: border-box !important;
                margin-bottom: 0 !important;
                padding-right: 2mm !important;
                vertical-align: top !important;
                line-height: 1.25 !important;
            }}
            body.o_body_pdf #informations [name="informations_customer"] address,
            body.o_body_pdf #informations [name="informations_customer"] div,
            body.o_body_pdf #informations [name="informations_customer"] p {{
                margin: 0 !important;
                padding: 0 !important;
                line-height: 1.25 !important;
            }}
            /* Reference / expiration on their own full-width rows */
            body.o_body_pdf #informations [name="informations_reference"] {{
                order: 1 !important;
                flex: 1 1 100% !important;
                width: 100% !important;
                max-width: 100% !important;
            }}
            body.o_body_pdf #informations [name="expiration_date"] {{
                order: 5 !important;
                flex: 1 1 100% !important;
                width: 100% !important;
                max-width: 100% !important;
            }}
            /* Customer moved into #informations; hide duplicate top address row on invoices */
            body.o_body_pdf .invoice_main > .row:first-child {{
                display: none !important;
                height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
            }}
            body.o_body_pdf .article > .oe_structure:empty,
            body.o_body_pdf .oe_structure:empty {{
                display: none !important;
                height: 0 !important;
                min-height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
            }}
            body.o_body_pdf .article h2 {{
                margin-top: 1mm !important;
                margin-bottom: 1mm !important;
            }}
            /* Bubble (and similar): title was flexed to the opposite side of the customer block */
            body.o_body_pdf .article > div.d-flex.justify-content-between.align-items-end {{
                justify-content: flex-start !important;
                flex-direction: column !important;
                align-items: flex-start !important;
            }}
            body.o_body_pdf .article > div.d-flex.justify-content-between.align-items-end > h2.text-end {{
                text-align: left !important;
                align-self: flex-start !important;
                width: 100%;
            }}
            /* Bubble + quotations: h2 keeps text-end even when parent has no d-flex (e.g. information_block) */
            body.o_body_pdf .article h2.text-end {{
                text-align: left !important;
                align-self: flex-start !important;
                width: 100%;
            }}
            /* Folder layout: "Quotation #" / title is h2.o_folder_title inside header flex after SVGs (reads right) */
            .o_weasy_running_header .o_folder_adaptative_shape.d-flex {{
                flex-wrap: wrap !important;
                justify-content: flex-start !important;
                align-items: flex-start !important;
            }}
            .o_weasy_running_header h2.o_folder_title {{
                text-align: left !important;
                order: -1 !important;
                margin-right: auto !important;
            }}
            /* Match Odoo report inner gutters (see web report.scss $o-default-report-margins).
               Zero padding flushed Myanmar/Latin glyphs against the page box and WeasyPrint
               clipped ascenders and table edge text; restore side inset + top breathing room. */
            body.o_body_pdf.container {{
                max-width: none !important;
                width: 100% !important;
                box-sizing: border-box !important;
                padding-left: 11mm !important;
                padding-right: 11mm !important;
                padding-top: 0 !important;
            }}
            body.o_body_pdf.o_css_margins.container {{
                padding-top: 0 !important;
            }}
            body.o_body_pdf.o_css_margins .header {{
                padding-top: 0 !important;
                margin-top: 0 !important;
            }}
            body.o_body_pdf.o_css_margins .footer > .o_footer_content {{
                padding-bottom: 11mm !important;
            }}
            /* report_tables.scss zeros first/last cell padding; restore min inset so edge columns are not clipped */
            .o_table_standard table:not(.o_ignore_layout_styling) th:first-child,
            .o_table_standard table:not(.o_ignore_layout_styling) td:first-child {{
                padding-left: 0.5rem !important;
            }}
            .o_table_standard table:not(.o_ignore_layout_styling) th:last-child,
            .o_table_standard table:not(.o_ignore_layout_styling) td:last-child {{
                padding-right: 0.5rem !important;
            }}
            body.o_body_pdf td, body.o_body_pdf th {{
                overflow: visible !important;
            }}
            /* Keep SO line table borders visible on every page fragment */
            body.o_body_pdf .sale_main_table {{
                border-left: 0.30mm solid #111 !important;
                border-right: 0.30mm solid #111 !important;
                border-bottom: 0.30mm solid #111 !important;
                border-top: 0.30mm solid #111 !important;
                border-collapse: separate !important;
                border-spacing: 0 !important;
            }}
            body.o_body_pdf .sale_main_table th,
            body.o_body_pdf .sale_main_table td {{
                border-right: 0.30mm solid #111 !important;
                border-bottom: 0.30mm solid #111 !important;
                border-top: 0 !important;
            }}
            body.o_body_pdf .sale_main_table th:last-child,
            body.o_body_pdf .sale_main_table td:last-child {{
                border-right: 0 !important;
            }}
            body.o_body_pdf .sale_main_table thead th:first-child {{
                border-top-left-radius: 7px !important;
            }}
            body.o_body_pdf .sale_main_table thead th:last-child {{
                border-top-right-radius: 7px !important;
            }}
            /* Invoice line table should use the same bordered theme as SO */
            body.o_body_pdf .invoice_main_table {{
                border-left: 0.30mm solid #111 !important;
                border-right: 0.30mm solid #111 !important;
                border-bottom: 0.30mm solid #111 !important;
                border-top: 0.30mm solid #111 !important;
                border-collapse: separate !important;
                border-spacing: 0 !important;
                table-layout: auto !important;
            }}
            body.o_body_pdf .invoice_main_table th,
            body.o_body_pdf .invoice_main_table td {{
                border-right: 0.30mm solid #111 !important;
                border-bottom: 0.30mm solid #111 !important;
                border-top: 0 !important;
            }}
            body.o_body_pdf .invoice_main_table th:last-child,
            body.o_body_pdf .invoice_main_table td:last-child {{
                border-right: 0 !important;
            }}
            body.o_body_pdf .invoice_main_table thead th:first-child {{
                border-top-left-radius: 7px !important;
            }}
            body.o_body_pdf .invoice_main_table thead th:last-child {{
                border-top-right-radius: 7px !important;
            }}
            /* Prevent left-edge clipping in first column for both SO and Invoice tables */
            body.o_body_pdf .sale_main_table th:first-child,
            body.o_body_pdf .sale_main_table td:first-child,
            body.o_body_pdf .invoice_main_table th:first-child,
            body.o_body_pdf .invoice_main_table td:first-child {{
                padding-left: 2mm !important;
            }}
            /* Fix first-letter clipping on document titles (e.g., Quotation/Invoice) */
            body.o_body_pdf .article h2,
            body.o_body_pdf .article .o_folder_title,
            body.o_body_pdf .invoice_main .page h2 {{
                padding-left: 2mm !important;
                margin-left: 0 !important;
                overflow: visible !important;
                text-indent: 0 !important;
            }}
            /* Footer line above contact info should not appear */
            .o_weasy_running_footer .o_footer_content,
            .o_weasy_running_footer .border-top {{
                border-top: 0 !important;
            }}
            /* WeasyPrint does not fill span.page/topage by JS; use CSS counters */
            .o_weasy_running_footer .page::before {{
                content: counter(page);
            }}
            .o_weasy_running_footer .topage::before {{
                content: counter(pages);
            }}
            /* Keep totals block clean and detached from the line table */
            body.o_body_pdf #total {{
                margin-top: 2mm !important;
            }}
            body.o_body_pdf #total .o_total_table {{
                border-collapse: separate !important;
                border-spacing: 0 !important;
                border: 0.30mm solid #111 !important;
                border-radius: 8px !important;
                overflow: hidden !important;
            }}
            body.o_body_pdf #total .o_total_table tr:first-child td:first-child {{
                border-top-left-radius: 8px !important;
            }}
            body.o_body_pdf #total .o_total_table tr:first-child td:last-child {{
                border-top-right-radius: 8px !important;
            }}
            body.o_body_pdf #total .o_total_table tr:last-child td:first-child {{
                border-bottom-left-radius: 8px !important;
            }}
            body.o_body_pdf #total .o_total_table tr:last-child td:last-child {{
                border-bottom-right-radius: 8px !important;
            }}
            body.o_body_pdf, body.o_body_pdf table {{
                line-height: 1.55 !important;
            }}
            /* Overall smaller report text (~3px below default) */
            body.o_body_pdf,
            body.o_body_pdf table,
            body.o_body_pdf td,
            body.o_body_pdf th,
            body.o_body_pdf div,
            body.o_body_pdf span,
            body.o_body_pdf p,
            body.o_body_pdf address,
            body.o_body_pdf strong,
            body.o_body_pdf b,
            body.o_body_pdf i,
            body.o_body_pdf em,
            body.o_body_pdf small,
            body.o_body_pdf .page,
            body.o_body_pdf article,
            body.o_body_pdf .o_report_layout,
            .o_weasy_running_header,
            .o_weasy_running_header table,
            .o_weasy_running_header td,
            .o_weasy_running_header th,
            .o_weasy_running_header div,
            .o_weasy_running_header span,
            .o_weasy_running_header p,
            .o_weasy_running_footer,
            .o_weasy_running_footer table,
            .o_weasy_running_footer td,
            .o_weasy_running_footer th,
            .o_weasy_running_footer div,
            .o_weasy_running_footer span,
            .o_weasy_running_footer p {{
                font-size: {REPORT_FONT_SIZE_PX}px !important;
            }}
            body.o_body_pdf h1 {{
                font-size: {REPORT_FONT_SIZE_PX + 6}px !important;
            }}
            body.o_body_pdf h2 {{
                font-size: {REPORT_FONT_SIZE_PX + 2}px !important;
            }}
            body.o_body_pdf h3,
            body.o_body_pdf h4,
            body.o_body_pdf h5,
            body.o_body_pdf h6 {{
                font-size: {REPORT_FONT_SIZE_PX + 1}px !important;
            }}
            body, table, td, th, div, span, p, h1, h2, h3, h4, h5, h6,
            address, strong, b, i, em, small, .page, article,
            .o_report_layout, .article, .o_weasy_running_header, .o_weasy_running_footer {{
                font-family: 'Noto Sans Myanmar', 'Padauk', 'Lato', 'DejaVu Sans', 'FreeSans', sans-serif !important;
            }}
        '''
        return base

    def _render_weasyprint_pdf(
            self,
            bodies,
            header=None,
            footer=None,
            report_ref=False,
            specific_paperformat_args=None,
            landscape=False,
    ):
        """Render HTML to PDF using WeasyPrint with proper Odoo styling."""
        try:
            from weasyprint import CSS, HTML
            from weasyprint.text.fonts import FontConfiguration
        except ImportError:
            _logger.error("WeasyPrint not installed. Run: pip install weasyprint")
            return None

        font_config = FontConfiguration()
        base_url = self._get_weasyprint_base_url()
        paperformat_id = self._get_report(report_ref).get_paperformat() if report_ref else self.get_paperformat()

        pdf_files = []

        for page_index, body in enumerate(bodies):
            try:
                h, f = header, footer
                if header or footer:
                    h, f = self._weasyprint_subst_header_footer(header, footer, page_index)

                processed_body = body
                has_rh, has_rf = False, False
                if h or f:
                    processed_body, has_rh, has_rf = self._merge_header_footer_into_body(body, h, f)

                if len(processed_body) >= 4 * 1024 * 1024:
                    tree = lxml.html.fromstring(processed_body)
                    _split_table(tree, 500)
                    processed_body = lxml.html.tostring(tree, encoding='unicode')

                processed_body = self._sanitize_html_for_weasyprint(processed_body)

                css_string = self._build_weasyprint_stylesheet_string(
                    paperformat_id,
                    specific_paperformat_args,
                    landscape,
                    has_rh,
                    has_rf,
                )
                myanmar_font_css = CSS(string=css_string, font_config=font_config)

                html_doc = HTML(string=processed_body, base_url=base_url)
                pdf_bytes = html_doc.write_pdf(
                    stylesheets=[myanmar_font_css],
                    font_config=font_config,
                )
                pdf_files.append(io.BytesIO(pdf_bytes))

            except Exception as e:
                _logger.error("WeasyPrint rendering error for body: %s", e)
                import traceback
                _logger.error(traceback.format_exc())
                return None

        if not pdf_files:
            return None

        if len(pdf_files) == 1:
            return pdf_files[0].getvalue()

        try:
            from PyPDF2 import PdfFileReader, PdfFileWriter
            writer = PdfFileWriter()
            for pdf_file in pdf_files:
                reader = PdfFileReader(pdf_file)
                for page_num in range(reader.getNumPages()):
                    writer.addPage(reader.getPage(page_num))
            output = io.BytesIO()
            writer.write(output)
            return output.getvalue()
        except Exception as e:
            _logger.error("PDF merge error: %s", e)
            return pdf_files[0].getvalue()

    @api.model
    def _run_wkhtmltopdf(
            self,
            bodies,
            report_ref=False,
            header=None,
            footer=None,
            landscape=False,
            specific_paperformat_args=None,
            set_viewport_size=False):
        """Use WeasyPrint for Myanmar text, wkhtmltopdf for others."""

        has_myanmar = any(_has_myanmar_text(b) for b in bodies)
        if not has_myanmar and header:
            has_myanmar = _has_myanmar_text(header)
        if not has_myanmar and footer:
            has_myanmar = _has_myanmar_text(footer)

        if has_myanmar:
            _logger.info("Myanmar text detected - using WeasyPrint for proper Unicode rendering")

            try:
                pdf_content = self._render_weasyprint_pdf(
                    bodies,
                    header=header,
                    footer=footer,
                    report_ref=report_ref,
                    specific_paperformat_args=specific_paperformat_args,
                    landscape=landscape,
                )
                if pdf_content:
                    return pdf_content
                _logger.warning("WeasyPrint rendering failed, falling back to wkhtmltopdf")
            except Exception as e:
                _logger.warning("WeasyPrint error, falling back to wkhtmltopdf: %s", e)
                import traceback
                _logger.warning(traceback.format_exc())

        return super()._run_wkhtmltopdf(
            bodies,
            report_ref=report_ref,
            header=header,
            footer=footer,
            landscape=landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )
