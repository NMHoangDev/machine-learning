# IMPLEMENTATION PLAN: Next Phase Development

## ICU Mortality Prediction ML Pipeline - Advanced Analytics

**Document Version**: 1.0  
**Last Updated**: May 28, 2026  
**Current Progress**: 70% Complete  
**Next Phase Target**: 100% Complete in 2-3 weeks

---

## 🎯 Objective

Expand the ML pipeline with advanced statistical analysis and visualization to meet comprehensive data science requirements from the specification image.

---

## 📋 Phase-by-Phase Implementation Plan

### PHASE 7: ADVANCED STATISTICAL ANALYSIS

#### 7.1 Descriptive Statistics Module

**File to create**: `analysis/descriptive_statistics.py`

**Inputs**:

- `outputs/features_lab.csv`
- `outputs/cohort.csv`
- Raw data files: `hosp/labevents.csv`, `hosp/admissions.csv`, etc.

**Outputs**:

- `outputs/descriptive_stats.json` - Comprehensive statistics summary
- `outputs/data_quality_report.csv` - Quality metrics by feature
- `outputs/distributions.json` - Distribution parameters (skewness, kurtosis)

**Tasks**:

1. **Database Shape Analysis** (Complexity: Low)

   ```python
   # Number of records, features, data types
   - Total rows in features_lab.csv: [count]
   - Total columns: [count]
   - Data type distribution
   - Time span: [min_date] to [max_date]
   - Unique patients: [count]
   - Unique ICU stays: [count]
   ```

2. **Univariate Statistics per Feature** (Complexity: Medium)

   ```python
   For each numeric feature compute:
   - Count (non-null values)
   - Mean, Median, Mode
   - Std Dev, Variance
   - Min, Q1, Q2, Q3, Max (5-number summary)
   - IQR = Q3 - Q1
   - Skewness (measure of asymmetry)
   - Kurtosis (measure of tail heaviness)
   - Range = Max - Min

   For categorical/string features:
   - Unique value count
   - Mode (most frequent)
   - Value frequency distribution
   ```

3. **Missing Data Analysis** (Complexity: Medium)

   ```python
   Per feature:
   - Count of missing values
   - Percentage missing
   - Type of missingness:
     * MCAR (Missing Completely At Random): No pattern
     * MAR (Missing At Random): Missing depends on other observed variables
     * MNAR (Missing Not At Random): Missing depends on the value itself
   - Missing data mechanism visualization

   Outputs:
   - Missing data heatmap
   - Missing data patterns by feature group
   ```

4. **Outlier Detection (IQR Method)** (Complexity: Medium)

   ```python
   For each numeric feature:
   - Calculate IQR (Interquartile Range)
   - Lower bound = Q1 - 1.5 * IQR
   - Upper bound = Q3 + 1.5 * IQR
   - Flag values outside [Lower, Upper] as outliers
   - Count outliers and percentage
   - List extreme outliers (beyond 3 * IQR)

   Outputs:
   - Feature-wise outlier statistics
   - Clinical validation: Are they real values or data errors?
   ```

5. **Duplicate Detection** (Complexity: Low)

   ```python
   - Check for exact duplicate rows
   - Check for duplicate stays (same stay_id, different rows)
   - Check for temporal duplicates (same lab measurement at same time)
   - Count and percentage
   ```

6. **Unique Value Analysis** (Complexity: Low)
   ```python
   Per feature:
   - Count of unique values
   - Cardinality ratio (unique / total)
   - Most/least frequent values
   - Distribution of value frequencies
   ```

**Output Format (JSON)**:

