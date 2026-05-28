# 📖 Hướng Dẫn Đọc Dữ Liệu - MIMIC-IV ML Pipeline

## 🎯 Mục Đích

Hướng dẫn này giúp bạn:

- ✅ Hiểu cấu trúc dữ liệu
- ✅ Đọc & giải thích files CSV/JSON
- ✅ Xem dashboard
- ✅ Sử dụng dữ liệu trong thực tế

---

## 📊 Các Loại DỮ LIỆU

### Level 1: Raw Data (Dữ liệu thô - đầu vào)

```
hosp/ folder          Hospital data
├─ labevents.csv      Lab test results ← MAIN!
├─ patients.csv       Patient info
├─ admissions.csv     Hospital admissions
└─ d_labitems.csv     Lab item definitions

icu/ folder           ICU data
├─ icustays.csv       ICU stay info
└─ chartevents.csv    Vital signs
```

### Level 2: Intermediate Data (Dữ liệu xử lý - giữa chừng)

```
outputs/ folder       After Phase 1-6
├─ cohort.csv         140 patients với labels
├─ features_lab.csv   140 × 200+ features
└─ models/*.joblib    Trained ML models
```

### Level 3: Analysis Data (Dữ liệu phân tích - cuối)

```
analysis/ folder      After Phase 7-9
├─ *.csv              Statistics & metrics
├─ *.json             Detailed results
├─ visualizations/    7 PNG plots
└─ dashboard.html     Interactive dashboard
```

---

## 🔴 LEVEL 1: DỮ LIỆU THÔI (Raw Data)

### File 1: `hosp/labevents.csv` - Kết Quả Xét Nghiệm

**Cách mở:**

```bash
# Option 1: Mở trong Excel
D:\...\hosp\labevents.csv (double-click)

# Option 2: Mở trong Python
import pandas as pd
df = pd.read_csv('hosp/labevents.csv')
print(df.head())
print(df.info())
```

**Cấu trúc (Structure):**

```
subject_id | hadm_id | itemid | charttime | value | valuenum
-----------|---------|--------|-----------|-------|----------
10000001   | 2096416 | 50861  | 2104-...  | 95    | 95.0
10000001   | 2096416 | 50885  | 2104-...  | 7.5   | 7.5
10000001   | 2096416 | 50912  | 2104-...  | 10    | 10.0
...
```

**Giải thích từng column:**

```
subject_id    = Mã bệnh nhân (Patient ID)
hadm_id       = Mã nhập viện (Admission ID)
itemid        = Mã xét nghiệm (Test ID, ví dụ: 50861 = Hemoglobin)
charttime     = Thời gian xét nghiệm (When the test was done)
value         = Giá trị string (Ví dụ: "95 g/dL")
valuenum      = Giá trị số (Numeric value for analysis)
```

**Ví dụ thực tế:**

```
Dòng 1: Bệnh nhân 10000001 lúc 2104-01-20 xét nghiệm Hemoglobin (50861)
        Kết quả: 95 g/dL (normal)

Dòng 2: Cùng bệnh nhân, cùng ngày, xét nghiệm Albumin (50885)
        Kết quả: 7.5 g/dL (low)

Dòng 3: Cùng bệnh nhân, cùng ngày, xét nghiệm WBC (50912)
        Kết quả: 10 K/uL (normal)
```

**Thống kê:**

```python
df = pd.read_csv('hosp/labevents.csv')
print(f"Total rows: {len(df)}")           # ~107,727 (hàng)
print(f"Unique patients: {df['subject_id'].nunique()}")  # ~140
print(f"Unique tests: {df['itemid'].nunique()}")  # ~498
print(f"Date range: {df['charttime'].min()} to {df['charttime'].max()}")
```

**Output:**

```
Total rows: 107,727
Unique patients: 140
Unique tests: 498
Date range: 2104-01-01 to 2104-12-31
```

### File 2: `hosp/d_labitems.csv` - Định Nghĩa Xét Nghiệm

