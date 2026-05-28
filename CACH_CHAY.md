# 🚀 CÁCH CHẠY - MIMIC-IV ML Pipeline

## ⚡ TÓM TẮT NHANH (30 giây)

```bash
# Cách 1: Nhanh nhất (15 phút)
double-click quick_dashboard_15min.bat

# Cách 2: Full stats (1 giờ)
double-click stats_only_1hour.bat

# Cách 3: Đầy đủ (2.5 giờ)
double-click run_pipeline_and_open_dashboard.bat
```

**Done!** Dashboard mở tự động trong browser 🎉

---

## 📋 YÊUITỰ HỆ THỐNG

### Phần Cứng

```
CPU:     Intel i5 hoặc tương đương (OK)
RAM:     8GB minimum, 16GB recommended
SSD:     10GB dung lượng trống
```

### Phần Mềm

```
OS:      Windows 7+ (hoặc Mac/Linux)
Python:  3.8 hoặc cao hơn
Browser: Chrome/Firefox/Edge (để mở dashboard)
```

### Kiểm Tra Python

```bash
# Mở Command Prompt (Win+R, gõ cmd)
py --version

# Kết quả mong đợi
Python 3.8.0 (hoặc cao hơn)

# Nếu không có Python: Download từ python.org
```

---

## 📖 CHUẨN BỊ (1 phút)

### Bước 1: Mở Command Prompt

```
Win+R → gõ cmd → Enter
```

### Bước 2: Vào Folder Project

```bash
cd "D:\Học máy'\mimic-iv-clinical-database-demo-2.2"

# Hoặc: Shift+Right-click tại folder → "Open PowerShell here"
```

### Bước 3: Kiểm Tra Files

```bash
# Xem files batch
dir *.bat

# Output (phải thấy 4 files):
# ├─ choose_option.bat
# ├─ quick_dashboard_15min.bat
# ├─ stats_only_1hour.bat
# └─ run_pipeline_and_open_dashboard.bat
```

### Bước 4: Cài Dependencies (Lần Đầu)

```bash
# Nếu chưa cài lần nào
pip install -r requirements.txt

# Output phải là: Successfully installed ...

# Nếu có lỗi: Thử
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🎯 CÁCH CHẠY - CHI TIẾT

### OPTION A: NHANH NHẤT (15 phút) ⚡⚡⚡

**Thích hợp:** Lần đầu tiên / Muốn xem kết quả nhanh

```bash
# Cách 1: Double-click file
D:\...\quick_dashboard_15min.bat

# Cách 2: Command line
quick_dashboard_15min.bat

# Cách 3: Python trực tiếp
py analysis/visualization.py
py analysis/generate_dashboard.py
start analysis/dashboard.html
```

**Timeline:**

```
0-2 min:    Khởi tạo
2-7 min:    Tạo 7 visualizations (PNG)
7-10 min:   Tạo dashboard HTML
10-15 min:  Mở dashboard trong browser
```

**Output Mong Đợi:**

```
✓ analysis/visualizations/ (7 PNG files)
✓ analysis/dashboard.html (2MB)
✓ Browser mở tự động
✓ 7 tabs hiện lên
```

**Verify:**

```bash
# Kiểm tra files được tạo
dir analysis\visualizations\
# Phải có 7 files PNG

ls -lh analysis\dashboard.html
# Phải ~2MB
```

---

### OPTION B: FULL STATS (1 giờ) ⚡⚡

**Thích hợp:** Muốn phân tích thống kê chi tiết / Không cần model mới

```bash
# Cách 1: Double-click file
D:\...\stats_only_1hour.bat

# Cách 2: Command line từng phase
py analysis/descriptive_statistics.py     # 20 min
py analysis/bivariate_analysis.py         # 25 min
py analysis/multivariate_analysis.py      # 15 min
py analysis/visualization.py              # 10 min
py analysis/generate_dashboard.py         # 5 min
```

**Timeline:**

```
0-20 min:   Descriptive stats (mean, std, outliers)
20-45 min:  Bivariate analysis (correlation, VIF)
45-60 min:  Multivariate analysis (PCA, RFE)
60-70 min:  Visualizations (7 plots)
70-75 min:  Dashboard generation
75-60 min:  Dashboard opens
```

**Output Mong Đợi:**

```
✓ analysis/descriptive_stats_summary.csv
✓ analysis/correlation_matrix.csv
✓ analysis/multicollinearity_vif.csv
✓ analysis/pca_loadings.csv
✓ analysis/feature_ranking_rfe.csv
✓ analysis/visualizations/ (7 PNG)
✓ analysis/dashboard.html
```

**Verify:**

```bash
# Kiểm tra CSV files
dir analysis\*.csv
# Phải có 5 CSV files

