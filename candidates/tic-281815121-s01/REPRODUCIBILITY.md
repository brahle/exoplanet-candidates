# Evidence inspection only

Run `uv sync --frozen`, then `uv run python scripts/catalogue.py check`.
This verifies schema, time bookkeeping, covariance and exact exported hashes. It does not
recompute the light curve, source images or fitted event profiles. Original artifact hashes
are in the evidence manifest; private storage references were removed from exported JSON.
Mission product names, exact native-byte hashes and time/exposure conventions are in inputs.json.
A future numerical release needs exact public input bytes, versioned code, frozen environment
and a clean public-input rerun certificate. No planet probability or discovery priority is certified.