**Cách mở:**

```
D:\...\hosp\d_labitems.csv (double-click)
```

**Cấu trúc:**

```
itemid | label
-------|---------------------------------------------------
50861  | HEMOGLOBIN
50885  | ALBUMIN
50912  | WBC (White Blood Cell Count)
50931  | GLUCOSE
50971  | POTASSIUM
...
```

**Ý nghĩa:**

- `itemid = 50861` tương ứng với "HEMOGLOBIN" (Máu)
- Dùng để tra cứu tên của mỗi xét nghiệm

**Ví dụ:**

```python
items = pd.read_csv('hosp/d_labitems.csv')
# Tìm tên của itemid 50861
print(items[items['itemid'] == 50861]['label'].values[0])
# Output: HEMOGLOBIN
```

### File 3: `icu/icustays.csv` - Thông Tin Nằm ICU

**Cấu trúc:**

```
subject_id | hadm_id | icustay_id | intime             | outtime
-----------|---------|------------|--------------------|-----------------------
10000001   | 2096416 | 200001     | 2104-02-01 12:45   | 2104-02-08 08:30
10000001   | 2096416 | 200002     | 2104-02-15 15:20   | 2104-02-18 10:15
...
```

**Giải thích:**

```
subject_id  = Mã bệnh nhân
hadm_id     = Mã nhập viện
icustay_id  = Mã nằm ICU
intime      = Lúc vào ICU
outtime     = Lúc ra khỏi ICU (hoặc chết)
```

**Ý nghĩa:**

```
intime = 2104-02-01 12:45
outtime = 2104-02-08 08:30
         → Bệnh nhân nằm ICU 7 ngày
```

### File 4: `hosp/patients.csv` - Thông Tin Bệnh Nhân

**Cấu trúc:**

```
subject_id | gender | dob        | dod
-----------|--------|------------|---------------------
10000001   | M      | 1941-04-14 | 2104-02-08 (hoặc NULL)
10000002   | F      | 1952-07-21 | NULL (bệnh nhân còn sống)
...
```

**Giải thích:**

```
subject_id  = Mã bệnh nhân
gender      = Giới tính (M=Male, F=Female)
dob         = Ngày sinh
dod         = Ngày chết (NULL = còn sống)
```

---

## 🟡 LEVEL 2: DỮ LIỆU TRUNG GIAN (Intermediate Output)

### File 1: `outputs/cohort.csv` - Nhóm Bệnh Nhân

**Cách mở:**

```bash
# Mở trong Excel hoặc Python
import pandas as pd
df = pd.read_csv('outputs/cohort.csv')
print(df.head())
```

**Cấu trúc:**

```
subject_id | hadm_id | gender | age | in_icu_mortality | in_hospital_mortality
-----------|---------|--------|-----|-----------------|----------------------
10000001   | 2096416 | M      | 63  | 1                | 1
10000002   | 2096417 | F      | 71  | 0                | 0
10000003   | 2096418 | M      | 58  | 1                | 1
...
```

**Giải thích:**

```
subject_id             = Mã bệnh nhân
hadm_id                = Mã nhập viện
gender                 = Giới tính
age                    = Tuổi tính lúc nhập viện
in_icu_mortality       = 1 = Chết trong ICU, 0 = Sống
in_hospital_mortality  = 1 = Chết trong bệnh viện, 0 = Sống
```

**Thống kê:**

```python
df = pd.read_csv('outputs/cohort.csv')
print(f"Total patients: {len(df)}")  # 140
print(f"Males: {(df['gender'] == 'M').sum()}")
print(f"Females: {(df['gender'] == 'F').sum()}")
print(f"Mortality rate: {df['in_hospital_mortality'].mean():.1%}")  # ~23%
print(f"Age: {df['age'].mean():.1f} ± {df['age'].std():.1f}")
```

**Output:**