# Kiểm tra visualizations
dir analysis\visualizations\
# Phải có 7 PNG files
```

---

### OPTION C: ĐẦYỦ (2.5 giờ) ⚡

**Thích hợp:** Muốn chạy toàn bộ pipeline / Lần đầu tiên training models

```bash
# Cách 1: Double-click file
D:\...\run_pipeline_and_open_dashboard.bat

# Cách 2: Command line
py run_complete_pipeline.py

# Cách 3: Từng phase thủ công
py etl/quick_eda.py
py etl/build_cohort.py
py features/build_lab_features.py
py features/compute_lab_trends.py
py models/check_leakage.py
py models/train_baseline.py
py models/evaluate_temporal.py
py models/posthoc_thresholds_and_calibration.py
py models/shap_explain_xgb.py
py analysis/descriptive_statistics.py
py analysis/bivariate_analysis.py
py analysis/multivariate_analysis.py
py models/compare_models.py
py analysis/visualization.py
py analysis/generate_dashboard.py
```

**Timeline:**

```
0-30 min:     Phases 1-6 (baseline pipeline)
              ├─ EDA (2 min)
              ├─ Cohort (1 min)
              ├─ Features (10 min)
              ├─ Quality check (2 min)
              └─ Train baseline models (15 min)

30-90 min:    Phases 7-8 (advanced analysis)
              ├─ Descriptive stats (20 min)
              ├─ Bivariate analysis (25 min)
              ├─ Multivariate analysis (15 min)
              └─ Model comparison (30 min)

90-150 min:   Phase 9 (visualization & dashboard)
              ├─ Visualizations (10 min)
              └─ Dashboard (5 min)

150+ min:     Dashboard opens
```

**Output Mong Đợi:**

```
outputs/ folder:
✓ cohort.csv (140 bệnh nhân)
✓ features_lab.csv (140 × 200+ features)
✓ model_metrics.json (baseline models)
✓ model_comparison.csv (4 models)
✓ *_model.joblib (4 trained models)
✓ ... 40+ files khác

analysis/ folder:
✓ 5 CSV files (stats)
✓ 7 visualizations PNG
✓ dashboard.html (MAIN)

TỔNG: 50+ files
```

**Verify:**

```bash
# Kiểm tra outputs
dir outputs\*.csv outputs\*.json outputs\*.joblib
# Phải có 30+ files

# Kiểm tra analysis
dir analysis\*.csv
# Phải có 5 CSV files

# Mở dashboard
start analysis\dashboard.html
# Phải mở browser + 7 tabs visible
```

---

## 🎮 CHỌN OPTION BẰNG MENU

### Cách Dùng Menu Interactif

```bash
# Run file này
double-click choose_option.bat

# Output:
# ============================================================
# MIMIC-IV ML Pipeline - Choose Your Option
# ============================================================
#
# 1. FASTEST (15 min)    - Dashboard only
# 2. STATS ONLY (1 hour) - Advanced statistical analysis
# 3. FULL (2.5 hours)    - Complete pipeline
#
# Select option (1/2/3):

# Gõ: 1 (hoặc 2 hoặc 3)
# Enter
# Tự động chạy!
```

---

## 🛠️ CHẠY TỪNG PHASE (Advanced)

**Dùng khi:** Muốn chạy từng bước / Debug / Customize

### Phase 1: EDA

```bash
py etl/quick_eda.py

# Xem kết quả
cat outputs/summary.json
```

### Phase 2: Cohort

```bash
py etl/build_cohort.py

# Xem kết quả
more outputs/cohort.csv
# hoặc mở trong Excel
```

### Phase 3: Features

```bash
py features/build_lab_features.py
py features/compute_lab_trends.py

# Xem kết quả
more outputs/features_lab.csv
```

### Phase 4-6: Models

```bash
py models/check_leakage.py
py models/train_baseline.py
py models/evaluate_temporal.py
py models/posthoc_thresholds_and_calibration.py
py models/shap_explain_xgb.py

# Xem kết quả
more outputs/model_metrics.json
```

### Phase 7-9: Analysis

```bash
py analysis/descriptive_statistics.py
py analysis/bivariate_analysis.py
py analysis/multivariate_analysis.py
py models/compare_models.py
py analysis/visualization.py
py analysis/generate_dashboard.py

# Xem dashboard
start analysis/dashboard.html
```

---

## 📊 MONITOR TIẾN ĐỘ

### Xem Console Output

```
Khi chạy, bạn sẽ thấy:

