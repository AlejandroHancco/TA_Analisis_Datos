"""Índice de atención: recalcula los puntajes del PCA (Step 7) para una ficha nominal nueva.

Uso típico (Step 9):
    from src.atencion import trayectoria, puntajes
    tr = trayectoria(panel)                         # panel = ficha limpia, una fila por niño y mes (Step 3)
    res = puntajes(tr, json.load(open("datos/4_resultados/step7_modelo_pca.json")))

`res` trae, por niño, los puntajes de permanencia e intensidad psicosocial, el cuadrante y el índice de prioridad.
"""
import numpy as np
import pandas as pd

VARS = ["tiempo_hogar", "legal_definitiva", "p_acompan", "p_psicoter", "p_taller", "p_salud_mental",
        "p_pti_vencido", "p_pti_no_tiene", "discap_sev", "anemia_alguna"]
PRIORIDAD = "Prioridad: larga permanencia, baja atención"


def trayectoria(panel, edad_max=19):
    """Resume la ficha (niño × mes) en una fila por niño con las 10 variables del PCA (misma regla que el Step 3)."""
    p = panel.sort_values(["id_nna", "periodo"]); g = p.groupby("id_nna")
    t = pd.DataFrame({
        "edad": g["edad"].last(),
        "tiempo_hogar": g["tiempo_hogar_meses"].last(),
        "legal_definitiva": g["situacion_legal"].last().eq("Definitiva").astype(int),
        "p_acompan": g["soporte_acompanamiento"].mean(), "p_psicoter": g["soporte_psicoterapia"].mean(),
        "p_taller": g["soporte_taller"].mean(), "p_salud_mental": g["salud_mental_especializada"].mean(),
        "p_pti_vencido": g["estado_pti"].apply(lambda s: (s == "Vencido").mean()),
        "p_pti_no_tiene": g["estado_pti"].apply(lambda s: (s == "No tiene").mean()),
        "discap_sev": g["severidad_discapacidad"].max(), "tiene_discapacidad": g["tiene_discapacidad"].max(),
        "anemia_alguna": g["anemia"].max()})
    t.loc[(t["tiene_discapacidad"] == 1) & t["discap_sev"].isna(), "discap_sev"] = 1
    return t[t["edad"] <= edad_max].drop(columns="tiene_discapacidad").dropna(subset=VARS).reset_index()


def cuadrante(permanencia, intensidad):
    return np.select([(permanencia > 0) & (intensidad < 0), (permanencia > 0) & (intensidad >= 0), (permanencia <= 0) & (intensidad >= 0)],
                     [PRIORIDAD, "Larga permanencia, atención activa", "Reciente, atención activa"], "Reciente, baja atención")


def puntajes(tr, modelo):
    """Aplica la estandarización y las cargas guardadas en el Step 7 (no se reajusta nada)."""
    media, desv = np.array(modelo["media"]), np.array(modelo["desv"])
    W = np.array(modelo["cargas"])                      # componentes × variables
    Z = (tr[modelo["variables"]].to_numpy(float) - media) / desv
    P = Z @ W.T
    out = tr[["id_nna"]].copy()
    out["permanencia"], out["intensidad"] = P[:, 0], P[:, 1]
    out["cuadrante"] = cuadrante(out["permanencia"], out["intensidad"])
    out["indice_prioridad"] = np.where(out["cuadrante"] == PRIORIDAD, out["permanencia"] - out["intensidad"], np.nan)
    return out
