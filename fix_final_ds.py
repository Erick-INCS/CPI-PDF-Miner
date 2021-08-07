#!/usr/bin/env python3
""" Group by state """

import pandas as pd


ds = pd.read_csv('./CPI_Mex.csv')

# Asegurarse que todos los estados tengan las mismas categorias
categories = ds['desc'].unique()
estados = ds['estado'].unique()

for est in estados:
    for cat in categories:
        if len(ds[(ds['estado'] == est) & (ds['desc'] == cat)]) > 1:
            print(est, cat)


# pd.pivot(ds.groupby(['estado', 'desc']), index='estado', columns='desc', values='municipio')
