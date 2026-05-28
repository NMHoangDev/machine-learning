#!/usr/bin/env python3
"""
Phase 7.2: Bivariate Analysis

Correlation analysis, feature-target associations, multicollinearity detection.

Usage: python analysis/bivariate_analysis.py
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr, chi2_contingency
from scipy.stats.contingency import association
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings('ignore')

ROOT = Path('.').resolve()
OUT = ROOT / 'outputs'
ANALYSIS = ROOT / 'analysis'


def compute_correlations(df, numeric_cols):
    """Compute Pearson, Spearman, and Kendall correlations."""
    print("\n  Computing correlations (Pearson, Spearman)...")
    
    correlations = {
        'pearson': {},
        'spearman': {},
    }
    
    # Pearson correlation matrix
    pearson_matrix = df[numeric_cols].corr(method='pearson')
    
    # Spearman correlation matrix
    spearman_matrix = df[numeric_cols].corr(method='spearman')
    
    # Get top correlations (excluding diagonal)
    top_pairs = []
    for i, col1 in enumerate(numeric_cols):
        for col2 in numeric_cols[i+1:]:
            pearson_r = float(pearson_matrix.loc[col1, col2])
            spearman_rho = float(spearman_matrix.loc[col1, col2])
            
            if abs(pearson_r) > 0.3 or abs(spearman_rho) > 0.3:  # Threshold: moderate correlation
                top_pairs.append({
                    'Feature1': col1,
                    'Feature2': col2,
                    'Pearson_r': pearson_r,
                    'Spearman_rho': spearman_rho,
                    'Abs_Pearson': abs(pearson_r),
                })
    
    # Sort by absolute correlation
    top_pairs = sorted(top_pairs, key=lambda x: x['Abs_Pearson'], reverse=True)
    
    return {
        'pearson_matrix': pearson_matrix.to_dict(),
        'spearman_matrix': spearman_matrix.to_dict(),
        'top_correlated_pairs': top_pairs[:100],  # Top 100
    }


def compute_target_associations(df, target_col='in_icu_mortality'):
    """Compute feature-target associations."""
    print(f"\n  Computing feature-target associations (target: {target_col})...")
    
    if target_col not in df.columns:
        print(f"  ⚠ Target column '{target_col}' not found!")
        return {}
    
    associations = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        if col in [target_col, 'stay_id', 'subject_id', 'hadm_id']:
            continue
        
        # Remove missing values
        valid_idx = df[[col, target_col]].notna().all(axis=1)
        X = df.loc[valid_idx, col].values
        y = df.loc[valid_idx, target_col].astype(int).values
        
        if len(X) < 10 or X.std() == 0:
            continue
        
        # Point-biserial correlation (continuous vs binary)
        try:
            corr, pval = pearsonr(X, y)
        except:
            corr = pval = np.nan
        
        # AUC (individual feature predictive power)
        try:
            auc = float(roc_auc_score(y, X))
        except:
            auc = np.nan
        
        # Odds ratio approximation (log odds)
        try:
            # Standardize for comparison
            X_std = (X - X.mean()) / X.std()
            # Logistic regression coefficient
            from sklearn.linear_model import LogisticRegression
            lr = LogisticRegression(max_iter=100)
            lr.fit(X_std.reshape(-1, 1), y)
            coef = float(lr.coef_[0][0])
            odds_ratio = np.exp(coef)
        except:
            odds_ratio = np.nan
        
        associations.append({
            'Feature': col,
            'Correlation': float(corr) if not np.isnan(corr) else None,
            'P_value': float(pval) if not np.isnan(pval) else None,
            'AUC': float(auc) if not np.isnan(auc) else None,
            'Odds_Ratio': float(odds_ratio) if not np.isnan(odds_ratio) else None,
            'Significant': pval < 0.05 if not np.isnan(pval) else False,
        })
    
    # Sort by AUC
    associations = sorted([a for a in associations if a['AUC'] is not None], 
                         key=lambda x: x['AUC'], reverse=True)
    
    return associations


def compute_vif(df, numeric_cols):
    """Compute Variance Inflation Factor for multicollinearity."""
    print("\n  Computing VIF (Variance Inflation Factor)...")
    
    from sklearn.linear_model import LinearRegression
    
    vif_data = []
    X = df[numeric_cols].fillna(df[numeric_cols].median())
    
    for i, col in enumerate(numeric_cols):
        # Regress col on all other features
        X_others = X.drop(columns=[col])
        y = X[col]
        
        if X_others.shape[1] == 0:
            continue
        
        try:
            lr = LinearRegression()
            lr.fit(X_others, y)
            r_squared = float(lr.score(X_others, y))
            
            # Avoid division by zero
            if r_squared >= 0.9999:
                vif = 1000.0  # Cap at 1000
            else:
                vif = 1.0 / (1.0 - r_squared)
        except:
            vif = np.nan
        
        vif_data.append({
            'Feature': col,
            'VIF': float(vif) if not np.isnan(vif) else None,
            'R_squared': float(r_squared),
            'Issue': 'High multicollinearity' if vif > 10 else 'Acceptable' if vif > 0 else 'Unknown',
        })
    
    # Sort by VIF
    vif_data = sorted([v for v in vif_data if v['VIF'] is not None], 
                      key=lambda x: x['VIF'], reverse=True)
    
    return vif_data


def main():
    print("=" * 80)
    print("PHASE 7.2: BIVARIATE ANALYSIS")
    print("=" * 80)
    
    # Load data
    print("\n[1/4] Loading data...")
    features_df = pd.read_csv(OUT / 'features_lab.csv', parse_dates=['intime', 'outtime'])
    print(f"✓ Loaded: {features_df.shape[0]} records × {features_df.shape[1]} features")
    
    numeric_cols = list(features_df.select_dtypes(include=[np.number]).columns)
    numeric_cols = [c for c in numeric_cols if c not in ['stay_id', 'subject_id', 'hadm_id', 
                                                          'in_icu_mortality', 'in_hospital_mortality']]
    print(f"✓ Numeric features for analysis: {len(numeric_cols)}")
    
    # 1. Correlation analysis
    print("\n[2/4] Correlation analysis...")
    correlation_results = compute_correlations(features_df, numeric_cols)
    
    # 2. Feature-target associations
    print("\n[3/4] Feature-target associations...")
    target_associations = compute_target_associations(features_df, 'in_icu_mortality')
    print(f"✓ Computed associations for {len(target_associations)} features")
    
    # 3. Multicollinearity (VIF)
    print("\n[4/4] Multicollinearity analysis...")
    vif_results = compute_vif(features_df, numeric_cols)
    print(f"✓ Computed VIF for {len(vif_results)} features")
    
    # Identify problematic features
    high_vif_features = [v['Feature'] for v in vif_results if v['VIF'] and v['VIF'] > 10]
    print(f"  ⚠ {len(high_vif_features)} features with VIF > 10 (potential multicollinearity)")
    
    # Compile report
    bivariate_report = {
        'timestamp': pd.Timestamp.now().isoformat(),
        'correlation_analysis': {
            'total_feature_pairs': len(numeric_cols) * (len(numeric_cols) - 1) // 2,
            'top_correlated_pairs': correlation_results['top_correlated_pairs'][:50],
        },
        'target_associations': target_associations[:50],
        'multicollinearity': {
            'total_features_analyzed': len(vif_results),
            'high_vif_features': high_vif_features,
            'vif_details': vif_results[:30],
        },
    }
    
    # Save results
    with open(ANALYSIS / 'bivariate_analysis_full.json', 'w', encoding='utf8') as f:
        json.dump(bivariate_report, f, ensure_ascii=False, indent=2, default=str)
    
    # Save correlation matrix
    corr_df = pd.DataFrame(correlation_results['pearson_matrix'])
    corr_df.to_csv(ANALYSIS / 'correlation_matrix.csv')
    
    # Save target associations
    target_assoc_df = pd.DataFrame(target_associations)
    target_assoc_df.to_csv(ANALYSIS / 'target_associations.csv', index=False)
    
    # Save VIF results
    vif_df = pd.DataFrame(vif_results)
    vif_df.to_csv(ANALYSIS / 'multicollinearity_vif.csv', index=False)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\n📊 Results saved:")
    print(f"   - {ANALYSIS / 'bivariate_analysis_full.json'}")
    print(f"   - {ANALYSIS / 'correlation_matrix.csv'}")
    print(f"   - {ANALYSIS / 'target_associations.csv'}")
    print(f"   - {ANALYSIS / 'multicollinearity_vif.csv'}")
    
    return bivariate_report


if __name__ == '__main__':
    report = main()
