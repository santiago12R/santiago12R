"""Dibuja las contribuciones de GitHub como una pared de mina en pixel art.

Cada bloque es un día: piedra si no hubo actividad, mineral según la cantidad de contribuciones
y gema brillante en los días con más actividad.

Uso (en GitHub Actions):  GITHUB_TOKEN=... python3 tools/contribuciones.py santiago12R dist
Prueba local sin red:     python3 tools/contribuciones.py santiago12R dist --demo
"""
import json
import os
import random
import sys
import urllib.request
from datetime import date

FUENTE = "'Courier New',Consolas,'Liberation Mono',monospace"
NIVELES = {
    "NONE": None,
    "FIRST_QUARTILE": ("#6b4fa0", "#8a6ac0"),
    "SECOND_QUARTILE": ("#c05cc0", "#e07ae0"),
    "THIRD_QUARTILE": ("#e8b830", "#ffe066"),
    "FOURTH_QUARTILE": ("#2fc4c0", "#5ee6e0"),
}
PIEDRA = ["#3a3352", "#352e4c", "#40385a"]
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
    paso = bloque + gap
    n = len(semanas)
    alto_titulo = 106 if movil else 70
    H = alto_titulo + 7 * paso + 64
    r = random.Random(5)
    o = []
    add = o.append
    add(f'<rect width="{ancho}" height="{H}" fill="url(#bg)"/>')
    add(f'<text x="{margen}" y="38" font-family="{FUENTE}" font-size="18" font-weight="700" fill="#fff1e6">CONTRIBUCIONES</text>')
    add(f'<rect x="{margen}" y="46" width="160" height="3" fill="#ff8fb8"/>')
    periodo = "en los últimos 6 meses" if movil else "en el último año"
    suma = sum(d["contributionCount"] for s in semanas for d in s["contributionDays"]) if movil else total
    if movil:
        add(f'<text x="{margen}" y="74" font-family="{FUENTE}" font-size="14" fill="#7dd3fc">{suma} contribuciones {periodo}</text>')
    else:
        add(f'<text x="{ancho - margen}" y="38" font-family="{FUENTE}" font-size="14" fill="#7dd3fc" text-anchor="end">{suma} contribuciones {periodo}</text>')
    y0 = alto_titulo
    # meses
    previo, ultimo_x = None, -99
    for i, s_ in enumerate(semanas):
        mes = int(s_["contributionDays"][0]["date"][5:7])
        x = margen + i * paso
        if mes != previo and x - ultimo_x >= 3 * paso:
            add(f'<text x="{x}" y="{y0 - 8}" font-family="{FUENTE}" font-size="11" fill="#b7a9d6">{MESES[mes - 1]}</text>')
            ultimo_x = x
        previo = mes
    # bloques
    for i, s in enumerate(semanas):
        for d in s["contributionDays"]:
            x = margen + i * paso
            y = y0 + d["weekday"] * paso
            nivel = NIVELES.get(d["contributionLevel"])
            if nivel is None:
                add(f'<rect x="{x}" y="{y}" width="{bloque}" height="{bloque}" fill="{r.choice(PIEDRA)}"/>')
                continue
            base, brillo = nivel
            add(f'<rect x="{x}" y="{y}" width="{bloque}" height="{bloque}" fill="{base}"/>')
            add(f'<rect x="{x}" y="{y}" width="{bloque}" height="{max(2, bloque // 4)}" fill="{brillo}"/>')
            if d["contributionLevel"] == "FOURTH_QUARTILE":
                add(f'<rect class="s" x="{x + bloque // 2 - 1}" y="{y + bloque // 2 - 1}" width="3" height="3" fill="#ffffff" '
                    f'style="animation-delay:{r.uniform(0, 3):.2f}s"/>')
    # leyenda
    yl = y0 + 7 * paso + 26
    add(f'<text x="{margen}" y="{yl + 10}" font-family="{FUENTE}" font-size="12" fill="#b7a9d6">Cada bloque es un día:</text>')
    xl = margen + (int(len("Cada bloque es un día:") * 7.2) + 10)
    if movil:
        xl, yl = margen, yl + 20
    for etiqueta, col in [("piedra", PIEDRA[0]), ("", NIVELES["FIRST_QUARTILE"][0]), ("", NIVELES["SECOND_QUARTILE"][0]),
                          ("", NIVELES["THIRD_QUARTILE"][0]), ("gema", NIVELES["FOURTH_QUARTILE"][0])]:
        if etiqueta == "piedra":
            add(f'<text x="{xl}" y="{yl + 10}" font-family="{FUENTE}" font-size="12" fill="#b7a9d6">sin actividad</text>')
            xl += 104
        add(f'<rect x="{xl}" y="{yl}" width="12" height="12" fill="{col}"/>')
        xl += 16
        if etiqueta == "gema":
            add(f'<text x="{xl + 4}" y="{yl + 10}" font-family="{FUENTE}" font-size="12" fill="#b7a9d6">más commits</text>')
    alt = (f"Contribuciones de santiago12R {periodo}: {suma}. Cada día es un bloque de una pared de mina; "
           f"piedra si no hubo actividad y mineral o gema según la cantidad de commits. Se actualiza todos los días.")
    cab = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {H}" width="{ancho}" height="{H}" role="img" '
           f'aria-label="{alt}"><title>Contribuciones de santiago12R</title><defs>'
           f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1c1033"/>'
           f'<stop offset=".6" stop-color="#2a1245"/><stop offset="1" stop-color="#3a1646"/></linearGradient>'
           f'<style>.s{{animation:tw 2.4s steps(2,end) infinite}}@keyframes tw{{0%,100%{{opacity:.1}}50%{{opacity:1}}}}'
           f'@media (prefers-reduced-motion:reduce){{.s{{animation:none}}}}</style></defs>')
    return cab + "".join(o) + "</svg>\n"


def main():
    usuario = sys.argv[1] if len(sys.argv) > 1 else "santiago12R"
    salida = sys.argv[2] if len(sys.argv) > 2 else "dist"
    total, semanas = demo() if "--demo" in sys.argv else obtener(usuario)
    os.makedirs(salida, exist_ok=True)
    with open(os.path.join(salida, "contribuciones.svg"), "w", encoding="utf-8") as f:
        f.write(dibujar(total, semanas, 1000, 14, 3, 50, False))
    with open(os.path.join(salida, "contribuciones-movil.svg"), "w", encoding="utf-8") as f:
        f.write(dibujar(total, semanas[-26:], 400, 11, 2, 31, True))
    print(f"{total} contribuciones; imágenes en {salida}/ ({date.today()})")


if __name__ == "__main__":
    main()
