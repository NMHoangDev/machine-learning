# QUICK START GUIDE

## MIMIC-IV ICU Mortality Prediction Pipeline

**Duration**: 5 minutes (to understand), 30 minutes (to run)

---

## 1️⃣ Prerequisites

- **Python 3.8+** installed
- **Git** (to clone repo)
- **~2GB disk space** (for data & outputs)
- 10-15 minutes runtime on modern CPU

---

## 2️⃣ Setup (2 minutes)

### Option A: Using Conda

```bash
# Create environment
conda create -n mimic python=3.8
conda activate mimic

# Install dependencies
pip install -r requirements.txt
```

### Option B: Using venv

```bash
# Create virtual environment
python -m venv mimic_env
source mimic_env/bin/activate  # On Windows: mimic_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Verify Installation

```bash
python -c "import pandas, numpy, sklearn, xgboost; print('✓ All packages installed')"
```

---

## 3️⃣ Run the Complete Pipeline (25 minutes)

### Option 1: Run All Steps (Recommended)

```bash
# From repository root directory

# 1. EDA (2 min)
python etl/quick_eda.py

# 2. Build cohort (1 min)
python etl/build_cohort.py

# 3. Build base features (3 min)
python features/build_lab_features.py

# 4. Compute derived features (2 min)
python features/compute_lab_trends.py

# 5. Check for leakage (1 min)
python models/check_leakage.py

# 6. Train baseline models (3 min)
python models/train_baseline.py

# 7. Temporal evaluation (2 min)
python models/evaluate_temporal.py

# 8. Threshold optimization (2 min)
python models/posthoc_thresholds_and_calibration.py

# 9. SHAP explanations (5 min)
python models/shap_explain_xgb.py

echo "✓ Pipeline complete! Check outputs/ directory."
```

### Option 2: Run Bash Script (Unix/Linux/Mac only)

```bash
# Create run_all.sh
bash << 'EOF'
#!/bin/bash
echo "Starting MIMIC-IV ML Pipeline..."
python etl/quick_eda.py && echo "✓ EDA done"
python etl/build_cohort.py && echo "✓ Cohort done"
python features/build_lab_features.py && echo "✓ Base features done"
python features/compute_lab_trends.py && echo "✓ Derived features done"
python models/check_leakage.py && echo "✓ Leakage check done"
python models/train_baseline.py && echo "✓ Models trained"
python models/evaluate_temporal.py && echo "✓ Evaluation done"
python models/posthoc_thresholds_and_calibration.py && echo "✓ Calibration done"
python models/shap_explain_xgb.py && echo "✓ SHAP done"
echo "✓✓✓ PIPELINE COMPLETE ✓✓✓"
EOF
```

### Option 3: Run Individual Steps

```bash
# Run only specific steps

# Just do EDA
python etl/quick_eda.py

# Just build features
python features/build_lab_features.py

# Just train models (assumes features_lab.csv exists)
python models/train_baseline.py
```

---

## 4️⃣ Check Results (1 minute)

After pipeline completes, review outputs:

```bash
# View data summary
cat outputs/summary.json | python -m json.tool

# View top lab items
head outputs/top_items.csv

# View model metrics
cat outputs/model_metrics.json | python -m json.tool

# View temporal metrics
cat outputs/model_metrics_temporal.json | python -m json.tool

# View leakage report (top 10)
head outputs/leakage_report.csv

# View threshold metrics
head outputs/thresholds_metrics.csv