```json
{
  "database": {
    "total_records": 140,
    "total_features": 245,
    "numeric_features": 200,
    "categorical_features": 45,
    "date_range": {
      "earliest": "2023-01-15",
      "latest": "2023-12-20"
    },
    "unique_patients": 100,
    "unique_stays": 140
  },
  "feature_statistics": {
    "item_50971_last": {
      "count": 135,
      "missing": 5,
      "missing_pct": 3.6,
      "mean": 7.42,
      "median": 7.35,
      "std": 0.95,
      "min": 5.1,
      "q1": 6.8,
      "q3": 8.1,
      "max": 10.5,
      "iqr": 1.3,
      "outliers": 2,
      "skewness": 0.15,
      "kurtosis": -0.42
    }
    // ... more features
  },
  "data_quality": {
    "duplicate_rows": 0,
    "temporal_duplicates": 3,
    "columns_with_zero_variance": 0,
    "columns_mostly_missing": 2,
    "data_type_mismatches": 0
  }
}
```

**Estimated Time**: 6-8 hours

---

#### 7.2 Bivariate Analysis Module

**File to create**: `analysis/bivariate_analysis.py`

**Inputs**:

- `outputs/features_lab.csv`
- `outputs/cohort.csv`

**Outputs**:

- `outputs/correlation_matrix.csv` - Pairwise correlations
- `outputs/target_associations.csv` - Feature-target associations
- `outputs/multicollinearity_vif.csv` - Variance Inflation Factors

**Tasks**:

1. **Correlation Analysis** (Complexity: Medium)

   ```python
   Method 1: Pearson Correlation (Linear relationships)
   - Range: -1 (negative) to +1 (positive)
   - Formula: ρ = Cov(X,Y) / (σ_X * σ_Y)
   - Interpret: |ρ| > 0.7 = strong, 0.3-0.7 = moderate, < 0.3 = weak

   Method 2: Spearman Rank Correlation (Non-linear, monotonic)
   - Better for skewed or ordinal data
   - Formula: correlation of ranks, not values

   Method 3: Kendall Tau Correlation
   - More robust to outliers than Pearson

   Outputs:
   - Correlation matrix (all features)
   - Ranked correlation pairs (sorted by |correlation|)
   - High correlation pairs (|r| > 0.7): potential redundancy
   - Heatmap visualization
   ```

2. **Feature-Target Association Analysis** (Complexity: Medium)

   ```python
   For association with in_icu_mortality (target):

   For numeric features:
   - Point-biserial correlation (continuous vs binary)
   - Logistic regression coefficient
   - Odds ratio (for binary splits)

   For categorical features:
   - Cramér's V (categorical association measure)
   - Chi-square test (independence test)
   - Contingency table analysis

   For all features:
   - Individual feature AUC (predictive power)
   - Sorted by strength of association

   Output example:
   ```

   Feature,Correlation,P-value,AUC,Odds_Ratio
   item_50971_mean,0.45,0.001,0.68,2.3
   item_50983_max,0.38,0.005,0.64,1.8

   ```

   ```

3. **Multicollinearity Assessment** (Complexity: High)

   ```python
   Variance Inflation Factor (VIF):
   - VIF = 1 / (1 - R²) where R² is from regressing X_i on other X's
   - VIF interpretation:
     * VIF = 1: No correlation
     * VIF < 5: Generally acceptable
     * VIF > 10: Problematic multicollinearity

   Steps:
   1. For each feature, compute VIF
   2. Identify highly correlated feature pairs
   3. Recommend features to remove (keep lower correlation)
   4. Re-compute VIF after removal

   Output:
   - Feature ranking by VIF
   - Recommended features to remove
   ```

4. **Interaction Patterns** (Complexity: Medium)
   ```python
   - Identify feature pairs with significant interactions
   - Compute interaction terms for top pairs
   - Analyze if interaction improves prediction
   ```

**Output Format (CSV)**:

```csv
Feature1,Feature2,Pearson_r,Spearman_rho,Kendall_tau
item_50971_last,item_50983_last,0.72,0.68,0.55
item_50971_last,item_50912_last,0.45,0.42,0.31
...

Feature,Target_Correlation,P_value,AUC,Odds_Ratio,Risk_Group
item_50971_mean,0.45,0.001,0.68,2.3,High Risk
item_50983_max,0.38,0.005,0.64,1.8,High Risk
...

Feature,VIF_Before,VIF_After,Recommendation
item_50971_last,3.2,2.1,Keep
item_50983_last,4.1,2.8,Keep
item_50912_last,8.5,3.5,Consider Removing
```

