#!/usr/bin/env python3
"""Compute time-trend derived features for top lab items per ICU stay.

Reads:
 - hosp/labevents.csv
 - outputs/cohort.csv
 - outputs/top_items.csv (optional)

Writes:
 - outputs/features_lab_derived.csv

Features per (stay_id): for each top itemid produce
 - item_{itemid}_slope (valuenum per hour)
 - item_{itemid}_delta (last - first)
 - item_{itemid}_time_to_first_hours
 - item_{itemid}_count

This script focuses on top-N items (default 20).
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path('.').resolve()
OUT = ROOT / 'outputs'
HOSP = ROOT / 'hosp'


def top_items_from_file(n=20):
    p = OUT / 'top_items.csv'
    if p.exists():
        df = pd.read_csv(p)
        # expect column named 'itemid' or first column
        if 'itemid' in df.columns:
            return df['itemid'].astype(int).tolist()[:n]
        else:
            return df.iloc[:,0].astype(int).tolist()[:n]
    return None


def main(top_n=20):
    cohort_p = OUT / 'cohort.csv'
    if not cohort_p.exists():
        raise RuntimeError('Missing outputs/cohort.csv — run etl/build_cohort.py first')

    levents_p = HOSP / 'labevents.csv'
    if not levents_p.exists():
        raise RuntimeError('Missing hosp/labevents.csv')

    cohort = pd.read_csv(cohort_p, parse_dates=['intime','outtime'])
    lab = pd.read_csv(levents_p, parse_dates=['charttime'], low_memory=False)

    # ensure valuenum exists
    if 'valuenum' not in lab.columns:
        # try to coerce value
        lab['valuenum'] = pd.to_numeric(lab.get('value', None), errors='coerce')

    # restrict lab to hadm_ids in cohort
    hadms = cohort['hadm_id'].dropna().unique().astype(int).tolist()
    lab = lab[lab['hadm_id'].isin(hadms)].copy()

    # merge cohort info (intime/outtime/stay_id) on hadm_id
    cohort_small = cohort[['stay_id','hadm_id','intime','outtime']]
    lab = lab.merge(cohort_small, on='hadm_id', how='left')

    # filter charttime within ICU stay
    lab = lab[(lab['charttime'] >= lab['intime']) & (lab['charttime'] <= lab['outtime'])].copy()

    # determine top items
    top = top_items_from_file(top_n)
    if top is None:
        top = lab['itemid'].value_counts().head(top_n).index.astype(int).tolist()

    # keep only relevant itemids
    lab = lab[lab['itemid'].isin(top)]

    # compute hours from intime
    lab['hours_from_intime'] = (lab['charttime'] - lab['intime']).dt.total_seconds()/3600.0

    rows = []
    # group by stay + itemid
    grouped = lab.groupby(['stay_id','itemid'])
    for (stay_id, itemid), g in grouped:
        # drop rows where valuenum is missing so times align with values
        g_nonnull = g.dropna(subset=['valuenum']).copy()
        vals = g_nonnull['valuenum'].values
        times = g_nonnull['hours_from_intime'].values
        if len(vals) == 0:
            continue
        count = int(len(vals))
        # compute first/last by time
        first_idx = int(np.argmin(times))
        last_idx = int(np.argmax(times))
        first_val = float(vals[first_idx])
        last_val = float(vals[last_idx])
        delta = last_val - first_val if count >= 2 else 0.0
        time_to_first = float(times.min())
        slope = np.nan
        if count >= 2:
            try:
                slope = float(np.polyfit(times, vals, 1)[0])
            except Exception:
                slope = np.nan
        rows.append({'stay_id': stay_id, 'itemid': int(itemid), 'count': count, 'first_val': first_val, 'last_val': last_val, 'delta': delta, 'time_to_first_hours': time_to_first, 'slope_per_hour': slope})

    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError('No lab events found for selected stays/items')

    # pivot to wide
    def pivot_agg(col, new_suffix):
        p = df.pivot(index='stay_id', columns='itemid', values=col)
        p.columns = [f'item_{int(c)}_{new_suffix}' for c in p.columns]
        return p

    wide = []
    wide.append(pivot_agg('slope_per_hour', 'slope'))
    wide.append(pivot_agg('delta', 'delta'))
    wide.append(pivot_agg('time_to_first_hours', 'time_to_first_hours'))
    wide.append(pivot_agg('count', 'count'))

    wide_df = pd.concat(wide, axis=1).reset_index()

    # merge with cohort to include labels
    out = cohort.merge(wide_df, on='stay_id', how='left')
    OUT.mkdir(exist_ok=True)
    out.to_csv(OUT / 'features_lab_derived.csv', index=False)
    print('Wrote outputs/features_lab_derived.csv with derived trend features')


if __name__ == '__main__':
    main()
