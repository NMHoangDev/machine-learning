#!/usr/bin/env python3
"""Compute SHAP explanations for the saved XGBoost temporal model.

Usage: py -3 models/shap_explain_xgb.py
Reads: outputs/xgb_temporal_model.joblib, outputs/features_lab.csv
Writes: outputs/shap_summary.csv, outputs/shap_test_values.npz
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from joblib import load

ROOT = Path('.').resolve()
OUT = ROOT / 'outputs'

def numeric_feature_selection(df, min_nonnull_frac=0.1, min_var=1e-6):
    num = df.select_dtypes(include=[np.number])
    keep = num.columns[(num.notna().mean() >= min_nonnull_frac) & (num.var() >= min_var)]
    return num[keep]


def main():
    model_path = OUT / 'xgb_temporal_model.joblib'
    if not model_path.exists():
        raise RuntimeError('Model not found: outputs/xgb_temporal_model.joblib - run posthoc script first')

    clf = load(model_path)

    feats = pd.read_csv(OUT / 'features_lab.csv', parse_dates=['intime'])
    feats = feats.sort_values('intime')
    median_idx = len(feats)//2
    split_time = feats['intime'].iloc[median_idx]
    train = feats[feats['intime'] <= split_time].copy()
    test = feats[feats['intime'] > split_time].copy()

    X_train = numeric_feature_selection(train.drop(columns=['in_icu_mortality','in_hospital_mortality','stay_id','subject_id','hadm_id','intime','outtime'], errors='ignore'))
    X_test = numeric_feature_selection(test.drop(columns=['in_icu_mortality','in_hospital_mortality','stay_id','subject_id','hadm_id','intime','outtime'], errors='ignore'))
    common = X_train.columns.intersection(X_test.columns)
    X_train = X_train[common]
    X_test = X_test[common]

    imputer = SimpleImputer(strategy='median')
    X_train_imp = imputer.fit_transform(X_train)
    X_test_imp = imputer.transform(X_test)

    # Prefer SHAP if available, otherwise fall back to model feature importances
    try:
        import shap
        shap_available = True
    except Exception:
        shap_available = False

    OUT.mkdir(exist_ok=True)

    if not shap_available:
        print('`shap` package not installed — falling back to model feature importances.')
        print('To get SHAP explanations install it with:')
        print('  py -3 -m pip install shap')
        # Many tree models expose `feature_importances_`
        if hasattr(clf, 'feature_importances_'):
            fi = np.array(clf.feature_importances_)
            df = pd.DataFrame({'feature': list(common), 'mean_abs_shap': fi})
            df = df.sort_values('mean_abs_shap', ascending=False)
            df.to_csv(OUT / 'shap_summary.csv', index=False)
            np.savez_compressed(OUT / 'shap_test_values.npz', shap=fi, features=np.array(list(common)))
            print('Saved feature_importances_ summary to outputs/shap_summary.csv')
            return
        else:
            raise RuntimeError('Model does not expose feature_importances_ and shap is not installed')

    # Use TreeExplainer for XGBoost
    explainer = shap.TreeExplainer(clf)
    # shap API variants: shap_values or explainer(...)
    try:
        shap_vals = explainer.shap_values(X_test_imp)
    except Exception:
        shap_vals = explainer(X_test_imp).values

    # shap_vals shape: (n_samples, n_features)
    mean_abs = np.mean(np.abs(shap_vals), axis=0)
    df = pd.DataFrame({'feature': list(common), 'mean_abs_shap': mean_abs})
    df = df.sort_values('mean_abs_shap', ascending=False)
    df.to_csv(OUT / 'shap_summary.csv', index=False)

    # save full arrays
    np.savez_compressed(OUT / 'shap_test_values.npz', shap=shap_vals, features=np.array(list(common)))

    print('Saved SHAP summary to outputs/shap_summary.csv and full values to outputs/shap_test_values.npz')


if __name__ == '__main__':
    main()