**Estimated Time**: 4-6 hours

---

#### 7.3 Multivariate Analysis Module

**File to create**: `analysis/multivariate_analysis.py`

**Inputs**:

- `outputs/features_lab.csv`
- Preprocessed feature matrix

**Outputs**:

- `outputs/pca_components.csv` - PCA loadings
- `outputs/pca_variance_explained.json` - Variance per PC
- `outputs/feature_importance_comparison.csv` - Compare methods
- `outputs/stratified_analysis.csv` - Subgroup analysis

**Tasks**:

1. **Dimensionality Reduction: PCA** (Complexity: High)

   ```python
   Steps:
   1. Standardize features (mean=0, std=1)
   2. Compute covariance matrix
   3. Eigenvalue decomposition
   4. Sort by variance explained (descending)
   5. Determine n_components:
      - Keep 80-90% of variance
      - Elbow method

   Outputs:
   - PC1, PC2, ... loadings (contribution of each feature to PC)
   - Scree plot (variance vs PC number)
   - Cumulative variance explained
   - 2D/3D scatter plot of samples in PC space

   Interpretation:
   - Which features drive variation?
   - Natural groupings/clusters?
   - Can we reduce to N dimensions without loss?
   ```

2. **Visualization: t-SNE Clustering** (Complexity: High)

   ```python
   - Nonlinear dimensionality reduction for visualization
   - Project to 2D/3D
   - Color by:
     * Mortality outcome (binary outcome visualization)
     * Patient groups (age, gender, admission type)
     * Model predictions
   - Identify natural clusters and outliers
   ```

3. **Feature Selection: Recursive Feature Elimination (RFE)** (Complexity: High)

   ```python
   Steps:
   1. Train model on all features
   2. Rank features by importance (from model)
   3. Remove lowest-ranking feature
   4. Retrain and repeat
   5. Stop when performance plateaus

   Outputs:
   - Feature ranking
   - Performance vs number of features curve
   - Optimal feature subset
   - Comparison: Model AUC with all features vs selected features
   ```

4. **Feature Importance Comparison** (Complexity: Medium)

   ```python
   Compare multiple methods:
   - SHAP importance (from Phase 6)
   - Model feature importance (XGBoost, LR coefficients)
   - Statistical tests (correlation magnitude)
   - Permutation importance

   Outputs:
   - Ranking agreement between methods
   - Top-10 features by each method
   - Features only important by one method (investigate)
   ```

5. **Stratified Analysis (Subgroup Performance)** (Complexity: Medium)

   ```python
   Analyze model performance for subgroups:

   Grouping variables:
   - Age: <40, 40-60, >60 (from patients.csv)
   - Gender: M/F
   - Admission type: emergency, urgent, elective
   - Stay duration: short, medium, long

   For each group:
   - Model AUC, AUPRC
   - Feature importance (does it change?)
   - Number of positive cases (balance)
   - Average predictions

   Outputs:
   - Subgroup performance matrix
   - Visualization: AUC by subgroup
   - Identify underperforming groups
   ```

**Output Format (CSV)**:

```csv
Component,Variance_Explained,Cumulative_Variance
PC1,0.35,0.35
PC2,0.18,0.53
PC3,0.12,0.65
...

Feature,PCA_Loading_PC1,PCA_Loading_PC2,PCA_Loading_PC3
item_50971_last,0.45,0.12,-0.05
item_50983_last,0.38,0.35,0.08
...

Feature,SHAP_Importance,Model_Importance,Correlation_Rank
item_50971_last,1,2,1
item_50983_last,2,1,3
...

Subgroup,N_Samples,N_Positive,AUC,AUPRC,Sensitivity,Specificity
Age_<40,35,8,0.62,0.28,0.75,0.55
Age_40-60,62,15,0.68,0.35,0.80,0.60
Age_>60,43,12,0.58,0.22,0.67,0.52
```

**Estimated Time**: 8-10 hours

---

### PHASE 8: ADVANCED MODELING

