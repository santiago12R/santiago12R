"""Dibuja las contribuciones de GitHub como una cuadrícula minimalista sobre fondo negro.

Cada cuadrado es un día; el azul más intenso indica más contribuciones.

Uso (en GitHub Actions):  GITHUB_TOKEN=... python3 tools/contribuciones.py santiago12R dist
Prueba local sin red:     python3 tools/contribuciones.py santiago12R dist --demo
"""
import json
import os
import random
import sys
import urllib.request
from datetime import date

FUENTE = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
NIVELES = {
    "NONE": "#161b22",
    "FIRST_QUARTILE": "#123a5c",
    "SECOND_QUARTILE": "#1f6198",
    "THIRD_QUARTILE": "#3d8fd6",
    "FOURTH_QUARTILE": "#7cc4fa",
}
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

CONSULTA = """query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount contributionLevel weekday}}}}}}"""


def obtener(usuario):
    token = os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": CONSULTA, "variables": {"u": usuario}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        datos = json.load(r)
    cal = datos["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["totalContributions"], cal["weeks"]


def demo():
    r = random.Random(3)
    semanas, total = [], 0
    for w in range(53):
        dias = []
        for d in range(7):
            n = r.choice([0, 0, 0, 0, 1, 2, 3, 6, 10])
            total += n
            lvl = "NONE" if n == 0 else ["FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"][min(3, n // 3)]
            dias.append({"date": f"2026-{(w // 4.5) % 12 + 1:02.0f}-01", "contributionCount": n, "contributionLevel": lvl, "weekday": d})
        semanas.append({"contributionDays": dias})
    return total, semanas


def dibujar(total, semanas, ancho, bloque, gap, margen, movil):
    """Cuadrícula minimalista: cada día es un cuadrado; más intenso, más contribuciones."""
    paso = bloque + gap
    arriba = 100 if movil else 84
    H = arriba + 7 * paso + 56
    o = []
    add = o.append
    add(f'<rect width="{ancho}" height="{H}" rx="12" fill="#0d1117"/>')
    add(f'<text x="{margen}" y="52" font-size="20" font-weight="600" fill="#e6edf3">Contribuciones</text>')
    periodo = "en los últimos 6 meses" if movil else "en el último año"
    suma = sum(d["contributionCount"] for s in semanas for d in s["contributionDays"]) if movil else total
    if movil:
        add(f'<text x="{margen}" y="76" font-size="13" fill="#9aa4b1">{suma} contribuciones {periodo}</text>')
    else:
        add(f'<text x="{ancho - margen}" y="52" font-size="13" fill="#9aa4b1" text-anchor="end">{suma} contribuciones {periodo}</text>')
    previo, ultimo_x = None, -99
    for i, s in enumerate(semanas):
        mes = int(s["contributionDays"][0]["date"][5:7])
        x = margen + i * paso
        if mes != previo and x - ultimo_x >= 3 * paso:
            add(f'<text x="{x}" y="{arriba - 10}" font-size="11" fill="#6b7480">{MESES[mes - 1]}</text>')
            ultimo_x = x
        previo = mes
    for i, s in enumerate(semanas):
        for d in s["contributionDays"]:
            x = margen + i * paso
            y = arriba + d["weekday"] * paso
            add(f'<rect x="{x}" y="{y}" width="{bloque}" height="{bloque}" rx="2.5" fill="{NIVELES[d["contributionLevel"]]}"/>')
    yl = arriba + 7 * paso + 28
    xl = ancho - margen - 5 * (bloque + 4) - 36 if not movil else margen + 36
    add(f'<text x="{xl - 8}" y="{yl + bloque - 2}" font-size="11" fill="#6b7480" text-anchor="end">Menos</text>' if not movil
        else f'<text x="{margen}" y="{yl + bloque - 2}" font-size="11" fill="#6b7480">Menos</text>')
    for j, k in enumerate(["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]):
        add(f'<rect x="{xl + j * (bloque + 4)}" y="{yl}" width="{bloque}" height="{bloque}" rx="2.5" fill="{NIVELES[k]}"/>')
    add(f'<text x="{xl + 5 * (bloque + 4) + 4}" y="{yl + bloque - 2}" font-size="11" fill="#6b7480">Más</text>')
    alt = (f"Contribuciones de santiago12R {periodo}: {suma}. Cada cuadrado es un día; más intenso significa más "
           f"contribuciones. Se actualiza todos los días.")
    cab = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {H}" width="{ancho}" height="{H}" role="img" '
           f'aria-label="{alt}" font-family="{FUENTE}"><title>Contribuciones de santiago12R</title>'
           f'<style>text{{font-family:{FUENTE}}}</style>')
    return cab + "".join(o) + "</svg>\n"


def main():
    usuario = sys.argv[1] if len(sys.argv) > 1 else "santiago12R"
    salida = sys.argv[2] if len(sys.argv) > 2 else "dist"
    total, semanas = demo() if "--demo" in sys.argv else obtener(usuario)
    os.makedirs(salida, exist_ok=True)
    with open(os.path.join(salida, "contribuciones.svg"), "w", encoding="utf-8") as f:
        f.write(dibujar(total, semanas, 1000, 13, 4, 48, False))
    with open(os.path.join(salida, "contribuciones-movil.svg"), "w", encoding="utf-8") as f:
        f.write(dibujar(total, semanas[-26:], 400, 10, 3, 28, True))
    print(f"{total} contribuciones; imágenes en {salida}/ ({date.today()})")


if __name__ == "__main__":
    main()
