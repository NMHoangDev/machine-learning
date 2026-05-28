#!/usr/bin/env python3
"""
Master Execution Script

Run all pipeline phases in sequence.

Usage: python run_complete_pipeline.py
"""

import subprocess
import sys
from pathlib import Path
import time

ROOT = Path('.').resolve()


def print_header(phase_num, phase_name):
    """Print phase header."""
    print("\n" + "=" * 80)
    print(f"PHASE {phase_num}: {phase_name}")
    print("=" * 80 + "\n")


def run_script(script_path, phase_name):
    """Run a Python script and handle errors."""
    print(f"▶ Running {script_path.name}...\n")
    
    try:
        result = subprocess.run([sys.executable, str(script_path)], check=True)
        print(f"\n✓ {phase_name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error in {phase_name}: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


def main():
    print("\n" + "=" * 80)
    print("MIMIC-IV ML PIPELINE - COMPLETE EXECUTION")
    print("=" * 80)
    print("\nThis script will execute all pipeline phases sequentially.")
    print("Estimated total time: 2-3 hours\n")
    
    start_time = time.time()
    results = {}
    
    # Phase 1: EDA
    if (ROOT / 'etl' / 'quick_eda.py').exists():
        print_header(1, "Exploratory Data Analysis")
        results['Phase 1: EDA'] = run_script(ROOT / 'etl' / 'quick_eda.py', 'EDA')
    
    # Phase 2: Cohort Building
    if (ROOT / 'etl' / 'build_cohort.py').exists():
        print_header(2, "Cohort Building")
        results['Phase 2: Cohort'] = run_script(ROOT / 'etl' / 'build_cohort.py', 'Cohort Building')
    
    # Phase 3.1: Base Features
    if (ROOT / 'features' / 'build_lab_features.py').exists():
        print_header(3.1, "Base Feature Engineering")
        results['Phase 3.1: Features'] = run_script(ROOT / 'features' / 'build_lab_features.py', 'Feature Engineering')
    
    # Phase 3.2: Derived Features
    if (ROOT / 'features' / 'compute_lab_trends.py').exists():
        print_header(3.2, "Derived Feature Engineering")
        results['Phase 3.2: Derived'] = run_script(ROOT / 'features' / 'compute_lab_trends.py', 'Derived Features')
    
    # Phase 4: Leakage Detection
    if (ROOT / 'models' / 'check_leakage.py').exists():
        print_header(4, "Leakage Detection")
        results['Phase 4: Leakage'] = run_script(ROOT / 'models' / 'check_leakage.py', 'Leakage Detection')
    
    # Phase 5.1: Baseline Models
    if (ROOT / 'models' / 'train_baseline.py').exists():
        print_header(5.1, "Baseline Model Training")
        results['Phase 5.1: Baseline'] = run_script(ROOT / 'models' / 'train_baseline.py', 'Baseline Models')
    
    # Phase 5.2: Temporal Evaluation
    if (ROOT / 'models' / 'evaluate_temporal.py').exists():
        print_header(5.2, "Temporal-Split Evaluation")
        results['Phase 5.2: Temporal'] = run_script(ROOT / 'models' / 'evaluate_temporal.py', 'Temporal Evaluation')
    
    # Phase 5.3: Threshold Optimization
    if (ROOT / 'models' / 'posthoc_thresholds_and_calibration.py').exists():
        print_header(5.3, "Threshold Optimization")
        results['Phase 5.3: Calibration'] = run_script(ROOT / 'models' / 'posthoc_thresholds_and_calibration.py', 'Threshold Optimization')
    
    # Phase 6: SHAP Interpretation
    if (ROOT / 'models' / 'shap_explain_xgb.py').exists():
        print_header(6, "Model Interpretation (SHAP)")
        results['Phase 6: SHAP'] = run_script(ROOT / 'models' / 'shap_explain_xgb.py', 'SHAP Explanations')
    
    # Phase 7.1: Descriptive Statistics
    if (ROOT / 'analysis' / 'descriptive_statistics.py').exists():
        print_header(7.1, "Descriptive Statistics")
        results['Phase 7.1: Descriptive'] = run_script(ROOT / 'analysis' / 'descriptive_statistics.py', 'Descriptive Statistics')
    
    # Phase 7.2: Bivariate Analysis
    if (ROOT / 'analysis' / 'bivariate_analysis.py').exists():
        print_header(7.2, "Bivariate Analysis")
        results['Phase 7.2: Bivariate'] = run_script(ROOT / 'analysis' / 'bivariate_analysis.py', 'Bivariate Analysis')
    
    # Phase 7.3: Multivariate Analysis
    if (ROOT / 'analysis' / 'multivariate_analysis.py').exists():
        print_header(7.3, "Multivariate Analysis")
        results['Phase 7.3: Multivariate'] = run_script(ROOT / 'analysis' / 'multivariate_analysis.py', 'Multivariate Analysis')
    
    # Phase 8.1: Model Comparison
    if (ROOT / 'models' / 'compare_models.py').exists():
        print_header(8.1, "Advanced Modeling & Comparison")
        results['Phase 8.1: Comparison'] = run_script(ROOT / 'models' / 'compare_models.py', 'Model Comparison')
    
    # Phase 9: Visualization
    if (ROOT / 'analysis' / 'visualization.py').exists():
        print_header(9, "Visualization")
        results['Phase 9: Visualization'] = run_script(ROOT / 'analysis' / 'visualization.py', 'Visualization')
    
    # Dashboard Generation
    if (ROOT / 'analysis' / 'generate_dashboard.py').exists():
        print_header("Dashboard", "Interactive HTML Dashboard")
        results['Dashboard'] = run_script(ROOT / 'analysis' / 'generate_dashboard.py', 'Dashboard Generation')
    
    # Summary
    print("\n" + "=" * 80)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 80 + "\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for phase, status in results.items():
        status_str = "✓ PASS" if status else "✗ FAIL"
        print(f"{status_str} | {phase}")
    
    print(f"\nTotal: {passed}/{total} phases completed successfully")
    
    elapsed_time = time.time() - start_time
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)
    
    print(f"Total execution time: {hours}h {minutes}m {seconds}s")
    
    if passed == total:
        print("\n✓✓✓ ALL PHASES COMPLETED SUCCESSFULLY! ✓✓✓")
        print("\nNext steps:")
        print("1. Open analysis/dashboard.html in a web browser")
        print("2. Review outputs/ directory for all results")
        print("3. Check analysis/ directory for detailed reports")
        print("4. Read IMPLEMENTATION_PLAN.md for deployment options")
        return 0
    else:
        print(f"\n⚠ {total - passed} phase(s) failed. Check output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
