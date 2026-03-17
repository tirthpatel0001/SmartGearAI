# Workload Analyzer - Explanation and How It Works

## What this module does
The workload analyzer is a production head tool that predicts:
1. Lead time for gearbox production
2. Machine requirements (count)
3. Workload status (overloaded / normal / underutilized)
4. Remaining time based on progress
5. Smart AI adjustment for high-risk conditions (tool wear/machine risk)

It exposes API endpoint: `POST /api/production/workload-analyzer` and a production UI in `app/main.py` for production head users.

## Input fields
- `gear_type`: "Spur", "Helical", or "Bevel"
- `teeth`, `diameter`, `process_steps`
- `machine_count`, `current_jobs`, `machine_capacity`, `progress`
- optional risk fields: `air_temperature`, `process_temperature`, `rotational_speed`, `torque`, `tool_wear`

## Output
- `lead_time` (hours)
- `machine_needed` (count)
- `workload_status` (overloaded / normal / underutilized)
- `remaining_time` (hours)
- `machine_risk` (normal / high)
- Human-friendly summary messages

## AI/ML used
### Data sources
- Gear dataset: `data/raw/gear_custom_data_4500.xlsx`
- AI4I dataset: `data/raw/ai4i2020.csv`

### Models
- `RandomForestRegressor` for lead time prediction
- `RandomForestClassifier` for machine failure risk classification

### Feature engineering
- `complexity_score = Teeth * Process_Steps`
- `size_factor = Diameter / Teeth`
- `gear_type` factors (spurs 1.0, helical 1.15, bevel 1.25)
- risk adjustment: +20% time for high risk/tool wear

## How it is created (module flow)
1. On app startup, models are loaded from `C:/Projects/SGMAS/models`.
2. If model files are missing, the module trains on the datasets and saves them.
3. API verifies user role is `production_head`.
4. API calls `predict_workload` in `backend/modules/workload_analyzer.py`.
5. Predictions and status are returned to frontend and logged in DB table `workload_logs`.

## Where code lives
- Backend module: `backend/modules/workload_analyzer.py`
- Route: `backend/routes.py` (`/production/workload-analyzer`)
- Models: `backend/models.py` (`WorkloadLog`)
- Startup registration: `backend/__init__.py`
- UI: `app/main.py` `display_workload_analyzer()`

## Key files and behavior
- `backend/modules/workload_analyzer.py`: data loading, auto-training, prediction functions.
- `backend/routes.py`: protected endpoint for production head, logs results.
- `app/main.py`: production head interactive form and metrics display.

## How to use
1. Start backend service with Flask (needs DB configured).
2. Start Streamlit app (`streamlit run app/main.py`).
3. Login as production head.
4. Navigate to Workload Analyzer and submit values.

## Notes
- No manual training step is required; the app trains models automatically if missing.
- To retrain, delete model pickle files under `models/` and restart backend.
