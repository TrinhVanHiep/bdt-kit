#!/usr/bin/env python3
"""bdt-kit docfill: read, inspect and fill .docx / .xlsx / .md / .csv templates with the standard library only.

Usage:
  docfill.py text    <file>                     plain text of a document or workbook (for reading inputs)
  docfill.py inspect <template>                 JSON: structure, placeholders, tables and header rows
  docfill.py fill    <template> <data.json> <out>
  docfill.py build   <sample.docx> <content.json> <out>   new document in the sample's look (see docx_build)
  docfill.py check   <file>                     JSON: placeholders left over after a fill (exit 1 if any)
  docfill.py results <sheet.xlsx|csv> <results.json> <out>   write test results into existing rows matched by ID

Template conventions (docx and xlsx):
  {{key}}            replaced by data["key"] (newlines become line breaks in docx)
  {{list.field}}     in a table row (docx) or a sheet row (xlsx): the row is repeated for each item of data["list"]
  {{list[]}}         alone in a paragraph (docx): the paragraph is repeated for each string in data["list"]
xlsx without placeholders: data["sheets"][name] = {"header_row": N (optional), "rows": [{"<column header>": value}]}
appends rows under the header, copying the style of the first data row.
results: {"sheet": name (xlsx, optional), "header_row": N or "header_rows": [top, bottom] (optional), "id_column": "ID" (default),
"rows": [{"ID": "TC-001", "<column header>": value}]} sets only the named cells of the row with that ID;
every other cell, style and formula is kept, and the input file is never overwritten.
"""

import copy
import csv
import os
import io
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG_R = 'http://schemas.openxmlformats.org/package/2006/relationships'
PLACEHOLDER = re.compile(r'\{\{\s*([^{}]+?)\s*\}\}')
LIST_FIELD = re.compile(r'^([A-Za-z0-9_\-]+)\.([^\[\]]+)$')
LIST_ITEM = re.compile(r'^([A-Za-z0-9_\-]+)\[\]$')


def w(tag):
    return f'{{{W}}}{tag}'


def s(tag):
    return f'{{{S}}}{tag}'


def register_namespaces(xml_bytes):
    # Keep the original prefixes (w:, r:, mc:, …) so Word accepts the rewritten part.
    for _, (prefix, uri) in ET.iterparse(io.BytesIO(xml_bytes), events=['start-ns']):
        if not re.fullmatch(r'ns\d+', prefix):
            ET.register_namespace(prefix, uri)


ROOT_TAG = re.compile(rb'<(?![?!])[^>]*>')
ORIGINAL_ROOT = {}


def parse(xml_bytes):
    register_namespaces(xml_bytes)
    root = ET.fromstring(xml_bytes)
    match = ROOT_TAG.search(xml_bytes)
    if match:
        ORIGINAL_ROOT[id(root)] = match.group(0)
    return root


def serialize(root):
    body = ET.tostring(root, encoding='unicode').encode('utf-8')
    original = ORIGINAL_ROOT.get(id(root))
    if original:
        # ElementTree drops namespace declarations it does not see used (for example the prefixes listed in
        # mc:Ignorable), which makes Word and Excel report the file as damaged; keep the original root tag.
        current = ROOT_TAG.search(body).group(0)
        declared = set(re.findall(rb'xmlns(?::[\w.-]+)?=', original))
        added = [d for d in re.findall(rb'\sxmlns(?::[\w.-]+)?="[^"]*"', current)
                 if re.match(rb'\s(xmlns(?::[\w.-]+)?=)', d).group(1) not in declared]
        merged = original[:-1].rstrip(b'/') + b''.join(added) + (b'/>' if original.endswith(b'/>') else b'>')
        body = ROOT_TAG.sub(lambda _: merged, body, count=1)
    return b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + body


def lookup(data, key):
    value = data
    for part in key.split('.'):
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return None
    return value


# ---------- docx ----------

def paragraph_text(p):
    return ''.join(t.text or '' for t in p.iter(w('t')))


def paragraph_style(p):
    style = p.find(f'{w("pPr")}/{w("pStyle")}')
    return style.get(w('val')) if style is not None else ''


def merge_runs(p):
    """Put the paragraph text into its first text run so a placeholder split across runs can be replaced."""
    texts = list(p.iter(w('t')))
    if len(texts) < 2 or not PLACEHOLDER.search(paragraph_text(p)):
        return
    texts[0].text = paragraph_text(p)
    texts[0].set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    for t in texts[1:]:
        t.text = ''


def set_paragraph_text(p, value):
    texts = list(p.iter(w('t')))
    if not texts:
        return
    first = texts[0]
    for t in texts[1:]:
        t.text = ''
    lines = str(value).split('\n')
    first.text = lines[0]
    first.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    run = next(r for r in p.iter(w('r')) if first in list(r))
    anchor = first
    for line in lines[1:]:
        br = ET.Element(w('br'))
        t = ET.Element(w('t'))
        t.text = line
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        index = list(run).index(anchor)
        run.insert(index + 1, br)
        run.insert(index + 2, t)
        anchor = t


def replace_in_paragraph(p, resolve):
    merge_runs(p)
    text = paragraph_text(p)
    if not PLACEHOLDER.search(text):
        return
    set_paragraph_text(p, PLACEHOLDER.sub(lambda m: resolve(m.group(1), m.group(0)), text))


def scalar_resolver(data):
    def resolve(key, original):
        value = lookup(data, key)
        if value is None or isinstance(value, (list, dict)):
            return original
        return str(value)
    return resolve


def expand_table_rows(root, data):
    for table in root.iter(w('tbl')):
        for row in list(table.findall(w('tr'))):
            keys = PLACEHOLDER.findall(''.join(paragraph_text(p) for p in row.iter(w('p'))))
            lists = {LIST_FIELD.match(k).group(1) for k in keys if LIST_FIELD.match(k)}
            lists = {name for name in lists if isinstance(data.get(name), list)}
            if not lists:
                continue
            name = sorted(lists)[0]
            index = list(table).index(row)
            table.remove(row)
            for offset, item in enumerate(data[name]):
                clone = copy.deepcopy(row)
                scoped = {**data, name: item}
                for p in clone.iter(w('p')):
                    replace_in_paragraph(p, scalar_resolver(scoped))
                table.insert(index + offset, clone)


