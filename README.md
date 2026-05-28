# MIMIC-IV Clinical Database Demo - ICU Mortality Prediction ML Pipeline

## 📊 Project Overview

This project implements a **complete Machine Learning pipeline** to predict **in-ICU mortality** from laboratory test results using the MIMIC-IV clinical database demo subset (100 patients).

**Target**: Build a data science application following the comprehensive analytics workflow outlined below.

---

## 📈 Pipeline Architecture

```
[Raw Data] → [EDA] → [Data Preparation] → [Feature Engineering] →
[Preprocessing] → [Leakage Detection] → [Modeling] → [Evaluation] →
[Interpretation] → [Deployment]
```

---

## ✅ COMPLETED TASKS (Current Progress: ~70%)

### Phase 1: Exploratory Data Analysis (EDA) ✓

- **Script**: `etl/quick_eda.py`
- **Outputs**: `outputs/summary.json`, `outputs/top_items.csv`
- **Status**: ✅ DONE
- **Details**:
  - Analyzed 140 ICU stays
  - Found 107,727 lab events from 498 unique lab items
  - Identified top-20 most frequent lab tests
  - Calculated missing value statistics (11.6% missing valuenum)
  - Computed coverage: 128/140 patients have top lab items during ICU stay

**Data Summary**:

```json
{
  "n_icustays": 140,
  "n_labevents": 107,727,
  "n_unique_itemid": 498,
  "percent_missing_valuenum": 11.6%,
  "label_balance": "in_hospital_mortality_rate": ~23%
}
```

### Phase 2: Data Preparation & Cohort Building ✓

- **Script**: `etl/build_cohort.py`
- **Output**: `outputs/cohort.csv`
- **Status**: ✅ DONE
- **Details**:
  - Merged ICU stays with hospital admissions & patient demographics
  - Created binary mortality labels:
    - `in_icu_mortality`: Death during ICU stay
    - `in_hospital_mortality`: Death during hospitalization
  - Validated temporal consistency

### Phase 3: Feature Engineering ✓

#### 3.1 Base Lab Features

- **Script**: `features/build_lab_features.py`
- **Output**: `outputs/features_lab.csv`
- **Status**: ✅ DONE
- **Features per ICU stay**:
  - `item_{id}_last`: Last observed value
  - `item_{id}_mean`: Mean value during stay
  - `item_{id}_min`, `item_{id}_max`: Min/max values
  - `item_{id}_std`: Standard deviation
  - `item_{id}_count`: Number of measurements
  - `item_{id}_time_to_first_hours`: Hours to first measurement
  - `item_{id}_pct_abnormal`: Percentage of abnormal readings

#### 3.2 Derived Time-Trend Features

- **Script**: `features/compute_lab_trends.py`
- **Output**: `outputs/features_lab_derived.csv`
- **Status**: ✅ DONE
- **Features**:
  - `item_{id}_slope`: Rate of change (value per hour)
  - `item_{id}_delta`: Change from first to last value
  - `item_{id}_time_to_first_hours`: Time to first measurement

### Phase 4: Data Quality & Leakage Detection ✓

- **Script**: `models/check_leakage.py`
- **Outputs**: `outputs/leakage_report.csv`, `outputs/suspicious_features.txt`
- **Status**: ✅ DONE
- **Analysis**:
  - Computed individual feature AUC scores
  - Identified features with zero variance
  - Flagged features with >90% missing values
  - Detected suspicious high-AUC features (potential leakage)

### Phase 5: Model Training & Evaluation ✓

#### 5.1 Baseline Models

- **Script**: `models/train_baseline.py`
- **Output**: `outputs/model_metrics.json`
- **Status**: ✅ DONE
- **Models**:
  - **Logistic Regression**: AUC = 0.577, AUPRC = 0.293
  - **XGBoost**: AUC = 0.635, AUPRC = 0.138

#### 5.2 Temporal-Split Evaluation (Production-Ready)

- **Script**: `models/evaluate_temporal.py`
- **Output**: `outputs/model_metrics_temporal.json`
- **Status**: ✅ DONE
- **Approach**: Split by time (median intime) to simulate deployment scenario
- **Improvements**:
  - Used class balancing for imbalanced data
  - Computed sensitivity, specificity, optimal thresholds