```
Total patients: 140
Males: 82
Females: 58
Mortality rate: 23.6%
Age: 68.5 ± 14.2
```

### File 2: `outputs/features_lab.csv` - 200+ Features

**Cấu trúc (ĐẠI DIỆN):**

```
subject_id | item_50861_mean | item_50861_std | item_50861_min | item_50861_max | item_50885_mean | ...
-----------|----------------|----------------|----------------|----------------|-----------------|----
10000001   | 95.2           | 5.3            | 88.1           | 103.5          | 3.5             | ...
10000002   | 102.1          | 8.2            | 92.0           | 115.2          | 2.8             | ...
10000003   | 87.3           | 12.5           | 71.0           | 98.5           | 4.2             | ...
...
```

**Giải thích:**

```
Mỗi column là 1 feature:

item_50861_mean  = Giá trị trung bình Hemoglobin (cho ICU stay này)
item_50861_std   = Độ lệch chuẩn Hemoglobin
item_50861_min   = Giá trị nhỏ nhất Hemoglobin
item_50861_max   = Giá trị lớn nhất Hemoglobin
...

Tương tự cho 498 items khác
```

**Sao có 200+ features từ 498 items?**

```
498 items × 7 loại stats mỗi item
= Có thể đến 3,486 features
Nhưng chỉ ~200 features được giữ lại vì:
- Loại bỏ features với >50% missing
- Loại bỏ features với zero variance
- Loại bỏ duplicates
```

**Ví dụ sử dụng:**

```python
df = pd.read_csv('outputs/features_lab.csv')
print(f"Số bệnh nhân: {len(df)}")  # 140
print(f"Số features: {len(df.columns) - 1}")  # 200+
print(f"Patient 1 Hemoglobin mean: {df.iloc[0]['item_50861_mean']}")  # 95.2
```

### File 3: `outputs/model_metrics.json` - Kết Quả Mô Hình

**Cách mở:**

```bash
# Mở trong text editor hoặc Python
import json
with open('outputs/model_metrics.json') as f:
    metrics = json.load(f)
print(json.dumps(metrics, indent=2))
```

**Nội dung (ví dụ):**

```json
{
  "logistic_regression": {
    "auc": 0.577,
    "auprc": 0.293,
    "accuracy": 0.68,
    "sensitivity": 0.6,
    "specificity": 0.72
  },
  "xgboost": {
    "auc": 0.635,
    "auprc": 0.138,
    "accuracy": 0.74,
    "sensitivity": 0.7,
    "specificity": 0.76
  }
}
```

**Giải thích các metrics:**

```
AUC (Area Under Curve)
  = Measure of model performance (0.5 = random, 1.0 = perfect)
  = 0.635 = XGBoost khá tốt

AUPRC (Area Under Precision-Recall Curve)
  = Phù hợp cho dữ liệu imbalanced
  = 0.138 = Khó dự đoán mortality (class imbalance)

Accuracy
  = Phần trăm dự đoán đúng
  = 0.74 = 74% đúng

Sensitivity (Recall)
  = Bao nhiêu bệnh nhân chết được phát hiện
  = 0.70 = Phát hiện được 70% những ai sẽ chết

Specificity
  = Bao nhiêu bệnh nhân sống được phát hiện
  = 0.76 = Phát hiện được 76% những ai sẽ sống
```

---

## 🟢 LEVEL 3: DỮ LIỆU PHÂN TÍCH (Analysis Output)

### File 1: `analysis/descriptive_stats_summary.csv` - Thống Kê Mô Tả

**Cấu trúc:**

```
feature_id | feature_name    | count | mean   | std    | min | max   | median | mode | outliers | missing_count | missing_percent
-----------|-----------------|-------|--------|--------|-----|-------|--------|------|----------|---------------|---------------
50861      | HEMOGLOBIN      | 140   | 95.23  | 18.54  | 45  | 150   | 94.5   | 92   | 3        | 0             | 0.0%
50885      | ALBUMIN         | 137   | 3.21   | 0.75   | 1.2 | 5.1   | 3.2    | 3.0  | 2        | 3             | 2.1%
50912      | WBC             | 138   | 12.10  | 8.30   | 2   | 45    | 10.5   | 8    | 5        | 2             | 1.4%
...
```

