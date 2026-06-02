# -*- coding: utf-8 -*-
"""
WeasyPrint PDF renderer for Myanmar text support.

wkhtmltopdf cannot properly render Myanmar Unicode due to missing HarfBuzz support.
WeasyPrint has proper complex text shaping and renders Myanmar correctly.
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

REPORT_FONT_SIZE_PX = 14

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
        """Mimic wkhtmltopdf minimal_layout subst()."""
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
        """Fix Odoo HTML that causes WeasyPrint clipping issues."""
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
        """Insert Odoo PDF header/footer for WeasyPrint running elements."""
        header_content = ''
        footer_content = ''

        if header:
            match = re.search(r'<body[^>]*>(.*?)</body>', header, re.DOTALL | re.IGNORECASE)
            if match:
                header_content = match.group(1).strip()
            else:
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
            body = re.sub(r'(<body[^>]*>)', _after_open_body_for_footer, body, count=1, flags=re.IGNORECASE)

        return body, bool(header_content), bool(footer_content)

    def _weasyprint_margins_mm(self, paperformat_id, specific_paperformat_args,
                               has_running_header=False, has_running_footer=False):
        """Calculate margins matching Odoo wkhtmltopdf."""
        args = specific_paperformat_args or {}
        mt = float(args.get('data-report-margin-top') or (paperformat_id.margin_top if paperformat_id else 40))
        mb = float(args.get('data-report-margin-bottom') or (paperformat_id.margin_bottom if paperformat_id else 20))
        ml = float(paperformat_id.margin_left if paperformat_id else 7)
        mr = float(paperformat_id.margin_right if paperformat_id else 7)
        mlr = max(ml, mr)
        if has_running_header:
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

    def _build_weasyprint_stylesheet_string(self, paperformat_id, specific_paperformat_args,
                                            landscape, has_running_header, has_running_footer):
        mt, mb, mlr = self._weasyprint_margins_mm(
            paperformat_id, specific_paperformat_args, has_running_header, has_running_footer)
        size = self._weasyprint_page_size_css(paperformat_id, landscape)

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
            .o_weasy_running_footer .page::before {{
                content: counter(page);
            }}
            .o_weasy_running_footer .topage::before {{
                content: counter(pages);
            }}
            body.o_body_pdf.container {{
                max-width: none !important;
                width: 100% !important;
                box-sizing: border-box !important;
                padding-left: 11mm !important;
                padding-right: 11mm !important;
                padding-top: 0 !important;
            }}
            body.o_body_pdf td, body.o_body_pdf th {{
                overflow: visible !important;
            }}
            body.o_body_pdf, body.o_body_pdf table {{
                line-height: 1.55 !important;
            }}
            /* Hongsar report styles */
            .hongsar-report-wrap,
            .hongsar-report-wrap table,
            .hongsar-report-wrap td,
            .hongsar-report-wrap th,
            .hongsar-report-wrap div,
            .hongsar-report-wrap span,
            .hongsar-report-wrap p,
            .hongsar-invoice-wrap,
            .hongsar-invoice-wrap table,
            .hongsar-invoice-wrap td,
            .hongsar-invoice-wrap th,
            .hongsar-invoice-wrap div,
            .hongsar-invoice-wrap span,
            .hongsar-invoice-wrap p {{
                font-size: {REPORT_FONT_SIZE_PX}px !important;
            }}
            body, table, td, th, div, span, p, h1, h2, h3, h4, h5, h6,
            address, strong, b, i, em, small, .page, article,
            .o_report_layout, .article, .o_weasy_running_header, .o_weasy_running_footer,
            .hongsar-report-wrap, .hongsar-report-wrap *,
            .hongsar-invoice-wrap, .hongsar-invoice-wrap * {{
                font-family: 'Noto Sans Myanmar', 'Pyidaungsu', 'Padauk', 'Lato', 'DejaVu Sans', sans-serif !important;
            }}
        '''
        return base

    def _render_weasyprint_pdf(self, bodies, header=None, footer=None, report_ref=False,
                               specific_paperformat_args=None, landscape=False):
        """Render HTML to PDF using WeasyPrint."""
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
                    paperformat_id, specific_paperformat_args, landscape, has_rh, has_rf)
                myanmar_font_css = CSS(string=css_string, font_config=font_config)

                html_doc = HTML(string=processed_body, base_url=base_url)
                pdf_bytes = html_doc.write_pdf(stylesheets=[myanmar_font_css], font_config=font_config)
                pdf_files.append(io.BytesIO(pdf_bytes))

            except Exception as e:
                _logger.error("WeasyPrint rendering error: %s", e)
                import traceback
                _logger.error(traceback.format_exc())
                return None

        if not pdf_files:
            return None

        if len(pdf_files) == 1:
            return pdf_files[0].getvalue()

        try:
            from PyPDF2 import PdfReader, PdfWriter
            writer = PdfWriter()
            for pdf_file in pdf_files:
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    writer.add_page(page)
            output = io.BytesIO()
            writer.write(output)
            return output.getvalue()
        except Exception as e:
            _logger.error("PDF merge error: %s", e)
            return pdf_files[0].getvalue()

    @api.model
    def _build_wkhtmltopdf_args(self, paperformat_id, landscape, specific_paperformat_args=None, set_viewport_size=False):
        """Override to ensure utf-8 encoding is always used by wkhtmltopdf."""
        args = super()._build_wkhtmltopdf_args(
            paperformat_id, landscape, specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size)
        if '--encoding' not in args:
            args.extend(['--encoding', 'utf-8'])
        return args

    @api.model
    def _run_wkhtmltopdf(self, bodies, report_ref=False, header=None, footer=None,
                         landscape=False, specific_paperformat_args=None, set_viewport_size=False):
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
                    bodies, header=header, footer=footer, report_ref=report_ref,
                    specific_paperformat_args=specific_paperformat_args, landscape=landscape)
                if pdf_content:
                    return pdf_content
                _logger.warning("WeasyPrint rendering failed, falling back to wkhtmltopdf")
            except Exception as e:
                _logger.warning("WeasyPrint error, falling back to wkhtmltopdf: %s", e)

        return super()._run_wkhtmltopdf(
            bodies, report_ref=report_ref, header=header, footer=footer,
            landscape=landscape, specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size)
