"""Puntajes z con la referencia CDC 2000 (método LMS), para 2 a 20 años.

Es la referencia de las tablas de valoración nutricional del MINSA/INS (CENAN) para 5 a 19 años
(«Fuente: CDC Growth Charts, 2000»). Tablas oficiales en datos/0_crudos/referencias/cdc_lms/
(descargadas de cdc.gov): bmiagerev.csv (IMC para la edad) y statage.csv (talla para la edad).
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import norm

TABLAS = Path(__file__).resolve().parent.parent / "datos" / "0_crudos" / "referencias" / "cdc_lms"
_ARCH = {"imc": "bmiagerev.csv", "talla": "statage.csv"}
_CACHE = {}


def _tabla(indicador):
    if indicador not in _CACHE:
        t = pd.read_csv(TABLAS / _ARCH[indicador])
        t = t[pd.to_numeric(t["Sex"], errors="coerce").notna()].astype(float)   # el archivo repite el encabezado
        _CACHE[indicador] = t
    return _CACHE[indicador]


def zscore(indicador, valor, edad_anios, sexo_m):
    """Puntaje z CDC 2000. indicador: 'imc' o 'talla'; sexo_m: 1 = masculino, 0 = femenino. NaN fuera de 2–20 años."""
    valor, edad, sexo = (np.asarray(v, dtype=float) for v in (valor, edad_anios, sexo_m))
    meses = edad * 12
    z = np.full(valor.shape, np.nan)
    t = _tabla(indicador)
    for s in (0, 1):
        ts = t[t["Sex"] == (1 if s == 1 else 2)].sort_values("Agemos")
        m = (sexo == s) & np.isfinite(valor) & (meses >= ts["Agemos"].min()) & (meses <= ts["Agemos"].max())
        if not m.any():
            continue
        L, M, S = (np.interp(meses[m], ts["Agemos"], ts[c]) for c in ("L", "M", "S"))
        z[m] = np.where(np.abs(L) < 1e-8, np.log(valor[m] / M) / S, ((valor[m] / M) ** L - 1) / (L * S))
    return z


def percentil(z):
    return 100 * norm.cdf(z)
