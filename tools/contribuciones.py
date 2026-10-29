"""Dibuja las contribuciones de GitHub como el corte de una mina en pixel art.

Arriba, la superficie: el minero recorre la vía en su vagón. Abajo, la roca: cada día del último año es
una veta; queda en piedra si no hubo actividad y brilla como mineral o gema según cuántas contribuciones hubo.
Encima van cuatro cifras: contribuciones, días activos, racha más larga y mejor día.

Uso (en GitHub Actions):  GITHUB_TOKEN=... python3 tools/contribuciones.py santiago12R dist
Prueba local sin red:     python3 tools/contribuciones.py santiago12R dist --demo
"""
import json
import os
import random
import sys
import urllib.request
from datetime import date, timedelta

from fuente import FUENTE, font_face

# paleta del README
BG0, BG1, BG2 = "#06090f", "#0b1120", "#0f1729"
PANEL, BORDE = "#0e1525", "#2a3b5f"
CREMA, VIOLETA, CIAN, GEMA, AMAR, GRIS = "#f5f1ea", "#a78bfa", "#7dd3fc", "#5ee6e0", "#ffe066", "#93a4bf"
NIVELES = {
    "FIRST_QUARTILE": ("#2d5a9e", "#4a7cc4"),
    "SECOND_QUARTILE": ("#7c5fd6", "#a78bfa"),
    "THIRD_QUARTILE": ("#e8b830", "#ffe066"),
    "FOURTH_QUARTILE": ("#2fc4c0", "#5ee6e0"),
}
ROCA = ["#141b2a", "#161e2f", "#121827", "#18202f"]
VACIO = "#1d2638"
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
P = 4

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
    hoy = date.today()
    inicio = hoy - timedelta(days=364 + (hoy.weekday() + 1) % 7)
    semanas, total, d = [], 0, inicio
    while d <= hoy:
        dias = []
        for _ in range(7):
            if d > hoy:
                break
            n = r.choice([0, 0, 0, 0, 0, 1, 2, 3, 6, 10])
            total += n
            lvl = "NONE" if n == 0 else ["FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"][min(3, n // 3)]
            dias.append({"date": d.isoformat(), "contributionCount": n, "contributionLevel": lvl, "weekday": (d.weekday() + 1) % 7})
            d += timedelta(days=1)
        semanas.append({"contributionDays": dias})
    return total, semanas


def cifras(semanas):
    dias = [x for s in semanas for x in s["contributionDays"]]
    activos = sum(1 for x in dias if x["contributionCount"] > 0)
    racha = mejor_racha = 0
    for x in dias:
        racha = racha + 1 if x["contributionCount"] > 0 else 0
        mejor_racha = max(mejor_racha, racha)
    mejor_dia = max((x["contributionCount"] for x in dias), default=0)
    return activos, mejor_racha, mejor_dia


def fecha_es(d):
    return f"{d.day} de {MESES[d.month - 1]}. de {d.year}"


class SVG:
    def __init__(self):
        self.o = []

    def add(self, s):
        self.o.append(s)

    def px(self, x, y, c, w=P, h=P, extra=""):
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"{extra}/>')

    def texto(self, x, y, t, size, color, peso=400, anchor="start"):
        self.add(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{peso}" fill="{color}" text-anchor="{anchor}">{t}</text>')

    def sprite(self, ox, oy, filas, pal, p=P):
        for r, fila in enumerate(filas):
            c = 0
            while c < len(fila):
                ch = fila[c]
                if ch not in pal:
                    c += 1
                    continue
                j = c
                while j < len(fila) and fila[j] == ch:
                    j += 1
                self.px(ox + c * p, oy + r * p, pal[ch], (j - c) * p, p)
                c = j

    def marco(self, x, y, w, h, borde=BORDE, fill=PANEL, n=4):
        def pts(a, b, c, d):
            return " ".join(f"{u},{v}" for u, v in [(a + n, b), (a + c - n, b), (a + c - n, b + n), (a + c, b + n), (a + c, b + d - n), (a + c - n, b + d - n),
                                                     (a + c - n, b + d), (a + n, b + d), (a + n, b + d - n), (a, b + d - n), (a, b + n), (a + n, b + n)])
        self.add(f'<polygon points="{pts(x, y, w, h)}" fill="{borde}"/>')
        self.add(f'<polygon points="{pts(x + 2, y + 2, w - 4, h - 4)}" fill="{fill}"/>')


MINERO_CABEZA = [
    "....YYYYY.....",
    "...YYYYYYYL...",
    "..yYYYYYYYYYY.",
    "...HSSSSSS....",
    "...HSSWES.....",
    "...SSSSSSs....",
    "...SBBBBBB....",
    "....bBBBb.....",
    "....CSSC......",
    "..COOOCCOOO...",
]
PAL_MINERO = {"Y": "#f2c230", "y": "#c99a16", "L": "#fff6b0", "H": "#3a2418", "S": "#f0b98a", "s": "#d99a6c",
              "E": "#1b1424", "W": "#ffffff", "B": "#5a3524", "b": "#43271b", "O": "#ff8a3d", "C": "#3b4256"}
VAGON = ["SSSSSSSSSSSSSSSS", "sGGGGGGGGGGGGGGs", "sGRGGGGGGGGGGRGs", "sGGGgggggggggGGs", ".sGGGGGGGGGGGGs.", "..ssssssssssss.."]
PAL_VAGON = {"S": "#d6dce6", "s": "#4e5568", "G": "#7d8597", "g": "#6a7284", "R": "#e6ecf5"}


def escena(semanas, ancho, bloque, gap, margen, movil, total):
    s = SVG()
    paso = bloque + gap
    activos, racha, mejor = cifras(semanas)
    hoy = date.today()
    periodo = "últimos 6 meses" if movil else "último año"
    suma = sum(x["contributionCount"] for w in semanas for x in w["contributionDays"]) if movil else total

    # ------------------------------------------------ encabezado
    s.texto(margen, 46, "CONTRIBUCIONES", 20, CREMA, 700)
    s.add(f'<rect x="{margen}" y="54" width="182" height="3" fill="{VIOLETA}"/>')
    s.texto(margen, 80, "Cada veta que brilla es un día que programé.", 13 if movil else 14, "#d3dceb")
    s.texto(margen, 100, f"{periodo.capitalize()} · actualizado el {fecha_es(hoy)}", 11, GRIS)
    datos = [(suma, "contribuciones"), (activos, "días activos"), (racha, "racha más larga"), (mejor, "en mi mejor día")]
    if movil:
        bw, bh, x0, y0 = 164, 56, margen, 118
        pos = [(x0 + (i % 2) * (bw + 10), y0 + (i // 2) * (bh + 10)) for i in range(4)]
        y_cielo = y0 + 2 * (bh + 10) + 6
    else:
        bw, bh = 120, 58
        x0 = ancho - margen - 4 * bw - 3 * 10
        pos = [(x0 + i * (bw + 10), 30) for i in range(4)]
        y_cielo = 112
    for (v, et), (x, y), col in zip(datos, pos, [AMAR, CIAN, VIOLETA, GEMA]):
        s.marco(x, y, bw, bh, BORDE, PANEL, 3)
        s.texto(x + 12, y + 28, str(v), 22, col, 700)
        s.texto(x + 12, y + 46, et, 11, GRIS)

    # ------------------------------------------------ cielo y superficie
    alto_grid = 7 * paso
    y_suelo = y_cielo + 86
    y_grid = y_suelo + 36
    H = y_grid + alto_grid + 64
    r = random.Random(9)
    for _ in range(18 if not movil else 9):
        x, y = r.randint(margen, ancho - margen), r.randint(y_cielo + 4, y_suelo - 50)
        s.add(f'<rect class="tw" x="{x}" y="{y}" width="2" height="2" fill="{CREMA}" style="animation-delay:{r.uniform(0, 3):.2f}s"/>')
    picos, x = [], 0
    while x < ancho:
        alto = r.randint(16, 46)
        picos += [(x, y_suelo), (x + 40, y_suelo - alto), (x + 80, y_suelo)]
        x += r.randint(50, 90)
    s.add(f'<polygon points="{" ".join(f"{a},{b}" for a, b in [(0, y_suelo)] + picos + [(ancho, y_suelo)])}" fill="#17223a"/>')
    # vía
    for x in range(8, ancho - 8, 16):
        s.px(x, y_suelo - 4, "#5a3a22", 8, 4)
    s.px(8, y_suelo - 7, "#9aa7b8", ancho - 16, 3)
    s.px(8, y_suelo - 7, "#e6ecf5", ancho - 16, 1)
    # vagón con el minero cruzando
    vy = y_suelo - 7 - 24
    s.add('<g class="cruce">')
    s.sprite(-74, vy - 38, MINERO_CABEZA, PAL_MINERO)
    s.sprite(-80, vy, VAGON, PAL_VAGON)
    for wx in (-72, -36):
        s.add(f'<g class="rA"><rect x="{wx}" y="{vy + 18}" width="12" height="12" fill="#2a2f3c"/><rect x="{wx + 4}" y="{vy + 22}" width="4" height="4" fill="#9aa7b8"/></g>')
    s.add('</g>')
    # pasto, tierra y roca
    s.px(0, y_suelo, "#4fa834", ancho, 6)
    for x in range(0, ancho, 8):
        if r.random() < 0.35:
            s.px(x, y_suelo - 3, "#6fd04a", 4, 3)
    s.px(0, y_suelo + 6, "#6e4426", ancho, 14)
    for x in range(0, ancho, 12):
        s.px(x + r.randint(0, 6), y_suelo + 8 + r.randint(0, 8), "#8a5a33", 4, 4)
    s.add(f'<rect x="0" y="{y_suelo + 20}" width="{ancho}" height="{H - y_suelo - 20}" fill="url(#roca)"/>')
    if not movil:
        for tx in (margen - 30, ancho - margen + 22):
            s.px(tx, y_grid + 40, "#8b5a2b", 4, 16)
            s.add(f'<circle cx="{tx + 2}" cy="{y_grid + 34}" r="20" fill="#ffb36b" opacity=".10"/>')
            s.add(f'<g class="fl"><rect x="{tx - 2}" y="{y_grid + 32}" width="8" height="8" fill="#ff9a3c"/><rect x="{tx}" y="{y_grid + 30}" width="4" height="4" fill="{AMAR}"/></g>')

    # ------------------------------------------------ vetas: un bloque por día
    for i, w in enumerate(semanas):
        for d in w["contributionDays"]:
            x = margen + i * paso
            y = y_grid + d["weekday"] * paso
            nivel = NIVELES.get(d["contributionLevel"])
            if nivel is None:
                s.add(f'<rect x="{x}" y="{y}" width="{bloque}" height="{bloque}" fill="{VACIO}"/>')
                s.add(f'<rect x="{x}" y="{y + bloque - 2}" width="{bloque}" height="2" fill="#0c111c"/>')
                continue
            base, brillo = nivel
            s.add(f'<rect x="{x}" y="{y}" width="{bloque}" height="{bloque}" fill="{base}"><title>{d["date"]}: {d["contributionCount"]} contribuciones</title></rect>')
            s.add(f'<rect x="{x}" y="{y}" width="{bloque}" height="3" fill="{brillo}"/>')
            s.add(f'<rect x="{x + 3}" y="{y + 5}" width="3" height="3" fill="#ffffff" opacity=".55"/>')
            if d["contributionLevel"] == "FOURTH_QUARTILE":
                s.add(f'<rect class="tw" x="{x + bloque - 5}" y="{y + bloque - 6}" width="3" height="3" fill="#ffffff" style="animation-delay:{r.uniform(0, 3):.2f}s"/>')
    previo, ultimo_x = None, -99
    for i, w in enumerate(semanas):
        mes = int(w["contributionDays"][0]["date"][5:7])
        x = margen + i * paso
        if mes != previo and x - ultimo_x >= 3 * paso:
            s.texto(x, y_grid + alto_grid + 22, MESES[mes - 1], 11, GRIS)
            ultimo_x = x
        previo = mes
    yl = y_grid + alto_grid + 38
    xl = ancho - margen - 5 * 16 - 30
    s.texto(xl - 8, yl + 10, "menos", 11, GRIS, 400, "end")
    for j, col in enumerate([VACIO] + [NIVELES[k][0] for k in ("FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE")]):
        s.px(xl + j * 16, yl, col, 12, 12)
    s.texto(xl + 5 * 16 + 4, yl + 10, "más", 11, GRIS)

    alt = (f"Contribuciones de santiago12R en los {periodo}: {suma} contribuciones, {activos} días activos, racha más larga "
           f"de {racha} días y {mejor} contribuciones en el mejor día. Se dibujan como el corte de una mina: cada día es una "
           f"veta que brilla según cuánto programó. Se actualiza todos los días.").replace("los último año", "el último año")
    defs = (f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG0}"/>'
            f'<stop offset=".5" stop-color="{BG1}"/><stop offset="1" stop-color="{BG2}"/></linearGradient>'
            '<pattern id="roca" width="16" height="16" patternUnits="userSpaceOnUse">'
            + "".join(f'<rect x="{a}" y="{b}" width="4" height="4" fill="{ROCA[(a // 4 * 3 + b // 4 * 5) % 4]}"/>' for a in range(0, 16, 4) for b in range(0, 16, 4))
            + '</pattern>')
    dur = 22 if not movil else 14
    css = (f"{font_face()}text{{font-family:{FUENTE}}}"
           ".tw{animation:tw 2.4s steps(2,end) infinite}@keyframes tw{0%,100%{opacity:.15}50%{opacity:1}}"
           f".cruce{{animation:cruce {dur}s linear infinite}}@keyframes cruce{{0%{{transform:translateX(0)}}100%{{transform:translateX({ancho + 160}px)}}}}"
           ".rA{animation:rA .4s steps(2) infinite}@keyframes rA{0%{opacity:1}50%{opacity:.6}}"
           ".fl{animation:fl .5s steps(2) infinite}@keyframes fl{0%{transform:translateY(0)}50%{transform:translateY(-2px)}}"
           "@media (prefers-reduced-motion:reduce){.tw,.cruce,.rA,.fl{animation:none}}")
    cab = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {H}" width="{ancho}" height="{H}" role="img" '
           f'aria-label="{alt}" font-family="{FUENTE}"><title>Contribuciones de santiago12R</title>'
           f'<defs>{defs}<style>{css}</style></defs>'
           f'<rect width="{ancho}" height="{H}" fill="url(#bg)"/>')
    return cab + "".join(s.o) + f'<rect x="1" y="1" width="{ancho - 2}" height="{H - 2}" fill="none" stroke="{BORDE}" stroke-width="2"/></svg>\n'


def main():
    usuario = sys.argv[1] if len(sys.argv) > 1 else "santiago12R"
    salida = sys.argv[2] if len(sys.argv) > 2 else "dist"
    total, semanas = demo() if "--demo" in sys.argv else obtener(usuario)
    os.makedirs(salida, exist_ok=True)
    with open(os.path.join(salida, "contribuciones.svg"), "w", encoding="utf-8") as f:
        f.write(escena(semanas, 1000, 13, 4, 50, False, total))
    with open(os.path.join(salida, "contribuciones-movil.svg"), "w", encoding="utf-8") as f:
        f.write(escena(semanas[-26:], 400, 10, 3, 30, True, total))
    print(f"{total} contribuciones; imágenes en {salida}/ ({date.today()})")


if __name__ == "__main__":
    main()
