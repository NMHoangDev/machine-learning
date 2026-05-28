#!/usr/bin/env python3
"""
Phase 7.1: Descriptive Statistics Analysis

Comprehensive statistical analysis of the MIMIC-IV dataset.
Outputs: Univariate statistics, missing data patterns, outlier detection, duplicates.

Usage: python analysis/descriptive_statistics.py
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

ROOT = Path('.').resolve()
OUT = ROOT / 'outputs'
ANALYSIS = ROOT / 'analysis'
ANALYSIS.mkdir(exist_ok=True)


def compute_univariate_stats(series, name):
    """Compute comprehensive statistics for a single feature."""
    if series.dtype in ['object', 'string']:
        # Categorical
        return {
            'name': name,
            'dtype': str(series.dtype),
            'count': int(series.count()),
            'missing': int(series.isna().sum()),
            'missing_pct': float(series.isna().mean() * 100),
            'unique': int(series.nunique()),
            'unique_pct': float(series.nunique() / len(series) * 100),
            'mode': str(series.mode()[0]) if len(series.mode()) > 0 else 'N/A',
            'categorical': True,
        }
    
    # Numeric
    series_clean = series.dropna()
    if len(series_clean) == 0:
        return {
            'name': name,
            'dtype': str(series.dtype),
            'count': 0,
            'missing': int(series.isna().sum()),
            'missing_pct': 100.0,
        }
    
    try:
        skew = float(stats.skew(series_clean))
        kurt = float(stats.kurtosis(series_clean))
    except:
        skew = np.nan
        kurt = np.nan
    
    try:
        q1 = float(series_clean.quantile(0.25))
        q3 = float(series_clean.quantile(0.75))
        iqr = q3 - q1
    except:
        q1 = q3 = iqr = np.nan
    
    return {
        'name': name,
        'dtype': str(series.dtype),
        'count': int(series.count()),
        'missing': int(series.isna().sum()),
        'missing_pct': float(series.isna().mean() * 100),
        'mean': float(series_clean.mean()),
        'median': float(series_clean.median()),
        'std': float(series_clean.std()),
        'var': float(series_clean.var()),
        'min': float(series_clean.min()),
        'q1': q1,
        'q3': q3,
        'max': float(series_clean.max()),
        'iqr': iqr,
        'range': float(series_clean.max() - series_clean.min()),
        'skewness': skew,
        'kurtosis': kurt,
        'categorical': False,
    }


def detect_outliers_iqr(series, name):
    """Detect outliers using IQR method."""
    series_clean = series.dropna()
    if len(series_clean) < 4:
        return {'name': name, 'outliers': 0, 'outlier_pct': 0.0, 'outlier_values': []}
    
    Q1 = series_clean.quantile(0.25)
    Q3 = series_clean.quantile(0.75)
    IQR = Q3 - Q1
    
    if IQR == 0:
        return {'name': name, 'outliers': 0, 'outlier_pct': 0.0, 'outlier_values': []}
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = series_clean[(series_clean < lower_bound) | (series_clean > upper_bound)]
    
    return {
        'name': name,
        'lower_bound': float(lower_bound),
        'upper_bound': float(upper_bound),
        'outliers': int(len(outliers)),
        'outlier_pct': float(len(outliers) / len(series_clean) * 100),
        'outlier_values': sorted([float(x) for x in outliers.unique()[:20]]),  # Top 20
        'extreme_outliers': int(len(series_clean[(series_clean < Q1 - 3*IQR) | (series_clean > Q3 + 3*IQR)])),
    }


def analyze_missing_patterns(df):
    """Analyze missing data patterns."""
    missing_info = {}
    total_cells = df.shape[0] * df.shape[1]
    total_missing = df.isna().sum().sum()
    
    missing_info['total_cells'] = int(total_cells)
    missing_info['total_missing'] = int(total_missing)
    missing_info['overall_missing_pct'] = float(total_missing / total_cells * 100)
    
    # Columns with highest missingness
    col_missing = df.isna().sum().sort_values(ascending=False)
    missing_info['columns_with_missing'] = {
        str(col): {'count': int(count), 'pct': float(count / len(df) * 100)}
        for col, count in col_missing[col_missing > 0].items()
    }
    
    # Missing data mechanism estimation
    # MCAR: random across rows
    # MAR: depends on other variables
    # MNAR: depends on the missing values themselves
    
    missing_info['total_columns_with_missing'] = int((df.isna().sum() > 0).sum())
    missing_info['columns_mostly_missing'] = int((df.isna().mean() > 0.5).sum())
    missing_info['columns_all_missing'] = int((df.isna().mean() == 1.0).sum())
    
    return missing_info


def detect_duplicates(df):
    """Detect duplicate rows and stays."""
    duplicates = {
        'total_rows': len(df),
        'exact_duplicates': int(df.duplicated().sum()),
        'exact_duplicate_pct': float(df.duplicated().sum() / len(df) * 100),
    }
    
    # Check for duplicate stays
    if 'stay_id' in df.columns:
        stay_dups = df[df['stay_id'].duplicated(keep=False)]
        duplicates['duplicate_stays'] = int(len(stay_dups))
    
    if 'hadm_id' in df.columns:
        hadm_dups = df[df['hadm_id'].duplicated(keep=False)]
        duplicates['duplicate_hadm'] = int(len(hadm_dups))
    
    return duplicates


def check_data_types(df):
    """Check data type distribution."""
    dtype_info = {}
    for dtype in df.dtypes.unique():
        cols = list(df.columns[df.dtypes == dtype])
        dtype_info[str(dtype)] = {
            'count': len(cols),
            'columns': cols[:10],  # First 10
        }
    return dtype_info


def check_variance(df):
    """Check for zero-variance features."""
    numeric_df = df.select_dtypes(include=[np.number])
    
    zero_variance = []
    for col in numeric_df.columns:
        if numeric_df[col].var() == 0:
            zero_variance.append(col)
    
    return {
        'zero_variance_count': len(zero_variance),
        'zero_variance_columns': zero_variance,
    }


def main():
    print("=" * 80)
    print("PHASE 7.1: DESCRIPTIVE STATISTICS ANALYSIS")
    print("=" * 80)
    
    # Load data
    print("\n[1/6] Loading data...")
    features_df = pd.read_csv(OUT / 'features_lab.csv', parse_dates=['intime', 'outtime'])
    cohort_df = pd.read_csv(OUT / 'cohort.csv', parse_dates=['intime', 'outtime', 'admittime', 'dischtime', 'deathtime'])
    
    print(f"✓ Features loaded: {features_df.shape}")
    print(f"✓ Cohort loaded: {cohort_df.shape}")
    
    # 1. Database shape
    print("\n[2/6] Analyzing database shape...")
    database_info = {
        'total_records': int(features_df.shape[0]),
        'total_features': int(features_df.shape[1]),
        'numeric_features': int(features_df.select_dtypes(include=[np.number]).shape[1]),
        'categorical_features': int(features_df.select_dtypes(include=['object', 'string']).shape[1]),
        'datetime_features': int(features_df.select_dtypes(include=['datetime64']).shape[1]),
        'date_range': {
            'earliest': str(features_df['intime'].min()),
            'latest': str(features_df['intime'].max()),
        } if 'intime' in features_df.columns else {},
        'unique_patients': int(features_df['subject_id'].nunique()) if 'subject_id' in features_df.columns else 0,
        'unique_stays': int(features_df['stay_id'].nunique()) if 'stay_id' in features_df.columns else 0,
    }
    
    print(f"✓ Database: {database_info['total_records']} rows × {database_info['total_features']} features")
    
    # 2. Univariate statistics
    print("\n[3/6] Computing univariate statistics...")
    univariate_stats = {}
    numeric_cols = features_df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        univariate_stats[col] = compute_univariate_stats(features_df[col], col)
        univariate_stats[col]['outliers'] = detect_outliers_iqr(features_df[col], col)
    
    print(f"✓ Computed stats for {len(univariate_stats)} numeric features")
    
    # 3. Missing data analysis
    print("\n[4/6] Analyzing missing data patterns...")
    missing_info = analyze_missing_patterns(features_df)
    print(f"✓ Overall missing: {missing_info['overall_missing_pct']:.2f}%")
    
    # 4. Duplicates
    print("\n[5/6] Detecting duplicates...")
    duplicates = detect_duplicates(features_df)
    print(f"✓ Exact duplicates: {duplicates['exact_duplicates']}")
    
    # 5. Data types
    print("\n[6/6] Checking data types...")
    dtypes = check_data_types(features_df)
    variance_info = check_variance(features_df)
    print(f"✓ Zero-variance features: {variance_info['zero_variance_count']}")
    
    # Compile comprehensive report
    comprehensive_report = {
        'timestamp': pd.Timestamp.now().isoformat(),
        'database_shape': database_info,
        'missing_data': missing_info,
        'duplicates': duplicates,
        'data_types': dtypes,
        'variance_analysis': variance_info,
        'univariate_statistics': {
            col: {k: v for k, v in stats.items() if k != 'outliers'}
            for col, stats in univariate_stats.items()
        },
        'outlier_analysis': {
            col: stats['outliers']
            for col, stats in univariate_stats.items()
            if 'outliers' in stats and stats['outliers']['outliers'] > 0
        },
    }
    
    # Save comprehensive report
    with open(ANALYSIS / 'descriptive_stats_full.json', 'w', encoding='utf8') as f:
        json.dump(comprehensive_report, f, ensure_ascii=False, indent=2, default=str)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\n📊 Results saved:")
    print(f"   - {ANALYSIS / 'descriptive_stats_full.json'}")
    
    # Create summary CSV for quick reference
    summary_rows = []
    for col, stat in univariate_stats.items():
        row = {
            'Feature': col,
            'Type': stat['dtype'],
            'Count': stat['count'],
            'Missing': stat['missing'],
            'Missing%': f"{stat['missing_pct']:.2f}",
        }
        if not stat['categorical']:
            row['Mean'] = f"{stat['mean']:.4f}"
            row['Std'] = f"{stat['std']:.4f}"
            row['Min'] = f"{stat['min']:.4f}"
            row['Max'] = f"{stat['max']:.4f}"
            row['Skew'] = f"{stat['skewness']:.4f}" if not np.isnan(stat['skewness']) else 'N/A'
            row['Outliers'] = stat['outliers']['outliers']
        summary_rows.append(row)
    
    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(ANALYSIS / 'descriptive_stats_summary.csv', index=False)
    print(f"   - {ANALYSIS / 'descriptive_stats_summary.csv'}")
    
    return comprehensive_report


if __name__ == '__main__':
    report = main()