#### 8.1 Model Comparison

**File to create**: `models/compare_models.py`

**New models to implement**:

1. Random Forest
2. LightGBM
3. Neural Network (optional: simple MLP)

**Implementation steps**:

```python
# For each model:
1. Train on training set (temporal split)
2. Evaluate on test set
3. Compute metrics: AUC, AUPRC, Brier, Sensitivity, Specificity
4. Cross-validation: 5-fold with temporal consistency
5. Hyperparameter tuning: GridSearchCV (small grid) or RandomSearchCV
6. Learning curves: plot training vs validation performance vs sample size
7. Detection of overfitting/underfitting
```

**Output**: `outputs/model_comparison.json`, `outputs/model_comparison.csv`

**Estimated Time**: 12-16 hours

---

#### 8.2 Model Robustness Validation

**File to create**: `models/robustness_validation.py`

**Tests**:

1. Bootstrap validation (100 bootstrap samples)
2. Subgroup performance (stability across demographics)
3. Temporal stability (does performance degrade over time?)
4. Sensitivity analysis (what if we remove feature X?)

**Output**: `outputs/robustness_report.csv`

**Estimated Time**: 8-10 hours

---

### PHASE 9: VISUALIZATION & REPORTING

**File to create**: `analysis/visualization.py`

**Plots to generate**:

1. Feature distribution plots (histograms, box plots)
2. Missing data heatmap
3. Correlation heatmap
4. ROC curves (all models)
5. Precision-Recall curves
6. Calibration plots
7. SHAP summary plots (beeswarm, bar)
8. Partial dependence plots
9. Learning curves

**Output format**: PNG files + HTML interactive dashboard

**Estimated Time**: 6-8 hours

---

### PHASE 10: DOCUMENTATION

**Files to create/update**:

1. `PIPELINE_GUIDE.md` - Step-by-step execution guide
2. `METHODOLOGY.md` - Detailed methodology & theory
3. Update docstrings in all Python files
4. Create `RESULTS_SUMMARY.md` with key findings
5. Add unit tests: `tests/test_data_validation.py`

**Estimated Time**: 4-6 hours

---

### PHASE 11: DEPLOYMENT (Optional)

**Files to create**:

1. `api/inference_api.py` - FastAPI endpoint
2. `api/model_server.py` - Model serving
3. `Dockerfile` - Containerization
4. `docker-compose.yml` - Local deployment

**Estimated Time**: 12-16 hours

---

## 📅 Timeline & Priority

### Week 1: Foundation (Required)

- **Priority 1**: Phase 7.1 (Descriptive Stats) - 6-8h
- **Priority 1**: Phase 7.2 (Bivariate Analysis) - 4-6h
- **Priority 2**: Phase 9 (Visualization) - 6-8h
- **Total**: 16-22 hours (~2-3 days intensive work)

### Week 2: Deepening (Recommended)

- **Priority 2**: Phase 7.3 (Multivariate) - 8-10h
- **Priority 2**: Phase 8.1 (Model Comparison) - 12-16h
- **Priority 3**: Phase 8.2 (Robustness) - 8-10h
- **Total**: 28-36 hours (~4-5 days intensive work)

### Week 3: Finalization (Optional)

- **Priority 3**: Phase 10 (Documentation) - 4-6h
- **Priority 4**: Phase 11 (Deployment) - 12-16h
- **Total**: 16-22 hours (~2-3 days intensive work)

**Overall Timeline**: 60-80 hours (1.5-2 weeks full-time)

---

## 🔄 Dependencies Between Phases

```
Phase 7 (Stats) ──→ Phase 9 (Visualization)
                ↘
Phase 8 (Models) ──→ Phase 10 (Documentation) ──→ Phase 11 (Deployment)
                ↙
        Phase 7.3
```

---

## 📊 Success Criteria

### Quantitative

- [ ] All 200+ features have complete statistical summary
- [ ] Correlation matrix computed & validated
- [ ] Feature importance methods agree on top-10 features (>70% overlap)
- [ ] Model comparison: 3+ models with cross-validation
- [ ] Robustness: performance stable across subgroups (AUC variance < 0.1)

