#!/usr/bin/env python3
"""Map feature names (item_<<itemid>>_agg) to lab item labels using d_labitems and d_items.

Writes: outputs/feature_mapping.csv and outputs/data_dictionary.csv
"""
from pathlib import Path
import re
import pandas as pd

ROOT = Path('.').resolve()
OUT = ROOT / 'outputs'


def load_lab_dicts():
    lab_paths = [ROOT / 'hosp' / 'd_labitems.csv', ROOT / 'icu' / 'd_items.csv']
    dfs = []
    for p in lab_paths:
        if p.exists():
            try:
                dfs.append(pd.read_csv(p))
            except Exception:
                pass
    if not dfs:
        raise RuntimeError('Could not find d_labitems.csv or d_items.csv in hosp/ or icu/')
    df = pd.concat(dfs, ignore_index=True, sort=False)
    # normalize columns
    if 'itemid' not in df.columns:
        # try 'id' fallback
        if 'id' in df.columns:
            df = df.rename(columns={'id':'itemid'})
    return df


def parse_feature(name):
    m = re.match(r'^item_(\d+)_(.+)$', name)
    if not m:
        return None, None
    return int(m.group(1)), m.group(2)


def main():
    OUT.mkdir(exist_ok=True)
    lab_df = load_lab_dicts()
    # index by itemid
    lab_df = lab_df.drop_duplicates(subset=['itemid']).set_index('itemid')

    # read shap summary if available, otherwise read features from outputs/features_lab.csv
    shap_path = OUT / 'shap_summary.csv'
    if shap_path.exists():
        feats = pd.read_csv(shap_path)
        feat_names = feats['feature'].tolist()
    else:
        feats_path = OUT / 'features_lab.csv'
        if not feats_path.exists():
            raise RuntimeError('Neither outputs/shap_summary.csv nor outputs/features_lab.csv found')
        df = pd.read_csv(feats_path, nrows=1)
        feat_names = [c for c in df.columns if c.startswith('item_')]

    rows = []
    for f in feat_names:
        itemid, agg = parse_feature(f)
        if itemid is None:
            rows.append({'feature': f, 'itemid': None, 'agg': None, 'label': None, 'category': None, 'notes': 'unparsed_feature'})
            continue
        meta = lab_df.loc[itemid] if itemid in lab_df.index else None
        label = meta.get('label') if meta is not None and 'label' in meta else None
        category = None
        loinc = None
        if meta is not None:
            for k in ('category', 'fluid', 'loinc_code', 'loinc'): 
                if k in meta:
                    category = meta.get(k)
                    break
        rows.append({'feature': f, 'itemid': int(itemid), 'agg': agg, 'label': label, 'category': category})

    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUT / 'feature_mapping.csv', index=False)

    # write a simple data dictionary from lab_df
    dict_cols = [c for c in ['label','fluid','category','loinc_code','loinc'] if c in lab_df.columns]
    if dict_cols:
        dd = lab_df.reset_index()[['itemid'] + dict_cols]
    else:
        dd = lab_df.reset_index()[['itemid']]
    dd.to_csv(OUT / 'data_dictionary.csv', index=False)

    print('Wrote outputs/feature_mapping.csv and outputs/data_dictionary.csv')


if __name__ == '__main__':
    main()
