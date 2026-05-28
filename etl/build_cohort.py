#!/usr/bin/env python3
"""Build ICU cohort and labels (in-ICU mortality, in-hospital mortality).

Outputs: outputs/cohort.csv
"""
from pathlib import Path
import pandas as pd
import json


ROOT = Path('.').resolve()
ICU = ROOT / 'icu'
HOSP = ROOT / 'hosp'
OUT = ROOT / 'outputs'
OUT.mkdir(exist_ok=True)


def main():
    icustays = pd.read_csv(ICU / 'icustays.csv', parse_dates=['intime','outtime'])
    admissions = pd.read_csv(HOSP / 'admissions.csv', parse_dates=['admittime','dischtime','deathtime'])
    patients = pd.read_csv(HOSP / 'patients.csv', parse_dates=['dod'])

    # merge admissions/patients info for hadm_id
    adm = admissions[['subject_id','hadm_id','admittime','dischtime','deathtime','hospital_expire_flag']]
    pat = patients[['subject_id','dod']]

    icu = icustays.merge(adm, on=['subject_id','hadm_id'], how='left')
    icu = icu.merge(pat, on='subject_id', how='left')

    # label: in-ICU death if deathtime or dod within [intime, outtime]
    def in_interval(ts, start, end):
        if pd.isna(ts):
            return False
        return (ts >= start) & (ts <= end)

    icu['in_icu_mortality'] = icu.apply(lambda r: int(in_interval(r['deathtime'], r['intime'], r['outtime']) or in_interval(r['dod'], r['intime'], r['outtime'])), axis=1)
    # in-hospital mortality from hospital_expire_flag (if available)
    icu['in_hospital_mortality'] = icu['hospital_expire_flag'].fillna(0).astype(int)

    outf = OUT / 'cohort.csv'
    icu.to_csv(outf, index=False)
    print('Wrote cohort to', outf)


if __name__ == '__main__':
    main()
