#!/usr/bin/env python3
"""
Phase 7.3: Multivariate Analysis

PCA, dimensionality reduction, feature selection, stratified analysis.

Usage: python analysis/multivariate_analysis.py
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
import warnings

warnings.filterwarnings('ignore')

ROOT = Path('.').resolve()
OUT = ROOT / 'outputs'
ANALYSIS = ROOT / 'analysis'


def perform_pca(df, numeric_cols, variance_target=0.85):
    """Perform PCA and determine optimal components."""
    print("\n  Performing PCA...")
    
    # Prepare data
    X = df[numeric_cols].fillna(df[numeric_cols].median())
    X_scaled = StandardScaler().fit_transform(X)
    
    # Fit PCA with all components
    pca = PCA()
    pca.fit(X_scaled)
    
    # Find components for variance target
    cumsum = np.cumsum(pca.explained_variance_ratio_)
    n_components = np.argmax(cumsum >= variance_target) + 1
    
    # Components analysis
    components_info = {
        'total_features': len(numeric_cols),
        'variance_target': variance_target,
        'n_components_needed': int(n_components),
        'variance_captured': float(cumsum[n_components-1]),
        'variance_explained_by_component': [float(x) for x in pca.explained_variance_ratio_[:10]],
        'cumulative_variance': [float(x) for x in cumsum[:10]],
    }
    
    # Feature loadings (contribution of each feature to first 3 PCs)
    n_show = min(3, pca.components_.shape[0])
    loadings = {}
    for i in range(n_show):
        pc_loadings = {}
        for j, col in enumerate(numeric_cols):
            pc_loadings[col] = float(pca.components_[i][j])
        loadings[f'PC{i+1}'] = pc_loadings
    
    return {
        'components_info': components_info,
        'loadings': loadings,
        'pca': pca,
        'X_scaled': X_scaled,
    }


def perform_feature_selection_rfe(df, numeric_cols, target_col='in_icu_mortality', n_features=20):
    """Recursive Feature Elimination."""
    print("\n  Performing RFE (Recursive Feature Elimination)...")
    
    # Prepare data
    X = df[numeric_cols].fillna(df[numeric_cols].median())
    y = df[target_col].astype(int)
    
    # Use Random Forest for feature selection
    rf = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
    
    rfe = RFE(estimator=rf, n_features_to_select=n_features, step=5)
    rfe.fit(X, y)
    
    # Get selected features
    selected_features = [col for col, selected in zip(numeric_cols, rfe.support_) if selected]
    
    # Feature ranking (lower = better)
    feature_ranking = pd.DataFrame({
        'Feature': numeric_cols,
        'Ranking': rfe.ranking_,
        'Selected': rfe.support_,
    }).sort_values('Ranking')
    
    return {
        'selected_features': selected_features,
        'n_selected': len(selected_features),
        'feature_ranking': feature_ranking.to_dict('records'),
    }


def stratified_subgroup_analysis(df, target_col='in_icu_mortality'):
    """Analyze model performance by subgroups."""
    print("\n  Stratified subgroup analysis...")
    
    subgroup_results = {}
    
    # Define subgroups
    subgroups = {}
    
    # By stay duration
    if 'intime' in df.columns and 'outtime' in df.columns:
        df['stay_duration'] = (pd.to_datetime(df['outtime']) - pd.to_datetime(df['intime'])).dt.total_seconds() / 3600
        subgroups['stay_duration'] = {
            'Short (<24h)': df['stay_duration'] < 24,
            'Medium (24-72h)': (df['stay_duration'] >= 24) & (df['stay_duration'] < 72),
            'Long (>72h)': df['stay_duration'] >= 72,
        }
    
    # By mortality outcome
    if target_col in df.columns:
        subgroups['mortality'] = {
            'Survivors': df[target_col] == 0,
            'Non-survivors': df[target_col] == 1,
        }
    
    # Analyze each subgroup
    for subgroup_type, groups in subgroups.items():
        subgroup_results[subgroup_type] = {}
        for group_name, mask in groups.items():
            group_df = df[mask]
            
            if len(group_df) == 0:
                continue
            
            subgroup_results[subgroup_type][group_name] = {
                'n_samples': len(group_df),
                'n_positive': int(group_df[target_col].sum()) if target_col in group_df.columns else 0,
                'positive_pct': float(group_df[target_col].mean() * 100) if target_col in group_df.columns else 0,
                'feature_means': group_df.select_dtypes(include=[np.number]).mean().to_dict(),
            }
    
    return subgroup_results


def feature_importance_comparison(df, numeric_cols, target_col='in_icu_mortality'):
    """Compare multiple feature importance methods."""
    print("\n  Comparing feature importance methods...")
    
    # Prepare data
    X = df[numeric_cols].fillna(df[numeric_cols].median())
    y = df[target_col].astype(int)
    
    importance_methods = {}
    
    # Method 1: Random Forest importance
    try:
        rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
        rf.fit(X, y)
        rf_importance = pd.DataFrame({
            'Feature': numeric_cols,
            'RF_Importance': rf.feature_importances_,
        }).sort_values('RF_Importance', ascending=False)
        importance_methods['RandomForest'] = rf_importance.to_dict('records')[:20]
    except Exception as e:
        print(f"    ⚠ RF failed: {str(e)[:50]}")
    
    # Method 2: Correlation with target
    try:
        correlations = []
        for col in numeric_cols:
            corr = X[col].corr(y)
            correlations.append({'Feature': col, 'Correlation': abs(corr)})
        corr_importance = sorted(correlations, key=lambda x: x['Correlation'], reverse=True)
        importance_methods['Correlation'] = corr_importance[:20]
    except Exception as e:
        print(f"    ⚠ Correlation failed: {str(e)[:50]}")
    
    # Method 3: AUC per feature
    try:
        auc_scores = []
        for col in numeric_cols:
            X_valid = X[[col]].dropna()
            y_valid = y[X_valid.index]
            if len(np.unique(y_valid)) > 1 and X_valid[col].std() > 0:
                try:
                    auc = roc_auc_score(y_valid, X_valid[col])
                    auc_scores.append({'Feature': col, 'AUC': auc})
                except:
                    pass
        auc_importance = sorted(auc_scores, key=lambda x: x['AUC'], reverse=True)
        importance_methods['AUC'] = auc_importance[:20]
    except Exception as e:
        print(f"    ⚠ AUC failed: {str(e)[:50]}")
    
    return importance_methods


def main():
    print("=" * 80)
    print("PHASE 7.3: MULTIVARIATE ANALYSIS")
    print("=" * 80)
    
    # Load data
    print("\n[1/5] Loading data...")
    features_df = pd.read_csv(OUT / 'features_lab.csv', parse_dates=['intime', 'outtime'])
    print(f"✓ Loaded: {features_df.shape[0]} records × {features_df.shape[1]} features")
    
    numeric_cols = list(features_df.select_dtypes(include=[np.number]).columns)
    numeric_cols = [c for c in numeric_cols if c not in ['stay_id', 'subject_id', 'hadm_id', 
                                                          'in_icu_mortality', 'in_hospital_mortality']]
    
    # 1. PCA
    print("\n[2/5] Principal Component Analysis...")
    pca_results = perform_pca(features_df, numeric_cols, variance_target=0.85)
    
    # 2. Feature selection (RFE)
    print("\n[3/5] Recursive Feature Elimination...")
    rfe_results = perform_feature_selection_rfe(features_df, numeric_cols, n_features=20)
    
    # 3. Stratified analysis
    print("\n[4/5] Stratified subgroup analysis...")
    stratified_results = stratified_subgroup_analysis(features_df)
    
    # 4. Feature importance comparison
    print("\n[5/5] Feature importance comparison...")
    importance_comparison = feature_importance_comparison(features_df, numeric_cols)
    
    # Compile comprehensive report
    multivariate_report = {
        'timestamp': pd.Timestamp.now().isoformat(),
        'pca_analysis': {
            'components_info': pca_results['components_info'],
            'top_loadings': pca_results['loadings'],
        },
        'feature_selection_rfe': {
            'selected_features': rfe_results['selected_features'],
            'n_selected': rfe_results['n_selected'],
            'top_ranked_features': rfe_results['feature_ranking'][:20],
        },
        'stratified_analysis': stratified_results,
        'feature_importance_comparison': {
            method: importance_comparison.get(method, [])
            for method in ['RandomForest', 'Correlation', 'AUC']
        },
    }
    
    # Save results
    with open(ANALYSIS / 'multivariate_analysis_full.json', 'w', encoding='utf8') as f:
        json.dump(multivariate_report, f, ensure_ascii=False, indent=2, default=str)
    
    # Save PCA loadings
    if 'loadings' in pca_results:
        loadings_df = pd.DataFrame(pca_results['loadings']).T
        loadings_df.to_csv(ANALYSIS / 'pca_loadings.csv')
    
    # Save feature ranking
    rfe_df = pd.DataFrame(rfe_results['feature_ranking'])
    rfe_df.to_csv(ANALYSIS / 'feature_ranking_rfe.csv', index=False)
    
    # Save importance comparison
    for method, importance_list in importance_comparison.items():
        if importance_list:
            imp_df = pd.DataFrame(importance_list)
            imp_df.to_csv(ANALYSIS / f'feature_importance_{method.lower()}.csv', index=False)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\n📊 Results saved:")
    print(f"   - {ANALYSIS / 'multivariate_analysis_full.json'}")
    print(f"   - {ANALYSIS / 'pca_loadings.csv'}")
    print(f"   - {ANALYSIS / 'feature_ranking_rfe.csv'}")
    print(f"   - Feature importance files (RandomForest, Correlation, AUC)")
    
    print(f"\n🎯 Key findings:")
    print(f"   - PCA: {pca_results['components_info']['n_components_needed']} components for 85% variance")
    print(f"   - RFE selected: {rfe_results['n_selected']} top features")
    print(f"   - Stratified analysis: {len(stratified_results)} subgroup types analyzed")
    
    return multivariate_report


if __name__ == '__main__':
    report = main()