### Qualitative

- [ ] Clear interpretation of results (written explanations)
- [ ] Actionable insights from statistical analysis
- [ ] Model selection justified with evidence
- [ ] Code fully documented and reproducible
- [ ] Visualization dashboard comprehensive and professional

---

## 🛠️ Technical Stack

**Current**:

- Python 3.8+
- pandas, numpy, scikit-learn
- xgboost
- joblib

**New packages needed**:

- `scipy` (for statistics: correlation, tests)
- `matplotlib`, `seaborn` (visualization)
- `shap` (already in pipeline)
- `scikit-plot` (for ROC, precision-recall)
- `plotly` (optional: interactive visualizations)
- `lightgbm` (for model comparison)
- `tensorflow/keras` (optional: neural networks)

**Installation**:

```bash
pip install scipy scikit-plot plotly lightgbm
```

---

## 📝 Code Structure Example

```python
# analysis/descriptive_statistics.py
import pandas as pd
import numpy as np
from scipy import stats

def compute_univariate_stats(series):
    """Compute statistics for a single feature."""
    return {
        'count': series.count(),
        'mean': series.mean(),
        'median': series.median(),
        'std': series.std(),
        'min': series.min(),
        'q1': series.quantile(0.25),
        'q3': series.quantile(0.75),
        'max': series.max(),
        'skewness': stats.skew(series.dropna()),
        'kurtosis': stats.kurtosis(series.dropna()),
        'missing': series.isna().sum(),
        'missing_pct': series.isna().mean() * 100,
    }

def detect_outliers_iqr(series):
    """Detect outliers using IQR method."""
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = series[(series < lower_bound) | (series > upper_bound)]
    return {
        'count': len(outliers),
        'percentage': len(outliers) / len(series) * 100,
        'values': outliers.values.tolist(),
    }

def main():
    # Load data
    df = pd.read_csv('outputs/features_lab.csv')

    # Compute stats for all numeric features
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    stats_dict = {}
    for col in numeric_cols:
        stats_dict[col] = compute_univariate_stats(df[col])
        stats_dict[col]['outliers'] = detect_outliers_iqr(df[col])

    # Save results
    import json
    with open('outputs/descriptive_stats.json', 'w') as f:
        json.dump(stats_dict, f, indent=2, default=str)

    print("Descriptive statistics saved!")
```

---

## ✅ Checklist for Implementation

### Before starting Phase 7:

- [ ] Review requirements from specification image
- [ ] Review existing `outputs/` files
- [ ] Understand target variable distribution (in_icu_mortality)
- [ ] Set up separate `analysis/` directory
- [ ] Update `requirements.txt` with new packages

### During Phase 7:

- [ ] Write each analysis module separately
- [ ] Test on sample data first
- [ ] Save intermediate results as CSV/JSON
- [ ] Create visualizations for validation

### After each phase:

- [ ] Verify outputs are correct (spot checks)
- [ ] Write summary of findings
- [ ] Update README.md with results
- [ ] Commit to git with meaningful messages

---

## 🎯 Next Immediate Action

**START**: Implement Phase 7.1 (Descriptive Statistics)

**Steps**:

1. Create `analysis/` directory
2. Create `analysis/__init__.py` (empty file)
3. Create `analysis/descriptive_statistics.py` with functions:
   - `load_features()`: Load features_lab.csv
   - `compute_database_shape()`: Count records, features, date range
   - `compute_univariate_stats()`: Stats per feature
   - `detect_missing_patterns()`: Analyze missing data
   - `detect_outliers_iqr()`: Find outliers
   - `detect_duplicates()`: Find duplicate rows
   - `main()`: Orchestrate all analyses
4. Run script and validate outputs
5. Proceed to Phase 7.2

**Time estimate for Phase 7.1**: 6-8 hours

---

**END OF IMPLEMENTATION PLAN**

For questions or clarifications, refer to:

- README.md (Phase descriptions)
- Existing model scripts (code patterns)
- Output files (data format examples)