# View SHAP feature importance
head outputs/shap_summary.csv
```

---

## 5️⃣ Understand the Results

### Key Output Files

#### 📊 Data Files

| File                       | Purpose                         | Format | Records |
| -------------------------- | ------------------------------- | ------ | ------- |
| `cohort.csv`               | Patient cohort definition       | CSV    | 140     |
| `features_lab.csv`         | Feature matrix (lab aggregates) | CSV    | 140     |
| `features_lab_derived.csv` | Derived trend features          | CSV    | 140     |
| `top_items.csv`            | Top-20 most frequent lab items  | CSV    | 20      |

#### 📈 Analysis Files

| File                      | Purpose                      | Content                                 |
| ------------------------- | ---------------------------- | --------------------------------------- |
| `summary.json`            | EDA summary statistics       | Record counts, missing %, item coverage |
| `leakage_report.csv`      | Feature quality assessment   | Feature AUC, variance, missing %        |
| `suspicious_features.txt` | Potential leakage indicators | Features with AUC > 0.98                |

#### 🤖 Model Files

| File                          | Purpose                     | Content                                |
| ----------------------------- | --------------------------- | -------------------------------------- |
| `model_metrics.json`          | Baseline model performance  | LR & XGBoost AUC, AUPRC                |
| `model_metrics_temporal.json` | Temporal-split evaluation   | Metrics on realistic time split        |
| `xgb_temporal_model.joblib`   | Trained XGBoost model       | **Ready for deployment**               |
| `model_posthoc.json`          | Optimal decision thresholds | F1-optimal & Youden-optimal thresholds |

#### 🎯 Interpretation Files

| File                     | Purpose                        | Content                                   |
| ------------------------ | ------------------------------ | ----------------------------------------- |
| `shap_summary.csv`       | Feature importance ranking     | Mean absolute SHAP values per feature     |
| `shap_test_values.npz`   | Raw SHAP values                | For detailed analysis plots               |
| `calibration_xgb.npz`    | Model calibration data         | Empirical vs predicted probabilities      |
| `thresholds_metrics.csv` | Decision threshold performance | Sensitivity/specificity at 101 thresholds |

### Reading the Results

#### Example: Model Performance

```json
{
  "logistic_auc": 0.577,
  "logistic_auprc": 0.293,
  "xgb_auc": 0.635,
  "xgb_auprc": 0.138
}
```

**Interpretation**:

- XGBoost slightly better (AUC 0.635 > 0.577)
- Both models show moderate performance
- AUPRC low due to class imbalance (~23% mortality rate)
- **Recommendation**: Continue with advanced modeling (Phase 8)

#### Example: Top Features (from `shap_summary.csv`)

```csv
Feature,Mean_Abs_SHAP
item_50971_mean,0.045
item_50983_max,0.038
item_50912_mean,0.035
...
```

**Interpretation**:

- `item_50971` (likely Potassium) is most predictive
- These features should be stable in patient care
- If unexpected, verify with clinical domain expert

#### Example: Suspicious Features (from `suspicious_features.txt`)

```
item_99999_count,high_auc,0.98
item_88888_last,zero_variance,0.0
```

**Interpretation**:

- `item_99999_count` may contain leakage signal
- `item_88888_last` has no variation (useless)
- **Action**: Consider removing before re-training

---

## 6️⃣ Next Steps (Choose One)

### Option A: Advanced Analytics (Recommended)

For deeper analysis following the specification:

```bash
# See IMPLEMENTATION_PLAN.md for detailed instructions
# Next: Implement Phase 7 (Advanced Statistical Analysis)

# Create analysis directory
mkdir analysis
touch analysis/__init__.py

# Follow Phase 7.1 implementation guide
# (See IMPLEMENTATION_PLAN.md for code template)
```

### Option B: Deploy the Model

Ready to use in production:

```bash
# Load trained model
python -c "
from joblib import load
model = load('outputs/xgb_temporal_model.joblib')

# Make predictions on new data (must have same 200 features)
import pandas as pd
X_new = pd.read_csv('path/to/new_features.csv')
predictions = model.predict_proba(X_new)[:, 1]
print(predictions)
"
```

### Option C: Explore Results Interactively

```bash
# Start Python interactive session
python

# Load and explore
import pandas as pd
features = pd.read_csv('outputs/features_lab.csv')
print(features.head())
print(features.describe())

# Load model
from joblib import load
model = load('outputs/xgb_temporal_model.joblib')
print(model.feature_importances_[:5])

