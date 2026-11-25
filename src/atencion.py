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


def trayectoria(panel, edad_min=6, edad_max=19):
    """Resume la ficha (niño × mes) en una fila por niño con las 10 variables del PCA (misma regla que el Step 3).
    Solo NNA de edad_min a edad_max años en su último registro (los servicios medidos aplican desde los 6 años)."""
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
    return t[(t["edad"] >= edad_min) & (t["edad"] <= edad_max)].drop(columns="tiene_discapacidad").dropna(subset=VARS).reset_index()


def cobertura_primera_infancia(panel, edad_max=6):
    """Atención esperada para los menores de edad_max años (último registro): un mes está cubierto si el niño
    recibe estimulación temprana o está en educación inicial (la estimulación se da hasta los 2-3 años y luego
    la reemplaza el nivel inicial). Devuelve (meses, ninos): el detalle niño × mes y el resumen por niño, con la
    racha de meses sin cobertura al final del período (meses seguidos hasta el último mes de la ficha)."""
    p = panel.sort_values(["id_nna", "periodo"])
    ult = p.groupby("id_nna")["edad"].last()
    m = p[p["id_nna"].isin(ult[ult < edad_max].index)].copy()
    m["cubierto"] = (m["soporte_estimulacion"] == 1) | (m["estudia"] == 1)
    ultimo_periodo = p["periodo"].max()

    def racha(g):
        if g["periodo"].iloc[-1] != ultimo_periodo: return 0
        n = 0
        for c in g["cubierto"].iloc[::-1]:
            if c: break
            n += 1
        return n

    g = m.groupby("id_nna")
    ninos = pd.DataFrame({"edad": g["edad"].last(), "meses": g.size(), "pct_cubierto": 100 * g["cubierto"].mean(),
                          "meses_sin_cobertura": (~m["cubierto"]).groupby(m["id_nna"]).sum(),
                          "racha_actual": g[["periodo", "cubierto"]].apply(racha), "upe": g["upe"].last()}).reset_index()
    return m, ninos


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
