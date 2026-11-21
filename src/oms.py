"""Puntajes z de la OMS (método LMS) para IMC para la edad y talla para la edad.

Tablas oficiales en datos/0_crudos/referencias/oms_lms/ (descargadas de who.int):
- 0 a 5 años  (Patrones de crecimiento infantil OMS 2006, por día):   bfa-*, lhfa-*
- 5 a 19 años (Referencia de crecimiento OMS 2007, por mes):          bmi-*, hfa-*

z = ((X / M) ** L - 1) / (L * S). Para el IMC se aplica la corrección de la OMS fuera de ±3 DE
("restricted application of the LMS method"), porque la distribución se estira en las colas.
"""
from pathlib import Path
import numpy as np
import pandas as pd

TABLAS = Path(__file__).resolve().parent.parent / "datos" / "0_crudos" / "referencias" / "oms_lms"
DIAS_5A = 1856            # último día de las tablas 0-5 años
DIAS_MES = 30.4375


def _leer(indicador, sexo):
    """Devuelve una tabla única (edad en días, L, M, S) que une 0-5 y 5-19 años."""
    s = "boys" if sexo == 1 else "girls"
    chico, grande = {"imc": (f"bfa-{s}-zscore-expanded-tables.xlsx", f"bmi-{s}-z-who-2007-exp.xlsx"),
                     "talla": (f"lhfa-{s}-zscore-expanded-tables.xlsx", f"hfa-{s}-z-who-2007-exp.xlsx")}[indicador]
    a = pd.read_excel(TABLAS / chico)[["Day", "L", "M", "S"]].rename(columns={"Day": "dias"})
    b = pd.read_excel(TABLAS / grande)[["Month", "L", "M", "S"]]
    b["dias"] = b.pop("Month") * DIAS_MES
    b = b[b["dias"] > DIAS_5A]
    return pd.concat([a, b], ignore_index=True).sort_values("dias").reset_index(drop=True)


_CACHE = {}


def _lms(indicador, sexo, dias):
    clave = (indicador, sexo)
    if clave not in _CACHE:
        _CACHE[clave] = _leer(indicador, sexo)
    t = _CACHE[clave]
    return tuple(np.interp(dias, t["dias"], t[c]) for c in ("L", "M", "S"))


def _z(x, L, M, S):
    return ((x / M) ** L - 1) / (L * S)


def _corte(L, M, S, z):
    return M * (1 + L * S * z) ** (1 / L)


def zscore(indicador, valor, edad_anios, sexo_m):
    """Puntaje z OMS. indicador: 'imc' o 'talla'; sexo_m: 1 = masculino, 0 = femenino.
    Devuelve NaN fuera del rango de las tablas (más de 19 años) o si falta el valor."""
    valor, edad, sexo = (np.asarray(v, dtype=float) for v in (valor, edad_anios, sexo_m))
    dias = edad * 365.25
    z = np.full(valor.shape, np.nan)
    for s in (0, 1):
        m = (sexo == s) & np.isfinite(valor) & (dias >= 0) & (dias <= 228 * DIAS_MES)
        if not m.any():
            continue
        L, M, S = _lms(indicador, s, dias[m])
        zi = _z(valor[m], L, M, S)
        if indicador == "imc":
            sd3, sd2 = _corte(L, M, S, 3), _corte(L, M, S, 2)
            sd3n, sd2n = _corte(L, M, S, -3), _corte(L, M, S, -2)
            zi = np.where(zi > 3, 3 + (valor[m] - sd3) / (sd3 - sd2), zi)
            zi = np.where(zi < -3, -3 + (valor[m] - sd3n) / (sd2n - sd3n), zi)
        z[m] = zi
    return z


def categoria_imc(z, edad_anios):
    """Clasificación OMS del IMC para la edad (cortes distintos antes y después de los 5 años)."""
    z, e = np.asarray(z, float), np.asarray(edad_anios, float)
    menor = e < 5
    return np.select(
        [np.isnan(z),
         menor & (z > 3), menor & (z > 2), menor & (z > 1),
         ~menor & (z > 2), ~menor & (z > 1),
         z < -3, z < -2],
        [None, "Obesidad", "Sobrepeso", "Riesgo sobrepeso", "Obesidad", "Sobrepeso", "Delgadez severa", "Delgadez"],
        default="Normal").astype(object)


def categoria_talla(z):
    """Clasificación OMS de talla para la edad."""
    z = np.asarray(z, float)
    return np.select([np.isnan(z), z < -3, z < -2, z > 2], [None, "Talla baja severa", "Talla baja", "Alto"],
                     default="Normal").astype(object)
