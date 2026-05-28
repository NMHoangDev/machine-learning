#!/usr/bin/env python3
"""
Phase 8.1: Model Comparison & Advanced Modeling

Train and compare multiple models with cross-validation and hyperparameter tuning.

Usage: python models/compare_models.py
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, roc_curve
import warnings

warnings.filterwarnings('ignore')

try:
    from lightgbm import LGBMClassifier
    HAS_LIGHTGBM = True
except:
    HAS_LIGHTGBM = False

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except:
    HAS_XGBOOST = False

ROOT = Path('.').resolve()
OUT = ROOT / 'outputs'


def evaluate_model(clf, X_train, y_train, X_test, y_test, model_name):
    """Evaluate model on train and test sets."""
    # Training metrics
    y_train_pred = clf.predict_proba(X_train)[:, 1]
    train_auc = roc_auc_score(y_train, y_train_pred)
    train_auprc = average_precision_score(y_train, y_train_pred)
    
    # Test metrics
    y_test_pred = clf.predict_proba(X_test)[:, 1]
    test_auc = roc_auc_score(y_test, y_test_pred)
    test_auprc = average_precision_score(y_test, y_test_pred)
    test_brier = brier_score_loss(y_test, y_test_pred)
    
    # Overfitting check
    overfitting = train_auc - test_auc
    
    return {
        'model': model_name,
        'train_auc': float(train_auc),
        'test_auc': float(test_auc),
        'train_auprc': float(train_auprc),
        'test_auprc': float(test_auprc),
        'test_brier': float(test_brier),
        'overfitting': float(overfitting),
    }


def train_logistic_regression(X_train, y_train, X_test, y_test):
    """Train Logistic Regression with tuning."""
    print("\n  Training Logistic Regression...")
    
    # Grid search for hyperparameters
    param_grid = {
        'C': [0.001, 0.01, 0.1, 1, 10, 100],
        'max_iter': [1000],
        'class_weight': ['balanced', None],
    }
    
    lr = LogisticRegression(solver='lbfgs', random_state=42)
    grid = GridSearchCV(lr, param_grid, cv=3, scoring='roc_auc', n_jobs=-1)
    grid.fit(X_train, y_train)
    
    best_lr = grid.best_estimator_
    results = evaluate_model(best_lr, X_train, y_train, X_test, y_test, 'Logistic Regression')
    results['best_params'] = grid.best_params_
    
    return best_lr, results


def train_random_forest(X_train, y_train, X_test, y_test):
    """Train Random Forest with tuning."""
    print("\n  Training Random Forest...")
    
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [5, 10],
        'class_weight': ['balanced', 'balanced_subsample'],
    }
    
    rf = RandomForestClassifier(random_state=42, n_jobs=-1)
    grid = GridSearchCV(rf, param_grid, cv=3, scoring='roc_auc', n_jobs=-1)
    grid.fit(X_train, y_train)
    
    best_rf = grid.best_estimator_
    results = evaluate_model(best_rf, X_train, y_train, X_test, y_test, 'Random Forest')
    results['best_params'] = grid.best_params_
    
    return best_rf, results


def train_lightgbm(X_train, y_train, X_test, y_test):
    """Train LightGBM with tuning."""
    if not HAS_LIGHTGBM:
        print("\n  ⚠ LightGBM not installed, skipping")
        return None, None
    
    print("\n  Training LightGBM...")
    
    param_grid = {
        'num_leaves': [31, 50],
        'learning_rate': [0.01, 0.1],
        'n_estimators': [100, 200],
    }
    
    lgb = LGBMClassifier(random_state=42, n_jobs=-1, verbose=-1)
    grid = GridSearchCV(lgb, param_grid, cv=3, scoring='roc_auc', n_jobs=-1)
    grid.fit(X_train, y_train)
    
    best_lgb = grid.best_estimator_
    results = evaluate_model(best_lgb, X_train, y_train, X_test, y_test, 'LightGBM')
    results['best_params'] = grid.best_params_
    
    return best_lgb, results


def train_xgboost(X_train, y_train, X_test, y_test):
    """Train XGBoost with tuning."""
    if not HAS_XGBOOST:
        print("\n  ⚠ XGBoost not installed, skipping")
        return None, None
    
    print("\n  Training XGBoost...")
    
    param_grid = {
        'max_depth': [5, 7, 10],
        'learning_rate': [0.01, 0.1],
        'n_estimators': [100, 200],
    }
    
    xgb_clf = xgb.XGBClassifier(random_state=42, n_jobs=-1, verbosity=0, eval_metric='logloss')
    grid = GridSearchCV(xgb_clf, param_grid, cv=3, scoring='roc_auc', n_jobs=-1)
    grid.fit(X_train, y_train)
    
    best_xgb = grid.best_estimator_
    results = evaluate_model(best_xgb, X_train, y_train, X_test, y_test, 'XGBoost')
    results['best_params'] = grid.best_params_
    
    return best_xgb, results


def cross_validate_model(clf, X, y, cv=5):
    """Perform cross-validation."""
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    
    cv_auc = cross_val_score(clf, X, y, cv=skf, scoring='roc_auc')
    cv_auprc = cross_val_score(clf, X, y, cv=skf, scoring='average_precision')
    
    return {
        'cv_auc_mean': float(cv_auc.mean()),
        'cv_auc_std': float(cv_auc.std()),
        'cv_auprc_mean': float(cv_auprc.mean()),
        'cv_auprc_std': float(cv_auprc.std()),
    }


def main():
    print("=" * 80)
    print("PHASE 8.1: MODEL COMPARISON & ADVANCED MODELING")
    print("=" * 80)
    
    # Load data
    print("\n[1/6] Loading data...")
    features_df = pd.read_csv(OUT / 'features_lab.csv', parse_dates=['intime'])
    print(f"✓ Loaded: {features_df.shape}")
    
    # Temporal split
    print("\n[2/6] Temporal split...")
    features_df = features_df.sort_values('intime')
    median_idx = len(features_df) // 2
    split_time = features_df['intime'].iloc[median_idx]
    
    train_df = features_df[features_df['intime'] <= split_time].copy()
    test_df = features_df[features_df['intime'] > split_time].copy()
    
    print(f"  Train: {len(train_df)} | Test: {len(test_df)}")
    
    # Extract features and labels
    y_train = train_df['in_icu_mortality'].fillna(0).astype(int)
    y_test = test_df['in_icu_mortality'].fillna(0).astype(int)
    
    drop_cols = ['in_icu_mortality', 'in_hospital_mortality', 'stay_id', 'subject_id', 
                 'hadm_id', 'intime', 'outtime', 'admittime', 'dischtime']
    X_train = train_df.drop(columns=drop_cols, errors='ignore')
    X_test = test_df.drop(columns=drop_cols, errors='ignore')
    
    # Keep only numeric features
    X_train = X_train.select_dtypes(include=[np.number])
    X_test = X_test[X_train.columns]
    
    # Preprocessing
    print("\n[3/6] Preprocessing...")
    imputer = SimpleImputer(strategy='median')
    scaler = StandardScaler()
    
    X_train_imp = imputer.fit_transform(X_train)
    X_test_imp = imputer.transform(X_test)
    
    X_train_scaled = scaler.fit_transform(X_train_imp)
    X_test_scaled = scaler.transform(X_test_imp)
    
    print(f"  Features: {X_train_scaled.shape[1]}")
    
    # Train models
    print("\n[4/6] Training models (this may take a few minutes)...")
    
    comparison_results = []
    trained_models = {}
    
    # Logistic Regression
    lr_model, lr_results = train_logistic_regression(X_train_scaled, y_train, X_test_scaled, y_test)
    comparison_results.append(lr_results)
    trained_models['logistic_regression'] = lr_model
    
    # Random Forest (no scaling needed)
    rf_model, rf_results = train_random_forest(X_train_imp, y_train, X_test_imp, y_test)
    comparison_results.append(rf_results)
    trained_models['random_forest'] = rf_model
    
    # LightGBM
    if HAS_LIGHTGBM:
        lgb_model, lgb_results = train_lightgbm(X_train_imp, y_train, X_test_imp, y_test)
        if lgb_results:
            comparison_results.append(lgb_results)
            trained_models['lightgbm'] = lgb_model
    
    # XGBoost
    if HAS_XGBOOST:
        xgb_model, xgb_results = train_xgboost(X_train_imp, y_train, X_test_imp, y_test)
        if xgb_results:
            comparison_results.append(xgb_results)
            trained_models['xgboost'] = xgb_model
    
    # Cross-validation
    print("\n[5/6] Cross-validation (5-fold)...")
    
    for model_name, model in trained_models.items():
        print(f"  CV: {model_name}...")
        
        # Determine if scaled or not
        if model_name == 'logistic_regression':
            X_data = X_train_scaled
        else:
            X_data = X_train_imp
        
        cv_scores = cross_validate_model(model, X_data, y_train, cv=5)
        
        # Find and update corresponding result
        for result in comparison_results:
            if result['model'].lower().replace(' ', '_') == model_name or \
               model_name in result['model'].lower().replace(' ', '_'):
                result.update(cv_scores)
                break
    
    # Create comparison dataframe
    print("\n[6/6] Compiling results...")
    
    comparison_df = pd.DataFrame(comparison_results)
    comparison_df = comparison_df.sort_values('test_auc', ascending=False)
    
    # Save results
    comparison_df.to_csv(OUT / 'model_comparison.csv', index=False)
    
    with open(OUT / 'model_comparison.json', 'w', encoding='utf8') as f:
        json.dump(comparison_results, f, ensure_ascii=False, indent=2, default=str)
    
    # Save trained models
    from joblib import dump
    for model_name, model in trained_models.items():
        dump(model, OUT / f'{model_name}_model.joblib')
    
    print("\n" + "=" * 80)
    print("MODEL COMPARISON COMPLETE")
    print("=" * 80)
    
    print("\n📊 Model Performance Comparison:")
    print(comparison_df[['model', 'test_auc', 'test_auprc', 'overfitting']].to_string(index=False))
    
    print(f"\n📁 Results saved:")
    print(f"   - {OUT / 'model_comparison.csv'}")
    print(f"   - {OUT / 'model_comparison.json'}")
    print(f"   - Trained models saved to outputs/")


if __name__ == '__main__':
    main()