**Cách mở & giải thích:**

```python
import pandas as pd
df = pd.read_csv('analysis/descriptive_stats_summary.csv')

# Xem thống kê của Hemoglobin
hemoglobin = df[df['feature_id'] == 50861].iloc[0]
print(f"Feature: {hemoglobin['feature_name']}")
print(f"Mean: {hemoglobin['mean']}")  # Giá trị trung bình
print(f"Std: {hemoglobin['std']}")    # Độ lệch chuẩn (biến động)
print(f"Range: {hemoglobin['min']} - {hemoglobin['max']}")
print(f"Outliers: {hemoglobin['outliers']}")  # Giá trị lạ
```

**Ý nghĩa:**

```
Mean = 95.23    → Bình quân Hemoglobin là 95.23 g/dL
Std = 18.54     → Biến động khoảng ±18.54 g/dL
Min = 45        → Thấp nhất là 45 g/dL (bệnh rất nặng)
Max = 150       → Cao nhất là 150 g/dL (hiếm gặp)
Outliers = 3    → Có 3 giá trị lạ (rất thấp hoặc rất cao)
```

### File 2: `analysis/correlation_matrix.csv` - Ma Trận Tương Quan

**Cấu trúc (ĐẠI DIỆN 5×5):**

```
feature_id | 50861 | 50885 | 50912 | 50931 | 50971
-----------|-------|-------|-------|-------|-------
50861      | 1.00  | 0.45  | -0.12 | 0.08  | 0.22
50885      | 0.45  | 1.00  | 0.22  | 0.15  | -0.05
50912      | -0.12 | 0.22  | 1.00  | -0.05 | 0.38
50931      | 0.08  | 0.15  | -0.05 | 1.00  | 0.12
50971      | 0.22  | -0.05 | 0.38  | 0.12  | 1.00
```

**Cách đọc:**

```
Correlation = -1 to 1

 1.0  = Tương quan hoàn hảo (cùng lên cùng xuống)
 0.5  = Tương quan trung bình
 0.0  = Không tương quan
-0.5  = Tương quan âm (một lên một xuống)
-1.0  = Tương quan âm hoàn hảo
```

**Ví dụ:**

```
50861 & 50885 = 0.45
  → Hemoglobin & Albumin tương quan trung bình
  → Khi Hemoglobin cao, Albumin cũng có xu hướng cao

50861 & 50912 = -0.12
  → Hemoglobin & WBC tương quan yếu (âm)
  → Không có liên hệ mạnh giữa 2 chỉ số này
```

**Sử dụng trong thực tế:**

```python
import pandas as pd
corr = pd.read_csv('analysis/correlation_matrix.csv', index_col=0)

# Những features có tương quan cao (>0.7) với mortality
mortality_corr = corr['mortality'].sort_values(ascending=False)
print("Top features correlated with mortality:")
print(mortality_corr.head(5))
```

### File 3: `analysis/multicollinearity_vif.csv` - VIF (Multicollinearity)

**Cấu trúc:**

```
feature_id | feature_name | vif
-----------|--------------|-------
50861      | HEMOGLOBIN   | 1.2
50885      | ALBUMIN      | 2.5
50912      | WBC          | 1.8
50931      | GLUCOSE      | 3.2
...
```

**Ý nghĩa:**

```
VIF (Variance Inflation Factor)
  < 5    = OK (không có multicollinearity)
  5-10   = Caution (có vấn đề)
  > 10   = Problem (features bị lặp)

Ví dụ:
  HEMOGLOBIN (VIF=1.2) → OK, độc lập
  GLUCOSE (VIF=3.2)    → OK, nhưng có chút liên hệ
```