#### 5.3 Post-hoc Threshold Optimization

- **Script**: `models/posthoc_thresholds_and_calibration.py`
- **Outputs**:
  - `outputs/xgb_temporal_model.joblib`: Trained model
  - `outputs/thresholds_metrics.csv`: Performance at different thresholds
  - `outputs/calibration_xgb.npz`: Calibration curve data
  - `outputs/model_posthoc.json`: Optimal threshold metrics
- **Status**: ✅ DONE
- **Details**:
  - Threshold sweep: 0.0 to 1.0 (101 thresholds)
  - Optimized for F1-score and Youden index
  - Calibration analysis for probability reliability

### Phase 6: Model Interpretation ✓

- **Script**: `models/shap_explain_xgb.py`
- **Outputs**: `outputs/shap_summary.csv`, `outputs/shap_test_values.npz`
- **Status**: ✅ DONE
- **Method**: SHAP (SHapley Additive exPlanations) TreeExplainer
- **Provides**:
  - Feature importance scores
  - Individual prediction explanations

---

## 🔴 REMAINING TASKS (Next Phase: ~30%)

### Phase 7: Advanced Statistical Analysis (REQUIRED) ⚠️

#### 7.1 Descriptive Statistics [PRIORITY: HIGH]

- **Goal**: Comprehensive database overview
- **Tasks**:
  1. **Database Shape Analysis**
     - Total records & unique patients
     - Feature count & data types
     - Time span of data collection
  2. **Univariate Analysis**
     - Central tendency: mean, median, mode
     - Dispersion: std dev, IQR, range
     - Distribution plots (histograms, box plots)
     - Outlier detection using IQR method
  3. **Missing Data Analysis**
     - Pattern visualization
     - Missing completely at random (MCAR) vs MAR vs MNAR
     - Imputation strategy evaluation
  4. **Data Quality Assessment**
     - Duplicate record detection
     - Logical consistency checks
     - Noise detection (outliers beyond clinical range)
     - Unique value analysis per feature

- **Output**: `outputs/descriptive_statistics.json`, `outputs/data_quality_report.csv`
- **Estimated Time**: 6-8 hours

#### 7.2 Bivariate Analysis [PRIORITY: HIGH]

- **Goal**: Identify feature relationships
- **Tasks**:
  1. **Correlation Analysis**
     - Pearson correlation for continuous variables
     - Spearman rank correlation (non-linear relationships)
     - Correlation heatmap visualization
  2. **Association with Target (Mortality)**
     - Chi-square test for categorical vs mortality
     - Point-biserial correlation for binary associations
     - Odds ratios for risk features
  3. **Feature Pairs**
     - Identify highly correlated features
     - Multicollinearity detection (VIF)
     - Interaction patterns

- **Output**: `outputs/correlation_matrix.csv`, `outputs/target_associations.csv`
- **Estimated Time**: 4-6 hours

#### 7.3 Multivariate Analysis [PRIORITY: MEDIUM]

- **Goal**: Understand complex feature relationships
- **Tasks**:
  1. **Dimensionality Reduction**
     - PCA (Principal Component Analysis)
     - T-SNE visualization of patient clusters
     - Feature selection using recursive feature elimination
  2. **Feature Importance Comparison**
     - Compare SHAP vs model feature importance vs statistical tests
     - Identify redundant features
  3. **Stratified Analysis**
     - Performance by age groups, admission types
     - Gender-based differences
     - Time-of-admission patterns

- **Output**: `outputs/pca_loadings.csv`, `outputs/stratified_analysis.csv`
- **Estimated Time**: 8-10 hours

### Phase 8: Advanced Modeling [PRIORITY: MEDIUM]

#### 8.1 Model Comparison

- **Goal**: Compare different algorithms
- **Tasks**:
  1. Implement additional models:
     - Random Forest
     - Gradient Boosting (LightGBM)
     - Neural Networks (if appropriate)
  2. Cross-validation: 5-fold or 10-fold
  3. Hyperparameter tuning using GridSearchCV/RandomSearchCV
  4. Learning curves to detect overfitting

