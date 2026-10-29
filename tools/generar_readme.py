"""Genera todas las imágenes SVG del README de santiago12R (escritorio y celular).

Uso:  python3 tools/generar_readme.py
Salida: assets/readme/*.svg y assets/readme/movil/*.svg

Estilo: pixel art nocturno (morado), tipografía monoespaciada y acentos rosa, cian y amarillo.
"""
import os
import random
from xml.sax.saxutils import escape

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(RAIZ, "assets", "readme")
HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ paleta
BG0, BG1, BG2 = "#06090f", "#0b1120", "#0f1729"
PANEL, PANEL2, BORDE = "#0e1525", "#141d33", "#2a3b5f"
CREMA, ROSA, CIAN, GEMA, AMAR, VERDE, GRIS = "#f5f1ea", "#a78bfa", "#7dd3fc", "#5ee6e0", "#ffe066", "#7ee08a", "#93a4bf"
from fuente import FUENTE, font_face  # noqa: E402
P = 4

ESTILO_BASE = font_face() + f"""
.t{{font-family:{FUENTE}}}
.s{{animation:tw 3s steps(2,end) infinite}}
@keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.9}}}}
.f{{animation:flt 3.2s ease-in-out infinite}}
@keyframes flt{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-10px)}}}}
.b{{animation:rip 2.6s ease-in-out infinite}}
@keyframes rip{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}}
.cur{{animation:cur 1s steps(1) infinite}}
@keyframes cur{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.s,.f,.b,.cur{{animation:none}}}}
"""


def esc(t):
    return escape(t, {'"': "&quot;"})


class Lienzo:
    def __init__(self, w, h, titulo, css=""):
        self.w, self.h, self.titulo, self.css = w, h, titulo, css
        self.o = []
        self.grad = False

    def add(self, s):
        self.o.append(s)

    def px(self, x, y, c, w=P, h=P, extra=""):
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"{extra}/>')

    def sprite(self, ox, oy, filas, pal, p=P):
        # agrupa píxeles contiguos del mismo color en un solo rectángulo
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

    def texto(self, x, y, t, size, color, peso=400, anchor="start", extra=""):
        self.add(f'<text class="t" x="{x}" y="{y}" font-size="{size}" font-weight="{peso}" fill="{color}" text-anchor="{anchor}"{extra}>{esc(t)}</text>')

    def panel(self, x, y, w, h, fill=PANEL, borde=BORDE, n=P):
        """Rectángulo con esquinas escalonadas (pixel art)."""
        pts = [(x + n, y), (x + w - n, y), (x + w - n, y + n), (x + w, y + n), (x + w, y + h - n), (x + w - n, y + h - n),
               (x + w - n, y + h), (x + n, y + h), (x + n, y + h - n), (x, y + h - n), (x, y + n), (x + n, y + n)]
        d = " ".join(f"{a},{b}" for a, b in pts)
        self.add(f'<polygon points="{d}" fill="{borde}"/>')
        n2 = n
        x2, y2, w2, h2 = x + 2, y + 2, w - 4, h - 4
        pts = [(x2 + n2, y2), (x2 + w2 - n2, y2), (x2 + w2 - n2, y2 + n2), (x2 + w2, y2 + n2), (x2 + w2, y2 + h2 - n2),
               (x2 + w2 - n2, y2 + h2 - n2), (x2 + w2 - n2, y2 + h2), (x2 + n2, y2 + h2), (x2 + n2, y2 + h2 - n2),
               (x2, y2 + h2 - n2), (x2, y2 + n2), (x2 + n2, y2 + n2)]
        d = " ".join(f"{a},{b}" for a, b in pts)
        self.add(f'<polygon points="{d}" fill="{fill}"/>')

    def fondo(self, estrellas=0, semilla=1, evitar=None):
        self.add(f'<rect width="{self.w}" height="{self.h}" fill="url(#bg)"/>')
        self.grad = True
        r = random.Random(semilla)
        for _ in range(estrellas):
            x, y = r.randint(8, self.w - 8), r.randint(8, self.h - 8)
            if evitar and any(a <= x <= c and b <= y <= d for a, b, c, d in evitar):
                continue
            sz = r.choice([2, 2, 3])
            self.add(f'<rect class="s" x="{x}" y="{y}" width="{sz}" height="{sz}" fill="{CREMA}" style="animation-delay:{r.uniform(0, 3):.2f}s"/>')

    def guardar(self, nombre, alt=None):
        defs = ""
        if self.grad:
            defs = (f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG0}"/>'
                    f'<stop offset=".55" stop-color="{BG1}"/><stop offset="1" stop-color="{BG2}"/></linearGradient>')
        cab = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
               f'role="img" aria-label="{esc(alt or self.titulo)}"><title>{esc(self.titulo)}</title>'
               f'<defs>{defs}<style>{ESTILO_BASE}{self.css}</style></defs>')
        ruta = os.path.join(DEST, nombre)
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(cab + "\n".join(self.o) + "</svg>\n")
        return ruta


def partir(texto, n):
    """Parte un texto en líneas de máximo n caracteres."""
    lineas, act = [], ""
    for p in texto.split():
        if len(act) + len(p) + (1 if act else 0) > n:
            lineas.append(act)
            act = p
        else:
            act = f"{act} {p}" if act else p
    if act:
        lineas.append(act)
    return lineas


def ancho_texto(t, size):
    return len(t) * size * 0.6


# ================================================================== escena del minero
PIEDRA = ["#7d7f8a", "#6c6e79", "#8b8d98", "#5f616b"]
CESPED = ["#5fbf3f", "#4fa834", "#6fd04a"]
TIERRA = ["#8a5a33", "#7a4e2b", "#96643a", "#6e4426"]

MINERO = [
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
    ".CCOOOCCOOO...",
    ".CCRRRRRRRR...",
    ".GCOOOCCOOO...",
    ".G.oOOCCOOo...",
    "...KKKKkKKK...",
    "...PPPPPPPP...",
    "...PPPp.PPP...",
    "...PPP..PPP...",
    "...ppP..Ppp...",
    "..TTTT..TTTT..",
    "..tttt..tttt..",
]
PAL_MINERO = {
    "Y": "#f2c230", "y": "#c99a16", "L": "#fff6b0", "H": "#3a2418",
    "S": "#f0b98a", "s": "#d99a6c", "E": "#1b1424", "W": "#ffffff",
    "B": "#5a3524", "b": "#43271b", "O": "#ff8a3d", "o": "#d96a22", "R": "#e9eef5",
    "C": "#3b4256", "c": "#2b3142", "K": "#2a2016", "k": "#c9a24a",
    "P": "#4b5568", "p": "#363e4f", "T": "#6b4428", "t": "#2a1a10", "G": "#8a6a4a",
}