def expand_list_paragraphs(root, data):
    for parent in root.iter():
        for p in list(parent.findall(w('p'))):
            match = LIST_ITEM.match(paragraph_text(p).strip().strip('{}').strip())
            if not match or not PLACEHOLDER.fullmatch(paragraph_text(p).strip()):
                continue
            items = data.get(match.group(1))
            if not isinstance(items, list):
                continue
            index = list(parent).index(p)
            parent.remove(p)
            for offset, item in enumerate(items):
                clone = copy.deepcopy(p)
                set_paragraph_text(clone, item)
                parent.insert(index + offset, clone)


def docx_parts(names):
    return [n for n in names if re.match(r'word/(document|header\d*|footer\d*)\.xml$', n)]


def docx_fill(template, data, out):
    with zipfile.ZipFile(template) as zin, zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zout:
        parts = docx_parts(zin.namelist())
        for item in zin.infolist():
            content = zin.read(item.filename)
            if item.filename in parts:
                root = parse(content)
                for p in root.iter(w('p')):
                    merge_runs(p)
                expand_table_rows(root, data)
                expand_list_paragraphs(root, data)
                for p in root.iter(w('p')):
                    replace_in_paragraph(p, scalar_resolver(data))
                content = serialize(root)
            zout.writestr(item, content)


def docx_blocks(path):
    with zipfile.ZipFile(path) as z:
        root = parse(z.read('word/document.xml'))
    body = root.find(w('body'))
    for el in body:
        if el.tag == w('p'):
            yield 'p', paragraph_style(el), paragraph_text(el)
        elif el.tag == w('tbl'):
            rows = [[' / '.join(paragraph_text(p) for p in cell.iter(w('p'))) for cell in tr.findall(w('tc'))]
                    for tr in el.findall(w('tr'))]
            yield 'table', '', rows


def docx_text(path):
    lines = []
    for kind, style, value in docx_blocks(path):
        if kind == 'p':
            prefix = '#' * int(re.sub(r'\D', '', style) or 1) + ' ' if re.search(r'heading|見出し', style, re.I) else ''
            lines.append(prefix + value)
        else:
            lines.extend('| ' + ' | '.join(row) + ' |' for row in value)
    return '\n'.join(lines)


def docx_inspect(path):
    headings, tables, placeholders = [], [], set()
    with zipfile.ZipFile(path) as z:
        for part in docx_parts(z.namelist()):
            placeholders.update(PLACEHOLDER.findall(''.join(t.text or '' for t in parse(z.read(part)).iter(w('t')))))
    for kind, style, value in docx_blocks(path):
        if kind == 'p' and re.search(r'heading|見出し|title', style, re.I):
            headings.append({'style': style, 'text': value})
        elif kind == 'table':
            tables.append({'columns': value[0] if value else [], 'rows': len(value),
                           'row_template': next((r for r in value if PLACEHOLDER.search(' '.join(r))), None)})
    return {'format': 'docx', 'headings': headings, 'tables': tables, 'placeholders': sorted(placeholders),
            'blocks': docx_block_summary(path)}


def run_format(p):
    rpr = p.find(f'.//{w("r")}/{w("rPr")}')
    if rpr is None:
        return ''
    marks = []
    if rpr.find(w('b')) is not None:
        marks.append('bold')
    if rpr.find(w('i')) is not None:
        marks.append('italic')
    size = rpr.find(w('sz'))
    if size is not None:
        marks.append(f'{int(size.get(w("val"))) / 2:g}pt')
    color = rpr.find(w('color'))
    if color is not None and color.get(w('val')) not in (None, 'auto', '000000'):
        marks.append('#' + color.get(w('val')))
    return ' '.join(marks)


def docx_block_summary(path, limit=120):
    """Every top-level block with its index, so `build` can name prototypes: {"heading": 7, "body": 8}."""
    with zipfile.ZipFile(path) as z:
        body = parse(z.read('word/document.xml')).find(w('body'))
    out = []
    for index, el in enumerate(body):
        if el.tag == w('p'):
            entry = {'index': index, 'type': 'p', 'style': paragraph_style(el), 'format': run_format(el),
                     'text': paragraph_text(el)[:80]}
            if el.find(f'{w("pPr")}/{w("numPr")}') is not None:
                entry['list'] = True
            if el.find(f'.//{w("drawing")}') is not None:
                entry['image'] = True
            out.append(entry)
        elif el.tag == w('tbl'):
            first = el.find(w('tr'))
            out.append({'index': index, 'type': 'table',
                        'columns': [' '.join(paragraph_text(p) for p in tc.iter(w('p'))) for tc in first.findall(w('tc'))] if first is not None else []})
        if len(out) >= limit:
            break
    return out


# ---------- docx build (new document in the sample's look) ----------

EMU_PER_PX = 9525
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
PIC = 'http://schemas.openxmlformats.org/drawingml/2006/picture'
# Word's usual prefixes, so parts written here never get ElementTree's ns0/ns1 names.
for _prefix, _uri in (('wp', WP), ('a', A), ('pic', PIC), ('r', R)):
    ET.register_namespace(_prefix, _uri)


def png_size(data):
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return int.from_bytes(data[16:20], 'big'), int.from_bytes(data[20:24], 'big')
    if data[:2] == b'\xff\xd8':  # JPEG: walk the segments to the SOF marker
        i = 2
        while i < len(data):
            marker, length = data[i + 1], int.from_bytes(data[i + 2:i + 4], 'big')
            if marker in (0xC0, 0xC1, 0xC2):
                return int.from_bytes(data[i + 7:i + 9], 'big'), int.from_bytes(data[i + 5:i + 7], 'big')
            i += 2 + length
    raise SystemExit('Images must be PNG or JPEG.')


def text_page_width_emu(body):
    sect = body.find(w('sectPr'))
    size = sect.find(w('pgSz')) if sect is not None else None
    margin = sect.find(w('pgMar')) if sect is not None else None
    if size is None or margin is None:
        return 5486400
    twips = int(size.get(w('w'))) - int(margin.get(w('left'), 1440)) - int(margin.get(w('right'), 1440))
    return twips * 635


