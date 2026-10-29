#!/usr/bin/env python3
"""Self-test for docfill.py: builds small .docx / .xlsx / .csv / .md templates, fills them and checks the result.
Run: python3 tools/selftest.py   (no third-party packages needed)"""

import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
DOCFILL = os.path.join(HERE, 'docfill.py')

DOCX_CT = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'''
DOCX_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'''
DOCX_BODY = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>
<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>{{title}}</w:t></w:r></w:p>
<w:p><w:r><w:t>Ticket: {{tic</w:t></w:r><w:r><w:rPr><w:b/></w:rPr><w:t>ket}} / 作成者: {{author}}</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="ListBullet"/></w:pPr><w:r><w:t>{{rules[]}}</w:t></w:r></w:p>
<w:tbl><w:tr><w:tc><w:p><w:r><w:t>ID</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>手順</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>期待結果</w:t></w:r></w:p></w:tc></w:tr>
<w:tr><w:tc><w:p><w:r><w:t>{{cases.id}}</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>{{cases.steps}}</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>{{cases.expected}}</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
<w:sectPr/></w:body></w:document>'''

XLSX_FILES = {
    '[Content_Types].xml': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/></Types>''',
    '_rels/.rels': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>''',
    'xl/workbook.xml': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="TestCases" sheetId="1" r:id="rId1"/></sheets></workbook>''',
    'xl/_rels/workbook.xml.rels': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/></Relationships>''',
    'xl/sharedStrings.xml': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><si><t>{{project}} テストケース</t></si><si><t>No</t></si><si><t>シナリオ</t></si><si><t>期待結果</t></si></sst>''',
    'xl/worksheets/sheet1.xml': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><dimension ref="A1:C3"/><sheetData>