[Phase 1/9] EDA... ✓ COMPLETED (2 min)
[Phase 2/9] Cohort... ✓ COMPLETED (1 min)
[Phase 3/9] Features... ✓ COMPLETED (10 min)
...
[Phase 9/9] Dashboard... ✓ COMPLETED (5 min)

============================================================
PIPELINE COMPLETED SUCCESSFULLY
============================================================
Total time: 145 minutes
All phases: ✓ PASSED
```

### Xem Files Được Tạo

```bash
# Terminal 1: Chạy pipeline
py run_complete_pipeline.py

# Terminal 2: Monitor files (new)
# Mở cmd mới, chạy:
cd outputs
dir /s /b *.csv *.json *.joblib | find /c /v ""
# Sẽ tăng khi pipeline chạy

# hoặc Windows:
Get-ChildItem -Recurse -Filter "*.csv" | Measure-Object | Select-Object Count
```

---

## 🚨 KHẮC PHỤC SỰ CỐ

### Problem 1: `'py' is not recognized`

**Nguyên Nhân:** Python không được thêm vào PATH

**Giải Pháp:**

```bash
# Cách 1: Dùng đường dẫn đầy đủ
"C:\Users\USER\AppData\Local\Programs\Python\Python310\python.exe" run_complete_pipeline.py

# Cách 2: Cài Python lại, tích "Add Python to PATH"
# https://www.python.org/downloads/

# Cách 3: Check installation
py --version
python --version
python3 --version
# Dùng cái nào có kết quả
```

### Problem 2: Out of Memory Error

**Nguyên Nhân:** RAM không đủ (< 8GB)

**Giải Pháp:**

```bash
# Cách 1: Chạy từng phase riêng rẽ
py analysis/descriptive_statistics.py
# Chờ hoàn thành, close terminal

py analysis/bivariate_analysis.py
# Chờ, close

py analysis/multivariate_analysis.py
# Chờ, close

# Mỗi phase sẽ giải phóng memory

# Cách 2: Giảm data size (nâng cao)
# Sửa file, lọc bệnh nhân hoặc features
```

### Problem 3: Dashboard không mở

**Nguyên Nhân:** Browser mặc định không set

**Giải Pháp:**

```bash
# Cách 1: Manual open
# Tìm file: analysis/dashboard.html
# Double-click → chọn browser

# Cách 2: Command
start analysis/dashboard.html  # Windows
open analysis/dashboard.html   # Mac
xdg-open analysis/dashboard.html  # Linux

# Cách 3: Browser
# Mở Chrome/Firefox
# Ctrl+O → chọn analysis/dashboard.html
```

### Problem 4: Missing Dependencies

**Nguyên Nhân:** Chưa cài packages

**Giải Pháp:**

```bash
# Cách 1: Cài tất cả
pip install -r requirements.txt

# Cách 2: Cài từng package
pip install pandas numpy scikit-learn xgboost matplotlib seaborn scipy joblib

# Cách 3: Upgrade pip trước
pip install --upgrade pip
pip install -r requirements.txt

# Verify
py -c "import pandas; print(pandas.__version__)"
```

### Problem 5: Files không được tạo

**Nguyên Nhân:** Pipeline lỗi, dừng ở giữa

**Giải Pháp:**

```bash
# Cách 1: Xem error message
# Nhìn output cuối cùng của console
# "Error: ..."

# Cách 2: Run phase này một cách riêng
# Xem chi tiết lỗi
py analysis/descriptive_statistics.py

# Cách 3: Check input files
# Mỗi phase cần input files
# Ví dụ: descriptive_statistics.py cần outputs/features_lab.csv
# Kiểm tra file có tồn tại?

ls outputs/features_lab.csv
# Nếu không có → Chạy phases 1-3 trước
```

---

## ✅ KIỂM TRA KẾT QUẢ

### Sau Khi Chạy Option A (15 min)

```bash
# Bước 1: Kiểm tra files
dir analysis\visualizations\
# Phải thấy 7 files PNG:
# ├─ feature_distributions.png
# ├─ missing_data_heatmap.png
# ├─ correlation_heatmap.png
# ├─ model_metrics_comparison.png
# ├─ roc_curves.png
# ├─ threshold_analysis.png
# └─ feature_importance_shap.png

# Bước 2: Check dashboard
dir analysis\dashboard.html
# Phải có file ~2MB

# Bước 3: Mở dashboard
start analysis\dashboard.html

# Bước 4: Verify content
# □ Overview tab hiện lên
# □ 7 tabs visible: Overview, Stats, Corr, ...
# □ Có dữ liệu trong mỗi tab
# □ Images embedded (không loading từ web)
```

### Sau Khi Chạy Option B (1 hour)

```bash
# Bước 1: CSV files
ls analysis\*.csv
# Phải có:
# ├─ descriptive_stats_summary.csv
# ├─ correlation_matrix.csv
# ├─ multicollinearity_vif.csv
# ├─ pca_loadings.csv
# └─ feature_ranking_rfe.csv

