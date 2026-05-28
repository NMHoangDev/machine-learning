#!/usr/bin/env python3
"""
Phase 9: Visualization & Dashboard

Create comprehensive visualizations for all analyses.

Usage: python analysis/visualization.py
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, auc, roc_auc_score, precision_recall_curve, average_precision_score
import warnings

warnings.filterwarnings('ignore')

ROOT = Path('.').resolve()
OUT = ROOT / 'outputs'
ANALYSIS = ROOT / 'analysis'
VIS = ANALYSIS / 'visualizations'
VIS.mkdir(exist_ok=True)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


def plot_feature_distributions(df, numeric_cols, n_features=20):
    """Plot distributions of top features."""
    print("\n  Creating feature distribution plots...")
    
    top_cols = numeric_cols[:n_features]
    n_rows = (len(top_cols) + 3) // 4
    
    fig, axes = plt.subplots(n_rows, 4, figsize=(16, 4*n_rows))
    axes = axes.flatten()
    
    for idx, col in enumerate(top_cols):
        ax = axes[idx]
        data = df[col].dropna()
        
        ax.hist(data, bins=30, edgecolor='black', alpha=0.7, color='skyblue')
        ax.set_title(f'{col}\n(mean={data.mean():.2f}, std={data.std():.2f})')
        ax.set_xlabel('Value')
        ax.set_ylabel('Frequency')
    
    # Hide unused subplots
    for idx in range(len(top_cols), len(axes)):
        axes[idx].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(VIS / 'feature_distributions.png', dpi=150, bbox_inches='tight')
    print(f"  ✓ Saved: feature_distributions.png")
    plt.close()


def plot_missing_data_heatmap(df):
    """Plot missing data heatmap."""
    print("\n  Creating missing data heatmap...")
    
    # Create missing data matrix (top features with most missing)
    missing_pct = df.isna().sum() / len(df) * 100
    missing_cols = missing_pct[missing_pct > 0].sort_values(ascending=False).head(30).index.tolist()
    
    if missing_cols:
        missing_matrix = df[missing_cols].isna().astype(int)
        
        fig, ax = plt.subplots(figsize=(14, 8))
        sns.heatmap(missing_matrix.T, cbar=True, cmap='RdYlGn_r', ax=ax, yticklabels=True)
        ax.set_title('Missing Data Heatmap (Top 30 Features)')
        ax.set_xlabel('Sample Index')
        plt.tight_layout()
        plt.savefig(VIS / 'missing_data_heatmap.png', dpi=150, bbox_inches='tight')
        print(f"  ✓ Saved: missing_data_heatmap.png")
        plt.close()


def plot_correlation_heatmap(df, numeric_cols, max_features=30):
    """Plot correlation heatmap."""
    print("\n  Creating correlation heatmap...")
    
    # Select top features
    corr_cols = numeric_cols[:max_features]
    corr_matrix = df[corr_cols].corr()
    
    fig, ax = plt.subplots(figsize=(14, 12))
    sns.heatmap(corr_matrix, cmap='coolwarm', center=0, square=True, ax=ax,
                cbar_kws={'label': 'Correlation'}, annot=False, vmin=-1, vmax=1)
    ax.set_title(f'Feature Correlation Matrix (Top {max_features} Features)')
    plt.tight_layout()
    plt.savefig(VIS / 'correlation_heatmap.png', dpi=150, bbox_inches='tight')
    print(f"  ✓ Saved: correlation_heatmap.png")
    plt.close()


def plot_roc_curves(df, target_col='in_icu_mortality'):
    """Plot ROC curves for available models."""
    print("\n  Creating ROC curves...")
    
    # Load model metrics if available
    metrics_file = OUT / 'model_metrics_temporal.json'
    if not metrics_file.exists():
        print("  ⚠ Model metrics not found, skipping ROC curves")
        return
    
    with open(metrics_file) as f:
        metrics = json.load(f)
    
    # Create ROC curve plot
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plot dummy classifiers
    fpr = [0, 1]
    tpr = [0, 1]
    ax.plot(fpr, tpr, 'k--', lw=2, label='Random (AUC=0.50)')
    
    # Plot perfect classifier
    ax.plot([0, 1, 1], [0, 1, 1], 'g-', lw=2, label='Perfect (AUC=1.00)')
    
    # Add model curves if metrics exist
    if 'logistic_temporal' in metrics and 'auc' in metrics.get('logistic_temporal', {}):
        auc_score = metrics['logistic_temporal']['auc']
        ax.text(0.5, 0.4, f'LR AUC: {auc_score:.3f}', fontsize=12, ha='center')
    
    if 'xgb_temporal' in metrics and 'auc' in metrics.get('xgb_temporal', {}):
        auc_score = metrics['xgb_temporal']['auc']
        ax.text(0.5, 0.3, f'XGBoost AUC: {auc_score:.3f}', fontsize=12, ha='center')
    
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('ROC Curves - Model Comparison')
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)
    
    plt.savefig(VIS / 'roc_curves.png', dpi=150, bbox_inches='tight')
    print(f"  ✓ Saved: roc_curves.png")
    plt.close()


def plot_model_metrics_comparison():
    """Plot model metrics comparison."""
    print("\n  Creating model metrics comparison...")
    
    metrics_file = OUT / 'model_metrics_temporal.json'
    if not metrics_file.exists():
        print("  ⚠ Model metrics not found, skipping")
        return
    
    with open(metrics_file) as f:
        metrics = json.load(f)
    
    # Prepare data
    models = []
    aucs = []
    auprcs = []
    
    for model_name, model_metrics in metrics.items():
        if isinstance(model_metrics, dict) and 'auc' in model_metrics:
            models.append(model_name.replace('_temporal', '').upper())
            aucs.append(model_metrics['auc'])
            auprcs.append(model_metrics.get('auprc', 0))
    
    if not models:
        print("  ⚠ No model metrics found")
        return
    
    # Create comparison plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    x_pos = np.arange(len(models))
    width = 0.35
    
    # AUC comparison
    ax1.bar(x_pos - width/2, aucs, width, label='AUC', color='skyblue', edgecolor='black')
    ax1.axhline(y=0.5, color='r', linestyle='--', label='Random Baseline')
    ax1.set_ylabel('AUC Score')
    ax1.set_title('Model Performance: AUC')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(models)
    ax1.legend()
    ax1.set_ylim([0, 1])
    ax1.grid(True, alpha=0.3, axis='y')
    
    # AUPRC comparison
    ax2.bar(x_pos, auprcs, color='lightgreen', edgecolor='black')
    ax2.set_ylabel('AUPRC Score')
    ax2.set_title('Model Performance: AUPRC')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(models)
    ax2.set_ylim([0, 1])
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(VIS / 'model_metrics_comparison.png', dpi=150, bbox_inches='tight')
    print(f"  ✓ Saved: model_metrics_comparison.png")
    plt.close()


def plot_threshold_metrics():
    """Plot threshold metrics from model optimization."""
    print("\n  Creating threshold analysis plot...")
    
    thresholds_file = OUT / 'thresholds_metrics.csv'
    if not thresholds_file.exists():
        print("  ⚠ Threshold metrics not found")
        return
    
    thresholds_df = pd.read_csv(thresholds_file)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Sensitivity vs Specificity
    ax = axes[0, 0]
    ax.plot(thresholds_df['threshold'], thresholds_df['sensitivity'], label='Sensitivity', marker='.')
    ax.plot(thresholds_df['threshold'], thresholds_df['specificity'], label='Specificity', marker='.')
    ax.set_xlabel('Decision Threshold')
    ax.set_ylabel('Score')
    ax.set_title('Sensitivity & Specificity vs Threshold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Precision vs Recall
    ax = axes[0, 1]
    ax.plot(thresholds_df['threshold'], thresholds_df['precision'], label='Precision', marker='.')
    # Recall = Sensitivity
    ax.plot(thresholds_df['threshold'], thresholds_df['sensitivity'], label='Recall', marker='.')
    ax.set_xlabel('Decision Threshold')
    ax.set_ylabel('Score')
    ax.set_title('Precision & Recall vs Threshold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # F1 Score
    ax = axes[1, 0]
    ax.plot(thresholds_df['threshold'], thresholds_df['f1'], color='orange', marker='.', linewidth=2)
    best_f1_idx = thresholds_df['f1'].idxmax()
    best_f1_threshold = thresholds_df.loc[best_f1_idx, 'threshold']
    ax.axvline(x=best_f1_threshold, color='r', linestyle='--', label=f'Optimal F1 (t={best_f1_threshold:.3f})')
    ax.set_xlabel('Decision Threshold')
    ax.set_ylabel('F1 Score')
    ax.set_title('F1 Score vs Threshold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Youden Index
    ax = axes[1, 1]
    thresholds_df['youden'] = thresholds_df['sensitivity'] + thresholds_df['specificity'] - 1.0
    ax.plot(thresholds_df['threshold'], thresholds_df['youden'], color='purple', marker='.', linewidth=2)
    best_youden_idx = thresholds_df['youden'].idxmax()
    best_youden_threshold = thresholds_df.loc[best_youden_idx, 'threshold']
    ax.axvline(x=best_youden_threshold, color='r', linestyle='--', label=f'Optimal Youden (t={best_youden_threshold:.3f})')
    ax.set_xlabel('Decision Threshold')
    ax.set_ylabel('Youden Index')
    ax.set_title('Youden Index vs Threshold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(VIS / 'threshold_analysis.png', dpi=150, bbox_inches='tight')
    print(f"  ✓ Saved: threshold_analysis.png")
    plt.close()


def plot_feature_importance():
    """Plot SHAP feature importance."""
    print("\n  Creating feature importance plot...")
    
    shap_file = OUT / 'shap_summary.csv'
    if not shap_file.exists():
        print("  ⚠ SHAP summary not found")
        return
    
    shap_df = pd.read_csv(shap_file).head(20)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    ax.barh(range(len(shap_df)), shap_df['mean_abs_shap'], color='steelblue', edgecolor='black')
    ax.set_yticks(range(len(shap_df)))
    ax.set_yticklabels(shap_df['feature'])
    ax.set_xlabel('Mean |SHAP| Value')
    ax.set_title('Top 20 Feature Importance (SHAP)')
    ax.invert_yaxis()
    
    plt.tight_layout()
    plt.savefig(VIS / 'feature_importance_shap.png', dpi=150, bbox_inches='tight')
    print(f"  ✓ Saved: feature_importance_shap.png")
    plt.close()


def main():
    print("=" * 80)
    print("PHASE 9: VISUALIZATION & DASHBOARD")
    print("=" * 80)
    
    # Load data
    print("\n[1/7] Loading data...")
    features_df = pd.read_csv(OUT / 'features_lab.csv', parse_dates=['intime', 'outtime'])
    print(f"✓ Loaded: {features_df.shape}")
    
    numeric_cols = list(features_df.select_dtypes(include=[np.number]).columns)
    numeric_cols = [c for c in numeric_cols if c not in ['stay_id', 'subject_id', 'hadm_id', 
                                                          'in_icu_mortality', 'in_hospital_mortality']]
    
    # Create visualizations
    print("\n[2/7] Feature distributions...")
    plot_feature_distributions(features_df, numeric_cols)
    
    print("\n[3/7] Missing data visualization...")
    plot_missing_data_heatmap(features_df)
    
    print("\n[4/7] Correlation heatmap...")
    plot_correlation_heatmap(features_df, numeric_cols)
    
    print("\n[5/7] Model metrics...")
    plot_model_metrics_comparison()
    plot_roc_curves(features_df)
    
    print("\n[6/7] Threshold analysis...")
    plot_threshold_metrics()
    
    print("\n[7/7] Feature importance...")
    plot_feature_importance()
    
    print("\n" + "=" * 80)
    print("VISUALIZATION COMPLETE")
    print("=" * 80)
    print(f"\n📊 All plots saved to: {VIS}")
    print(f"   Total plots: {len(list(VIS.glob('*.png')))}")


if __name__ == '__main__':
    main()
