#!/usr/bin/env python3
""" Extract a single talbe from pdf """

import re
import tabula
import pdftotext
from io import StringIO
from statistics import mode
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser


RE_EX = r'(tabla).*\d.*Síntesis de resultados por dimensión y subdimensión'

def extract_table(path):
    """ Search the corresponging page """
    re_ex = RE_EX
    pages = []
    page_num = 1
    with open(path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        for page in PDFPage.create_pages(doc):
            rsrcmgr = PDFResourceManager()
            output_string = StringIO()
            device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            interpreter.process_page(page)
            finder = re.search(re_ex, output_string.getvalue(), re.IGNORECASE)
            print('Searching table', '\tCurrent page:', page_num)
            if finder:
                print('Table finded.')
                pages.append(page_num)
                print(output_string.getvalue())

            page_num += 1
            if pages and page_num - pages[-1] > 1:
                print('Searching break.')
                break

    print('Generating table in', pages)
    table = tabula.read_pdf(path, pages=pages, pandas_options={'header': None})
    columns = ['section_id', 'label', 'municipio', 'aglomeracion_urbana']
    return extract_text(path, pages)
    """
    final_table = table.copy()
    if isinstance(table, list):
        print('table:', table, '\n\n\n')
        final_table = table[0].rename(columns={
            table[0].columns[i]: l for i, l in enumerate(columns)})
        for current in table[1:]:
            if len(final_table.columns) != len(current.columns):
                print(f'Incompatible tables in {path}')
                continue

            current = current.rename(columns={
                current.columns[i]: l for i, l in enumerate(columns)})
            final_table = final_table.append(current)

    return final_table.reset_index()
    """


def extract_text(path, pages):
    """ Extract Raw text from PDF """
    out = []
    with open(path, 'rb') as file:
        pdftotext_string = pdftotext.PDF(file)

    for i in pages:
        out.append(pdftotext_string[i - 1])

    return out


def isolate(pages):
    """ Remove irrelevant content """
    # First cut
    c_ix = 0
    while c_ix < len(pages):
        print(pages[c_ix])
        pages[c_ix] = pages[c_ix].splitlines()
        for ln_ix, line in enumerate(pages[c_ix]):
            if re.search(RE_EX, line, re.IGNORECASE):
                pages[c_ix] = pages[c_ix][ln_ix+1:]
                break

        pages[c_ix] = '\n'.join(pages[c_ix])
        c_ix += 1

    return pages


def add_separations(pages):
    """ A bad way to add row separations """
    for p_ix, page in enumerate(pages):
        page = re.sub(' {3,}', '|', page)

        page_lines = pages[p_ix].splitlines()
        page_sep_ixs = page.splitlines()
        print(page_sep_ixs)
        page_sep_ixs = list(map(
            lambda ix_ln: list(map(
                page_lines[ix_ln[0]].index,
                filter(lambda e: e, ix_ln[1].split('|')))),
            enumerate(page_sep_ixs)))
        print(page_sep_ixs)

        def count_rows(line):
            return len(list(filter(lambda c: c == '|', line)))

        def is_numeric(string):
            """ Converts string to float """
            try:
                float(string)
                return True
            except ValueError:
                return False

        def filter_table(tb_page):
            tb_page = tb_page.splitlines()
            rows_mode = mode(map(count_rows, tb_page))
            min_page = list(filter(
                lambda r: count_rows(r) == rows_mode,
                tb_page))
            return min_page

            # TODO: Eliminar outliers
            # TODO: Definir los indices para las separaciones de las columnas
            # tb_page = filter(
              #   lambda ln: not(count_rows(ln) == rows_mode or ((count_rows(ln) - rows_mode <= 1) and
                #           ('|' in ln) and
                 #           (sum(map(is_numeric, ln.split('|'))) > 0))),
                # tb_page)
            # return list(tb_page)

        pages[p_ix] = filter_table(page)
    return pages


if __name__ == '__main__':
    TB_PATH = 'corrupt/05033_San_Pedro.pdf'
    my_table = extract_table(TB_PATH)
    my_table = isolate(my_table)
    my_table = add_separations(my_table)
    """print(my_table.head())
    print(my_table.tail())
    print(my_table.columns)
    print(my_table.shape)"""
