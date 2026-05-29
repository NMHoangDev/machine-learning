#!/usr/bin/env python3
"""Temporal-split evaluation and simple imbalance handling.

Usage: py -3 models/evaluate_temporal.py
Reads: outputs/features_lab.csv
Writes: outputs/model_metrics_temporal.json
"""
from pathlib import Path
import pandas as pd
import numpy as np
import json

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, roc_curve, confusion_matrix

try:
    import xgboost as xgb
except Exception:
    xgb = None


ROOT = Path('.').resolve()
OUT = ROOT / 'outputs'


def numeric_feature_selection(df, min_nonnull_frac=0.1, min_var=1e-6):
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
    feats = pd.read_csv(OUT / 'features_lab.csv', parse_dates=['intime'])
    if 'intime' not in feats.columns:
        raise RuntimeError('features_lab.csv must contain intime for temporal split')

    # sort by intime and split at median date
    feats = feats.sort_values('intime')
    median_idx = len(feats)//2
    split_time = feats['intime'].iloc[median_idx]

    train = feats[feats['intime'] <= split_time].copy()
    test = feats[feats['intime'] > split_time].copy()

    y_train = train['in_icu_mortality'].fillna(0).astype(int)
    y_test = test['in_icu_mortality'].fillna(0).astype(int)

    X_train = numeric_feature_selection(train.drop(columns=['in_icu_mortality','in_hospital_mortality','stay_id','subject_id','hadm_id','intime','outtime'], errors='ignore'))
    X_test = numeric_feature_selection(test.drop(columns=['in_icu_mortality','in_hospital_mortality','stay_id','subject_id','hadm_id','intime','outtime'], errors='ignore'))

    # align columns
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

    # Logistic with class balancing
    lr = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
    lr.fit(X_train_s, y_train)
    results['logistic_temporal'] = evaluate_model(lr, X_train_s, y_train, X_test_s, y_test)

    # XGBoost with scale_pos_weight
    if xgb is not None:
        pos = y_train.sum()
        neg = len(y_train) - pos
        scale = float(neg / pos) if pos > 0 else 1.0
        xgb_clf = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', verbosity=0, random_state=42, scale_pos_weight=scale, n_jobs=1)
        xgb_clf.fit(X_train_imp, y_train)
        results['xgb_temporal'] = evaluate_model(xgb_clf, X_train_imp, y_train, X_test_imp, y_test)

    # Save
    with open(OUT / 'model_metrics_temporal.json', 'w', encoding='utf8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print('Saved temporal metrics to outputs/model_metrics_temporal.json')
    print(results)


if __name__ == '__main__':
    main()
