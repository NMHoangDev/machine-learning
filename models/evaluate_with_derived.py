#!/usr/bin/env python3
"""Evaluate models using original lab features + derived trend features.

Usage: py -3 models/evaluate_with_derived.py
Reads: outputs/features_lab.csv, outputs/features_lab_derived.csv
Writes: outputs/model_metrics_with_derived.json, outputs/xgb_with_derived.joblib, outputs/lr_with_derived.joblib
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, roc_curve, confusion_matrix
from joblib import dump

try:
    import xgboost as xgb
except Exception:
    xgb = None

ROOT = Path('.').resolve()
OUT = ROOT / 'outputs'


def numeric_feature_selection(df, min_nonnull_frac=0.05, min_var=1e-8):
    num = df.select_dtypes(include=[np.number])
    keep = num.columns[(num.notna().mean() >= min_nonnull_frac) & (num.var() >= min_var)]
    return num[keep]


def choose_threshold(y_true, y_score):
    fpr, tpr, thr = roc_curve(y_true, y_score)
    youden = tpr - fpr
    idx = np.argmax(youden)
    return float(thr[idx])


def evaluate_model(clf, X_train, y_train, X_test, y_test, pred_proba=None):
    if pred_proba is None:
        pred_proba = clf.predict_proba(X_test)[:,1]
    auc = float(roc_auc_score(y_test, pred_proba))
    auprc = float(average_precision_score(y_test, pred_proba))
    brier = float(brier_score_loss(y_test, pred_proba))
    thr = choose_threshold(y_test, pred_proba)
    preds = (pred_proba >= thr).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, preds).ravel()
    sens = tp / (tp + fn) if (tp+fn)>0 else 0.0
    spec = tn / (tn + fp) if (tn+fp)>0 else 0.0
    return dict(auc=auc, auprc=auprc, brier=brier, threshold=thr, sensitivity=sens, specificity=spec)


def main():
    f1 = OUT / 'features_lab.csv'
    f2 = OUT / 'features_lab_derived.csv'
    if not f1.exists() or not f2.exists():
        raise RuntimeError('Missing feature files in outputs/. Run feature builders first')

    df1 = pd.read_csv(f1, parse_dates=['intime'])
    df2 = pd.read_csv(f2, parse_dates=['intime']) if 'intime' in pd.read_csv(f2, nrows=0).columns else pd.read_csv(f2)

    # merge on stay_id
    if 'stay_id' not in df1.columns:
        raise RuntimeError('features_lab.csv must contain stay_id')
    if 'stay_id' not in df2.columns:
        raise RuntimeError('features_lab_derived.csv must contain stay_id')

    merged = df1.merge(df2.drop(columns=['intime','outtime'], errors='ignore'), on='stay_id', how='left', suffixes=('_orig','_der'))

    # ensure intime exists for temporal split
    if 'intime' not in merged.columns:
        raise RuntimeError('Merged features must contain `intime` for temporal split')

    merged = merged.sort_values('intime')
    median_idx = len(merged)//2
    split_time = merged['intime'].iloc[median_idx]

    train = merged[merged['intime'] <= split_time].copy()
    test = merged[merged['intime'] > split_time].copy()

    # Ensure label column exists; try common names, otherwise merge from outputs/cohort.csv
    label_candidates = ['in_icu_mortality', 'icu_mortality', 'in_hospital_mortality', 'hospital_expire_flag']
    label_col = None
    for c in label_candidates:
        if c in merged.columns:
            label_col = c
            break

    if label_col is None:
        # try to load cohort and merge label
        cohort_p = OUT / 'cohort.csv'
        if cohort_p.exists():
            cohort = pd.read_csv(cohort_p, usecols=['stay_id','in_icu_mortality'] if 'in_icu_mortality' in pd.read_csv(cohort_p, nrows=0).columns else ['stay_id'], parse_dates=['intime'], low_memory=False)
            if 'in_icu_mortality' in cohort.columns:
                merged = merged.merge(cohort[['stay_id','in_icu_mortality']], on='stay_id', how='left')
                label_col = 'in_icu_mortality'
    if label_col is None:
        raise RuntimeError('Could not find a mortality label column in merged features or outputs/cohort.csv')

    y_train = train[label_col].fillna(0).astype(int)
    y_test = test[label_col].fillna(0).astype(int)

    drop_cols = ['in_icu_mortality','in_hospital_mortality','stay_id','subject_id','hadm_id','intime','outtime']
    X_train = numeric_feature_selection(train.drop(columns=drop_cols, errors='ignore'))
    X_test = numeric_feature_selection(test.drop(columns=drop_cols, errors='ignore'))

    # align
    common = X_train.columns.intersection(X_test.columns)
    X_train = X_train[common]
    X_test = X_test[common]

    imputer = SimpleImputer(strategy='median')
    scaler = StandardScaler()

    X_train_imp = imputer.fit_transform(X_train)
    X_test_imp = imputer.transform(X_test)
    X_train_s = scaler.fit_transform(X_train_imp)
    X_test_s = scaler.transform(X_test_imp)

    results = {}

    lr = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
    lr.fit(X_train_s, y_train)
    results['logistic_with_derived'] = evaluate_model(lr, X_train_s, y_train, X_test_s, y_test)
    dump(lr, OUT / 'lr_with_derived.joblib')

    if xgb is not None:
        pos = y_train.sum()
        neg = len(y_train) - pos
        scale = float(neg / pos) if pos > 0 else 1.0
        xgb_clf = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', verbosity=0, random_state=42, scale_pos_weight=scale, n_jobs=1)
        xgb_clf.fit(X_train_imp, y_train)
        results['xgb_with_derived'] = evaluate_model(xgb_clf, X_train_imp, y_train, X_test_imp, y_test)
        dump(xgb_clf, OUT / 'xgb_with_derived.joblib')

    with open(OUT / 'model_metrics_with_derived.json', 'w', encoding='utf8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print('Saved metrics to outputs/model_metrics_with_derived.json')
    print(results)


if __name__ == '__main__':
    main()
