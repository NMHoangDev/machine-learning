#!/usr/bin/env python3
"""Remove flagged leaky features and retrain models (temporal split).

Usage: py -3 models/remove_leaky_and_retrain.py
Reads: outputs/suspicious_features.txt, outputs/features_lab.csv, outputs/features_lab_derived.csv
Writes: outputs/dropped_features.txt, outputs/model_metrics_cleaned.json, outputs/xgb_cleaned.joblib, outputs/lr_cleaned.joblib
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


def read_suspicious():
    p = OUT / 'suspicious_features.txt'
    if not p.exists():
        return []
    rows = []
    for line in p.read_text(encoding='utf8').splitlines():
        if not line.strip():
            continue
        parts = line.split(',')
        rows.append(parts[0].strip())
    return rows


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

    merged = df1.merge(df2.drop(columns=['intime','outtime'], errors='ignore'), on='stay_id', how='left', suffixes=('_orig','_der'))

    # find label BEFORE dropping any suspicious columns so we don't remove the true label
    label_candidates = ['in_icu_mortality','icu_mortality','in_hospital_mortality','hospital_expire_flag']
    label_col = None
    for c in label_candidates:
        if c in merged.columns:
            label_col = c
            break
    # if label still missing, try to merge from cohort
    if label_col is None:
        cohort_p = OUT / 'cohort.csv'
        if cohort_p.exists():
            cohort = pd.read_csv(cohort_p, usecols=['stay_id','in_icu_mortality'] if 'in_icu_mortality' in pd.read_csv(cohort_p, nrows=0).columns else ['stay_id'])
            if 'in_icu_mortality' in cohort.columns:
                merged = merged.merge(cohort[['stay_id','in_icu_mortality']], on='stay_id', how='left')
                label_col = 'in_icu_mortality'

    # load suspicious list and create drop set
    suspect = set(read_suspicious())
    # also drop any column that clearly encodes outcome, but never drop the confirmed label
    leak_patterns = ['in_hospital', 'in_icu', 'hospital_expire', 'los']
    drop_cols = set(suspect)
    for c in merged.columns:
        for p in leak_patterns:
            if p in c and c != label_col:
                drop_cols.add(c)

    # never drop ids used for merging or the label
    protected = set(['stay_id','subject_id','hadm_id','intime','outtime'])
    if label_col is not None:
        protected.add(label_col)
    drop_cols = [c for c in drop_cols if c in merged.columns and c not in protected]

    # save dropped list
    OUT.mkdir(exist_ok=True)
    (OUT / 'dropped_features.txt').write_text('\n'.join(drop_cols), encoding='utf8')

    cleaned = merged.drop(columns=drop_cols, errors='ignore')

    # temporal split
    if 'intime' not in cleaned.columns:
        raise RuntimeError('features must include intime for temporal split')
    cleaned = cleaned.sort_values('intime')
    median_idx = len(cleaned)//2
    split_time = cleaned['intime'].iloc[median_idx]
    train = cleaned[cleaned['intime'] <= split_time].copy()
    test = cleaned[cleaned['intime'] > split_time].copy()

    # find label
    label_candidates = ['in_icu_mortality','icu_mortality','in_hospital_mortality','hospital_expire_flag']
    label_col = None
    for c in label_candidates:
        if c in cleaned.columns:
            label_col = c
            break
    if label_col is None:
        cohort_p = OUT / 'cohort.csv'
        if cohort_p.exists():
            cohort = pd.read_csv(cohort_p, usecols=['stay_id','in_icu_mortality'] if 'in_icu_mortality' in pd.read_csv(cohort_p, nrows=0).columns else ['stay_id'])
            if 'in_icu_mortality' in cohort.columns:
                cleaned = cleaned.merge(cohort[['stay_id','in_icu_mortality']], on='stay_id', how='left')
                label_col = 'in_icu_mortality'
    if label_col is None:
        raise RuntimeError('Could not find label column')

    y_train = train[label_col].fillna(0).astype(int)
    y_test = test[label_col].fillna(0).astype(int)

    drop_cols_for_model = [label_col,'stay_id','subject_id','hadm_id','intime','outtime']
    X_train = train.drop(columns=drop_cols_for_model, errors='ignore')
    X_test = test.drop(columns=drop_cols_for_model, errors='ignore')

    # select numeric
    X_train = X_train.select_dtypes(include=[np.number])
    X_test = X_test.select_dtypes(include=[np.number])

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
    results['logistic_cleaned'] = evaluate_model(lr, X_train_s, y_train, X_test_s, y_test)
    dump(lr, OUT / 'lr_cleaned.joblib')

    if xgb is not None:
        pos = y_train.sum()
        neg = len(y_train) - pos
        scale = float(neg / pos) if pos > 0 else 1.0
        xgb_clf = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', verbosity=0, random_state=42, scale_pos_weight=scale, n_jobs=1)
        xgb_clf.fit(X_train_imp, y_train)
        results['xgb_cleaned'] = evaluate_model(xgb_clf, X_train_imp, y_train, X_test_imp, y_test)
        dump(xgb_clf, OUT / 'xgb_cleaned.joblib')

    with open(OUT / 'model_metrics_cleaned.json', 'w', encoding='utf8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print('Dropped features:')
    for c in drop_cols:
        print(' -', c)
    print('Saved cleaned metrics to outputs/model_metrics_cleaned.json')


if __name__ == '__main__':
    main()
