"""Ejecuta todo el proyecto desde cero, en orden, y verifica su consistencia.

Uso (desde la carpeta TA_E10):  python ejecutar_todo.py

1. Verifica que los datos crudos no cambiaron (hashes en datos/0_crudos/hashes.json).
2. Borra todo lo generado (datos/1_ a 4_, figuras/) y ejecuta los notebooks en el orden KDD.
   Se detiene en el primer error o assert fallido.
3. Comprueba que cada archivo generado sea nuevo y que ninguno quede huérfano
   (todo archivo generado debe estar nombrado en el código de algún notebook).
"""
import hashlib, json, shutil, sys, time
from pathlib import Path
import nbformat
from nbclient import NotebookClient

RAIZ = Path(__file__).resolve().parent
NB = RAIZ / "notebooks"
ORDEN = [
    "Step1_Entendimiento_del_Dominio.ipynb",
    "Step2a_Consolidacion_Bloque2.ipynb",
    "Step2b_Seleccion_y_Entendimiento.ipynb",
    "Step3_Limpieza_y_Preprocesamiento.ipynb",
    "Anexo_Step4_solo_ficha.ipynb",
    "Anexo_Step6_solo_ficha.ipynb",
    "Step4_Reduccion_y_Proyeccion.ipynb",
    "Step5_Seleccion_Tarea_de_Mineria.ipynb",
    "Step6_Seleccion_de_Algoritmos.ipynb",
]
GENERADOS = [RAIZ / "datos" / d for d in ["1_consolidados", "2_limpios", "3_transformados", "4_resultados"]] + [RAIZ / "figuras"]


def verificar_crudos():
    crudos = RAIZ / "datos" / "0_crudos"
    esperado = json.loads((crudos / "hashes.json").read_text())
    for rel, h in esperado.items():
        real = hashlib.md5((crudos / rel).read_bytes()).hexdigest()
        if real != h:
            sys.exit(f"ERROR: el archivo crudo {rel} cambió (hash distinto)")
    print(f"[ok] {len(esperado)} archivos crudos sin cambios")


def limpiar():
    for d in GENERADOS:
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
    print("[ok] salidas anteriores borradas")


def ejecutar(nombre):
    t0 = time.time()
    nb = nbformat.read(NB / nombre, as_version=4)
    NotebookClient(nb, timeout=3600, kernel_name="python3", resources={"metadata": {"path": str(NB)}}).execute()
    nbformat.write(nb, NB / nombre)
    print(f"[ok] {nombre} ({time.time() - t0:.0f} s)")


def verificar_salidas(inicio):
    codigo = ""
    for nombre in ORDEN:
        nb = nbformat.read(NB / nombre, as_version=4)
        codigo += "\n".join(c.source for c in nb.cells if c.cell_type == "code")
    archivos = [p for d in GENERADOS for p in d.rglob("*") if p.is_file()]
    viejos = [p for p in archivos if p.stat().st_mtime < inicio]
    huerfanos = [p for p in archivos if p.name not in codigo]
    if viejos:
        sys.exit(f"ERROR: archivos no regenerados en esta corrida: {viejos}")
    if huerfanos:
        sys.exit(f"ERROR: archivos generados que ningún notebook nombra: {huerfanos}")
    print(f"[ok] {len(archivos)} archivos generados, todos nuevos y referenciados")


if __name__ == "__main__":
    inicio = time.time()
    verificar_crudos()
    limpiar()
    for nombre in ORDEN:
        ejecutar(nombre)
    verificar_salidas(inicio)
    print(f"OK – proyecto ejecutado en {time.time() - inicio:.0f} s")