def css_escena(sx, cx, cy, bx, by):
    return f"""
.arm{sx}{{transform-origin:{cx}px {cy}px;animation:swing{sx} 1.4s infinite}}
@keyframes swing{sx}{{0%{{transform:rotate(-78deg);animation-timing-function:ease-out}}48%{{transform:rotate(-88deg);animation-timing-function:cubic-bezier(.6,0,1,.6)}}62%{{transform:rotate(13deg);animation-timing-function:ease-out}}72%{{transform:rotate(9deg);animation-timing-function:ease-in-out}}100%{{transform:rotate(-78deg)}}}}
.body{sx}{{animation:lean 1.4s infinite}}
@keyframes lean{{0%,48%,100%{{transform:translateY(0)}}62%,70%{{transform:translateY(2px)}}}}
.ore{sx}{{transform-origin:{bx + 20}px {by + 20}px;animation:shake 1.4s infinite}}
@keyframes shake{{0%,61%{{transform:translate(0,0)}}63%{{transform:translate(3px,-1px)}}66%{{transform:translate(-2px,1px)}}69%{{transform:translate(1px,0)}}72%,100%{{transform:translate(0,0)}}}}
.k1{{animation:k1 4.2s steps(1) infinite}}.k2{{animation:k2 4.2s steps(1) infinite}}
@keyframes k1{{0%,20%{{opacity:0}}21%,95%{{opacity:1}}96%,100%{{opacity:0}}}}
@keyframes k2{{0%,53%{{opacity:0}}54%,95%{{opacity:1}}96%,100%{{opacity:0}}}}
.pt{{opacity:0;animation:pt 1.4s infinite}}
@keyframes pt{{0%,61%{{opacity:0;transform:translate(0,0)}}62%{{opacity:1;transform:translate(0,0)}}92%{{opacity:0;transform:translate(var(--dx),var(--dy))}}100%{{opacity:0;transform:translate(var(--dx),var(--dy))}}}}
.gem{{opacity:0;animation:gem 4.2s infinite}}
@keyframes gem{{0%,87%{{opacity:0;transform:translate(0,0)}}88%{{opacity:1;transform:translate(0,0)}}94%{{opacity:1;transform:translate(10px,-34px)}}100%{{opacity:0;transform:translate(18px,-46px)}}}}
.fl{{animation:fl .5s steps(2) infinite}}
@keyframes fl{{0%{{transform:translateY(0)}}50%{{transform:translateY(-2px)}}}}
.lamp{{animation:lamp 3s ease-in-out infinite}}
@keyframes lamp{{0%,100%{{opacity:.9}}50%{{opacity:.6}}}}
.cl{{animation:drift 40s linear infinite}}
@keyframes drift{{0%{{transform:translateX(0)}}50%{{transform:translateX(26px)}}100%{{transform:translateX(0)}}}}
@media (prefers-reduced-motion:reduce){{.arm{sx},.body{sx},.ore{sx},.k1,.k2,.pt,.gem,.fl,.lamp,.cl{{animation:none}}.pt,.gem{{opacity:0}}}}
"""


def suelo(L, gy, w, semilla=7):
    r = random.Random(semilla)
    tw = 64
    alto = L.h - gy + P
    L.add(f'<pattern id="ground" x="0" y="{gy - P}" width="{tw}" height="{alto}" patternUnits="userSpaceOnUse">')
    for x in range(0, tw, P):
        top = 0 if r.random() < 0.2 else P
        L.px(x, top, r.choice(CESPED), P, 12 - top)
        for y in range(12, 40, P):
            L.px(x, y, "#5a3820" if r.random() < 0.05 else r.choice(TIERRA))
        for y in range(40, alto, P):
            L.px(x, y, r.choice(PIEDRA))
    L.add('</pattern>')
    L.add(f'<rect x="0" y="{gy - P}" width="{w}" height="{alto}" fill="url(#ground)"/>')
    L.add(f'<rect x="0" y="{gy + 8}" width="{w}" height="2" fill="#000" opacity=".18"/>')
    for ox, col in [(0.1, GEMA), (0.3, AMAR), (0.47, ROSA), (0.61, GEMA), (0.9, AMAR)]:
        x0, y0 = int(w * ox) // 4 * 4, gy + 44
        if y0 + 8 < L.h:
            for dx, dy in [(0, 0), (4, 4), (8, 0)]:
                L.px(x0 + dx, y0 + dy, col)


def escena_minero(L, mx, gy, sx="", semilla=11):
    """Antorcha, minero que pica y bloque de mineral. mx = x del minero, gy = línea del suelo."""
    r = random.Random(semilla)
    my = gy - 84
    cx, cy = mx + 34, gy - 46
    bx, by = mx + 90, gy - 40
    # antorcha
    tx, ty = mx - 50, gy - 36
    L.px(tx + 2, ty + 12, "#8b5a2b", 4, 24)
    L.px(tx + 2, ty + 12, "#a8743d", 2, 24)
    L.add('<g class="fl">')
    L.sprite(tx - 2, ty - 4, [".YY.", "YOOY", "OROO", ".OO."], {"Y": AMAR, "O": "#ff9a3c", "R": "#fff1b0"})
    L.add('</g>')
    L.add(f'<circle cx="{tx + 4}" cy="{ty + 2}" r="22" fill="#ffb36b" opacity=".12"/>')
    # bloque de mineral
    L.add(f'<g class="ore{sx}">')
    for rr in range(10):
        for c in range(10):
            L.px(bx + c * P, by + rr * P, r.choice(PIEDRA))
    L.px(bx, by, "#a3a5b0", 40, 4)
    L.px(bx, by, "#9597a2", 4, 40)
    L.px(bx + 36, by, "#4e505a", 4, 40)
    L.px(bx, by + 36, "#4e505a", 40, 4)
    for dx, dy in [(8, 8), (12, 8), (8, 12), (24, 12), (28, 16), (24, 16), (12, 24), (16, 28), (28, 28)]:
        L.px(bx + dx, by + dy, GEMA)
    for dx, dy in [(8, 8), (24, 12), (12, 24), (28, 28)]:
        L.px(bx + dx, by + dy, "#c8fffb", 2, 2)
    L.add('<g class="k1">')
    for dx, dy in [(4, 4), (8, 8), (12, 8), (16, 12)]:
        L.px(bx + dx, by + dy, "#24252c", P, 2)
    L.add('</g><g class="k2">')
    for dx, dy in [(16, 16), (20, 20), (20, 24), (28, 26), (8, 20), (4, 24)]:
        L.px(bx + dx, by + dy, "#24252c", P, 2)
    L.add('</g></g>')
    L.add('<g class="gem">')
    L.add(f'<polygon points="{bx + 12},{by - 2} {bx + 20},{by - 10} {bx + 28},{by - 2} {bx + 20},{by + 6}" fill="{GEMA}"/>')
    L.add(f'<polygon points="{bx + 12},{by - 2} {bx + 20},{by - 10} {bx + 20},{by - 2}" fill="#c8fffb"/>')
    L.add('</g>')
    for dx, dy, col in [(-14, -26, "#a3a5b0"), (6, -32, GEMA), (18, -20, "#8b8d98"), (-22, -12, "#c8fffb"), (12, -40, AMAR), (-4, -36, "#7d7f8a")]:
        L.add(f'<rect class="pt" x="{bx + 4}" y="{by + 10}" width="4" height="4" fill="{col}" style="--dx:{dx}px;--dy:{dy}px"/>')
    # minero
    L.add(f'<g class="body{sx}">')
    L.add(f'<rect x="{mx + 4}" y="{gy - 2}" width="52" height="4" fill="#000" opacity=".22"/>')
    L.sprite(mx, my, MINERO, PAL_MINERO)
    L.add(f'<polygon class="lamp" points="{mx + 44},{my + 6} {mx + 150},{my - 16} {mx + 150},{my + 40}" fill="url(#beam)"/>')
    L.add('</g>')
    # brazo y pico
    L.add(f'<g class="arm{sx}">')
    L.px(cx - 2, cy - 4, "#3b4256", 16, 8)
    L.px(cx - 2, cy + 2, "#2b3142", 16, 2)
    L.px(cx + 14, cy - 5, "#8a6a4a", 8, 10)
    L.px(cx + 14, cy - 5, "#a8865f", 8, 2)
    L.px(cx + 10, cy - 2, "#8b5a2b", 64, 5)
    L.px(cx + 10, cy - 2, "#b07a43", 64, 1)
    L.px(cx + 10, cy + 2, "#5e3a1a", 64, 1)
    for gx in range(cx + 24, cx + 40, 4):
        L.px(gx, cy - 3, "#3a2418", 2, 7)
    L.px(cx + 66, cy - 5, "#5b6678", 8, 11)
    L.px(cx + 66, cy - 5, "#9aa7b8", 8, 2)
    cabeza = []
    for dy in range(-34, 35, 4):
        t = dy / 36
        x0 = cx + 64 + int(round(12 * (1 - t * t)))
        w = 8 if abs(dy) < 26 else 4
        cabeza.append((x0, cy + dy - 2, w))
    for x0, y0, w in cabeza:
        L.px(x0, y0, "#9aa7b8", w, 4)
        L.px(x0 + w - 2, y0, "#e6ecf5", 2, 4)
        L.px(x0, y0, "#5b6678", 2, 4)
    x0, y0, _ = cabeza[0]
    L.px(x0 + 2, y0 - 4, "#e6ecf5", 2, 4)
    x0, y0, _ = cabeza[-1]
    L.px(x0 + 2, y0 + 4, "#e6ecf5", 2, 4)
    L.add(f'<rect x="{cx + 82}" y="{cy - 14}" width="2" height="6" fill="#ffffff" opacity=".9"/>')
    L.add('</g>')
    return css_escena(sx, cx, cy, bx, by)


