# Complete Pipeline Execution Guide

## 🚀 Run Everything in One Command

For those who want to run the entire pipeline from start to finish:

### Option 1: One Command (Recommended)

```bash
python run_complete_pipeline.py
```

This single command will:

1. ✓ Execute all 9 phases automatically
2. ✓ Handle errors gracefully
3. ✓ Generate comprehensive reports
4. ✓ Create interactive dashboard
5. ✓ Print summary at the end

**Estimated time**: 2-3 hours (depending on your CPU)

### Option 2: Step-by-Step Execution

If you prefer to run individual phases and monitor progress:

```bash
# Phase 1: EDA (2 min)
python etl/quick_eda.py

# Phase 2: Cohort Building (1 min)
python etl/build_cohort.py

# Phase 3: Feature Engineering (5 min)
python features/build_lab_features.py
python features/compute_lab_trends.py

# Phase 4: Leakage Detection (1 min)
python models/check_leakage.py

# Phase 5: Model Training & Evaluation (7 min)
python models/train_baseline.py
python models/evaluate_temporal.py
python models/posthoc_thresholds_and_calibration.py
python models/shap_explain_xgb.py

# Phase 7: Advanced Statistical Analysis (20 min)
python analysis/descriptive_statistics.py
python analysis/bivariate_analysis.py
python analysis/multivariate_analysis.py

# Phase 8: Model Comparison (30 min)
python models/compare_models.py

# Phase 9: Visualization & Dashboard (15 min)
python analysis/visualization.py
python analysis/generate_dashboard.py
```

**Total time**: ~90 minutes for new analysis

### Option 3: Run Specific Phase Only

```bash
# Just run descriptive statistics
python analysis/descriptive_statistics.py

# Just run model comparison
python models/compare_models.py

# Just generate dashboard from existing results
python analysis/generate_dashboard.py
```

---

## 📊 View Results

After execution completes, check these locations:

### 1. Interactive Dashboard (RECOMMENDED)

```bash
# Open in your web browser
start analysis/dashboard.html          # Windows
open analysis/dashboard.html           # Mac
xdg-open analysis/dashboard.html       # Linux
```

**Features**:

- 📈 Tabs for each analysis phase
- 📊 Embedded visualizations
- 📋 Statistical summaries
- 🎯 Model comparison tables
- 💡 Recommendations

### 2. Generated Reports

```bash
outputs/                               # Model outputs
├── cohort.csv                         # Study population
├── features_lab.csv                   # Feature matrix
├── model_metrics_temporal.json        # Model performance
└── thresholds_metrics.csv             # Decision thresholds

analysis/                              # Statistical analysis
├── descriptive_stats_summary.csv      # Quick reference
├── correlation_matrix.csv             # Feature correlations
├── target_associations.csv            # Feature-target relationships
├── multicollinearity_vif.csv          # Multicollinearity analysis
├── feature_ranking_rfe.csv            # Feature selection ranking
├── feature_importance_*.csv           # Feature importance (multiple methods)
└── visualizations/                    # 7 high-res PNG plots
    ├── feature_distributions.png
    ├── missing_data_heatmap.png
    ├── correlation_heatmap.png
    ├── model_metrics_comparison.png
    ├── roc_curves.png
    ├── threshold_analysis.png
    └── feature_importance_shap.png
```

### 3. Command-Line Summary

```bash
# Print all available outputs
ls -la outputs/
ls -la analysis/

# View key metrics
cat outputs/model_metrics_temporal.json
cat analysis/descriptive_stats_summary.csv
```

---

## ⚙️ System Requirements

- **Python**: 3.8 or higher
- **Memory**: 8 GB RAM (16 GB recommended)
- **Disk Space**: 2-3 GB for data and outputs
- **Time**: 2-3 hours for full pipeline
- **CPU**: Modern multi-core processor

### Required Packages

```bash
pip install -r requirements.txt

# Optional (for enhanced features)
pip install shap lightgbm scipy plotly
```

### Installation

```bash
# Create virtual environment
python -m venv mimic_env
source mimic_env/bin/activate  # Windows: mimic_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🔍 Monitor Execution

### Progress Indicators

Each phase prints:

```
✓ Phase X: Description started
  [1/5] Loading data...        # Sub-step indicators
  [2/5] Processing...
  ...
  [5/5] Saving results...
✓ Phase X completed successfully
```

### Expected Timeline

| Phase            | Time        | Task                     |
| ---------------- | ----------- | ------------------------ |
| 1. EDA           | 2 min       | Quick data exploration   |
| 2. Cohort        | 1 min       | Build study population   |
| 3. Features      | 5 min       | Engineer 200+ features   |
| 4. Leakage       | 1 min       | Detect data leakage      |
| 5. Models        | 7 min       | Train baseline models    |
| 6. SHAP          | 5 min       | Explain predictions      |
| 7. Stats         | 20 min      | Advanced statistics      |
| 8. Comparison    | 30 min      | Compare multiple models  |
| 9. Visualization | 15 min      | Create plots & dashboard |
| **TOTAL**        | **~90 min** | Full pipeline            |

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError"

```bash
# Make sure all dependencies are installed
pip install -r requirements.txt

