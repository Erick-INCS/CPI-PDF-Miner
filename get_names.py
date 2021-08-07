#!/usr/bin/env python3
""" Extract a single talbe from pdf """

import re
import pdftotext
import pandas as pd
from os import listdir


def extract_name(path):
    """ get name """
    table = extract_text(path, 2)[0]
    rg_name = re.compile(r' *([\w| ]+), *M.{1}xico')

    res = rg_name.search(table)
    if res:
        spl_name = path.split('/')[-1].replace('pdf', '').split('_')
        return (res.groups()[0],
                spl_name[1],
                ' '.join(spl_name[2:]),
                spl_name[0])
    return None


def extract_text(path, page):
    """ Extract Raw text from PDF """
    out = []
    with open(path, 'rb') as file:
        pdftotext_string = pdftotext.PDF(file)
        out.append(pdftotext_string[page])
    return out


if __name__ == '__main__':
    # path = 'pdfs/2018_11014_Dolores_Hidalgo_Cuna_de_la_Independencia_Nacional.pdf'
    # path = 'pdfs/2018_15070_La_Paz.pdf'
    # path = 'pdfs/2015_03003_La_Paz.pdf'
    pdfs_path = 'pdfs/'
    pdfs = pdfs_path + pd.Series(listdir(pdfs_path))

    df = pd.DataFrame(
        pdfs.map(extract_name).to_list(),
        columns=['estado', 'clave', 'municipio', 'periodo'])

    df.to_csv('Names.csv', index=False)
    print(df, 'saved')