<row r="1"><c r="A1" t="s"><v>0</v></c></row>
<row r="3"><c r="A3" t="s" s="1"><v>1</v></c><c r="B3" t="s" s="1"><v>2</v></c><c r="C3" t="s" s="1"><v>3</v></c></row>
<row r="4"><c r="A4" s="2"/><c r="B4" s="2"/><c r="C4" s="2"/></row>
</sheetData></worksheet>''',
}


def build(path, files):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content)


def run(*args):
    result = subprocess.run([sys.executable, DOCFILL, *args], capture_output=True, text=True)
    if result.returncode not in (0, 1):
        raise AssertionError(result.stderr or result.stdout)
    return result.stdout


def main():
    failures = []

    def check(name, condition):
        print(('PASS ' if condition else 'FAIL ') + name)
        if not condition:
            failures.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        docx = os.path.join(tmp, 't.docx')
        build(docx, {'[Content_Types].xml': DOCX_CT, '_rels/.rels': DOCX_RELS, 'word/document.xml': DOCX_BODY})
        info = json.loads(run('inspect', docx))
        check('docx inspect finds placeholders split across runs', 'ticket' in info['placeholders'])
        check('docx inspect finds the table row template', info['tables'][0]['row_template'] is not None)
        data = {'title': '会員登録 業務シナリオ', 'ticket': 'ABC-1', 'author': 'Hiep',
                'rules': ['BR-001 パスワードは8文字以上', 'BR-002 メールは一意'],
                'cases': [{'id': 'TC-001', 'steps': '1. 開く\n2. 入力', 'expected': '登録完了'},
                          {'id': 'TC-002', 'steps': '空で送信', 'expected': 'エラー表示'}]}
        data_path = os.path.join(tmp, 'd.json')
        json.dump(data, open(data_path, 'w', encoding='utf-8'), ensure_ascii=False)
        out = os.path.join(tmp, 'out.docx')
        result = json.loads(run('fill', docx, data_path, out))
        text = run('text', out)
        check('docx fill leaves no placeholders', result['placeholders_left'] == [])
        check('docx scalar across runs replaced', 'Ticket: ABC-1 / 作成者: Hiep' in text)
        check('docx list paragraph repeated', 'BR-001' in text and 'BR-002' in text)
        check('docx table row repeated per item', 'TC-001' in text and 'TC-002' in text and text.count('| TC-') == 2)
        check('docx heading kept', text.startswith('# 会員登録 業務シナリオ'))

        xlsx = os.path.join(tmp, 't.xlsx')
        build(xlsx, XLSX_FILES)
        info = json.loads(run('inspect', xlsx))
        sheet = info['sheets'][0]
        check('xlsx inspect finds header row 3', sheet['header_rows'] == [3, 3] and sheet['columns'] == ['No', 'シナリオ', '期待結果'])
        xdata = {'project': 'DEMO', 'sheets': {'TestCases': {'rows': [
            {'No': 1, 'シナリオ': '正常系 登録', '期待結果': '完了画面'},
            {'No': 2, 'シナリオ': '異常系 空入力', '期待結果': 'エラー'}]}}}
        json.dump(xdata, open(data_path, 'w', encoding='utf-8'), ensure_ascii=False)
        xout = os.path.join(tmp, 'out.xlsx')
        result = json.loads(run('fill', xlsx, data_path, xout))
        xtext = run('text', xout)
        check('xlsx title placeholder replaced', 'DEMO テストケース' in xtext and result['placeholders_left'] == [])
        check('xlsx rows written under the header', '4: 1 | 正常系 登録 | 完了画面' in xtext and '5: 2 | 異常系 空入力 | エラー' in xtext)
        with zipfile.ZipFile(xout) as z:
            sheet_xml = z.read('xl/worksheets/sheet1.xml').decode()
        check('xlsx keeps the data row style', 'r="A4" s="2"' in sheet_xml or 's="2" r="A4"' in sheet_xml or ('A4' in sheet_xml and 's="2"' in sheet_xml))

        # Clearing the sample's rows must not leave their text anywhere in the file.
        secret_files = dict(XLSX_FILES)
        secret_files['xl/sharedStrings.xml'] = XLSX_FILES['xl/sharedStrings.xml'].replace('</sst>', '<si><t>OLD-CLIENT-SECRET</t></si></sst>')
        secret_files['xl/worksheets/sheet1.xml'] = XLSX_FILES['xl/worksheets/sheet1.xml'].replace(
            '<c r="A4" s="2"/>', '<c r="A4" s="2" t="s"><v>4</v></c>')
        secret = os.path.join(tmp, 'secret.xlsx')
        build(secret, secret_files)
        json.dump({'sheets': {'TestCases': {'clear_existing': True, 'rows': [{'No': 1, 'シナリオ': 'new', '期待結果': 'ok'}]}}},
                  open(data_path, 'w', encoding='utf-8'), ensure_ascii=False)
        sout = os.path.join(tmp, 'secret-out.xlsx')
        run('fill', secret, data_path, sout)
        with zipfile.ZipFile(sout) as z:
            blob = b''.join(z.read(n) for n in z.namelist())
        check('xlsx clear_existing leaves no sample text in the file', b'OLD-CLIENT-SECRET' not in blob and 'new' in run('text', sout))

        bad = {'sheets': {'TestCases': {'rows': [{'Unknown': 1}]}}}
        json.dump(bad, open(data_path, 'w', encoding='utf-8'))
        proc = subprocess.run([sys.executable, DOCFILL, 'fill', xlsx, data_path, xout], capture_output=True, text=True)
        check('xlsx rejects a column the template does not have', proc.returncode != 0 and 'Unknown' in (proc.stderr + proc.stdout))

        # results: test execution written back into a filled sheet, matched by ID.
        run_files = dict(XLSX_FILES)
        run_files['xl/sharedStrings.xml'] = XLSX_FILES['xl/sharedStrings.xml'].replace(
            '</sst>', '<si><t>結果</t></si><si><t>Bug ID</t></si><si><t>正常系</t></si><si><t>完了画面</t></si><si><t>異常系</t></si><si><t>エラー</t></si></sst>')
        run_files['xl/worksheets/sheet1.xml'] = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>
<row r="3"><c r="A3" t="s" s="1"><v>1</v></c><c r="B3" t="s" s="1"><v>2</v></c><c r="C3" t="s" s="1"><v>3</v></c><c r="D3" t="s" s="1"><v>4</v></c><c r="E3" t="s" s="1"><v>5</v></c></row>
<row r="4"><c r="A4" s="2"><v>1</v></c><c r="B4" s="2" t="s"><v>6</v></c><c r="C4" s="2" t="s"><v>7</v></c><c r="D4" s="2"/><c r="E4" s="2"/></row>
<row r="5"><c r="A5" s="2"><v>2</v></c><c r="B5" s="2" t="s"><v>8</v></c><c r="C5" s="2" t="s"><v>9</v></c><c r="D5" s="2"/><c r="E5" s="2"/></row>
<row r="7"><c r="D7"><f>COUNTIF(D4:D5,"NG")</f><v>0</v></c></row>
</sheetData></worksheet>'''
        run_sheet = os.path.join(tmp, 'run.xlsx')
        build(run_sheet, run_files)
        json.dump({'id_column': 'No', 'rows': [{'No': 2, '結果': 'NG', 'Bug ID': 'BUG-REG-001'}]},
                  open(data_path, 'w', encoding='utf-8'), ensure_ascii=False)
        rout = os.path.join(tmp, 'run-results.xlsx')
        result = json.loads(run('results', run_sheet, data_path, rout))
        lines = {l.split(':', 1)[0]: l for l in run('text', rout).splitlines()}
        check('results updates only the row with that ID',
              result['rows_updated'] == 1 and lines['5'].startswith('5: 2 | 異常系 | エラー | NG | BUG-REG-001')
              and 'NG' not in lines['4'] and lines['4'].startswith('4: 1 | 正常系 | 完了画面'))
        with zipfile.ZipFile(rout) as z:
            sheet_xml = z.read('xl/worksheets/sheet1.xml').decode()
            book_xml = z.read('xl/workbook.xml').decode()
        check('results keeps cell styles and formulas, recalculated on open',
              re.search(r'<c [^>]*r="D5"[^>]*s="2"|<c [^>]*s="2"[^>]*r="D5"', sheet_xml) is not None
              and 'COUNTIF(D4:D5,"NG")' in sheet_xml and 'fullCalcOnLoad="1"' in book_xml)
        rejected = []
        for bad_rows, out_path in (([{'No': 99, '結果': 'OK'}], rout), ([{'No': 1, 'Unknown': 'OK'}], rout), ([{'No': 1, '結果': 'OK'}], run_sheet)):
            json.dump({'id_column': 'No', 'rows': bad_rows}, open(data_path, 'w', encoding='utf-8'), ensure_ascii=False)
            proc = subprocess.run([sys.executable, DOCFILL, 'results', run_sheet, data_path, out_path], capture_output=True, text=True)
            rejected.append(proc.returncode != 0)
        check('results rejects an unknown ID, an unknown column and writing over the input', all(rejected))

        refused = []
        link = os.path.join(tmp, 'link.xlsx')
        os.symlink(run_sheet, link)
        json.dump({'id_column': 'No', 'rows': [{'No': 1, '結果': 'OK'}]}, open(data_path, 'w', encoding='utf-8'), ensure_ascii=False)
        for out_path in (link, os.path.join(tmp, 'wrong-format.csv')):
            proc = subprocess.run([sys.executable, DOCFILL, 'results', run_sheet, data_path, out_path], capture_output=True, text=True)
            refused.append(proc.returncode != 0)
        check('results refuses the input under another name (symlink) and a different format',
              all(refused) and '異常系' in run('text', run_sheet))

        # A two-row header whose parent is merged across columns only: "header_rows" names the sub-columns.
        inline = lambda ref, text: f'<c r="{ref}" t="inlineStr"><is><t>{text}</t></is></c>'
        two_row = dict(XLSX_FILES)
        two_row['xl/worksheets/sheet1.xml'] = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
            f'<row r="3">{inline("A3", "No")}{inline("B3", "シナリオ")}{inline("C3", "PC")}<c r="D3"/></row>'
            f'<row r="4">{inline("C4", "Lần 1")}{inline("D4", "Lần 2")}</row>'
            f'<row r="5"><c r="A5"><v>1</v></c>{inline("B5", "x")}<c r="C5"/><c r="D5"/></row>'
            '</sheetData><mergeCells count="1"><mergeCell ref="C3:D3"/></mergeCells></worksheet>')
        two_path = os.path.join(tmp, 'two-row.xlsx')
        build(two_path, two_row)
        json.dump({'id_column': 'No', 'rows': [{'No': 1, 'PC': 'OK'}]}, open(data_path, 'w', encoding='utf-8'), ensure_ascii=False)
        ambiguous = subprocess.run([sys.executable, DOCFILL, 'results', two_path, data_path, os.path.join(tmp, 'two-a.xlsx')], capture_output=True, text=True)
        json.dump({'id_column': 'No', 'header_rows': [3, 4], 'rows': [{'No': 1, 'PC / Lần 1': 'OK'}]}, open(data_path, 'w', encoding='utf-8'), ensure_ascii=False)
        two_out = os.path.join(tmp, 'two-b.xlsx')
        run('results', two_path, data_path, two_out)
        check('results refuses a repeated column name and writes under "header_rows"',
              ambiguous.returncode != 0 and 'repeat' in ambiguous.stderr + ambiguous.stdout
              and any(l.startswith('5: 1 | x | OK') for l in run('text', two_out).splitlines()))

        # Furigana (<rPh>) is not part of a cell's text.
        furigana = dict(XLSX_FILES)
        furigana['xl/sharedStrings.xml'] = XLSX_FILES['xl/sharedStrings.xml'].replace(
            '<si><t>期待結果</t></si>', '<si><t>期待結果</t><rPh sb="0" eb="4"><t>キタイケッカ</t></rPh></si>')
        furi_path = os.path.join(tmp, 'furigana.xlsx')
        build(furi_path, furigana)
        check('xlsx headers and text skip furigana', json.loads(run('inspect', furi_path))['sheets'][0]['columns'] == ['No', 'シナリオ', '期待結果'])

        run_csv = os.path.join(tmp, 'run.csv')
        open(run_csv, 'w', encoding='utf-8').write('ID,Scenario,Result\nTC-1,Đăng ký,\nTC-2,Đăng nhập,\n')
        json.dump({'rows': [{'ID': 'TC-2', 'Result': 'Pass'}]}, open(data_path, 'w', encoding='utf-8'))
        rcsv = os.path.join(tmp, 'run-results.csv')
        run('results', run_csv, data_path, rcsv)
        text = open(rcsv, encoding='utf-8-sig').read()
        check('csv results updates by ID and keeps the BOM',
              open(rcsv, 'rb').read().startswith(b'\xef\xbb\xbf') and 'TC-1,Đăng ký,\n' in text and 'TC-2,Đăng nhập,Pass' in text)

        rounds = os.path.join(tmp, 'rounds.csv')
        open(rounds, 'w', encoding='utf-8').write('ID,Result,Date,Result,Date,Note\nTC-1,Pass,10/01,,,\nTC-2,,,,,\n')
        json.dump({'rows': [{'ID': 'TC-2', 'Note': 'retest'}]}, open(data_path, 'w', encoding='utf-8'))
        rounds_out = os.path.join(tmp, 'rounds-out.csv')
        run('results', rounds, data_path, rounds_out)
        json.dump({'rows': [{'ID': 'TC-2', 'Result': 'Pass'}]}, open(data_path, 'w', encoding='utf-8'))
        clash = subprocess.run([sys.executable, DOCFILL, 'results', rounds, data_path, os.path.join(tmp, 'r2.csv')], capture_output=True, text=True)
        rtext = open(rounds_out, encoding='utf-8-sig').read()
        check('csv results keeps repeated columns and refuses to write into one',
              'TC-1,Pass,10/01,,,\n' in rtext and 'TC-2,,,,,retest' in rtext and clash.returncode != 0)

        csv_path = os.path.join(tmp, 't.csv')
        open(csv_path, 'w', encoding='utf-8').write('ID,Scenario,Expected\n')
        json.dump({'rows': [{'ID': 'TC-1', 'Scenario': 'Đăng ký', 'Expected': 'OK'}]}, open(data_path, 'w', encoding='utf-8'), ensure_ascii=False)
        cout = os.path.join(tmp, 'out.csv')
        run('fill', csv_path, data_path, cout)
        check('csv written with BOM and rows', open(cout, 'rb').read().startswith(b'\xef\xbb\xbf') and 'Đăng ký' in open(cout, encoding='utf-8-sig').read())

        md_path = os.path.join(tmp, 't.md')
        open(md_path, 'w', encoding='utf-8').write('# {{title}}\n\n| ID | Name |\n| -- | ---- |\n')
        json.dump({'title': 'Guide'}, open(data_path, 'w', encoding='utf-8'))
        mout = os.path.join(tmp, 'out.md')
        run('fill', md_path, data_path, mout)
        check('md placeholder replaced', open(mout, encoding='utf-8').read().startswith('# Guide'))

        # build: a new document in the sample's look, with a table and an image
        import struct, zlib
        raw = b''.join(b'\x00' + b'\xff\x00\x00' * 4 for _ in range(2))
        def chunk(kind, payload):
            return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload) & 0xffffffff)
        png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 4, 2, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')
        png_path = os.path.join(tmp, 'shot.png')
        open(png_path, 'wb').write(png)
        rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>'
        sample = os.path.join(tmp, 'sample.docx')
        build(sample, {'[Content_Types].xml': DOCX_CT, '_rels/.rels': DOCX_RELS, 'word/document.xml': DOCX_BODY,
                       'word/_rels/document.xml.rels': rels})
        content = {'prototypes': {'title': 0, 'body': 1, 'bullet': 2, 'table': 3},
                   'blocks': [{'role': 'title', 'text': '利用ガイド'}, {'role': 'body', 'text': '手順は次のとおりです。'},
                              {'role': 'bullet', 'text': 'ログインする'}, {'role': 'table', 'rows': [['No', '操作', '結果'], ['1', '開く', '表示']]},
                              {'role': 'body', 'image': png_path}]}
        json.dump(content, open(data_path, 'w', encoding='utf-8'), ensure_ascii=False)
        bout = os.path.join(tmp, 'built.docx')
        run('build', sample, data_path, bout)
        btext = run('text', bout)
        with zipfile.ZipFile(bout) as z:
            names = z.namelist()
            doc = z.read('word/document.xml').decode()
            rels_xml = z.read('word/_rels/document.xml.rels').decode()
            types = z.read('[Content_Types].xml').decode()
        check('build keeps the prototype heading style', 'w:val="Heading1"' in doc and btext.startswith('# 利用ガイド'))
        check('build writes the table rows', '| 1 | 開く | 表示 |' in btext)
        check('build embeds the image with a relationship and content type',
              any(n.startswith('word/media/') for n in names) and 'relationships/image' in rels_xml and 'Extension="png"' in types and '<a:blip' in doc or 'blip' in doc)
        check('build drops the sample content', 'TC-' not in btext and '{{' not in btext)
        with zipfile.ZipFile(bout) as z:
            body = z.read('word/document.xml')
        media = [n for n in zipfile.ZipFile(bout).namelist() if n.startswith('word/media/')]
        check('build ships only the media it references', len(media) == 1 and b'r:embed' in body)

    print(f'\n{"OK" if not failures else "FAILED"}: {len(failures)} failure(s)')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
