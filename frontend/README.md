# Data Infrastructure AI Frontend

Complete React + TypeScript + Vite frontend.

## Run

```powershell
npm install
npm run dev
```

## Production test

```powershell
npm run build
npm run preview
```

## Vercel

Set the Vercel Root Directory to this frontend folder. Framework: Vite. Build: `npm run build`. Output: `dist`.

The included `public/demo-data` makes the dashboard work immediately. Replace those JSON files with exports from the Python pipeline later.


## Added platform features

- Dataset provenance and schema page
- End-to-end data lineage
- Quarantine explorer for rejected records
- ML readiness / feature groups
- Detailed pipeline execution profile

These pages currently use demo JSON in `public/demo-data`. Replace the JSON with real exports from the Python pipeline when your Kaggle processing is connected.


## Dataset management

The frontend now includes:
- Dataset registry
- Global dataset selector
- Add Dataset wizard
- File picker for CSV / JSON / Parquet
- Domain selection
- Pandas / Spark processing selection
- Schema preview
- Configurable validation controls
- Bronze / Silver / Gold / ML capability preview
- Simulated processing completion

Important: browser-selected files are not persisted or uploaded to a backend yet. The workflow is intentionally frontend-only until the FastAPI upload/storage endpoints are connected. Large datasets should ultimately be stored by the backend (for example Azure Blob/ADLS), not Vercel.
