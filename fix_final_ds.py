#!/usr/bin/env python3
""" Group by state """

import pandas as pd

ds = pd.read_csv('./CPI_Mex.csv')
estados = pd.read_csv('Names.csv')

ds = ds.join(estados[['clave', 'estado']].set_index('clave'), on='clave')
ds = pd.pivot(
        ds,
        index=['estado', 'municipio'],
        columns='desc',
        values='calificacion')

ds.to_csv('CPI_Mex_full.csv', index=False)
