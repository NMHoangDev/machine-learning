#!/usr/bin/env python3
"""Post-hoc threshold sweep and calibration data for temporal XGBoost model.

Usage: py -3 models/posthoc_thresholds_and_calibration.py
Reads: outputs/features_lab.csv
Writes: outputs/xgb_temporal_model.joblib, outputs/model_posthoc.json,
        outputs/thresholds_metrics.csv, outputs/calibration_xgb.npz
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, confusion_matrix, f1_score, precision_score
from sklearn.calibration import calibration_curve
from joblib import dump

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


def threshold_metrics(y_true, probs, thresholds):
    rows = []
    for t in thresholds:
        preds = (probs >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, preds).ravel()
        sens = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        prec = precision_score(y_true, preds, zero_division=0)
        f1 = f1_score(y_true, preds, zero_division=0)
        rows.append({'threshold': float(t), 'sensitivity': sens, 'specificity': spec, 'precision': prec, 'f1': f1, 'tp': int(tp), 'fp': int(fp), 'tn': int(tn), 'fn': int(fn)})
    return pd.DataFrame(rows)


def main():
    feats = pd.read_csv(OUT / 'features_lab.csv', parse_dates=['intime'])
    feats = feats.sort_values('intime')
    median_idx = len(feats)//2
    split_time = feats['intime'].iloc[median_idx]
    train = feats[feats['intime'] <= split_time].copy()
    test = feats[feats['intime'] > split_time].copy()

    y_train = train['in_icu_mortality'].fillna(0).astype(int)
    y_test = test['in_icu_mortality'].fillna(0).astype(int)

    X_train = numeric_feature_selection(train.drop(columns=['in_icu_mortality','in_hospital_mortality','stay_id','subject_id','hadm_id','intime','outtime'], errors='ignore'))
    X_test = numeric_feature_selection(test.drop(columns=['in_icu_mortality','in_hospital_mortality','stay_id','subject_id','hadm_id','intime','outtime'], errors='ignore'))
    common = X_train.columns.intersection(X_test.columns)
    X_train = X_train[common]
    X_test = X_test[common]

    imputer = SimpleImputer(strategy='median')
    X_train_imp = imputer.fit_transform(X_train)
    X_test_imp = imputer.transform(X_test)

    # Train XGBoost similarly to temporal script
    if xgb is None:
        raise RuntimeError('xgboost is required for this script')

    pos = y_train.sum()
    neg = len(y_train) - pos
    scale = float(neg / pos) if pos > 0 else 1.0
    clf = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', verbosity=0, random_state=42, scale_pos_weight=scale, n_jobs=1)
    clf.fit(X_train_imp, y_train)

    # save model
    OUT.mkdir(exist_ok=True)
    dump(clf, OUT / 'xgb_temporal_model.joblib')

    probs_test = clf.predict_proba(X_test_imp)[:,1]
    auc = float(roc_auc_score(y_test, probs_test))
    auprc = float(average_precision_score(y_test, probs_test))
    brier = float(brier_score_loss(y_test, probs_test))

    # threshold sweep
    thresholds = np.linspace(0.0, 1.0, 101)
    df_thr = threshold_metrics(y_test, probs_test, thresholds)
    df_thr.to_csv(OUT / 'thresholds_metrics.csv', index=False)

    # best by F1
    best_f1 = df_thr.loc[df_thr['f1'].idxmax()].to_dict()
    # best by Youden (sensitivity + specificity -1)
    df_thr['youden'] = df_thr['sensitivity'] + df_thr['specificity'] - 1.0
    best_youden = df_thr.loc[df_thr['youden'].idxmax()].to_dict()

    # calibration curve (fraction of positives vs mean predicted)
    prob_true, prob_pred = calibration_curve(y_test, probs_test, n_bins=10)
    np.savez(OUT / 'calibration_xgb.npz', prob_true=prob_true, prob_pred=prob_pred)

    summary = {
        'model': 'xgb_temporal',
        'auc': auc,
        'auprc': auprc,
        'brier': brier,
        'best_f1': best_f1,
        'best_youden': best_youden,
        'n_train': int(len(y_train)),
        'n_test': int(len(y_test)),
    }

    with open(OUT / 'model_posthoc.json', 'w', encoding='utf8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print('Saved model, thresholds, and calibration outputs to outputs/')


if __name__ == '__main__':
    main()
