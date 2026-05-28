#!/usr/bin/env python3
"""Aggregate lab events into per-stay features.

Inputs: outputs/top_items.csv, hosp/labevents.csv, outputs/cohort.csv
Outputs: outputs/features_lab.csv
"""
from pathlib import Path
import pandas as pd
import numpy as np


ROOT = Path('.').resolve()
HOSP = ROOT / 'hosp'
OUT = ROOT / 'outputs'
OUT.mkdir(exist_ok=True)


def to_numeric(x):
    try:
        return float(x)
    except Exception:
        try:
            return float(str(x).replace(',',''))
        except Exception:
            return np.nan


def main():
    top = pd.read_csv(OUT / 'top_items.csv')
    itemids = top['itemid'].astype(int).tolist()

    labevents = pd.read_csv(HOSP / 'labevents.csv', parse_dates=['charttime','storetime'])
    cohort = pd.read_csv(OUT / 'cohort.csv', parse_dates=['intime','outtime'])

    # keep only lab events for target itemids and hadm_ids present in cohort
    hadm_set = set(cohort['hadm_id'].dropna().unique())
    le = labevents[labevents['itemid'].isin(itemids) & labevents['hadm_id'].isin(hadm_set)].copy()

    # numeric conversion
    le['valuenum'] = pd.to_numeric(le['valuenum'], errors='coerce')
    # attempt parsing text values into valuenum when missing
    mask = le['valuenum'].isna() & le['value'].notna()
    if mask.any():
        le.loc[mask, 'valuenum'] = le.loc[mask, 'value'].apply(to_numeric)

    # merge intime/outtime for hadm_id to filter per stay
    cohort_small = cohort[['hadm_id','stay_id','intime','outtime']]
    le = le.merge(cohort_small, on='hadm_id', how='left')
    # filter by charttime in [intime,outtime]
    le = le[(le['charttime']>=le['intime']) & (le['charttime']<=le['outtime'])]

    # groupby stay_id and itemid
    aggs = []
    for iid in itemids:
        sub = le[le['itemid']==iid]
        if sub.empty:
            continue
        grp = sub.groupby('stay_id')
        df = grp['valuenum'].agg(['last','mean','min','max','std','count']).rename(columns={
            'last':f'item_{iid}_last', 'mean':f'item_{iid}_mean','min':f'item_{iid}_min','max':f'item_{iid}_max','std':f'item_{iid}_std','count':f'item_{iid}_count'
        })
        # time to first
        first = grp['charttime'].min().rename(f'item_{iid}_time_to_first_hours')
        df = df.join(first)
        # percent abnormal
        pct_ab = grp.apply(lambda g: (g['flag']=='abnormal').sum()/len(g)).rename(f'item_{iid}_pct_abnormal')
        df = df.join(pct_ab)
        aggs.append(df)

    if not aggs:
        print('No lab aggregates produced')
        return

    feats = pd.concat(aggs, axis=1)
    feats.reset_index(inplace=True)

    # join labels
    labels = cohort[['stay_id','subject_id','hadm_id','intime','outtime','in_icu_mortality','in_hospital_mortality']]
    outdf = labels.merge(feats, on='stay_id', how='left')

    outf = OUT / 'features_lab.csv'
    outdf.to_csv(outf, index=False)
    print('Wrote features to', outf)


if __name__ == '__main__':
    main()
