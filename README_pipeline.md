# Pipeline for Lab Events → ICU mortality prediction

Steps:

- `etl/quick_eda.py`: quick exploratory script that summarizes `labevents`, `icustays`, and `admissions`.
- Use `requirements.txt` to install dependencies.

Run:

```bash
pip install -r requirements.txt
python etl/quick_eda.py
```

Outputs are written to `outputs/summary.json` and `outputs/top_items.csv`.
