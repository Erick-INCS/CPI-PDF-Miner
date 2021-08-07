#!/usr/bin/env python3
""" Extract a single talbe from pdf """

import re
import tabula
import pdftotext
import pandas as pd
from collections import Counter
from io import StringIO
from sklearn.cluster import AffinityPropagation
from statistics import mode
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

import matplotlib.pyplot as plt


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

            page_num += 1
            if pages and page_num - pages[-1] > 1:
                print('Searching break.')
                break

    print('Generating table in', pages)
    table = tabula.read_pdf(path, pages=pages, pandas_options={'header': None})
    # return extract_text(path, pages)
    final_table = table.copy()
    # if isinstance(table, list):
        # print('table:', table, '\n\n\n')
        # final_table = table[0].rename(columns={
        #     table[0].columns[i]: l for i, l in enumerate(columns)})
        # for current in table[1:]:
        #     if len(final_table.columns) != len(current.columns):
        #         print(f'Incompatible tables in {path}')
        #         continue

        #     current = current.rename(columns={
        #         current.columns[i]: l for i, l in enumerate(columns)})
        #     final_table = final_table.append(current)
    return table


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

    filter_regex = [
        r' *Consolidar políticas *Fortalecer políticas *Priorizar políticas.*',
        r' *urbanas +urbanas +urbanas.*']

    c_ix = 0
    while c_ix < len(pages):
        pages[c_ix] = pages[c_ix].splitlines()
        for ln_ix, line in enumerate(pages[c_ix]):
            if re.search(RE_EX, line, re.IGNORECASE):
                pages[c_ix] = pages[c_ix][ln_ix+1:]
                break

        for rgex in filter_regex:
            for ln_ix, line in enumerate(pages[c_ix]):
                if re.search(rgex, line, re.IGNORECASE):
                    pages[c_ix] = pages[c_ix][:ln_ix]
                    break

        pages[c_ix] = '\n'.join(pages[c_ix])
        c_ix += 1

    return pages


def squeeze(a_list):
    """ Reduces dimentionallity """
    length = len(a_list)
    while length >= 0:
        current = a_list.pop(0)
        if isinstance(current, list):
            a_list.extend(current)
        else:
            a_list.append(current)
        length -= 1
    return a_list


def add_separations(pages, space_tolerance=3):
    """ A bad way to add row separations """
    for p_ix, page in enumerate(pages):
        page = re.sub(' {3,}', '|', page)

        page_lines = pages[p_ix].splitlines()
        page_sep_ixs = page.splitlines()
        page_sep_ixs = list(map(
            lambda ix_ln: list(map(
                page_lines[ix_ln[0]].index,
                filter(lambda e: e, ix_ln[1].split('|')))),
            enumerate(page_sep_ixs)))
        squeeze(page_sep_ixs)

        tb_cols = {}
        for num in set(page_sep_ixs):
            added = False

            for key in tb_cols:
                if (tb_cols[key]['min'] - space_tolerance <= num) and\
                   (tb_cols[key]['max'] + space_tolerance >= num):

                    tb_cols[key]['min'] = min(num, tb_cols[key]['min'])
                    tb_cols[key]['max'] = max(num, tb_cols[key]['max'])
                    added = True
            if not added:
                tb_cols[len(tb_cols.keys())] = {
                        'max': num,
                        'min': num}

        # Merge lines
        to_pop = []
        for key in tb_cols:
            if key in to_pop:
                continue

            other_keys = list(tb_cols.keys()).copy()
            other_keys.remove(key)
            for o_key in other_keys:
                if not ((tb_cols[key]['min'] - space_tolerance > tb_cols[o_key]['max']) or
                        (tb_cols[key]['max'] + space_tolerance < tb_cols[o_key]['min'])):
                    tb_cols[key]['min'] = min(
                            tb_cols[key]['min'],
                            tb_cols[o_key]['min'])

                    tb_cols[key]['max'] = max(
                        tb_cols[key]['max'],
                        tb_cols[o_key]['max'])

                    to_pop.append(o_key)

        for poop in to_pop:
            tb_cols.pop(poop)

        print('Columns: ', tb_cols, '\n\n')

        tb_cols = list(map(lambda e: e['min'], tb_cols.values()))
        tb_cols.sort()

        line_length = max(map(len, page_lines))

        pages[p_ix] = pd.DataFrame(map(
            lambda ln: [ln[tb_cols[pk[0]]:pk[1]]
                        for pk in enumerate(tb_cols[1:] + [line_length])],
            page_lines))

    return pages


if __name__ == '__main__':
    TB_PATH = 'corrupt/05033_San_Pedro.pdf'
    my_table = extract_table(TB_PATH)
    my_table = isolate(my_table)
    my_table = add_separations(my_table)
    print(my_table[0])
    """print(my_table.head())
    print(my_table.tail())
    print(my_table.columns)
    print(my_table.shape)"""
