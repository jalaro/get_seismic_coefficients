# Seismic Kx API

This is a simple Flask-based API to compute seismic horizontal force coefficient (Kx/Ky) using Taiwan RC code.

## Run Locally

```bash
pip install -r requirements.txt
python main.py
```

POST to `/seismic_kx` with input JSON containing fault info, direction, structure type, etc.
