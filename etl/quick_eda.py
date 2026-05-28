#!/usr/bin/env python3
"""Quick EDA for Lab Events and ICU stays.

Usage: run from repository root: python etl/quick_eda.py
Outputs: outputs/summary.json, outputs/top_items.csv
"""
import json
from pathlib import Path
import sys

try:
    import pandas as pd
    import numpy as np
except Exception as e:
    print("Required packages not installed. Please install from requirements.txt")
    raise


ROOT = Path('.').resolve()
HOSP = ROOT / 'hosp'
ICU = ROOT / 'icu'
OUT = ROOT / 'outputs'
OUT.mkdir(exist_ok=True)


def safe_read_csv(p, **kwargs):
    if not p.exists():
        print(f"Missing file: {p}")
        return None
    return pd.read_csv(p, **kwargs)


def main():
    print('Loading files (may be large)...')
    icustays = safe_read_csv(ICU / 'icustays.csv', parse_dates=['intime','outtime'])
    labevents = safe_read_csv(HOSP / 'labevents.csv', parse_dates=['charttime','storetime'])
    d_labitems = safe_read_csv(HOSP / 'd_labitems.csv')
    patients = safe_read_csv(HOSP / 'patients.csv')
    admissions = safe_read_csv(HOSP / 'admissions.csv', parse_dates=['admittime','dischtime','deathtime'])

    summary = {}
    if icustays is None or labevents is None:
        print('Required files missing, aborting.')
        sys.exit(1)

    summary['n_icustays'] = int(len(icustays))
    summary['n_labevents'] = int(len(labevents))
    summary['n_unique_itemid'] = int(labevents['itemid'].nunique())

    # top itemids
    top = labevents['itemid'].value_counts().head(20).rename_axis('itemid').reset_index(name='count')
    if d_labitems is not None:
        top = top.merge(d_labitems[['itemid','label']], on='itemid', how='left')
    top.to_csv(OUT / 'top_items.csv', index=False)
    summary['top_items_file'] = str(OUT / 'top_items.csv')

    # missing & text values
    summary['percent_missing_valuenum'] = float(labevents['valuenum'].isna().mean())
    # detect non-numeric value occurrences where valuenum is NA
    mask_val_text = labevents['valuenum'].isna() & labevents['value'].notna()
    sample_vals = labevents.loc[mask_val_text, 'value'].dropna().astype(str)
    non_numeric_count = 0
    if len(sample_vals) > 0:
        conv = pd.to_numeric(sample_vals, errors='coerce')
        non_numeric_count = int((conv.isna()).sum())
    summary['approx_non_numeric_value_count_when_valuenum_NA'] = non_numeric_count

    # Coverage: percent of icu hadm_ids with at least one top-lab measurement
    icu_hadm = set(icustays['hadm_id'].dropna().unique())
    coverage = []
    for _, row in top.iterrows():
        iid = row['itemid']
        hadm_with = set(labevents.loc[labevents['itemid']==iid, 'hadm_id'].dropna().unique())
        in_icu = len(icu_hadm & hadm_with)
        coverage.append({'itemid': int(iid), 'count': int(row['count']), 'hadm_in_icu_with_item': in_icu})
    summary['coverage_top_items'] = coverage

    # simple label prevalence (hospital_expire_flag in admissions)
    if admissions is not None:
        admissions_icustays = admissions[admissions['hadm_id'].isin(icustays['hadm_id'].unique())]
        if 'hospital_expire_flag' in admissions_icustays.columns:
            summary['in_hospital_mortality_rate_among_icustays'] = float(admissions_icustays['hospital_expire_flag'].mean())

    # Save summary
    with open(OUT / 'summary.json', 'w', encoding='utf8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print('Summary written to', OUT / 'summary.json')
    print('Top items written to', OUT / 'top_items.csv')


if __name__ == '__main__':
    main()