# For specific packages
pip install pandas numpy scikit-learn xgboost lightgbm scipy matplotlib seaborn shap
```

### Issue: "FileNotFoundError: hosp/labevents.csv"

```bash
# Make sure you're in the correct directory
pwd  # Check current directory
cd /path/to/mimic-iv-clinical-database-demo-2.2
```

### Issue: "Memory Error"

```bash
# Close other applications
# Or reduce data size in scripts (edit and use head() on dataframes)
# Or increase virtual memory
```

### Issue: Script takes too long

- This is normal! Some phases (especially Phase 8: Model Comparison) can take 30+ minutes
- Don't interrupt the script - let it run to completion
- Check console output for progress indicators

### Issue: Some phases fail

- Check the error message in console
- Review the phase requirements (certain packages might be missing)
- You can skip failed phases and move to next one manually

---

## 📈 Verify Successful Execution

After pipeline completes, verify these files exist:

```bash
# Check all critical outputs
test -f outputs/cohort.csv && echo "✓ Cohort"
test -f outputs/features_lab.csv && echo "✓ Features"
test -f outputs/model_comparison.csv && echo "✓ Models compared"
test -f analysis/descriptive_stats_summary.csv && echo "✓ Statistics"
test -f analysis/dashboard.html && echo "✓ Dashboard"
test -d analysis/visualizations && echo "✓ Visualizations"
```

Expected output:

```
✓ Cohort
✓ Features
✓ Models compared
✓ Statistics
✓ Dashboard
✓ Visualizations
```

---

## 📖 Next Steps

### 1. Review Results

```bash
# Open dashboard in web browser
start analysis/dashboard.html
```

### 2. Explore Reports

- Read `analysis/descriptive_stats_summary.csv` for data overview
- Check `analysis/correlation_matrix.csv` for feature relationships
- Review `outputs/model_comparison.csv` for model performance

### 3. Generate Insights

- Which features are most predictive? → Check `analysis/feature_importance_*.csv`
- Are there data quality issues? → Check `analysis/descriptive_stats_summary.csv`
- Which model performs best? → Check `analysis/dashboard.html` Modeling tab

### 4. Further Development

- Implement custom models
- Add domain-specific features
- Deploy model as API endpoint
- Fine-tune hyperparameters

---

## 📁 Output Structure

```
project_root/
├── outputs/                    # All analysis outputs
│   ├── *.csv                   # Data files
│   ├── *.json                  # Metrics
│   ├── *.joblib                # Trained models
│   └── *.npz                   # Numpy arrays (SHAP, calibration)
│
├── analysis/                   # Statistical analysis
│   ├── *.csv                   # Analysis reports
│   ├── *.json                  # Full analysis results
│   ├── dashboard.html          # ← OPEN THIS IN BROWSER
│   └── visualizations/         # PNG plots
│       ├── feature_distributions.png
│       ├── correlation_heatmap.png
│       ├── model_metrics_comparison.png
│       └── ... (7 total)
│
└── (original files)
    ├── etl/
    ├── features/
    ├── models/
    └── hosp/, icu/  (raw data)
```

---

## ✅ Validation Checklist

After execution, verify:

- [ ] All phases completed without errors
- [ ] `analysis/dashboard.html` opens in browser
- [ ] Dashboard shows all tabs and content
- [ ] Visualizations are clear and readable
- [ ] Model comparison shows multiple models
- [ ] Feature importance rankings are present
- [ ] No "N/A" or missing values in critical metrics
- [ ] Recommendations section has actionable items

---

## 💡 Tips for Success

1. **Run in background**: Use `nohup` or `screen` on Linux/Mac

   ```bash
   nohup python run_complete_pipeline.py > pipeline.log 2>&1 &
   ```

2. **Monitor progress**: Check log file while running

   ```bash
   tail -f pipeline.log
   ```

3. **Save intermediate results**: Each phase saves its own output
   - You can interrupt and resume from any phase

4. **Adjust hyperparameters**: Edit Phase 8.1 scripts to tune models
   - Modify `param_grid` for faster/slower tuning

5. **Customize analysis**: Edit Phase 7 scripts for custom analysis
   - Add your own statistical tests
   - Modify feature selection criteria

---

## 🆘 Getting Help

1. **Check README.md** for project overview
2. **Check IMPLEMENTATION_PLAN.md** for phase details
3. **Check PROJECT_STATUS.md** for known issues
4. **Review code comments** in each script
5. **Check console output** for error messages

---

## 📧 Questions or Issues?

If you encounter problems:

1. Note the exact error message
2. Note which phase failed
3. Check if all dependencies are installed
4. Review the relevant phase in IMPLEMENTATION_PLAN.md
5. Try running that phase individually

---

**Happy analyzing! 🎉**

Start with:

```bash
python run_complete_pipeline.py
```

When done, open: `analysis/dashboard.html`