def image_paragraph(prototype, rel_id, cx, cy, number, name):
    p = copy.deepcopy(prototype)
    for child in [c for c in p if c.tag != w('pPr')]:
        p.remove(child)
    run = ET.SubElement(p, w('r'))
    drawing = ET.SubElement(run, w('drawing'))
    inline = ET.SubElement(drawing, f'{{{WP}}}inline', {'distT': '0', 'distB': '0', 'distL': '0', 'distR': '0'})
    ET.SubElement(inline, f'{{{WP}}}extent', {'cx': str(cx), 'cy': str(cy)})
    ET.SubElement(inline, f'{{{WP}}}docPr', {'id': str(number), 'name': name})
    graphic = ET.SubElement(inline, f'{{{A}}}graphic')
    data = ET.SubElement(graphic, f'{{{A}}}graphicData', {'uri': PIC})
    pic = ET.SubElement(data, f'{{{PIC}}}pic')
    nv = ET.SubElement(pic, f'{{{PIC}}}nvPicPr')
    ET.SubElement(nv, f'{{{PIC}}}cNvPr', {'id': str(number), 'name': name})
    ET.SubElement(nv, f'{{{PIC}}}cNvPicPr')
    fill = ET.SubElement(pic, f'{{{PIC}}}blipFill')
    ET.SubElement(fill, f'{{{A}}}blip', {f'{{{R}}}embed': rel_id})
    stretch = ET.SubElement(fill, f'{{{A}}}stretch')
    ET.SubElement(stretch, f'{{{A}}}fillRect')
    sp = ET.SubElement(pic, f'{{{PIC}}}spPr')
    xfrm = ET.SubElement(sp, f'{{{A}}}xfrm')
    ET.SubElement(xfrm, f'{{{A}}}off', {'x': '0', 'y': '0'})
    ET.SubElement(xfrm, f'{{{A}}}ext', {'cx': str(cx), 'cy': str(cy)})
    geom = ET.SubElement(sp, f'{{{A}}}prstGeom', {'prst': 'rect'})
    ET.SubElement(geom, f'{{{A}}}avLst')
    return p


def table_from_prototype(prototype, rows):
    table = copy.deepcopy(prototype)
    template_rows = table.findall(w('tr'))
    header, body = template_rows[0], (template_rows[1] if len(template_rows) > 1 else template_rows[0])
    for tr in template_rows:
        table.remove(tr)
    for number, values in enumerate(rows):
        tr = copy.deepcopy(header if number == 0 else body)
        cells = tr.findall(w('tc'))
        for cell, value in zip(cells, values + [''] * (len(cells) - len(values))):
            paragraphs = cell.findall(w('p'))
            for extra in paragraphs[1:]:
                cell.remove(extra)
            first = paragraphs[0]
            if not list(first.iter(w('t'))):
                ET.SubElement(ET.SubElement(first, w('r')), w('t'))
            set_paragraph_text(first, value)
        table.append(tr)
    return table