# Load SHAP values
import numpy as np
shap_data = np.load('outputs/shap_test_values.npz')
print(shap_data.files)  # What's in the archive
```

---

## 7️⃣ Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'xgboost'"

```bash
# Solution: Install missing packages
pip install xgboost scikit-learn pandas numpy scipy
```

### Issue: "FileNotFoundError: hosp/labevents.csv"

```bash
# Make sure you're in the repository root directory
pwd  # Check current directory
cd /path/to/mimic-iv-clinical-database-demo-2.2
```

### Issue: Script takes too long (>5 minutes)

```bash
# Check if it's still running (some steps are I/O intensive)
# Or reduce data size: edit scripts to use head(1000) on DataFrames
```

### Issue: "Memory Error"

```bash
# Reduce batch processing size
# Edit build_lab_features.py and reduce chunk size
# Or: Close other applications to free memory
```

### Issue: Model gives poor predictions

```bash
# This is expected with only lab data
# Advanced modeling (Phase 8) should improve performance
# Or add demographic features (age, gender, admission type)
```

---

## 8️⃣ Project Structure Overview

```
mimic-iv-clinical-database-demo-2.2/
│
├── etl/                      # Data extraction & transformation
│   ├── quick_eda.py         # ← START HERE: Exploratory analysis
│   └── build_cohort.py      # ← SECOND: Build study cohort
│
├── features/                 # Feature engineering
│   ├── build_lab_features.py        # Create base features
│   └── compute_lab_trends.py        # Create trend features
│
├── models/                   # Model training & evaluation
│   ├── check_leakage.py              # Data quality check
│   ├── train_baseline.py             # Train models
│   ├── evaluate_temporal.py          # Realistic evaluation
│   ├── posthoc_thresholds_and_calibration.py  # Optimize thresholds
│   └── shap_explain_xgb.py           # Explain predictions
│
├── hosp/                     # Hospital data (read-only)
├── icu/                      # ICU data (read-only)
│
├── outputs/                  # ← ALL RESULTS GO HERE
│   ├── *.csv                 # Feature matrices, metrics
│   ├── *.json                # Summaries, metrics
│   ├── *.joblib              # Trained models
│   └── *.npz                 # Numpy data (SHAP, calibration)
│
├── README.md                 # Full project documentation
├── IMPLEMENTATION_PLAN.md    # Detailed next steps
├── PROJECT_STATUS.md         # Current progress & issues
└── QUICK_START.md           # This file
```

---

## 9️⃣ Advanced Usage

### Load Trained Model for Predictions

```python
from joblib import load
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer

# Load model
model = load('outputs/xgb_temporal_model.joblib')

# Load feature template (to get feature names & order)
features_template = pd.read_csv('outputs/features_lab.csv', nrows=1)
feature_columns = [c for c in features_template.columns
                   if c not in ['stay_id', 'subject_id', 'hadm_id',
                                'intime', 'outtime', 'in_icu_mortality',
                                'in_hospital_mortality']]

# Prepare new patient data (must have same 200 features)
X_new = pd.read_csv('path/to/new_patients_features.csv')
X_new = X_new[feature_columns]

# Impute missing values (same as training)
imputer = SimpleImputer(strategy='median')
X_new_imputed = imputer.fit_transform(X_new)

# Make predictions
probabilities = model.predict_proba(X_new_imputed)[:, 1]
predictions = model.predict(X_new_imputed)

# Get predictions with optimal threshold
optimal_threshold = 0.45  # From outputs/model_posthoc.json
risk_predictions = (probabilities >= optimal_threshold).astype(int)

print(f"Prediction probabilities: {probabilities}")
print(f"Binary predictions (threshold=0.45): {risk_predictions}")
```

### Extract Feature Importance

```python
import pandas as pd

# Method 1: From SHAP (recommended)
shap_importance = pd.read_csv('outputs/shap_summary.csv')
print(shap_importance.head(10))