# Bước 2: Mở CSV để xem
# Excel hoặc Python:
import pandas as pd
df = pd.read_csv('analysis/descriptive_stats_summary.csv')
print(df.shape)  # Phải (200+, columns)
print(df.head())  # Phải có dữ liệu

# Bước 3: Dashboard
start analysis\dashboard.html
# Kiểm tra 7 tabs có data
```

### Sau Khi Chạy Option C (2.5 hours)

```bash
# Bước 1: Console output
# Nhìn cuối cùng phải là:
# ============================================================
# PIPELINE COMPLETED SUCCESSFULLY
# ============================================================
# Phase 1: ✓ PASSED
# Phase 2: ✓ PASSED
# ...
# Phase 9: ✓ PASSED
# Total time: ~145 minutes

# Bước 2: Count output files
# Windows:
dir /s /b outputs\*.* | find /c /v ""
# Phải >= 40 files

# Mac/Linux:
find outputs -type f | wc -l
# Phải >= 40 files

# Bước 3: Check models
dir outputs\*.joblib
# Phải có 4 files:
# ├─ logistic_regression_model.joblib
# ├─ random_forest_model.joblib
# ├─ lightgbm_model.joblib
# └─ xgboost_model.joblib

# Bước 4: Mở dashboard
start analysis\dashboard.html
# Kiểm tra tất cả 7 tabs có full data
```

---

## 📝 COMMAND CHEAT SHEET

```bash
# === QUICK COMMANDS ===

# Chạy option nào đó
py run_complete_pipeline.py            # Full (2.5h)
py analysis/visualization.py           # Viz (10m)
py analysis/generate_dashboard.py      # Dashboard (5m)

# Xem kết quả
start analysis\dashboard.html          # Open dashboard
more outputs\model_metrics.json         # View JSON
type analysis\descriptive_stats_summary.csv  # View CSV

# Debug
py -c "import pandas; print('OK')"     # Check Python
dir outputs\cohort.csv                 # Check file exists
pip list                               # Check packages

# Clean (xóa results để chạy lại)
del /q outputs\*.csv outputs\*.json outputs\*.joblib
del /q analysis\*.csv analysis\*.json
del /q analysis\visualizations\*.png
del analysis\dashboard.html
```

---

## 📞 CÁCH LẤY HELP

### Nếu bị lỗi

```
1. Nhìn error message cụ thể
2. Tra Google: "python [error message]"
3. Check file này: HOW_TO_READ_DATA.md
4. Check: IMPLEMENTATION_PLAN.md (chi tiết kỹ thuật)
```

### Nếu muốn hiểu workflow

```
1. Đọc: README.md (overview)
2. Đọc: DEMO_GUIDE.md (demo là gì)
3. Đọc: CACH_CHAY.md (file này)
4. Đọc: HOW_TO_READ_DATA.md (cách đọc kết quả)
```

### Nếu muốn customize

```
1. Mở: analysis/descriptive_statistics.py
2. Thay đổi parameters
3. Test: py analysis/descriptive_statistics.py
4. Xem kết quả: analysis/*.csv
```

---

## 🎯 QUICK START - 5 PHÚT

```bash
# 1. Mở Command Prompt
Win+R → cmd → Enter

# 2. Vào folder
cd "D:\Học máy'\mimic-iv-clinical-database-demo-2.2"

# 3. Chạy (chọn 1 trong 3)
choose_option.bat      # Menu
# hoặc
quick_dashboard_15min.bat
# hoặc
run_pipeline_and_open_dashboard.bat

# 4. Chờ... ⏳

# 5. Dashboard mở tự động 🎉
```

**Done!** Bạn có dashboard với full analysis ✨

---

## 📅 LỊCH BIỂU THAM KHẢO

```
Lần 1:
├─ Chuẩn bị (1 phút)
├─ Cài dependencies (5 phút)
├─ Chạy pipeline (15-150 phút tùy option)
└─ Xem kết quả (5 phút)
TỔNG: 26-161 phút

Lần 2+:
├─ Chuẩn bị (0 phút - skip)
├─ Cài dependencies (0 phút - skip)
├─ Chạy pipeline (15-150 phút tùy option)
└─ Xem kết quả (5 phút)
TỔNG: 20-155 phút
```

---

**Bạn sẵn sàng chạy chưa?** 🚀

Nếu có câu hỏi, mở file này lại hoặc đọc các docs khác! 📚