**Sao phải quan tâm?**

```
Nếu 2 features có tương quan cao:
  → Chúng mang thông tin giống nhau
  → Dùng cả 2 là lãng phí
  → Nên chỉ dùng 1 trong 2
```

### File 4: `analysis/feature_ranking_rfe.csv` - Ranking Features

**Cấu trúc:**

```
rank | feature_id | feature_name    | importance
-----|------------|-----------------|------------
1    | 50861      | HEMOGLOBIN      | 0.150
2    | 50912      | WBC             | 0.120
3    | 50931      | GLUCOSE         | 0.098
4    | 50971      | POTASSIUM       | 0.085
5    | 50902      | CHLORIDE        | 0.072
...
20   | 50883      | BICARBONATE     | 0.020
21   | 50868      | AMYLASE         | 0.001
...
```

**Ý nghĩa:**

```
Ranking từ quan trọng nhất đến kém nhất

Top 5 features:
  1. HEMOGLOBIN (0.150)  → Quan trọng nhất
  2. WBC (0.120)         → Quan trọng thứ 2
  3. GLUCOSE (0.098)     → Quan trọng thứ 3
  ...

Bottom features:
  199. AMYLASE (0.001)   → Hầu như vô dụng
```

**Sử dụng:**

```python
# Chỉ dùng top 20 features thay vì 200+
top_20 = features[['subject_id', 'item_50861_mean', 'item_50912_mean',
                    'item_50931_mean', ... ]]  # Top 20

# Training model nhanh hơn & kết quả gần như nhau
model = train(top_20)  # Thay vì toàn bộ 200 features
```

---

## 🌐 LEVEL 4: DASHBOARD - Xem Tất Cả Cùng Một Lúc

### Cách mở Dashboard

```bash
# Cách 1: Double-click
analysis/dashboard.html

# Cách 2: Command line
start analysis/dashboard.html

# Cách 3: Drag vào browser
Kéo file dashboard.html vào Chrome/Firefox
```

### 7 Tabs trong Dashboard

#### **Tab 1: Overview**

```
Shows:
├─ Project name
├─ Total patients: 140
├─ Total features: 200+
├─ Mortality rate: 23%
├─ Best model: XGBoost
└─ Key metrics
```

#### **Tab 2: Descriptive Statistics**

```
Shows:
├─ Table: mean, std, min, max, outliers
├─ Missing data percentage
├─ Unique values per feature
└─ Data quality summary
```

#### **Tab 3: Bivariate Analysis**

```
Shows:
├─ Correlation matrix (heatmap)
├─ Target associations
├─ VIF multicollinearity
└─ Feature pairs with high correlation
```

#### **Tab 4: Multivariate Analysis**

```
Shows:
├─ PCA loadings (dimensionality reduction)
├─ Feature ranking (RFE)
├─ Feature importance comparison
└─ Stratified analysis
```

#### **Tab 5: Model Comparison**

```
Shows:
├─ 4 models: LR, RF, LightGBM, XGBoost
├─ Metrics: AUC, AUPRC, Sensitivity, Specificity
├─ Cross-validation scores
└─ Best model highlighted
```

#### **Tab 6: Visualizations**

```
Shows:
├─ 7 embedded PNG plots:
│  1. Feature distributions
│  2. Missing data heatmap
│  3. Correlation heatmap
│  4. Model metrics comparison
│  5. ROC curves
│  6. Threshold analysis
│  └─ Feature importance
└─ All images embedded (no external files needed)
```

#### **Tab 7: Recommendations**

```
Shows:
├─ Key findings
├─ Best model recommendation
├─ Top features to monitor
├─ Optimal threshold
└─ Next steps
```

---

## 🔍 CÁCH ĐỌC CỤ THỂ - VÍ DỤ

### Scenario 1: Bác Sĩ Muốn Hiểu Kết Quả