def docx_build(sample, content, out):
    """content = {"prototypes": {"<role>": <block index from inspect>}, "blocks": [{"role": "...", "text": "..."},
    {"role": "<table role>", "rows": [[...], ...]}, {"role": "<image role>", "image": "path.png", "width_ratio": 0.9}]}"""
    with zipfile.ZipFile(sample) as zin:
        names = zin.namelist()
        root = parse(zin.read('word/document.xml'))
        rels_root = parse(zin.read('word/_rels/document.xml.rels'))
        content_types = zin.read('[Content_Types].xml')
        body = root.find(w('body'))
        blocks = list(body)
        prototypes = {role: blocks[index] for role, index in content['prototypes'].items()}
        sect = body.find(w('sectPr'))
        for el in list(body):
            if el is not sect:
                body.remove(el)
        media = {}
        width_limit = text_page_width_emu(root.find(w('body')) if sect is None else body)
        next_id = max([int(re.sub(r'\D', '', r.get('Id')) or 0) for r in rels_root] + [0]) + 1
        insert_at = 0
        for number, block in enumerate(content['blocks'], start=1):
            proto = prototypes.get(block['role'])
            if proto is None:
                raise SystemExit(f'No prototype for role {block["role"]!r}; known: {sorted(prototypes)}')
            if 'image' in block:
                data = open(block['image'], 'rb').read()
                px_w, px_h = png_size(data)
                cx = min(int(px_w * EMU_PER_PX), int(width_limit * block.get('width_ratio', 1.0)))
                cy = int(cx * px_h / px_w)
                ext = 'png' if data[:4] == b'\x89PNG' else 'jpeg'
                target = f'media/bdt_image{number}.{ext}'
                rel_id = f'rId{next_id}'
                next_id += 1
                ET.SubElement(rels_root, f'{{{PKG_R}}}Relationship', {
                    'Id': rel_id, 'Target': target,
                    'Type': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'})
                media['word/' + target] = data
                el = image_paragraph(proto, rel_id, cx, cy, 1000 + number, os.path.basename(block['image']))
            elif 'rows' in block:
                el = table_from_prototype(proto, block['rows'])
            else:
                el = copy.deepcopy(proto)
                for run in [r for r in el.findall(w('r')) if r.find(w('drawing')) is not None]:
                    el.remove(run)
                if not list(el.iter(w('t'))):
                    ET.SubElement(ET.SubElement(el, w('r')), w('t'))
                set_paragraph_text(el, block.get('text', ''))
            body.insert(insert_at, el)
            insert_at += 1
        for ext, mime in (('png', 'image/png'), ('jpeg', 'image/jpeg')):
            if any(k.endswith(ext) for k in media) and f'Extension="{ext}"'.encode() not in content_types:
                content_types = content_types.replace(b'</Types>', f'<Default Extension="{ext}" ContentType="{mime}"/></Types>'.encode())
        with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == 'word/document.xml':
                    zout.writestr(item, serialize(root))
                elif item.filename == 'word/_rels/document.xml.rels':
                    zout.writestr(item, serialize(rels_root))
                elif item.filename == '[Content_Types].xml':
                    zout.writestr(item, content_types)
                else:
                    zout.writestr(item, zin.read(item.filename))
            for name, data in media.items():
                zout.writestr(name, data)
    prune_docx_parts(out)


# ---------- cleaning: nothing of the sample's own content may ship in the output ----------

CP = 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties'
DC = 'http://purl.org/dc/elements/1.1/'


def rewrite_zip(path, transform):
    """transform(name, bytes, names) -> bytes, or None to drop the part."""
    tmp = path + '.tmp'
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        names = zin.namelist()
        for item in zin.infolist():
            content = transform(item.filename, zin.read(item.filename), names)
            if content is not None:
                zout.writestr(item, content)
    os.replace(tmp, path)


def clean_core_properties(name, content):
    """Title, subject, keywords and description describe the sample, not the new document."""
    if name != 'docProps/core.xml':
        return content
    for tag in (f'{{{DC}}}title', f'{{{DC}}}subject', f'{{{CP}}}keywords', f'{{{DC}}}description'):
        content = re.sub(rb'<(\w+:)?' + tag.split('}')[1].encode() + rb'>[^<]*</(\w+:)?' + tag.split('}')[1].encode() + rb'>', b'', content)
    return content


def prune_shared_strings(path):
    """Keep only the shared strings the remaining cells use, so cleared sample rows leave no text behind."""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if 'xl/sharedStrings.xml' not in names:
            return
        sheets = [n for n in names if re.match(r'xl/worksheets/sheet\d+\.xml$', n)]
        used = set()
        for n in sheets:
            used.update(int(m) for m in re.findall(rb'<c [^>]*t="s"[^>]*>\s*<v>(\d+)</v>', z.read(n)))
        sst = parse(z.read('xl/sharedStrings.xml'))
    items = sst.findall(s('si'))
    order = sorted(used)
    remap = {old: new for new, old in enumerate(order)}
    for index, si in enumerate(items):
        if index not in remap:
            sst.remove(si)
    sst.set('count', str(len(order)))
    sst.set('uniqueCount', str(len(order)))
    new_sst = serialize(sst)

    def transform(name, content, _names):
        if name == 'xl/sharedStrings.xml':
            return new_sst
        if name in sheets:
            return re.sub(rb'(<c [^>]*t="s"[^>]*>\s*<v>)(\d+)(</v>)',
                          lambda m: m.group(1) + str(remap[int(m.group(2))]).encode() + m.group(3), content)
        return clean_core_properties(name, content)
    rewrite_zip(path, transform)


def prune_docx_parts(path):
    """Drop relationships and media the rebuilt body no longer references (for example the sample's screenshots)."""
    with zipfile.ZipFile(path) as z:
        doc = z.read('word/document.xml')
        rels = parse(z.read('word/_rels/document.xml.rels'))
    referenced = set(re.findall(rb'r:(?:embed|id|link|pict)="([^"]+)"', doc))
    removable = ('/image', '/hyperlink', '/oleObject', '/package', '/chart')
    dropped_targets = set()
    for rel in list(rels):
        if rel.get('Type', '').endswith(removable) and rel.get('Id').encode() not in referenced:
            if rel.get('TargetMode') != 'External':
                dropped_targets.add('word/' + rel.get('Target').lstrip('/').replace('word/', '', 1))
            rels.remove(rel)
    new_rels = serialize(rels)

    def transform(name, content, _names):
        if name in dropped_targets:
            return None
        if name == 'word/_rels/document.xml.rels':
            return new_rels
        if name == '[Content_Types].xml':
            for target in dropped_targets:
                content = re.sub(rb'<Override PartName="/' + re.escape(target.encode()) + rb'"[^>]*/>', b'', content)
            return content
        return clean_core_properties(name, content)
    rewrite_zip(path, transform)


# ---------- xlsx ----------

def col_index(ref):
    letters = re.match(r'[A-Z]+', ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n


def col_letter(n):
    out = ''
    while n:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out


def string_item_text(item):
    """Text of a shared or inline string: its <t> and rich-text runs, without phonetic guides (<rPh>, furigana)."""
    if item is None:
        return ''
    parts = [item.find(s('t'))] + [r.find(s('t')) for r in item.findall(s('r'))]
    return ''.join(t.text or '' for t in parts if t is not None)


class Workbook:
    def __init__(self, path):
        self.zip = zipfile.ZipFile(path)
        names = self.zip.namelist()
        self.shared = []
        if 'xl/sharedStrings.xml' in names:
            for si in parse(self.zip.read('xl/sharedStrings.xml')).findall(s('si')):
                self.shared.append(string_item_text(si))
        rels = parse(self.zip.read('xl/_rels/workbook.xml.rels'))
        targets = {r.get('Id'): r.get('Target') for r in rels}
        workbook = parse(self.zip.read('xl/workbook.xml'))
        self.sheets = []
        for sheet in workbook.iter(s('sheet')):
            target = targets[sheet.get(f'{{{R}}}id')].lstrip('/')
            self.sheets.append((sheet.get('name'), target if target.startswith('xl/') else 'xl/' + target))

    def cell_value(self, c):
        kind = c.get('t')
        if kind == 'inlineStr':
            return string_item_text(c.find(s('is')))
        v = c.find(s('v'))
        if v is None:
            return ''
        return self.shared[int(v.text)] if kind == 's' else v.text or ''

    def rows(self, part, root=None):
        root = root if root is not None else parse(self.zip.read(part))
        result = []
        for row in root.iter(s('row')):
            cells = {col_index(c.get('r')): self.cell_value(c) for c in row.findall(s('c'))}
            result.append((int(row.get('r')), cells))
        return result


def header_row(rows):
    best = None
    for number, cells in rows[:30]:
        filled = [v for v in cells.values() if v and not PLACEHOLDER.search(v)]
        if len(filled) >= 2 and (best is None or len(filled) > best[1]):
            best = (number, len(filled))
    return best[0] if best else None


def inline_cell(ref, value, style):
    c = ET.Element(s('c'), {'r': ref})
    if style:
        c.set('s', style)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        ET.SubElement(c, s('v')).text = str(value)
    else:
        c.set('t', 'inlineStr')
        t = ET.SubElement(ET.SubElement(c, s('is')), s('t'))
        t.text = '' if value is None else str(value)
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    return c


def make_row(number, values_by_col, styles, template_row=None):
    row = copy.deepcopy(template_row) if template_row is not None else ET.Element(s('row'))
    for c in list(row.findall(s('c'))):
        row.remove(c)
    row.set('r', str(number))
    for col in sorted(values_by_col):
        row.append(inline_cell(f'{col_letter(col)}{number}', values_by_col[col], styles.get(col)))
    return row


def xlsx_fill_sheet(book, part, root, spec, data):
    sheet_data = root.find(s('sheetData'))
    # 1. Rows holding {{list.field}} are repeated per item.
    for row_el in list(sheet_data.findall(s('row'))):
        cells = {col_index(c.get('r')): book.cell_value(c) for c in row_el.findall(s('c'))}
        keys = [k for v in cells.values() for k in PLACEHOLDER.findall(v)]
        lists = sorted({LIST_FIELD.match(k).group(1) for k in keys if LIST_FIELD.match(k)} & {k for k, v in data.items() if isinstance(v, list)})
        if not lists:
            continue
        name = lists[0]
        start = int(row_el.get('r'))
        styles = {col_index(c.get('r')): c.get('s') for c in row_el.findall(s('c'))}
        items = data[name]
        shift_rows(sheet_data, start + 1, len(items) - 1)
        index = list(sheet_data).index(row_el)
        sheet_data.remove(row_el)
        for offset, item in enumerate(items):
            scoped = {**data, name: item}
            values = {col: PLACEHOLDER.sub(lambda m: str(lookup(scoped, m.group(1)) if lookup(scoped, m.group(1)) is not None else m.group(0)), v)
                      for col, v in cells.items()}
            sheet_data.insert(index + offset, make_row(start + offset, values, styles, row_el))
    # 2. Scalar placeholders anywhere.
    for row_el in sheet_data.findall(s('row')):
        for c in row_el.findall(s('c')):
            value = book.cell_value(c)
            if PLACEHOLDER.search(value):
                new = PLACEHOLDER.sub(lambda m: str(lookup(data, m.group(1))) if lookup(data, m.group(1)) is not None and not isinstance(lookup(data, m.group(1)), (list, dict)) else m.group(0), value)
                replacement = inline_cell(c.get('r'), new, c.get('s'))
                index = list(row_el).index(c)
                row_el.remove(c)
                row_el.insert(index, replacement)
    # 3. Label/value fields: {"fields": {"<label>": value}} writes the value right of the label cell.
    if spec and spec.get('fields'):
        fill_fields(book, root, spec['fields'])
    # 4. Rows appended under the header by column name.
    if spec and spec.get('rows') is not None:
        write_rows(book, part, root, spec)
    dimension = root.find(s('dimension'))
    if dimension is not None:
        root.remove(dimension)


def merges(root):
    result = []
    block = root.find(s('mergeCells'))
    if block is None:
        return result
    for m in block.findall(s('mergeCell')):
        a, _, b = m.get('ref').partition(':')
        b = b or a
        result.append((col_index(a), int(re.sub(r'\D', '', a)), col_index(b), int(re.sub(r'\D', '', b)), m))
    return result


def header_block(rows, root, forced=None):
    """Header rows and column names; a two-row header with merged parents gives names like "PC / Lần 1"."""
    block = header_names(rows, root, forced)
    if block is None:
        return None
    top, bottom, names = block
    return top, bottom, {name: col for col, name in names.items()}


def header_names(rows, root, forced=None, forced_bottom=None):
    """(top, bottom, {column: name}) of the header; forced_bottom sets a header's last row when detection misses it."""
    top = forced or header_row(rows)
    if top is None:
        return None
    spans = merges(root)
    bottom = forced_bottom or top
    if not forced:
        if any(r1 == top - 1 and r2 >= top for _, r1, _, r2, _ in spans):
            top -= 1
        elif any(r1 == top and r2 > top for _, r1, _, r2, _ in spans):
            bottom = top + 1
    if any(r1 == top and r2 > bottom for _, r1, _, r2, _ in spans):
        bottom = max(r2 for _, r1, _, r2, _ in spans if r1 == top)
    by_number = dict(rows)
    names = {}
    for row in range(top, bottom + 1):
        cells = dict(by_number.get(row, {}))
        for c1, r1, c2, r2, _ in spans:
            if r1 == row and c2 > c1 and cells.get(c1):
                for col in range(c1 + 1, c2 + 1):
                    if not cells.get(col):
                        cells[col] = cells[c1]
        for col, value in cells.items():
            value = (value or '').strip()
            if not value:
                continue
            names[col] = f"{names[col]} / {value}" if col in names and names[col] != value else value
    return top, bottom, {col: name.replace('\n', ' ').strip() for col, name in names.items()}


def fill_fields(book, root, fields):
    spans = merges(root)
    for row_el in root.find(s('sheetData')).findall(s('row')):
        number = int(row_el.get('r'))
        for c in row_el.findall(s('c')):
            label = book.cell_value(c).strip()
            if label not in fields:
                continue
            col = col_index(c.get('r'))
            end = next((c2 for c1, r1, c2, r2, _ in spans if c1 == col and r1 <= number <= r2), col)
            set_cell(row_el, number, end + 1, fields[label], None)


def set_cell(row_el, number, col, value, style):
    ref = f'{col_letter(col)}{number}'
    old = next((c for c in row_el.findall(s('c')) if c.get('r') == ref), None)
    cell = inline_cell(ref, value, style if style is not None else (old.get('s') if old is not None else None))
    if old is not None:
        index = list(row_el).index(old)
        row_el.remove(old)
        row_el.insert(index, cell)
        return
    later = [c for c in row_el.findall(s('c')) if col_index(c.get('r')) > col]
    row_el.insert(list(row_el).index(later[0]) if later else len(row_el), cell)


def column_widths(root):
    widths = {}
    cols = root.find(s('cols'))
    for col in (cols.findall(s('col')) if cols is not None else []):
        for n in range(int(col.get('min')), int(col.get('max')) + 1):
            widths[n] = float(col.get('width', 8.43))
    return widths


def fit_row_height(row, values, widths, line_points=15.0):
    """Height from the text: lines per cell, wrapping at the column width (about one character per width unit)."""
    lines = 1
    for col, value in values.items():
        width = max(widths.get(col, 8.43) * 1.1, 1)
        text = '' if value is None else str(value)
        # Full-width (CJK) characters take about two columns.
        count = sum(max(1, -(-sum(2 if ord(ch) > 0x2E80 else 1 for ch in line) // int(width))) for line in text.split('\n'))
        lines = max(lines, count)
    row.set('ht', str(round(lines * line_points + 4, 1)))
    row.set('customHeight', '1')


def write_rows(book, part, root, spec):
    sheet_data = root.find(s('sheetData'))
    rows = book.rows(part, root)
    block = header_block(rows, root, spec.get('header_row'))
    if block is None:
        raise SystemExit(f'No header row found in sheet {part}; pass "header_row".')
    top, bottom, columns = block
    wanted = {k for r in spec['rows'] for k in r if not k.startswith('_')}
    missing = sorted(wanted - set(columns))
    if missing:
        raise SystemExit(f'Columns not in the template header (rows {top}-{bottom}): {missing}. Header: {list(columns)}')
    width = (min(columns.values()), max(columns.values()))
    spans = merges(root)
    existing = {int(r.get('r')): r for r in sheet_data.findall(s('row'))}
    body = [n for n in sorted(existing) if n > bottom]
    is_section = {n for n in body if any(r1 == n and r2 == n and c2 - c1 + 1 >= (width[1] - width[0] + 1) / 2 for c1, r1, c2, r2, _ in spans)}
    data_template = next((existing[n] for n in body if n not in is_section and any(book.cell_value(c) for c in existing[n].findall(s('c')))), existing.get(bottom + 1))
    section_template = next((existing[n] for n in body if n in is_section), None)
    section_span = next(((c1, c2) for c1, r1, c2, r2, _ in spans if section_template is not None and r1 == int(section_template.get('r'))), None)
    data_styles = {col_index(c.get('r')): c.get('s') for c in data_template.findall(s('c'))} if data_template is not None else {}
    section_styles = {col_index(c.get('r')): c.get('s') for c in section_template.findall(s('c'))} if section_template is not None else {}
    merge_block = root.find(s('mergeCells'))
    widths = column_widths(root)
    if spec.get('clear_existing'):
        for n in body:
            sheet_data.remove(existing[n])
        for c1, r1, c2, r2, m in spans:
            if r1 > bottom:
                merge_block.remove(m)
        start = bottom + 1
    else:
        filled = [n for n in body if any(book.cell_value(c) for c in existing[n].findall(s('c')))]
        start = (filled[-1] if filled else bottom) + 1
        for n in [n for n in body if n >= start]:
            sheet_data.remove(existing[n])
    for offset, item in enumerate(spec['rows']):
        number = start + offset
        if '_section' in item and section_template is not None and section_span:
            first = section_span[0]
            values = {first: item['_section']}
            values.update({col: '' for col in range(first + 1, section_span[1] + 1)})
            row = make_row(number, values, section_styles, section_template)
            ET.SubElement(merge_block, s('mergeCell'), {'ref': f'{col_letter(section_span[0])}{number}:{col_letter(section_span[1])}{number}'})
        else:
            values = {col: '' for col in range(width[0], width[1] + 1)}
            for key, value in item.items():
                if key == '_section':
                    values[width[0] + 1 if width[1] > width[0] else width[0]] = value
                elif not key.startswith('_'):
                    values[columns[key]] = value
            row = make_row(number, values, data_styles, data_template)
            fit_row_height(row, values, widths)
        sheet_data.append(row)
    if merge_block is not None:
        merge_block.set('count', str(len(merge_block.findall(s('mergeCell')))))


def shift_rows(sheet_data, from_row, by):
    if by <= 0:
        return
    for row in sheet_data.findall(s('row')):
        number = int(row.get('r'))
        if number >= from_row:
            row.set('r', str(number + by))
            for c in row.findall(s('c')):
                c.set('r', re.sub(r'\d+$', str(number + by), c.get('r')))


def sheet_selection(book, data):
    """Sheets to drop and names to change: data["keep_sheets"] = [names], data["rename_sheets"] = {old: new}."""
    keep = data.get('keep_sheets')
    names = [name for name, _ in book.sheets]
    if keep:
        unknown = sorted(set(keep) - set(names))
        if unknown:
            raise SystemExit(f'keep_sheets names not in the workbook: {unknown}. Sheets: {names}')
    dropped = {name for name in names if keep and name not in keep}
    renames = data.get('rename_sheets', {})
    unknown = sorted(set(renames) - set(names))
    if unknown:
        raise SystemExit(f'rename_sheets names not in the workbook: {unknown}. Sheets: {names}')
    return dropped, renames


def rewrite_workbook(content, dropped, renames):
    root = parse(content)
    sheets = root.find(s('sheets'))
    order = [sh.get('name') for sh in sheets.findall(s('sheet'))]
    removed_ids = set()
    for sh in list(sheets.findall(s('sheet'))):
        if sh.get('name') in dropped:
            removed_ids.add(sh.get(f'{{{R}}}id'))
            sheets.remove(sh)
        elif sh.get('name') in renames:
            sh.set('name', renames[sh.get('name')])
    kept_positions = [i for i, name in enumerate(order) if name not in dropped]
    names = root.find(s('definedNames'))
    if names is not None:
        for dn in list(names.findall(s('definedName'))):
            local = dn.get('localSheetId')
            if local is None:
                continue
            if int(local) not in kept_positions:
                names.remove(dn)
            else:
                dn.set('localSheetId', str(kept_positions.index(int(local))))
    for view in root.iter(s('workbookView')):
        for attr in ('activeTab', 'firstSheet'):
            if view.get(attr) is not None:
                view.set(attr, '0')
    calc = root.find(s('calcPr'))
    if calc is None:
        calc = ET.SubElement(root, s('calcPr'))
    # Formulas (for example pass/fail counts) are recalculated when the file is opened.
    calc.set('fullCalcOnLoad', '1')
    return serialize(root), removed_ids


def xlsx_fill(template, data, out):
    book = Workbook(template)
    specs = data.get('sheets', {})
    dropped, renames = sheet_selection(book, data)
    parts = {part: name for name, part in book.sheets}
    dropped_parts = {part for part, name in parts.items() if name in dropped}
    workbook_xml, removed_ids = rewrite_workbook(book.zip.read('xl/workbook.xml'), dropped, renames)
    # Parts only the dropped sheets use (their rels and drawings) go too.
    skip = set(dropped_parts)
    for part in dropped_parts:
        rels_name = part.replace('worksheets/', 'worksheets/_rels/') + '.rels'
        skip.add(rels_name)
        if rels_name in book.zip.namelist():
            for rel in parse(book.zip.read(rels_name)):
                target = os.path.normpath(os.path.join(os.path.dirname(part), rel.get('Target'))).replace(os.sep, '/')
                if 'drawings/' in target or 'comments' in target:
                    skip.add(target)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in book.zip.infolist():
            if item.filename in skip:
                continue
            content = book.zip.read(item.filename)
            if item.filename in parts:
                root = parse(content)
                name = parts[item.filename]
                xlsx_fill_sheet(book, item.filename, root, specs.get(name) or specs.get(renames.get(name, name)), data)
                content = serialize(root)
            elif item.filename == 'xl/workbook.xml':
                content = workbook_xml
            elif item.filename == 'xl/calcChain.xml':
                continue  # Excel rebuilds it; a stale chain makes the file "need repair".
            elif item.filename == '[Content_Types].xml':
                content = content.replace(b'<Override PartName="/xl/calcChain.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.calcChain+xml"/>', b'')
                for part in skip:
                    content = re.sub(rb'<Override PartName="/' + re.escape(part.encode()) + rb'"[^>]*/>', b'', content)
            elif item.filename == 'xl/_rels/workbook.xml.rels':
                content = re.sub(rb'<Relationship [^>]*Target="calcChain.xml"[^>]*/>', b'', content)
                for rid in removed_ids:
                    content = re.sub(rb'<Relationship [^>]*Id="' + re.escape(rid.encode()) + rb'"[^>]*/>', b'', content)
            elif item.filename == 'docProps/app.xml' and (dropped or renames):
                continue  # Only a cached list of sheet titles; Office rebuilds it, and a stale one confuses some readers.
            zout.writestr(item, content)
    if (dropped or renames) and 'docProps/app.xml' in book.zip.namelist():
        strip_app_reference(out)
    prune_shared_strings(out)


def strip_app_reference(path):
    """Remove the app.xml part and its references after it was skipped."""
    tmp = path + '.tmp'
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            content = zin.read(item.filename)
            if item.filename == '[Content_Types].xml':
                content = re.sub(rb'<Override PartName="/docProps/app.xml"[^>]*/>', b'', content)
            elif item.filename == '_rels/.rels':
                content = re.sub(rb'<Relationship [^>]*Target="docProps/app.xml"[^>]*/>', b'', content)
            zout.writestr(item, content)
    os.replace(tmp, path)


def xlsx_text(path):
    book = Workbook(path)
    out = []
    for name, part in book.sheets:
        out.append(f'## Sheet: {name}')
        for number, cells in book.rows(part):
            if any(cells.values()):
                out.append(f'{number}: ' + ' | '.join(cells.get(i, '') for i in range(1, max(cells) + 1)))
    return '\n'.join(out)


def xlsx_inspect(path):
    book = Workbook(path)
    sheets = []
    for name, part in book.sheets:
        rows = book.rows(part)
        root = parse(book.zip.read(part))
        block = header_block(rows, root)
        placeholders = sorted({k for _, cells in rows for v in cells.values() for k in PLACEHOLDER.findall(v)})
        labels = [cells[c].strip() for number, cells in rows if block and number < block[0] for c in sorted(cells) if cells[c].strip()]
        sheets.append({'name': name, 'header_rows': [block[0], block[1]] if block else None,
                       'columns': sorted(block[2], key=block[2].get) if block else [],
                       'labels_above_header': labels[:20], 'rows_used': len(rows), 'placeholders': placeholders})
    return {'format': 'xlsx', 'sheets': sheets}


# ---------- md / csv ----------

def md_inspect(path):
    text = open(path, encoding='utf-8').read()
    headings = [{'level': len(m.group(1)), 'text': m.group(2)} for m in re.finditer(r'^(#{1,6})\s+(.*)$', text, re.M)]
    tables = [[c.strip() for c in m.group(1).strip('|').split('|')] for m in re.finditer(r'^(\|.*\|)\s*\n\|[\s:\-|]+\|', text, re.M)]
    return {'format': 'md', 'headings': headings, 'tables': [{'columns': t} for t in tables],
            'placeholders': sorted(set(PLACEHOLDER.findall(text)))}


def md_fill(template, data, out):
    text = open(template, encoding='utf-8').read()
    text = PLACEHOLDER.sub(lambda m: str(lookup(data, m.group(1))) if lookup(data, m.group(1)) is not None else m.group(0), text)
    open(out, 'w', encoding='utf-8').write(text)


def csv_inspect(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f))
    return {'format': 'csv', 'columns': rows[0] if rows else [], 'rows': len(rows)}


def csv_fill(template, data, out):
    columns = csv_inspect(template)['columns']
    rows = data.get('rows', [])
    missing = sorted({k for r in rows for k in r} - set(columns))
    if missing:
        raise SystemExit(f'Columns not in the template: {missing}. Template columns: {columns}')
    # UTF-8 with BOM so Excel opens Japanese and Vietnamese text correctly.
    with open(out, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


# ---------- results (test execution written back by ID) ----------

def result_key(value):
    text = str(value).strip()
    return text[:-2] if re.fullmatch(r'-?\d+\.0', text) else text


def result_updates(data, columns, repeated=()):
    """{id: {column: value}} from data["rows"]; the ID column and every other column must be in the header, once."""
    id_column = data.get('id_column', 'ID')
    clash = sorted(set(repeated) & ({id_column} | {k for r in data.get('rows', []) for k in r}))
    if clash:
        raise SystemExit(f'Column names repeat in the header, so the target is ambiguous: {clash}. '
                         'For a two-row header pass "header_rows": [top, bottom]; otherwise rename the columns.')
    if id_column not in columns:
        raise SystemExit(f'ID column "{id_column}" not in the header; pass "id_column". Header: {list(columns)}')
    unknown = sorted({k for r in data.get('rows', []) for k in r} - set(columns))
    if unknown:
        hint = f'; repeated names left out: {sorted(repeated)} (for a two-row header pass "header_rows": [top, bottom])' if repeated else ''
        raise SystemExit(f'Columns not in the header: {unknown}. Header: {list(columns)}{hint}')
    updates = {}
    for r in data.get('rows', []):
        key = result_key(r.get(id_column, ''))
        if not key or key in updates:
            raise SystemExit(f'Each result row needs its own "{id_column}"; missing or repeated: {r}')
        updates[key] = {columns[k]: v for k, v in r.items() if k != id_column}
    return id_column, updates


def recalc_on_open(content):
    root = parse(content)
    calc = root.find(s('calcPr'))
    if calc is None:
        calc = ET.SubElement(root, s('calcPr'))
    # Pass/fail counts and other formulas that read the result cells are recalculated when the file is opened.
    calc.set('fullCalcOnLoad', '1')
    return serialize(root)


def xlsx_results(path, data, out):
    book = Workbook(path)
    names = [name for name, _ in book.sheets]
    name = data.get('sheet') or names[0]
    part = dict(book.sheets).get(name)
    if part is None:
        raise SystemExit(f'Sheet not in the workbook: {name}. Sheets: {names}')
    root = parse(book.zip.read(part))
    rows = book.rows(part, root)
    top, bottom = (data.get('header_rows') or [data.get('header_row'), None])[:2]
    block = header_names(rows, root, top, bottom)
    if block is None:
        raise SystemExit(f'No header row found in sheet {name}; pass "header_row".')
    _, bottom, names = block
    values = list(names.values())
    repeated = {n for n in values if values.count(n) > 1}
    columns = {n: col for col, n in names.items() if n not in repeated}
    id_column, updates = result_updates(data, columns, repeated)
    row_els = {int(r.get('r')): r for r in root.find(s('sheetData')).findall(s('row'))}
    seen = {}
    for number, cells in rows:
        key = result_key(cells.get(columns[id_column], ''))
        if number <= bottom or key not in updates:
            continue
        if key in seen:
            raise SystemExit(f'ID {key} is on rows {seen[key]} and {number} of sheet {name}; pass an "id_column" that is unique.')
        seen[key] = number
        for col, value in updates[key].items():
            set_cell(row_els[number], number, col, value, None)
    missing = [k for k in updates if k not in seen]
    if missing:
        raise SystemExit(f'IDs not found in sheet {name}: {missing}')
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in book.zip.infolist():
            content = book.zip.read(item.filename)
            if item.filename == part:
                content = serialize(root)
            elif item.filename == 'xl/workbook.xml':
                content = recalc_on_open(content)
            elif item.filename == 'xl/calcChain.xml':
                continue  # Excel rebuilds it; a stale chain makes the file "need repair".
            elif item.filename == '[Content_Types].xml':
                content = re.sub(rb'<Override PartName="/xl/calcChain.xml"[^>]*/>', b'', content)
            elif item.filename == 'xl/_rels/workbook.xml.rels':
                content = re.sub(rb'<Relationship [^>]*Target="calcChain.xml"[^>]*/>', b'', content)
            zout.writestr(item, content)
    return len(seen)


def csv_results(path, data, out):
    with open(path, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f))
    header = rows[0] if rows else []
    repeated = {c for c in header if header.count(c) > 1}
    columns = {c: i for i, c in enumerate(header) if c not in repeated}
    id_column, updates = result_updates(data, columns, repeated)
    id_index = columns[id_column]
    seen = set()
    for row in rows[1:]:
        key = result_key(row[id_index] if id_index < len(row) else '')
        if key not in updates:
            continue
        if key in seen:
            raise SystemExit(f'ID {key} appears twice in {path}; pass an "id_column" that is unique.')
        seen.add(key)
        for index, value in updates[key].items():
            row.extend([''] * (index + 1 - len(row)))
            row[index] = '' if value is None else str(value)
    missing = [k for k in updates if k not in seen]
    if missing:
        raise SystemExit(f'IDs not found in {path}: {missing}')
    with open(out, 'w', encoding='utf-8-sig', newline='') as f:
        csv.writer(f).writerows(rows)
    return len(seen)


# ---------- cli ----------

def kind(path):
    return path.rsplit('.', 1)[-1].lower()


def leftovers(path):
    k = kind(path)
    if k == 'docx':
        with zipfile.ZipFile(path) as z:
            text = ' '.join(''.join(t.text or '' for t in parse(z.read(p)).iter(w('t'))) for p in docx_parts(z.namelist()))
    elif k == 'xlsx':
        text = xlsx_text(path)
    else:
        text = open(path, encoding='utf-8-sig').read()
    return sorted(set(PLACEHOLDER.findall(text)))


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    command, path = argv[1], argv[2]
    k = kind(path)
    if command == 'text':
        print({'docx': docx_text, 'xlsx': xlsx_text}.get(k, lambda p: open(p, encoding='utf-8-sig').read())(path))
    elif command == 'inspect':
        result = {'docx': docx_inspect, 'xlsx': xlsx_inspect, 'md': md_inspect, 'csv': csv_inspect}[k](path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == 'fill':
        data = json.load(open(argv[3], encoding='utf-8'))
        {'docx': docx_fill, 'xlsx': xlsx_fill, 'md': md_fill, 'csv': csv_fill}[k](path, data, argv[4])
        left = leftovers(argv[4])
        print(json.dumps({'written': argv[4], 'placeholders_left': left}, ensure_ascii=False))
    elif command == 'build':
        if k != 'docx':
            raise SystemExit('build works on .docx samples; for xlsx use fill with "sheets".')
        docx_build(path, json.load(open(argv[3], encoding='utf-8')), argv[4])
        print(json.dumps({'written': argv[4], 'placeholders_left': leftovers(argv[4])}, ensure_ascii=False))
    elif command == 'results':
        if k not in ('xlsx', 'csv'):
            raise SystemExit('results works on .xlsx and .csv sheets.')
        if os.path.exists(argv[4]) and os.path.samefile(argv[4], path):
            raise SystemExit('Write the results to a new file; the input sheet is never overwritten.')
        if kind(argv[4]) != k:
            raise SystemExit(f'Write the results in the same format as the sheet (.{k}).')
        data = json.load(open(argv[3], encoding='utf-8'))
        updated = {'xlsx': xlsx_results, 'csv': csv_results}[k](path, data, argv[4])
        print(json.dumps({'written': argv[4], 'rows_updated': updated}, ensure_ascii=False))
    elif command == 'check':
        left = leftovers(path)
        print(json.dumps({'placeholders_left': left}, ensure_ascii=False))
        return 1 if left else 0
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
