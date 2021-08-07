#!/usr/bin/env python3
""" Fix the dataset's format """

from os import listdir
from collections import Counter
import re
from functools import reduce
from math import isnan
import pandas as pd


def read_datasets(d_dir):
    """ returns a groupped list of datasets """
    files = d_dir + pd.Series(listdir(d_dir))
    files = Counter(files.map(lambda fn: fn[:-6]))
    names = list(map(lambda s: ' '.join(s.split('_')[2:]), files.keys()))
    files = pd.Series([
        [f'{fn}_{i}.csv' for i in range(files[fn])] for fn in files])

    return files.map(
            lambda fl: [pd.read_csv(name, dtype=str) for name in fl]), names


def check_num_format(str_num):
    """ Checks if a number is complete """
    return (isinstance(str_num, float) and (not isnan(str_num))) or\
           (re.compile(r' *\d+\.\d{2} *').match(str(str_num)) is not None) or\
           (str(str_num).strip() in ('', '-'))


def is_part_num(str_num):
    """ Checks if a string is partially numeric """
    return re.compile(r' *[\.|\d]+ *').match(str_num) is not None


def is_invalid_col(dataset, col):
    """ Return True if given column is invalid """
    return dataset[col].apply(check_num_format).sum() == 0


def join_datasets(ds_list, name='', index=-1):
    """ Join multiple datasets of the same F.E. """
    # First cut
    first = ds_list[0]
    first['0'] = first['0'].str.strip()

    if not name:
        name = first[:first[first['0'] == 'ID'].index[0]]

    first = first[first[first['0'] == 'ID'].index[0]+1:]
    ds_list[0] = first

    for ix_ds, dataset in enumerate(ds_list):

        # Titulo de la categoria
        dataset['1'] = dataset['1'] + dataset['2']
        dataset = dataset.drop(['2'], axis=1)
        dataset['1'] = dataset['1'].str.strip()

        # Eliminar columna del grupo
        assert len(dataset['0'].unique()) in (3, 5), \
               f'Error de formato en {name}!'

        dataset = dataset.drop(['0'], axis=1)

        # Numeric format
        rem_cols = list(dataset.columns)[1:]
        for col in rem_cols:

            dataset[col] = dataset[col].fillna('')

            # Merge cutted column if necessary
            col_index = list(dataset.columns).index(col)
            if (dataset[col].apply(check_num_format).sum() not in
                    (0, dataset.shape[0])) and\
               (col_index > 1) and\
               ((dataset[col].astype(str).apply(is_part_num).sum() > 0) or
                   (dataset[col].isna().sum() > dataset.shape[0]/2)):

                l_invalid = is_invalid_col(
                        dataset,
                        dataset.columns[col_index-1])

                r_invalid = None
                if col_index + 1 == len(dataset.columns):
                    r_invalid = True
                else:
                    r_invalid = is_invalid_col(
                            dataset,
                            dataset.columns[col_index + 1])

                if not r_invalid and not l_invalid:
                    r_invalid = (dataset[col][
                        dataset[col].astype(str).apply(is_part_num)
                        ].astype(str).str[-1] == ' ').sum()

                    l_invalid = (dataset[col][
                        dataset[col].astype(str).apply(is_part_num)
                        ].astype(str).str[0] == ' ').sum()

                if r_invalid != l_invalid:
                    if r_invalid:
                        dataset[dataset.columns[col_index - 1]] = \
                            dataset[dataset.columns[col_index - 1]].\
                            fillna('').astype(str).str.replace('-', '') + \
                            dataset[col].astype(str).replace('NaN', '').\
                            fillna('')
                        dataset[dataset.columns[col_index - 1]] =\
                            pd.to_numeric(
                                    dataset[dataset.columns[col_index - 1]],
                                    errors='coerce')
                        dataset = dataset.drop([col], axis=1)
                    else:
                        dataset[dataset.columns[col_index + 1]] =\
                            dataset[col].astype(str).str.\
                            replace('-', '').replace('NaN', '').\
                            fillna('') +\
                            dataset[dataset.columns[col_index + 1]].\
                            astype(str).str.replace('-', '').\
                            replace('NaN', '').fillna('')
                        dataset = dataset.drop([col], axis=1)
                    continue

            dataset[col] = dataset[col].astype(str).str.strip()
            dataset[col] = pd.to_numeric(dataset[col], errors='coerce')

        dataset = dataset.dropna(how='all', axis=1)
        dataset = dataset.dropna(how='all', axis=0)

        assert len(dataset.columns) in (2, 3),\
               f'Bad columns for {name}, i:{index}.'

        ds_list[ix_ds] = dataset

    assert len(ds_list) == 2, f'Unexpected, more than 2 datasets in {name}'

    assert len(set(map(
        lambda ls: len(ls.columns),
        ds_list))) == 1, f'Different number of columns in {name}, i: {index}'

    c_names = ['desc', 'municipio']
    if len(ds_list[0].columns) == 3:
        c_names = c_names + ['aglomeracion_urbana']

    ds_list = list(map(
        lambda ds: ds.rename(columns={
            pnm[1]: c_names[pnm[0]] for pnm in enumerate(ds.columns)}),
        ds_list))

    ds_list = reduce(
        lambda ds1, ds2: ds1.append(ds2),
        ds_list).reset_index().drop(['index'], axis=1)

    ds_list['estado'] = name
    return ds_list


if __name__ == '__main__':
    datasets, ds_names = read_datasets('data/')

    the_dataset = reduce(
            lambda dsa, dsb: dsa.append(dsb),
            list(map(
                lambda zp: join_datasets(*zp),
                zip(datasets, ds_names, range(len(ds_names))))
            )
    )

    the_dataset = the_dataset.reset_index()
    the_dataset = the_dataset.drop(['index'], axis=1)
    the_dataset.to_csv('CPI_Mex.csv', index=False)
    print('Dataset', the_dataset, 'saved')