def nubes(L, posiciones):
    for x, y in posiciones:
        L.add('<g class="cl" opacity=".55">')
        for dx, dy, w in [(8, 0, 20), (0, 6, 44), (-8, 12, 60)]:
            L.px(x + dx, y + dy, "#1c2742", w, 6)
        L.add('</g>')


def luna(L, x, y):
    L.sprite(x, y, ["WWWW", "WwWW", "WWwW", "WWWW"], {"W": "#f4f0ff", "w": "#c9c2e6"}, 5)


BEAM = '<linearGradient id="beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff6b0" stop-opacity=".55"/><stop offset="1" stop-color="#fff6b0" stop-opacity="0"/></linearGradient>'

LINEAS_ROTAN = [
    "> Disponible para práctica empresarial",
    "> 7.º semestre · U. Cooperativa",
    "> Medellín, Colombia",
]
KT = [("0;1;1;0;0;0;0;0;0", "0;.03;.3;.33;.4;.7;.8;.9;1"),
      ("0;0;0;1;1;0;0;0;0", "0;.3;.33;.36;.63;.66;.8;.9;1"),
      ("0;0;0;0;0;1;1;0;0", "0;.3;.5;.63;.66;.69;.96;.99;1")]


def escritura(x, y, ancho, alto, pasos=24, dur=2.6):
    vals = ";".join(str(int(ancho * i / pasos)) for i in range(pasos + 1))
    kts = ";".join(f"{i / pasos:.3f}" for i in range(pasos + 1))
    return (f'<clipPath id="type"><rect x="{x}" y="{y}" width="0" height="{alto}"><animate attributeName="width" dur="{dur}s" '
            f'begin="0.4s" fill="freeze" calcMode="discrete" values="{vals}" keyTimes="{kts}"/></rect></clipPath>')


ALT_PORTADA = ("Santiago Rodríguez Jiménez, estudiante de Ingeniería de Software (7.º semestre) en la Universidad "
               "Cooperativa de Colombia, Medellín. Full stack y analítica de datos. Disponible para práctica empresarial. "
               "Escena pixel art de un minero que pica un bloque de mineral.")


def portada_escritorio():
    L = Lienzo(1000, 360, "Santiago Rodríguez Jiménez — Ingeniería de Software · Full Stack y Datos")
    L.fondo(28, 3, evitar=[(410, 50, 990, 200)])
    nubes(L, [(112, 22), (342, 40), (610, 18)])
    luna(L, 940, 20)
    L.add(open(os.path.join(HERE, "s_letra.svgfrag")).read())
    L.add(open(os.path.join(HERE, "gemas.svgfrag")).read())
    L.add(f'<g clip-path="url(#type)"><text class="t" x="420" y="96" font-size="35" font-weight="700" fill="{CREMA}" letter-spacing="-1">Santiago Rodríguez Jiménez</text></g>')
    L.add(f'<rect x="420" y="106" width="560" height="4" fill="{ROSA}" opacity="0"><animate attributeName="opacity" from="0" to=".9" begin="3s" dur=".01s" fill="freeze"/></rect>')
    L.add(f'<text class="t" x="420" y="140" font-size="20" font-weight="500" fill="{ROSA}" opacity="0">Ingeniería de Software · Full Stack &amp; Datos<animate attributeName="opacity" from="0" to="1" begin="3.1s" dur=".4s" fill="freeze"/></text>')
    for t, (v, k) in zip(LINEAS_ROTAN, KT):
        L.add(f'<text class="t" x="420" y="178" font-size="17" fill="{CIAN}" opacity="0">{esc(t)}<animate attributeName="opacity" values="{v}" keyTimes="{k}" dur="9s" begin="3.4s" repeatCount="indefinite"/></text>')
    suelo(L, 300, 1000)
    css = escena_minero(L, 810, 300, "d")
    L.css = css
    L.o.insert(0, "")  # marcador
    L.o[0] = f"<defs>{BEAM}{escritura(420, 56, 590, 50)}</defs>"
    return L.guardar("portada.svg", ALT_PORTADA)