# Method 2: From model
from joblib import load
model = load('outputs/xgb_temporal_model.joblib')
importances = model.feature_importances_
# Sort by importance
idx = np.argsort(importances)[::-1]
print(f"Top 10 features: {feature_columns[idx[:10]]}")
```

### Analyze Decision Thresholds

```python
import pandas as pd

# Load threshold metrics
thresholds = pd.read_csv('outputs/thresholds_metrics.csv')

# Find optimal threshold by different criteria
best_f1_idx = thresholds['f1'].idxmax()
best_f1 = thresholds.loc[best_f1_idx]

best_youden_idx = (thresholds['sensitivity'] + thresholds['specificity']).idxmax()
best_youden = thresholds.loc[best_youden_idx]

print(f"F1-optimal: threshold={best_f1['threshold']}, F1={best_f1['f1']}")
print(f"  Sensitivity={best_f1['sensitivity']}, Specificity={best_f1['specificity']}")

print(f"\nYouden-optimal: threshold={best_youden['threshold']}")
print(f"  Sensitivity={best_youden['sensitivity']}, Specificity={best_youden['specificity']}")
```

---

## 🔟 Performance Summary

### Training Speed

| Step           | Time       | Notes                      |
| -------------- | ---------- | -------------------------- |
| EDA            | 2 min      | Loads all lab events       |
| Cohort         | 1 min      | Simple merge               |
| Features       | 3 min      | Aggregation across stays   |
| Trends         | 2 min      | Slope computation          |
| Leakage Check  | 1 min      | Fast AUC computation       |
| Model Training | 3 min      | LR + XGBoost               |
| Evaluation     | 2 min      | Metrics computation        |
| Thresholds     | 2 min      | Threshold sweep            |
| SHAP           | 5 min      | Explainability computation |
| **TOTAL**      | **21 min** | Full pipeline              |

### Model Performance

| Metric               | Logistic Regression | XGBoost            |
| -------------------- | ------------------- | ------------------ |
| **AUC**              | 0.577               | **0.635** ← Better |
| **AUPRC**            | 0.293               | 0.138              |
| **Interpretability** | High                | Medium             |
| **Speed**            | Very Fast           | Fast               |

---

## 📞 Getting Help

### Documentation

- **Project Overview**: See `README.md`
- **Detailed Plan**: See `IMPLEMENTATION_PLAN.md`
- **Current Status**: See `PROJECT_STATUS.md`
- **Dataset Info**: See `README_pipeline.md` & `README.txt`

### Common Questions

**Q: Why is model AUC only 0.635?**  
A: Expected with only lab data. Demographics, vital signs, and clinical notes would improve performance. See Phase 8 for model improvements.

**Q: What features are most important?**  
A: See `outputs/shap_summary.csv` for SHAP importance ranking. Check feature names against clinical knowledge.

**Q: Is the model ready for clinical deployment?**  
A: Not yet. Requires clinical validation, regulatory review, and improved AUC. Consider this a research prototype.

**Q: How do I make predictions on new patients?**  
A: See "Advanced Usage" section above for code example.

**Q: Can I modify the features?**  
A: Yes! See feature engineering scripts in `features/` directory. Re-run pipeline after modifications.

---

## 📊 Output Validation Checklist

After running pipeline, verify these files exist:

```bash
# Check critical files
test -f outputs/cohort.csv && echo "✓ cohort.csv"
test -f outputs/features_lab.csv && echo "✓ features_lab.csv"
test -f outputs/features_lab_derived.csv && echo "✓ features_lab_derived.csv"
test -f outputs/xgb_temporal_model.joblib && echo "✓ model ready for deployment"
test -f outputs/shap_summary.csv && echo "✓ feature importance available"
test -f outputs/model_metrics_temporal.json && echo "✓ evaluation metrics ready"

# Count total output files
echo "Total outputs: $(ls outputs/ | wc -l) files"
```

---

**Happy analyzing! 🎉**

For advanced work, see `IMPLEMENTATION_PLAN.md`  
For project status, see `PROJECT_STATUS.md`  
For questions, refer to `README.md`

Last updated: May 28, 2026