```
Bác Sĩ: "Bệnh nhân này nằm ICU, anh chạy model xem nó sẽ sống hay chết?"

Step 1: Lấy dữ liệu bệnh nhân (lab test results)
  → features_lab.csv (row của bệnh nhân này)

Step 2: Dự đoán bằng trained model
  → Load model từ outputs/xgb_temporal_model.joblib
  → Cho vào 200+ features
  → Model output: probability = 0.72 (72% chết)

Step 3: So sánh với optimal threshold
  → Threshold = 0.43 (từ model tuning)
  → 0.72 > 0.43 → Dự đoán: SẼ CHẾT

Step 4: Xem dữ liệu chi tiết
  → Mở dashboard Tab 2 → Xem features của bệnh nhân
  → Hemoglobin = 60 (thấp) ⚠️
  → WBC = 35 (cao) ⚠️
  → Glucose = 450 (rất cao) ⚠️

Step 5: Quyết định
  → Bác Sĩ: "OK, cần can thiệp ngay"
```

### Scenario 2: Nhà Nghiên Cứu Muốn Viết Paper

```
Nhà Nghiên Cứu: "Tôi cần dữ liệu để viết paper"

Step 1: Xem tổng quát kết quả
  → Mở dashboard Tab 1 (Overview)
  → Ghi lại: XGBoost AUC = 0.635

Step 2: Xem features quan trọng
  → Tab 4 (Multivariate) → feature_ranking_rfe.csv
  → Top 5: Hemoglobin, WBC, Glucose, Potassium, Chloride

Step 3: Xem thống kê chi tiết
  → Tab 2 (Descriptive Stats) → descriptive_stats_summary.csv
  → Ghi: Mean ± Std cho mỗi feature

Step 4: Xem tương quan
  → Tab 3 (Bivariate) → correlation_matrix.csv
  → Ghi: Correlation với mortality

Step 5: Viết paper
  → "Methods: ML pipeline with XGBoost, AUC=0.635"
  → "Top predictors: Hemoglobin, WBC, Glucose"
  → "Data showed: Hemoglobin mean=95±18, WBC mean=12±8"
```

---

## 💾 CÁCH LƯU DỮLỆU & CHIA SẺ

### Export CSV từ Dashboard

```bash
# 1. Mở CSV trong Excel
analysis/descriptive_stats_summary.csv

# 2. Ctrl+A → Copy
# 3. Dán vào PowerPoint/Word

# Hoặc: File → Save As → PDF
```

### Export Visualizations

```bash
# PNGs đã sẵn trong visualizations/
analysis/visualizations/correlation_heatmap.png

# Cách dùng:
1. Insert vào PowerPoint
2. Gửi email
3. Upload lên trang web
```

### Share Dashboard

```bash
# Dashboard là single file
analysis/dashboard.html (2MB)

# Gửi cho team member:
1. Attach vào email
2. Họ double-click mở
3. Xem toàn bộ analysis (không cần code)
```

---

## 🐍 ĐỌCỨ LIỆU BẰNG PYTHON

### Ví Dụ 1: Thống Kê Bệnh Nhân

```python
import pandas as pd

# Đọc dữ liệu
cohort = pd.read_csv('outputs/cohort.csv')

# Bao nhiêu bệnh nhân?
print(f"Total: {len(cohort)}")  # 140

# Sống/Chết?
alive = (cohort['in_hospital_mortality'] == 0).sum()
dead = (cohort['in_hospital_mortality'] == 1).sum()
print(f"Alive: {alive}, Dead: {dead}")  # Alive: 107, Dead: 33

# Tuổi trung bình?
print(f"Age: {cohort['age'].mean():.1f} ± {cohort['age'].std():.1f}")
# Age: 68.5 ± 14.2

# Nam/Nữ?
males = (cohort['gender'] == 'M').sum()
females = (cohort['gender'] == 'F').sum()
print(f"Males: {males}, Females: {females}")
```

### Ví Dụ 2: So Sánh Models