def portada_movil():
    L = Lienzo(400, 500, "Santiago Rodríguez Jiménez — Ingeniería de Software · Full Stack y Datos")
    L.fondo(18, 4, evitar=[(16, 150, 390, 320)])
    nubes(L, [(220, 24)])
    luna(L, 350, 22)
    L.add('<g transform="translate(-28,-14) scale(.62)">' + open(os.path.join(HERE, "s_letra.svgfrag")).read() + '</g>')
    for x, y, c1, c2, c3 in [(300, 90, "#7dd3fc", "#2f8fc4", "#1f6a94"), (250, 130, "#ffe066", "#c9a21c", "#8f7310"), (370, 120, "#a78bfa", "#7c5fd6", "#5b3fb0")]:
        L.add(f'<g class="f"><polygon points="{x - 7},{y + 4} {x},{y + 8} {x},{y + 16} {x - 7},{y + 12}" fill="{c2}"/><polygon points="{x + 7},{y + 4} {x},{y + 8} {x},{y + 16} {x + 7},{y + 12}" fill="{c3}"/><polygon points="{x},{y} {x + 7},{y + 4} {x},{y + 8} {x - 7},{y + 4}" fill="{c1}"/></g>')
    L.add(f'<g clip-path="url(#type)"><text class="t" x="24" y="196" font-size="30" font-weight="700" fill="{CREMA}" letter-spacing="-1">Santiago</text>'
          f'<text class="t" x="24" y="232" font-size="30" font-weight="700" fill="{CREMA}" letter-spacing="-1">Rodríguez Jiménez</text></g>')
    L.add(f'<rect x="24" y="244" width="352" height="4" fill="{ROSA}" opacity="0"><animate attributeName="opacity" from="0" to=".9" begin="3s" dur=".01s" fill="freeze"/></rect>')
    L.add(f'<text class="t" x="24" y="274" font-size="16" font-weight="500" fill="{ROSA}" opacity="0">Ing. de Software · Full Stack &amp; Datos<animate attributeName="opacity" from="0" to="1" begin="3.1s" dur=".4s" fill="freeze"/></text>')
    for t, (v, k) in zip(LINEAS_ROTAN, KT):
        L.add(f'<text class="t" x="24" y="302" font-size="14" fill="{CIAN}" opacity="0">{esc(t)}<animate attributeName="opacity" values="{v}" keyTimes="{k}" dur="9s" begin="3.4s" repeatCount="indefinite"/></text>')
    suelo(L, 452, 400)
    css = escena_minero(L, 180, 452, "m")
    L.css = css
    L.o.insert(0, f"<defs>{BEAM}{escritura(24, 166, 400, 76, 18, 2.2)}</defs>")
    return L.guardar("movil/portada.svg", ALT_PORTADA)


# ================================================================== botones y chips
ICONOS = {
    "pdf": ([".WWWW..", ".WWWWW.", ".WRRRW.", ".WWWWW.", ".WRRRW.", ".WWWWW.", ".WWWWW."], {"W": CREMA, "R": ROSA}),
    "correo": (["CCCCCCC", "CWCCCWC", "CCWCWCC", "CCCWCCC", "CCCCCCC"], {"C": CIAN, "W": "#06090f"}),
    "codigo": (["..C.C..", ".C...C.", "C.....C", ".C...C.", "..C.C.."], {"C": CIAN}),
    "gema": (["..G..", ".GgG.", "GgGgG", ".GgG.", "..G.."], {"G": GEMA, "g": "#c8fffb"}),
    "insignia": ([".YYY.", "YYyYY", "YyYyY", ".YYY.", ".R.R.", "R...R"], {"Y": AMAR, "y": "#fff6b0", "R": ROSA}),
    "pico": (["SSSS.", "...S.", "..W.S", ".W...", "W...."], {"S": "#e6ecf5", "W": "#b07a43"}),
}


