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
from os import listdir

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
                break

            page_num += 1

    table = extract_text(path, pages)
    table = isolate(table)
    table = add_separations(table)

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

    cut_regex = [
        r' *Consolidar políticas *Fortalecer políticas *Priorizar políticas.*',
        r' *urbanas +urbanas +urbanas.*']
    filter_regex = [
            re.compile(r'^ *\w+ *$')]

    c_ix = 0
    while c_ix < len(pages):
        pages[c_ix] = pages[c_ix].splitlines()
        for ln_ix, line in enumerate(pages[c_ix]):
            if re.search(RE_EX, line, re.IGNORECASE):
                pages[c_ix] = pages[c_ix][ln_ix+1:]
                break

        for rgex in cut_regex:
            for ln_ix, line in enumerate(pages[c_ix]):
                if re.search(rgex, line, re.IGNORECASE):
                    pages[c_ix] = pages[c_ix][:ln_ix]
                    break

        pages[c_ix] = list(filter(
            lambda line: sum([
                rg.match(line) is not None for rg in filter_regex]) == 0,
            pages[c_ix]))

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
    return re.search(r' *ID +([\d|\.]+) *', pages[0]).groups()[0]


def save_datasets(ds, pdf_name, directory=''):
    """ Save the DataSets as CSV """
    print(f'{directory}{pdf_name.split("/")[-1].replace(".pdf", "")}_0..{len(ds)}.csv')
    list(map(
        lambda tb: tb[1].to_csv(
            f'{directory}{pdf_name.split("/")[-1].replace(".pdf", "")}_{tb[0]}.csv',
            index=False),
        enumerate(ds)))


def extract_and_save(file_path, out_dir=''):
    """ Extract a table from a pdf file and save the resulting dataset """
    save_datasets(
            extract_table(file_path),
            file_path,
            out_dir)


if __name__ == '__main__':
    # path = 'pdfs/2018_11014_Dolores_Hidalgo_Cuna_de_la_Independencia_Nacional.pdf'
    path = 'pdfs/2018_15070_La_Paz.pdf'
    # path = 'pdfs/2015_03003_La_Paz.pdf'
    names = listdir('pdfs')
    names = 'pdfs/' + pd.Series(names)
    cpis = names.apply(extract_table)
    names = list(map(
        lambda n: n.split('_')[1],
        names.to_list()))

    final = pd.DataFrame({'clave': names, 'cpi': cpis})
    print(final)
    final.to_csv('cpis_clave.csv', index=False)