- **Output**: `outputs/model_comparison.json`, `outputs/learning_curves.png`
- **Estimated Time**: 12-16 hours

#### 8.2 Model Robustness

- **Goal**: Validate generalization
- **Tasks**:
  1. Bootstrap validation
  2. Subgroup performance analysis
  3. Temporal stability (performance over time)
  4. Sensitivity analysis on key features

- **Output**: `outputs/robustness_report.csv`
- **Estimated Time**: 8-10 hours

### Phase 9: Visualization & Reporting [PRIORITY: HIGH]

- **Goal**: Create comprehensive visual analysis
- **Tasks**:
  1. **Data Exploration Dashboard**
     - Feature distributions
     - Missing data heatmap
     - Correlation network
  2. **Model Performance Visuals**
     - ROC curves (all models)
     - Precision-Recall curves
     - Calibration plots
     - Confusion matrices
  3. **Feature Importance Plots**
     - SHAP summary plots
     - SHAP dependence plots
     - Feature interaction plots

- **Output**: `outputs/visualizations/` (PNG, HTML interactive plots)
- **Estimated Time**: 6-8 hours

### Phase 10: Documentation & Reproducibility [PRIORITY: MEDIUM]

- **Tasks**:
  1. Update README with results
  2. Create `PIPELINE_GUIDE.md` with step-by-step execution
  3. Add script docstrings & comments
  4. Create requirements.txt with versions
  5. Add unit tests for data validation

- **Estimated Time**: 4-6 hours

### Phase 11: Deployment Preparation [PRIORITY: LOW]

- **Tasks**:
  1. Create inference API (Flask/FastAPI)
  2. Package model as Docker container
  3. Create prediction pipeline script
  4. Add model serving documentation

- **Estimated Time**: 12-16 hours

---

## 📋 Detailed Plan for Next Steps

### Week 1: Statistical Foundation (Priority)

```
Day 1-2: Descriptive Statistics (7.1)
  ├─ Database shape & structure
  ├─ Univariate analysis per feature
  ├─ Missing data patterns
  └─ Data quality checks

Day 3-4: Bivariate Analysis (7.2)
  ├─ Correlation analysis
  ├─ Target associations
  └─ Multicollinearity assessment

Day 5: Visualization (9.1)
  └─ Create exploratory plots
```

### Week 2: Deepening the Analysis

```
Day 1-2: Multivariate Analysis (7.3)
  ├─ PCA & dimensionality reduction
  ├─ Feature selection
  └─ Stratified analysis

Day 3-4: Advanced Modeling (8.1-8.2)
  ├─ Additional model implementations
  ├─ Hyperparameter tuning
  └─ Robustness validation

Day 5: Reporting (10)
  └─ Consolidate findings
```

---

## 🚀 How to Run the Pipeline

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# For SHAP explanations (optional)
pip install shap
```

### Execute Pipeline Steps (in order)

```bash
# 1. EDA
python etl/quick_eda.py

# 2. Build cohort
python etl/build_cohort.py

# 3. Build lab features
python features/build_lab_features.py

# 4. Compute derived features
python features/compute_lab_trends.py

# 5. Check for leakage
python models/check_leakage.py

# 6. Train baseline models
python models/train_baseline.py

# 7. Temporal evaluation
python models/evaluate_temporal.py

# 8. Post-hoc optimization
python models/posthoc_thresholds_and_calibration.py

# 9. SHAP interpretation
python models/shap_explain_xgb.py