def boton(nombre, etiqueta, icono, color):
    w = int(ancho_texto(etiqueta, 15)) + 70
    L = Lienzo(w, 44, etiqueta)
    L.panel(0, 0, w, 44, PANEL2, color)
    filas, pal = ICONOS[icono]
    L.sprite(16, 22 - len(filas) * 3 // 2, filas, pal, 3)
    L.texto(48, 28, etiqueta, 15, CREMA, 700)
    return L.guardar(nombre, etiqueta)


def chip(nombre, etiqueta, color=CIAN, icono="gema", etiqueta_alt=None, solo_texto=False):
    w = int(ancho_texto(etiqueta, 13)) + (24 if solo_texto else 46)
    L = Lienzo(w, 34, etiqueta)
    if solo_texto:
        L.texto(w - 6, 22, etiqueta, 13, GRIS, 700, "end")
    else:
        L.panel(0, 0, w, 34, PANEL, color)
        filas, pal = ICONOS[icono]
        L.sprite(13, 17 - len(filas), filas, pal, 2)
        L.texto(34, 22, etiqueta, 13, CREMA, 700)
    return L.guardar(nombre, etiqueta_alt or etiqueta)


# ================================================================== tarjetas de proyecto
ICONO_PROY = {
    "casa-rendon": (["..W.W...", "...W.W..", "CCCCCC..", "CCCCCCCC", "CCCCCC.C", "CCCCCCCC", "CCCCCC..", ".CCCC..."], {"C": "#c9895a", "W": CREMA}),
    "numi": (["...YY...", "..YYYY..", "YYYYYYYY", ".YYYYYY.", "..YYYY..", ".YY..YY.", "YY....YY"], {"Y": AMAR}),
    "blackjack": (["WWWWW...", "WRWWW...", "WWWRWWWW", "WWWWWRWW", "WRWWWWWW", "WWWWWWRW", "...WWWWW"], {"W": CREMA, "R": ROSA}),
    "cinex": (["KWKWKWKW", "WKWKWKWK", "CCCCCCCC", "CCCCCCCC", "CCCCCCCC", "CCCCCCCC", "CCCCCCCC"], {"K": "#06090f", "W": CREMA, "C": CIAN}),
}
COLOR_ESTADO = {"CLIENTE REAL": VERDE, "EN VIVO": VERDE, "EN DESARROLLO": AMAR, "ACADÉMICO": CIAN}


def tarjeta(nombre, titulo, estados, meta, desc, cifra_n, cifra_txt, rol, stack, icono, movil=False):
    if movil:
        W, H, fs_t, fs, fs_n = 400, 380, 26, 15, 40
    else:
        W, H, fs_t, fs, fs_n = 490, 340, 26, 14, 40
    cols = int((W - 44) / (fs * 0.6))
    alt = f"{titulo}, {', '.join(e.lower() for e in estados)}: {desc} {cifra_n} {cifra_txt}. Mi rol: {rol}"
    L = Lienzo(W, H, f"{titulo} — {desc}")
    L.panel(0, 0, W, H, PANEL, BORDE)
    L.add(f'<rect x="2" y="2" width="{W - 4}" height="6" fill="{ROSA}" opacity=".85"/>')
    # estados
    x = 20
    for e in estados:
        w = int(ancho_texto(e, 11)) + 16
        L.panel(x, 22, w, 22, PANEL2, COLOR_ESTADO[e], 2)
        L.texto(x + 8, 37, e, 11, COLOR_ESTADO[e], 700)
        x += w + 8
    L.texto(W - 20, 37, meta, 12, GRIS, 400, "end")
    # icono y título
    filas, pal = ICONO_PROY[icono]
    L.sprite(20, 62, filas, pal, 4)
    L.texto(62, 88, titulo, fs_t, CREMA, 700)
    y = 120
    for ln in partir(desc, cols):
        L.texto(20, y, ln, fs, "#d3dceb")
        y += fs + 6
    # cifra
    y += 14
    L.texto(20, y + fs_n - 8, cifra_n, fs_n, AMAR, 700)
    xn = 20 + ancho_texto(cifra_n, fs_n) + 12
    yy = y + 6
    for ln in partir(cifra_txt, int((W - xn - 20) / (fs * 0.6))):
        L.texto(xn, yy + fs, ln, fs, CREMA, 700)
        yy += fs + 4
    y = max(y + fs_n + 16, yy + fs + 14)
    # rol
    for i, ln in enumerate(partir("Mi rol: " + rol, cols)):
        if i == 0:
            L.add(f'<text class="t" x="20" y="{y}" font-size="{fs}" fill="#d3dceb"><tspan fill="{ROSA}" font-weight="700">Mi rol:</tspan>{esc(ln[7:])}</text>')
        else:
            L.texto(20, y, ln, fs, "#d3dceb")
        y += fs + 6
    # stack
    x, y = 20, H - 40
    for s in stack:
        w = int(ancho_texto(s, 11)) + 14
        if x + w > W - 20:
            break
        L.add(f'<rect x="{x}" y="{y}" width="{w}" height="22" fill="{PANEL2}"/>')
        L.add(f'<rect x="{x}" y="{y + 20}" width="{w}" height="2" fill="{CIAN}" opacity=".6"/>')
        L.texto(x + 7, y + 15, s, 11, CIAN, 700)
        x += w + 6
    return L.guardar(("movil/" if movil else "") + f"proyecto-{nombre}.svg", alt)


PROYECTOS = [
    dict(nombre="casa-rendon", titulo="Casa Rendón", estados=["CLIENTE REAL", "EN VIVO"], meta="2026 · equipo",
         desc="Sitio web de una marca familiar de café y vino de Andes, Antioquia: historia, catálogo y reservas.",
         cifra_n="7", cifra_txt="secciones; reservas y reseñas llegan a WhatsApp",
         rol="HTML, CSS, JavaScript y componentes en React.", stack=["HTML", "CSS", "JavaScript", "React"], icono="casa-rendon"),
    dict(nombre="numi", titulo="Numi", estados=["EN DESARROLLO"], meta="2026 · equipo de 4",
         desc="App educativa en Flutter para niños de 1.° a 5.° de primaria en zonas rurales de Medellín, sin internet.",
         cifra_n="15", cifra_txt="actividades en 5 materias, con asistente de IA offline",
         rol="pantallas de la app y diseño responsive.", stack=["Flutter", "Dart"], icono="numi"),
    dict(nombre="blackjack", titulo="BlackJack Royale", estados=["EN VIVO"], meta="2025 · equipo",
         desc="Casino web con BlackJack contra la máquina, multijugador en tiempo real y banco de fichas.",
         cifra_n="6", cifra_txt="módulos de JavaScript y un servidor de WebSockets",
         rol="front-end en HTML, CSS y JavaScript, y servidor en Python.", stack=["HTML", "CSS", "JavaScript", "Python"], icono="blackjack"),
    dict(nombre="cinex", titulo="CineX", estados=["ACADÉMICO"], meta="2025 · equipo",
         desc="Sistema para gestionar un cine: películas, salas, funciones y reservas.",
         cifra_n="8", cifra_txt="clases de servicio sobre 4 entidades de la API REST",
         rol="capa de servicios con la lógica de negocio.", stack=["Java", "Spring Boot", "MySQL", "Bootstrap"], icono="cinex"),
]


# ================================================================== trayectoria
HITOS = [
    ("2023", ["Ingeniería de Software", "U. Cooperativa"], ROSA, True),
    ("2024", ["Estructuras de datos", "en Python"], CIAN, True),
    ("2025", ["BlackJack · CineX", "Computación Ubicua"], CIAN, True),
    ("2026", ["Numi · Casa Rendón", "(cliente real)"], AMAR, True),
    ("SIGUE", ["Práctica empresarial"], VERDE, False),
    ("2027", ["Fin de la carrera", "(previsto)"], GRIS, False),
]
ALT_TRAY = ("Trayectoria: 2023 ingreso a Ingeniería de Software en la Universidad Cooperativa; 2024 estructuras de datos en "
            "Python; 2025 BlackJack Royale, CineX y Computación Ubicua; 2026 Numi y Casa Rendón con cliente real. "
            "Siguiente: práctica empresarial. 2027: fin de la carrera, previsto.")


def bloque_hito(L, x, y, color, lleno):
    if lleno:
        L.px(x, y, color, 20, 20)
        L.px(x, y, "#ffffff", 20, 4, ' opacity=".35"')
        L.px(x, y + 16, "#000", 20, 4, ' opacity=".25"')
    else:
        L.add(f'<rect x="{x + 1}" y="{y + 1}" width="18" height="18" fill="none" stroke="{color}" stroke-width="2" stroke-dasharray="4 2"/>')


# ---- vagón y rieles
VAGON = [
    "SSSSSSSSSSSSSSSS",
    "sGGGGGGGGGGGGGGs",
    "sGRGGGGGGGGGGRGs",
    "sGGGGGGGGGGGGGGs",
    "sGGGgggggggggGGs",
    "sGRGGGGGGGGGGRGs",
    ".sGGGGGGGGGGGGs.",
    "..ssssssssssss..",
]
PAL_VAGON = {"S": "#d6dce6", "s": "#4e5568", "G": "#7d8597", "g": "#6a7284", "R": "#e6ecf5"}
RUEDA_A = ["KKK", "KWK", "KKK"]
RUEDA_B = ["KWK", "WKW", "KWK"]
PAL_RUEDA = {"K": "#2a2f3c", "W": "#9aa7b8"}
PASAJERO = MINERO[:10]  # casco, cara, barba y hombros; el resto queda dentro del vagón

MOVER, PARAR = 1.1, 1.5  # segundos en movimiento y detenido en cada estación


def tiempos_viaje(n):
    """Devuelve (duración total, lista de (llegada, salida)) en fracciones de 0 a 1."""
    total = n * (MOVER + PARAR) + 0.8
    marcas, t = [], 0.0
    for i in range(n):
        if i > 0:
            t += MOVER
        marcas.append((t / total, (t + PARAR) / total))
        t += PARAR
    return total, marcas


def css_viaje(n, eje, paso):
    total, marcas = tiempos_viaje(n)
    k = []
    for i, (a, b) in enumerate(marcas):
        d = i * paso
        tr = f"translate({d}px,0)" if eje == "x" else f"translate(0,{d}px)"
        k.append(f"{a * 100:.2f}%{{transform:{tr};opacity:1}}")
        k.append(f"{b * 100:.2f}%{{transform:{tr};opacity:1}}")
    fin = (n - 1) * paso
    tr = f"translate({fin}px,0)" if eje == "x" else f"translate(0,{fin}px)"
    salida = marcas[-1][1] * 100
    k.append(f"{min(99.5, salida + 3):.2f}%{{transform:{tr};opacity:0}}")
    k.append(f"100%{{transform:{'translate(0,0)'};opacity:0}}")
    css = f".viaje{{animation:viaje {total:.1f}s linear infinite}}@keyframes viaje{{{''.join(k)}}}"
    for i, (a, b) in enumerate(marcas):
        css += (f".luz{i}{{opacity:0;animation:luz{i} {total:.1f}s steps(1) infinite}}"
                f"@keyframes luz{i}{{0%{{opacity:0}}{a * 100:.2f}%{{opacity:1}}{b * 100:.2f}%{{opacity:0}}100%{{opacity:0}}}}")
    css += (".rA{animation:rA .3s steps(1) infinite}.rB{animation:rB .3s steps(1) infinite}"
            "@keyframes rA{0%{opacity:1}50%{opacity:0}}@keyframes rB{0%{opacity:0}50%{opacity:1}}"
            ".saludo{transform-box:fill-box;transform-origin:50% 100%;animation:sal 1s ease-in-out infinite}"
            "@keyframes sal{0%,100%{transform:rotate(-12deg)}50%{transform:rotate(18deg)}}"
            "@media (prefers-reduced-motion:reduce){.viaje,.saludo,.rA,.rB{animation:none}"
            + "".join(f".luz{i}" + ("," if i < n - 1 else "") for i in range(n)) + "{animation:none;opacity:0}}")
    return css


def vagon_lateral(L, cx, base):
    """Vagón visto de lado con el minero adentro; cx = centro, base = altura del riel."""
    x = cx - 32
    y = base - 38
    L.add('<g class="viaje">')
    L.sprite(x + 6, y - 38, PASAJERO, PAL_MINERO, 4)
    L.add(f'<g class="saludo"><rect x="{x + 46}" y="{y - 14}" width="6" height="16" fill="#3b4256"/>'
          f'<rect x="{x + 45}" y="{y - 21}" width="8" height="8" fill="#8a6a4a"/></g>')
    L.sprite(x, y, VAGON, PAL_VAGON, 4)
    for wx in (x + 8, x + 44):
        L.add('<g class="rA">')
        L.sprite(wx, base - 9, RUEDA_A, PAL_RUEDA, 4)
        L.add('</g><g class="rB">')
        L.sprite(wx, base - 9, RUEDA_B, PAL_RUEDA, 4)
        L.add('</g>')
    L.add('</g>')


def rieles_h(L, x0, x1, y):
    for x in range(x0, x1, 16):
        L.px(x, y + 2, "#6b4428", 8, 8)
        L.px(x, y + 2, "#8b5a2b", 8, 2)
    L.add(f'<rect x="{x0}" y="{y - 2}" width="{x1 - x0}" height="4" fill="#9aa7b8"/>')
    L.add(f'<rect x="{x0}" y="{y - 2}" width="{x1 - x0}" height="1" fill="#e6ecf5"/>')
    L.add(f'<rect x="{x0}" y="{y + 2}" width="{x1 - x0}" height="1" fill="#4e5568"/>')


def trayectoria():
    W, H = 1000, 260
    L = Lienzo(W, H, "Trayectoria")
    L.fondo(14, 9, evitar=[(0, 30, W, H)])
    L.texto(32, 40, "TRAYECTORIA", 18, CREMA, 700)
    L.add(f'<rect x="32" y="48" width="150" height="3" fill="{ROSA}"/>')
    x0, x1, riel = 92, 908, 176
    paso = (x1 - x0) / (len(HITOS) - 1)
    L.css = css_viaje(len(HITOS), "x", round(paso, 2))
    rieles_h(L, 24, W - 24, riel)
    for i, (anio, lineas, color, lleno) in enumerate(HITOS):
        x = x0 + i * paso
        # estación: poste, letrero con el año y luz cuando llega el vagón
        L.px(x - 1, 92, "#4e5568", 3, riel - 94)
        L.add(f'<rect class="luz{i}" x="{x - 44}" y="62" width="88" height="34" fill="{color}" opacity="0"/>')
        L.panel(x - 40, 66, 80, 26, PANEL2, color, 2)
        L.texto(x, 84, anio, 14, color, 700, "middle")
        for j, ln in enumerate(lineas):
            L.texto(x, riel + 34 + j * 18, ln, 12, CREMA if j == 0 else GRIS, 700 if j == 0 else 400, "middle")
        if not lleno:
            L.add(f'<rect x="{x - 40}" y="66" width="80" height="26" fill="{BG0}" opacity=".35"/>')
    vagon_lateral(L, x0, riel - 2)
    return L.guardar("trayectoria.svg", ALT_TRAY)


def trayectoria_movil():
    W = 400
    paso, y0 = 84, 96
    H = y0 + paso * (len(HITOS) - 1) + 70
    L = Lienzo(W, H, "Trayectoria")
    L.fondo(8, 9, evitar=[(0, 50, W, H)])
    L.texto(24, 40, "TRAYECTORIA", 18, CREMA, 700)
    L.add(f'<rect x="24" y="48" width="150" height="3" fill="{ROSA}"/>')
    L.css = css_viaje(len(HITOS), "y", paso)
    # vía vertical vista desde arriba
    for y in range(64, H - 16, 14):
        L.px(30, y, "#6b4428", 36, 6)
        L.px(30, y, "#8b5a2b", 36, 2)
    for rx in (36, 56):
        L.add(f'<rect x="{rx}" y="60" width="4" height="{H - 76}" fill="#9aa7b8"/>')
        L.add(f'<rect x="{rx}" y="60" width="1" height="{H - 76}" fill="#e6ecf5"/>')
    for i, (anio, lineas, color, lleno) in enumerate(HITOS):
        y = y0 + i * paso
        L.add(f'<rect class="luz{i}" x="80" y="{y - 22}" width="300" height="56" fill="{color}" opacity="0" style="opacity:0"/>')
        L.panel(84, y - 18, 292, 48, PANEL if lleno else BG0, color, 2)
        L.texto(98, y + 2, anio, 15, color, 700)
        L.texto(166, y + 2, lineas[0], 13, CREMA, 700)
        if len(lineas) > 1:
            L.texto(166, y + 20, lineas[1], 12, GRIS)
    # vagón visto desde arriba con el minero (casco amarillo)
    cx, cy = 48, y0 + 6
    L.add('<g class="viaje">')
    L.px(cx - 18, cy - 20, "#4e5568", 36, 40)
    L.px(cx - 16, cy - 18, "#c3cad6", 32, 36)
    L.px(cx - 12, cy - 14, "#7d8597", 24, 28)
    L.px(cx - 12, cy - 2, "#ff8a3d", 24, 12)
    L.px(cx - 8, cy - 12, "#f2c230", 16, 14)
    L.px(cx - 4, cy - 12, "#fff6b0", 8, 4)
    L.px(cx - 6, cy - 16, "#fff6b0", 4, 4)
    L.add('</g>')
    return L.guardar("movil/trayectoria.svg", ALT_TRAY)


# ================================================================== stack
STACK = [
    ("HTML y CSS", "Estructura y estilos", "Casa Rendón · BlackJack", "#e8734a"),
    ("JavaScript", "Lógica en el navegador", "Casa Rendón · BlackJack", "#e8c94a"),
    ("React", "Componentes de interfaz", "Casa Rendón", "#5ec8e6"),
    ("Bootstrap", "Diseño responsive", "CineX (frontend)", "#8a6ae0"),
    ("Flutter y Dart", "Apps móviles", "Numi", "#4aa8e8"),
    ("Java", "Programación orientada a objetos", "CineX · POO en Java", "#e0884a"),
    ("Spring Boot", "APIs REST", "CineX", "#6ac86a"),
    ("Python", "Servidores y scripts", "BlackJack · Estructuras", "#4a8ae0"),
    ("MySQL", "Base de datos relacional", "CineX", "#4a9ac0"),
    ("Git y GitHub", "Trabajo en equipo", "Todos los proyectos", "#e86a5a"),
    ("VS Code", "Editor", "Todos los proyectos", "#3a9ae8"),
    ("Postman", "Probar APIs", "ACADÉMICO", "#e8864a"),
    ("Docker", "Contenedores", "ACADÉMICO", "#3a8ae0"),
]
ALT_STACK = "Stack: " + "; ".join(f"{n}, {u}, {p.lower() if p == 'ACADÉMICO' else 'en ' + p}" for n, u, p, _ in STACK) + "."


def ficha_stack(L, x, y, w, h, n, u, p, color, fs=13):
    L.panel(x, y, w, h, PANEL, BORDE, 2)
    L.px(x + 12, y + 14, color, 12, 12)
    L.px(x + 12, y + 14, "#ffffff", 12, 3, ' opacity=".35"')
    L.texto(x + 34, y + 25, n, fs + 2, CREMA, 700)
    L.texto(x + 12, y + 46, u, fs - 1, "#d3dceb")
    if p == "ACADÉMICO":
        wa = int(ancho_texto(p, 10)) + 12
        L.add(f'<rect x="{x + 12}" y="{y + 54}" width="{wa}" height="18" fill="none" stroke="{CIAN}" stroke-width="1.5"/>')
        L.texto(x + 18, y + 67, p, 10, CIAN, 700)
    else:
        L.texto(x + 12, y + 67, p, fs - 2, ROSA, 700)


def stack():
    cols, w, h, gap = 3, 304, 84, 12
    filas = (len(STACK) + cols - 1) // cols
    H = 70 + filas * (h + gap) + 10
    L = Lienzo(1000, H, "Stack")
    L.fondo(10, 5, evitar=[(0, 60, 1000, H)])
    L.texto(32, 44, "STACK", 18, CREMA, 700)
    L.add(f'<rect x="32" y="52" width="70" height="3" fill="{ROSA}"/>')
    L.texto(968, 44, "herramienta · para qué · dónde la usé", 12, GRIS, 400, "end")
    for i, (n, u, p, c) in enumerate(STACK):
        x = 32 + (i % cols) * (w + gap)
        y = 70 + (i // cols) * (h + gap)
        ficha_stack(L, x, y, w, h, n, u, p, c)
    return L.guardar("stack.svg", ALT_STACK)


def stack_movil():
    w, h, gap = 352, 84, 10
    H = 66 + len(STACK) * (h + gap) + 8
    L = Lienzo(400, H, "Stack")
    L.fondo(6, 5, evitar=[(0, 56, 400, H)])
    L.texto(24, 40, "STACK", 18, CREMA, 700)
    L.add(f'<rect x="24" y="48" width="70" height="3" fill="{ROSA}"/>')
    for i, (n, u, p, c) in enumerate(STACK):
        ficha_stack(L, 24, 66 + i * (h + gap), w, h, n, u, p, c, 14)
    return L.guardar("movil/stack.svg", ALT_STACK)


# ================================================================== cierre
ALT_CIERRE = ("¿Tu equipo necesita un practicante? Desarrollo de software o análisis de datos. Disponible para nuevos "
              "retos profesionales. Escríbeme: santiago.rodriguezj12@gmail.com")


def entrada_mina(L, x, y, w, h, gy):
    """Entrada de mina con marco de madera; (x, y) esquina superior del marco, gy = suelo."""
    L.add(f'<rect x="{x + 14}" y="{y + 14}" width="{w - 28}" height="{gy - y - 14}" fill="#04060a"/>')
    L.add(f'<rect x="{x + 14}" y="{y + 14}" width="{w - 28}" height="{gy - y - 14}" fill="url(#tunel)"/>')
    for px_ in (x, x + w - 14):
        L.px(px_, y + 8, "#6b4428", 14, gy - y - 8)
        L.px(px_, y + 8, "#8b5a2b", 4, gy - y - 8)
        L.px(px_ + 10, y + 8, "#4a2c18", 4, gy - y - 8)
    L.px(x - 10, y, "#6b4428", w + 20, 16)
    L.px(x - 10, y, "#a8743d", w + 20, 4)
    L.px(x - 10, y + 12, "#4a2c18", w + 20, 4)
    for bx in range(x - 4, x + w + 6, 24):
        L.px(bx, y + 6, "#3a2418", 2, 4)


def cartel(L, cx, y, linea1, linea2, size2):
    w = int(ancho_texto(linea2, size2)) + 40
    x = cx - w // 2
    L.add(f'<rect x="{x + 18}" y="{y + 38}" width="2" height="30" fill="#9aa7b8"/>')
    L.add(f'<rect x="{x + w - 20}" y="{y + 38}" width="2" height="30" fill="#9aa7b8"/>')
    L.panel(x, y, w, 42, PANEL2, ROSA, 3)
    L.texto(cx, y + 16, linea1, 10, GRIS, 700, "middle", ' letter-spacing="2"')
    L.texto(cx, y + 33, linea2, size2, CREMA, 700, "middle")


def vagon_gemas(L, x, gy):
    y = gy - 32
    for gx, gyy, c in [(x + 8, y - 10, GEMA), (x + 22, y - 14, AMAR), (x + 36, y - 10, ROSA), (x + 48, y - 8, GEMA), (x + 16, y - 4, CIAN), (x + 30, y - 4, GEMA)]:
        L.add(f'<polygon points="{gx},{gyy + 6} {gx + 6},{gyy} {gx + 12},{gyy + 6} {gx + 6},{gyy + 12}" fill="{c}"/>')
        L.add(f'<rect class="s" x="{gx + 4}" y="{gyy + 3}" width="2" height="2" fill="#ffffff" style="animation-delay:{(gx % 7) / 3:.2f}s"/>')
    L.sprite(x, y, VAGON, PAL_VAGON, 4)
    for wx in (x + 8, x + 44):
        L.sprite(wx, gy - 9, RUEDA_A, PAL_RUEDA, 4)


def minero_con_gema(L, x, gy):
    L.sprite(x, gy - 84, MINERO, PAL_MINERO, 4)
    L.add(f'<g class="alza"><rect x="{x + 44}" y="{gy - 64}" width="6" height="22" fill="#3b4256"/>'
          f'<rect x="{x + 43}" y="{gy - 70}" width="8" height="8" fill="#8a6a4a"/>'
          f'<polygon points="{x + 40},{gy - 76} {x + 47},{gy - 84} {x + 54},{gy - 76} {x + 47},{gy - 68}" fill="{GEMA}"/>'
          f'<polygon points="{x + 40},{gy - 76} {x + 47},{gy - 84} {x + 47},{gy - 76}" fill="#c8fffb"/></g>')
    L.add(f'<rect class="s" x="{x + 56}" y="{gy - 90}" width="3" height="3" fill="#ffffff"/>')
    L.add(f'<rect class="s" x="{x + 36}" y="{gy - 88}" width="2" height="2" fill="#ffffff" style="animation-delay:.8s"/>')


def suelo_cierre(L, gy, W):
    L.px(0, gy, "#4fa834", W, 6)
    for x in range(0, W, 12):
        L.px(x, gy - 3, "#6fd04a", 4, 3) if (x * 7) % 5 < 2 else None
    L.px(0, gy + 6, "#6e4426", W, L.h - gy - 6)
    for x in range(0, W, 14):
        L.px(x + (x * 3) % 8, gy + 10 + (x * 5) % 10, "#8a5a33", 4, 4)


CSS_CIERRE = (".halo{animation:halo 2.2s ease-in-out infinite}@keyframes halo{0%,100%{opacity:.2}50%{opacity:.1}}.farol{animation:farol 2.2s ease-in-out infinite}@keyframes farol{0%,100%{opacity:.9}50%{opacity:.55}}"
              ".alza{transform-box:fill-box;transform-origin:50% 100%;animation:alza 1.6s ease-in-out infinite}"
              "@keyframes alza{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}"
              "@media (prefers-reduced-motion:reduce){.halo,.farol,.alza{animation:none}}")
TUNEL = ('<radialGradient id="tunel" cx=".5" cy=".35" r=".7"><stop offset="0" stop-color="#ffb36b" stop-opacity=".18"/>'
         '<stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>')


def farol(L, cx, y):
    L.add(f'<rect x="{cx - 1}" y="{y}" width="2" height="12" fill="#9aa7b8"/>')
    L.add(f'<circle class="halo" cx="{cx}" cy="{y + 22}" r="30" fill="#ffb36b" opacity=".16"/>')
    L.px(cx - 6, y + 12, "#3a2418", 12, 4)
    L.add(f'<rect class="farol" x="{cx - 5}" y="{y + 16}" width="10" height="12" fill="{AMAR}"/>')
    L.px(cx - 6, y + 28, "#3a2418", 12, 4)


def cierre(movil=False):
    correo = "santiago.rodriguezj12@gmail.com"
    if movil:
        W, H, gy = 400, 440, 404
        L = Lienzo(W, H, "Contacto", CSS_CIERRE)
        L.fondo(10, 21, evitar=[(0, 0, W, 210)])
        L.o.insert(0, f"<defs>{TUNEL}</defs>")
        L.texto(24, 56, "¿TU EQUIPO NECESITA", 24, CREMA, 700)
        L.texto(24, 90, "UN PRACTICANTE?", 24, CIAN, 700)
        L.texto(24, 122, "Desarrollo de software o análisis de datos.", 13, "#d3dceb")
        L.texto(24, 142, "Disponible para nuevos retos profesionales.", 13, "#d3dceb")
        L.texto(24, 176, correo, 15, AMAR, 700)
        L.add(f'<rect class="cur" x="{24 + int(ancho_texto(correo, 15)) + 4}" y="164" width="8" height="15" fill="{AMAR}"/>')
        entrada_mina(L, 252, 300, 124, 0, gy)
        farol(L, 314, 316)
        cartel(L, 314, 236, "SALIDA", "→ TU EQUIPO", 14)
        for x in range(30, 262, 16):
            L.px(x, gy - 4, "#5a3a22", 8, 4)
        L.px(24, gy - 7, "#9aa7b8", 240, 3)
        vagon_gemas(L, 40, gy - 6)
        minero_con_gema(L, 150, gy)
        suelo_cierre(L, gy, W)
    else:
        W, H, gy = 1000, 290, 252
        L = Lienzo(W, H, "Contacto", CSS_CIERRE)
        L.fondo(16, 21, evitar=[(0, 0, 600, 230)])
        L.o.insert(0, f"<defs>{TUNEL}</defs>")
        L.texto(48, 86, "¿TU EQUIPO NECESITA", 34, CREMA, 700)
        L.texto(48, 130, "UN PRACTICANTE?", 34, CIAN, 700)
        L.texto(48, 166, "Desarrollo de software o análisis de datos.", 15, "#d3dceb")
        L.texto(48, 188, "Disponible para nuevos retos profesionales.", 15, "#d3dceb")
        L.texto(48, 224, correo, 18, AMAR, 700)
        L.add(f'<rect class="cur" x="{48 + int(ancho_texto(correo, 18)) + 6}" y="210" width="9" height="17" fill="{AMAR}"/>')
        entrada_mina(L, 790, 136, 168, 0, gy)
        farol(L, 874, 152)
        cartel(L, 874, 68, "SALIDA", "→ TU EQUIPO", 16)
        for x in range(600, 800, 16):
            L.px(x, gy - 4, "#5a3a22", 8, 4)
        L.px(596, gy - 7, "#9aa7b8", 214, 3)
        vagon_gemas(L, 612, gy - 6)
        minero_con_gema(L, 700, gy)
        suelo_cierre(L, gy, W)
    return L.guardar(("movil/" if movil else "") + "cierre.svg", ALT_CIERRE)


# ================================================================== principal
def main():
    portada_escritorio()
    portada_movil()
    boton("btn-cv.svg", "Hoja de vida · PDF", "pdf", ROSA)
    boton("btn-correo.svg", "Correo", "correo", CIAN)
    for pr in PROYECTOS:
        tarjeta(**pr)
        tarjeta(**pr, movil=True)
    chip("chip-codigo.svg", "Código:", solo_texto=True)
    chip("chip-casa-rendon.svg", "Casa Rendón", ROSA, "codigo", "Código de Casa Rendón")
    chip("chip-numi.svg", "Numi", AMAR, "codigo", "Código de Numi")
    chip("chip-blackjack.svg", "BlackJack", ROSA, "codigo", "Código de BlackJack, proyecto en equipo")
    chip("chip-cinex.svg", "CineX", CIAN, "codigo", "Código del backend de CineX")
    chip("chip-ubicua.svg", "Computación Ubicua", GEMA, "pico", "Código de Computación Ubicua: robot y sensores")
    chip("chip-poo-java.svg", "POO en Java", GEMA, "pico", "Código de POO en Java")
    chip("chip-estructuras.svg", "Estructuras de datos", GEMA, "pico", "Código de estructuras de datos en Python")
    chip("chip-credenciales.svg", "Credenciales:", solo_texto=True)
    chip("chip-cred-fundamentals.svg", "Cloud Computing Fundamentals", AMAR, "insignia", "Credencial: Cloud Computing Fundamentals")
    chip("chip-cred-infra.svg", "Infrastructure in Google Cloud", AMAR, "insignia", "Credencial: Infrastructure in Google Cloud")
    chip("chip-cred-balancing.svg", "Cloud Load Balancing", AMAR, "insignia", "Credencial: Cloud Load Balancing")
    chip("chip-cred-appdev.svg", "App Dev Environment", AMAR, "insignia", "Credencial: App Dev Environment")
    trayectoria()
    trayectoria_movil()
    stack()
    stack_movil()
    cierre()
    cierre(movil=True)
    print("Imágenes generadas en", DEST)


if __name__ == "__main__":
    main()