```python
import json

# Đọc kết quả models
with open('outputs/model_metrics.json') as f:
    metrics = json.load(f)

# So sánh AUC
models = {}
for model_name, scores in metrics.items():
    models[model_name] = scores['auc']

# Xếp hạng
for model, auc in sorted(models.items(), key=lambda x: x[1], reverse=True):
    print(f"{model:20} AUC: {auc:.3f}")

# Output:
# xgboost              AUC: 0.635
# random_forest        AUC: 0.610
# logistic_regression  AUC: 0.577
```

### Ví Dụ 3: Tìm Features Quan Trọng

```python
import pandas as pd

# Đọc ranking
ranking = pd.read_csv('analysis/feature_ranking_rfe.csv')

# Top 10
print("Top 10 features:")
print(ranking.head(10)[['rank', 'feature_name', 'importance']])

# Output:
#    rank feature_name importance
# 1     1   HEMOGLOBIN      0.150
# 2     2   WBC             0.120
# 3     3   GLUCOSE         0.098
# ...
```

### Ví Dụ 4: Phân Tích Một Bệnh Nhân

```python
import pandas as pd

# Đọc features
features = pd.read_csv('outputs/features_lab.csv')

# Bệnh nhân thứ 1
patient_1 = features.iloc[0]

# Xem Hemoglobin
hemoglobin = patient_1['item_50861_mean']
print(f"Hemoglobin: {hemoglobin:.1f} g/dL")

# So sánh với bình quân
all_hemoglobin = features['item_50861_mean']
mean = all_hemoglobin.mean()
std = all_hemoglobin.std()
z_score = (hemoglobin - mean) / std
print(f"Mean: {mean:.1f}, Std: {std:.1f}")
print(f"Z-score: {z_score:.2f}")  # Bao xa so với bình quân?

# Giải thích:
# Z-score = 1.0 → Cao hơn 1 độ lệch chuẩn so với bình quân
# Z-score > 2.0 → Bất thường (cần lưu ý)
```

---

## 🎯 CHEAT SHEET - TÓM TẮT NHANH

| Câu Hỏi                       | Cách Tìm                                  | File             | Tab          |
| ----------------------------- | ----------------------------------------- | ---------------- | ------------ |
| **Có bao nhiêu bệnh nhân?**   | `len(cohort.csv)`                         | cohort.csv       | -            |
| **Bao nhiêu features?**       | `len(features_lab.csv.columns)`           | features_lab.csv | -            |
| **Tỷ lệ tử vong?**            | `cohort.csv` → tính % mortality=1         | cohort.csv       | Overview     |
| **Features nào quan trọng?**  | `feature_ranking_rfe.csv`                 | analysis/        | Multivariate |
| **Tương quan giữa features?** | `correlation_matrix.csv`                  | analysis/        | Bivariate    |
| **Thống kê features**         | `descriptive_stats_summary.csv`           | analysis/        | Stats        |
| **Model nào tốt nhất?**       | `model_comparison.csv` (xem AUC cao nhất) | outputs/         | Models       |
| **Xem toàn bộ cùng lúc?**     | `dashboard.html`                          | analysis/        | All          |

---

## 🚀 MẪU LƯU QUI TRÌNH PHÂN TÍCH

```bash
# Bước 1: Chạy pipeline
py run_complete_pipeline.py

# Bước 2: Mở dashboard
start analysis/dashboard.html

# Bước 3: Xem tương quan
open analysis/correlation_matrix.csv  (Excel)

# Bước 4: Xem features quan trọng
open analysis/feature_ranking_rfe.csv  (Excel)

# Bước 5: Phân tích Python (optional)
python
>>> import pandas as pd
>>> features = pd.read_csv('outputs/features_lab.csv')
>>> print(features.describe())

# Bước 6: Export & Share
# Gửi analysis/dashboard.html cho team
```

---

**Bạn có câu hỏi gì về cách đọc dữ liệu không?** 📊