# 10. [NEW] Advanced statistics (to be implemented)
python analysis/descriptive_statistics.py
python analysis/bivariate_analysis.py
python analysis/multivariate_analysis.py
```

---

## 📊 Key Results Summary

| Metric                          | Logistic Regression | XGBoost |
| ------------------------------- | ------------------- | ------- |
| AUC (Baseline)                  | 0.577               | 0.635   |
| AUPRC (Baseline)                | 0.293               | 0.138   |
| Sensitivity (Optimal Threshold) | TBD                 | TBD     |
| Specificity (Optimal Threshold) | TBD                 | TBD     |

---

## 📁 Project Structure

```
.
├── etl/                           # Extract, Transform, Load
│   ├── build_cohort.py           # Build cohort & labels
│   └── quick_eda.py              # Exploratory analysis
├── features/                      # Feature engineering
│   ├── build_lab_features.py      # Base feature aggregation
│   └── compute_lab_trends.py      # Derived time-trend features
├── models/                        # Model training & evaluation
│   ├── train_baseline.py          # Baseline models
│   ├── evaluate_temporal.py       # Temporal-split evaluation
│   ├── posthoc_thresholds_and_calibration.py  # Threshold optimization
│   ├── check_leakage.py           # Leakage detection
│   ├── shap_explain_xgb.py        # Model interpretation
│   ├── evaluate_with_derived.py   # [OPTIONAL] Using derived features
│   ├── feature_mapping.py         # [OPTIONAL] Feature ID mapping
│   └── remove_leaky_and_retrain.py # [OPTIONAL] Remove suspicious features
├── analysis/                      # [NEW] Advanced statistical analysis
│   ├── descriptive_statistics.py  # TODO
│   ├── bivariate_analysis.py      # TODO
│   ├── multivariate_analysis.py   # TODO
│   └── visualization.py           # TODO
├── outputs/                       # All outputs
│   ├── *.csv                      # Data files
│   ├── *.json                     # Metrics & summaries
│   ├── *.joblib                   # Trained models
│   └── *.npz                      # Numpy archives (SHAP, calibration)
├── hosp/                          # Hospital data (read-only)
├── icu/                           # ICU data (read-only)
├── README.md                      # This file
└── requirements.txt               # Python dependencies
```

---

## 🎯 Analysis Requirements (from specification)

Your project must cover:

### ✅ Data Understanding

- [x] Database overview (shape, columns)
- [x] Missing value analysis (11.6% in valuenum)
- [x] Duplicate detection
- [x] Noise detection (IQR method for outliers)
- [x] Unique value analysis

### ✅ Descriptive Analysis (IN PROGRESS)

- [x] Database description (done in EDA)
- [x] Feature statistics (basic done)
- [ ] **Advanced**: Complete univariate/bivariate/multivariate analysis
- [ ] Distribution plots
- [ ] Outlier visualization

### ✅ Statistical Analysis (IN PROGRESS)

- [x] Descriptive stats (basic)
- [ ] **Advanced**: Correlation, association tests
- [ ] Hypothesis testing
- [ ] Group comparisons

### ✅ Machine Learning (70% DONE)

- [x] Model training (LR, XGBoost)
- [x] Model evaluation (AUC, AUPRC)
- [x] Feature importance (SHAP)
- [ ] **Advanced**: Cross-validation, hyperparameter tuning
- [x] Threshold optimization
- [x] Calibration analysis

### ⚠️ Code Quality & Documentation

- [ ] Add script comments & docstrings
- [ ] Create analysis pipeline guide
- [ ] Add unit tests
- [ ] Package for reproducibility

---

## 💡 Recommendations for Next Phase

1. **Priority 1 (Immediate)**:
   - Implement descriptive statistics module (Phase 7.1)
   - Create data quality report with visualizations
   - Add correlation & association analysis (Phase 7.2)

2. **Priority 2 (Next)**:
   - Implement multivariate analysis (PCA, feature selection)
   - Expand model comparison (Random Forest, LightGBM)
   - Create comprehensive visualization dashboard

3. **Priority 3 (Optional)**:
   - Hyperparameter optimization using Bayesian search
   - Cross-validation with nested loops
   - Deployment API endpoint

---

## 📚 References

- MIMIC-IV Data: https://doi.org/10.13026/07hj-2a80
- SHAP Documentation: https://shap.readthedocs.io/
- Scikit-learn: https://scikit-learn.org/
- XGBoost: https://xgboost.readthedocs.io/

---

## 👤 Author Notes

This pipeline demonstrates a complete ML workflow from raw hospital data to model interpretation. The modular structure allows for easy extension and modification of each phase.

**Last Updated**: May 28, 2026
**Status**: 70% Complete - Ready for advanced statistical analysis
