# The Mexican CPI Dataset
This repository contains a series of python scripts to generate the CPI (City Prosperity Index) dataset for 305 municipalities in Mexico.

## Setup
The use of a virtual environment is recommended.
```bash
python -m venv venv
source venv/bin/activate
```

### Required directories
- data
- pdfs

### Install dependecies
```bash
pip install -r requirements.txt
```

## Download all the PDFs
This dataset is made from the tables in 305 pdf files.
The command to download the files is as follows:
```bash
./scraper.py
```

## Extract the tables from the PDFs
```bash
./extractor.py
```

## Generate the final dataset
```bash
./preprocess.py
./fix_final_ds.py
```
After executing the above command the files `CPI_Mex.csv` and `CPI_Mex_full.csv` are generated.
