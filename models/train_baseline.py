#!/usr/bin/env python3
"""Train baseline models (LogisticRegression, XGBoost) on lab features.

Input: outputs/features_lab.csv
Saves: outputs/model_metrics.json
"""
from pathlib import Path
import pandas as pd
import numpy as np
import json

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score

try:
    import xgboost as xgb
except Exception:
    xgb = None


ROOT = Path('.').resolve()
OUT = ROOT / 'outputs'
OUT.mkdir(exist_ok=True)


def main():
    feats = pd.read_csv(OUT / 'features_lab.csv', parse_dates=['intime'])
    # label
    y = feats['in_icu_mortality'].fillna(0).astype(int)

    # Drop identifiers and non-numeric columns (datetimes, strings)
    drop_cols = ['in_icu_mortality','in_hospital_mortality','stay_id','subject_id','hadm_id']
    X_all = feats.drop(columns=drop_cols, errors='ignore')
    # Remove datetime columns if present
    for c in ['intime','outtime','admittime','dischtime']:
        if c in X_all.columns:
            X_all = X_all.drop(columns=[c])

    # keep only numeric columns
    X = X_all.select_dtypes(include=[np.number]).copy()
    if X.shape[1] == 0:
        raise RuntimeError('No numeric features found for training. Check features_lab.csv')

    # simple split: stratified random split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    imputer = SimpleImputer(strategy='median')
    scaler = StandardScaler()

    X_train_imp = imputer.fit_transform(X_train)
    X_test_imp = imputer.transform(X_test)
    X_train_s = scaler.fit_transform(X_train_imp)
    X_test_s = scaler.transform(X_test_imp)

    results = {}

    # Logistic Regression
    lr = LogisticRegression(max_iter=1000)
    lr.fit(X_train_s, y_train)
    p_lr = lr.predict_proba(X_test_s)[:,1]
    results['logistic_auc'] = float(roc_auc_score(y_test, p_lr))
    results['logistic_auprc'] = float(average_precision_score(y_test, p_lr))

    # XGBoost
    if xgb is not None:
        # avoid deprecated/unused parameters (use_label_encoder deprecated in newer xgboost)
        model = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', verbosity=0, random_state=42, n_jobs=1)
        model.fit(X_train_imp, y_train)
        p_xgb = model.predict_proba(X_test_imp)[:,1]
        results['xgb_auc'] = float(roc_auc_score(y_test, p_xgb))
        results['xgb_auprc'] = float(average_precision_score(y_test, p_xgb))

    with open(OUT / 'model_metrics.json', 'w', encoding='utf8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print('Results:', results)


if __name__ == '__main__':
    main()
