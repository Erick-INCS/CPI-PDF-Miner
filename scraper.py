#!/usr/bin/env python3
""" Fetchs all the pdf files """

import requests
import re
from bs4 import BeautifulSoup

URL = 'https://onuhabitat.org.mx/index.php/' +\
      'indice-de-las-ciudades-prosperas-cpi-mexico-2018'

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;' +
              'q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,' +
              'application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36' +
                  ' (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36}'
}


def get_urls(base_url):
    """ Get all the pdf files urls """
    res = requests.get(base_url, headers=HEADERS)
    res = BeautifulSoup(res.text, 'html.parser')
    res = res.find_all(href=re.compile('pdf'))
    return res


def download_files(links, directory=''):
    """ Download all files """
    links = list(map(
        lambda lk: lk.attrs['href'],
        links))

    def download_and_save(url):
        print('\nDownloading:', url)
        req = requests.get(url, verify=False)
        with open(directory + '_'.join(url.split('/')[-2:]), 'wb') as pdf:
            pdf.write(req.content)

    list(map(
        download_and_save,
        links))


if __name__ == '__main__':
    content = get_urls(URL)
    download_files(content, 'pdfs/')

    print('Done.')
