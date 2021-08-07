#!/usr/bin/env python3
""" Extract all tables from the stored PDF files """

from extract import extract_and_save
from os import listdir
import pandas as pd

PDF_DIR = 'pdfs/'
DATA_DIR = 'data/'


def extract_all(pdfs_dir, data_dir):
    """ As the name says """
    files = pd.Series(listdir(pdfs_dir))
    (pdfs_dir + files).apply(extract_and_save, args=[data_dir])


# Start!
extract_all(PDF_DIR, DATA_DIR)
