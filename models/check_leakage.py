#!/usr/bin/env python3
"""Detect potential leakage in merged features.

Usage: py -3 models/check_leakage.py
Reads: outputs/features_lab.csv, outputs/features_lab_derived.csv, outputs/cohort.csv (if needed)
Writes: outputs/leakage_report.csv and outputs/suspicious_features.txt
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path('.').resolve()
OUT = ROOT / 'outputs'


def find_label(merged):
    candidates = ['in_icu_mortality','icu_mortality','in_hospital_mortality','hospital_expire_flag']
    for c in candidates:
        if c in merged.columns:
            return c
    # try cohort
    cohort_p = OUT / 'cohort.csv'
    if cohort_p.exists():
        cohort = pd.read_csv(cohort_p, usecols=['stay_id','in_icu_mortality'] if 'in_icu_mortality' in pd.read_csv(cohort_p, nrows=0).columns else ['stay_id'])
        if 'in_icu_mortality' in cohort.columns:
            merged = merged.merge(cohort[['stay_id','in_icu_mortality']], on='stay_id', how='left')
            return 'in_icu_mortality'
    return None


def main():
    f1 = OUT / 'features_lab.csv'
    f2 = OUT / 'features_lab_derived.csv'
    if not f1.exists() or not f2.exists():
        raise RuntimeError('Missing feature files in outputs/. Run feature builders first')

    df1 = pd.read_csv(f1, parse_dates=['intime'])
    df2 = pd.read_csv(f2, parse_dates=['intime']) if 'intime' in pd.read_csv(f2, nrows=0).columns else pd.read_csv(f2)
    merged = df1.merge(df2.drop(columns=['intime','outtime'], errors='ignore'), on='stay_id', how='left', suffixes=('_orig','_der'))

    label_col = find_label(merged)
    if label_col is None:
        raise RuntimeError('Could not find label column in merged features or cohort.csv')

    y = merged[label_col].fillna(0).astype(int)

    # select numeric feature columns excluding ids and times
    exclude = set(['stay_id','subject_id','hadm_id','intime','outtime', label_col])
    num = merged.select_dtypes(include=[np.number]).columns.tolist()
    feats = [c for c in num if c not in exclude]

    rows = []
    suspicious = []
    for f in feats:
        vals = merged[f].values
        nan_frac = float(np.isnan(vals).mean())
        # use pandas to get unique values ignoring NaNs (np.nanunique may not exist)
        uniq = pd.Series(vals).dropna().unique()
        var = float(np.nanvar(vals))
        info = {'feature': f, 'nan_frac': nan_frac, 'n_unique': int(len(uniq)), 'var': var}
        # compute AUC if feature is not constant and not all nan
        try:
            if var > 0 and nan_frac < 1.0:
                # need finite values
                mask = np.isfinite(vals)
                if mask.sum() > 10:
                    auc = float(roc_auc_score(y[mask], vals[mask]))
                else:
                    auc = None
            else:
                auc = None
        except Exception:
            auc = None
        info['auc_single_feature'] = auc
        rows.append(info)

        # flag suspicious
        if auc is not None and auc >= 0.98:
            suspicious.append((f, 'high_auc', auc))
        if var == 0.0:
            suspicious.append((f, 'zero_variance', var))
        if nan_frac > 0.9:
            suspicious.append((f, 'mostly_missing', nan_frac))

    report = pd.DataFrame(rows).sort_values('auc_single_feature', ascending=False)
    OUT.mkdir(exist_ok=True)
    report.to_csv(OUT / 'leakage_report.csv', index=False)

    with open(OUT / 'suspicious_features.txt', 'w', encoding='utf8') as fh:
        for s in suspicious:
            fh.write(f"{s[0]},{s[1]},{s[2]}\n")

    print('Wrote outputs/leakage_report.csv and outputs/suspicious_features.txt')
    print('Top suspicious features:')
    for s in suspicious[:20]:
        print(s)


if __name__ == '__main__':
    main()
