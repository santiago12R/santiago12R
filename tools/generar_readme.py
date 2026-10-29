"""Genera las imágenes SVG del README de santiago12R (escritorio y celular).

Uso:  python3 tools/generar_readme.py
Salida: assets/readme/*.svg y assets/readme/movil/*.svg

Estilo minimalista sobre el negro de GitHub (#0d1117): tipografía sans-serif ligera, bordes finos,
paleta corta y un solo toque de pixel art (el minero y su vagón).
"""
import os
from xml.sax.saxutils import escape

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(RAIZ, "assets", "readme")

# ------------------------------------------------------------------ paleta (pensada para fondo negro)
FONDO = "#0d1117"      # igual al modo oscuro de GitHub
SUPERFICIE = "#11161d"
BORDE = "#262c36"
LINEA = "#1b212a"
TEXTO = "#e6edf3"      # texto principal
SUAVE = "#9aa4b1"      # texto secundario
TENUE = "#6b7480"      # etiquetas
ACENTO = "#7cc4fa"     # azul claro
VERDE = "#4ac26b"
AMBAR = "#e3b341"
ROSA = "#f0a1c2"
FUENTE = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
P = 4


def esc(t):
    return escape(t, {'"': "&quot;"})


def ancho(t, size, peso=400):
    return len(t) * size * (0.58 if peso >= 600 else 0.54)


def partir(texto, n):
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


class Lienzo:
    def __init__(self, w, h, titulo, fondo=True, radio=12):
        self.w, self.h, self.titulo = w, h, titulo
        self.css = ""
        self.defs = ""
        self.o = []
        if fondo:
            self.add(f'<rect width="{w}" height="{h}" rx="{radio}" fill="{FONDO}"/>')

    def add(self, s):
        self.o.append(s)

    def px(self, x, y, c, w=P, h=P, extra=""):
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"{extra}/>')

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

    def texto(self, x, y, t, size=14, color=TEXTO, peso=400, anchor="start", extra=""):
        self.add(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{peso}" fill="{color}" '
                 f'text-anchor="{anchor}"{extra}>{esc(t)}</text>')

    def caja(self, x, y, w, h, r=10, fill=FONDO, borde=BORDE):
        self.add(f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="{r}" fill="{fill}" stroke="{borde}"/>')

    def titulo_seccion(self, x, y, t):
        self.texto(x, y, t, 20, TEXTO, 600)

    def guardar(self, nombre, alt=None):
        cab = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
               f'role="img" aria-label="{esc(alt or self.titulo)}" font-family="{FUENTE}"><title>{esc(self.titulo)}</title>'
               f'<defs>{self.defs}<style>text{{font-family:{FUENTE}}}{self.css}</style></defs>')
        ruta = os.path.join(DEST, nombre)
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(cab + "\n".join(self.o) + "</svg>\n")


# ================================================================== pixel art: minero y bloque
PIEDRA = ["#5d616c", "#525661", "#686c77", "#4a4e58"]
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
HAZ = ('<linearGradient id="haz" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff6b0" stop-opacity=".35"/>'
       '<stop offset="1" stop-color="#fff6b0" stop-opacity="0"/></linearGradient>')


def css_minero(sx, cx, cy, bx, by):
    return f"""
.arm{sx}{{transform-origin:{cx}px {cy}px;animation:swing{sx} 1.4s infinite}}
@keyframes swing{sx}{{0%{{transform:rotate(-78deg);animation-timing-function:ease-out}}48%{{transform:rotate(-88deg);animation-timing-function:cubic-bezier(.6,0,1,.6)}}62%{{transform:rotate(13deg);animation-timing-function:ease-out}}72%{{transform:rotate(9deg)}}100%{{transform:rotate(-78deg)}}}}
.ore{sx}{{transform-origin:{bx + 20}px {by + 20}px;animation:shake 1.4s infinite}}
@keyframes shake{{0%,61%{{transform:translate(0,0)}}63%{{transform:translate(3px,-1px)}}66%{{transform:translate(-2px,1px)}}72%,100%{{transform:translate(0,0)}}}}
.pt{{opacity:0;animation:pt 1.4s infinite}}
@keyframes pt{{0%,61%{{opacity:0;transform:translate(0,0)}}62%{{opacity:1;transform:translate(0,0)}}92%,100%{{opacity:0;transform:translate(var(--dx),var(--dy))}}}}
@media (prefers-reduced-motion:reduce){{.arm{sx},.ore{sx},.pt{{animation:none}}.pt{{opacity:0}}}}
"""


def minero(L, mx, gy, sx):
    """Minero que pica un bloque de mineral; mx = x del minero, gy = línea del suelo."""
    my = gy - 84
    cx, cy = mx + 34, gy - 46
    bx, by = mx + 90, gy - 40
    # bloque
    L.add(f'<g class="ore{sx}">')
    tono = 0
    for r in range(10):
        for c in range(10):
            L.px(bx + c * P, by + r * P, PIEDRA[(r * 3 + c * 7 + tono) % 4])
    L.px(bx, by, "#7a7e89", 40, 4)
    L.px(bx + 36, by, "#3c404a", 4, 40)
    L.px(bx, by + 36, "#3c404a", 40, 4)
    for dx, dy in [(8, 8), (12, 8), (8, 12), (24, 12), (28, 16), (24, 16), (12, 24), (16, 28), (28, 28)]:
        L.px(bx + dx, by + dy, "#5ee6e0")
    L.add('</g>')
    for dx, dy, col in [(-14, -26, "#9aa4b1"), (6, -32, "#5ee6e0"), (18, -20, "#7a7e89"), (-22, -12, "#c8fffb"), (-4, -36, "#686c77")]:
        L.add(f'<rect class="pt" x="{bx + 4}" y="{by + 10}" width="4" height="4" fill="{col}" style="--dx:{dx}px;--dy:{dy}px"/>')
    # minero y luz del casco
    L.add(f'<polygon points="{mx + 44},{my + 6} {mx + 140},{my - 12} {mx + 140},{my + 34}" fill="url(#haz)"/>')
    L.sprite(mx, my, MINERO, PAL_MINERO)
    # brazo y pico
    L.add(f'<g class="arm{sx}">')
    L.px(cx - 2, cy - 4, "#3b4256", 16, 8)
    L.px(cx + 14, cy - 5, "#8a6a4a", 8, 10)
    L.px(cx + 10, cy - 2, "#8b5a2b", 64, 5)
    L.px(cx + 10, cy - 2, "#b07a43", 64, 1)
    for gx in range(cx + 24, cx + 40, 4):
        L.px(gx, cy - 3, "#3a2418", 2, 7)
    L.px(cx + 66, cy - 5, "#5b6678", 8, 11)
    for dy in range(-34, 35, 4):
        t = dy / 36
        x0 = cx + 64 + int(round(12 * (1 - t * t)))
        w = 8 if abs(dy) < 26 else 4
        L.px(x0, cy + dy - 2, "#9aa7b8", w, 4)
        L.px(x0 + w - 2, cy + dy - 2, "#e6ecf5", 2, 4)
        L.px(x0, cy + dy - 2, "#5b6678", 2, 4)
    L.add('</g>')
    # suelo mínimo: una línea fina con unas briznas de pasto
    L.add(f'<rect x="{mx - 60}" y="{gy}" width="{220}" height="1" fill="{BORDE}"/>')
    for gx in range(mx - 52, mx + 156, 20):
        L.px(gx, gy - 3, "#2f6b3e", 2, 3)
    L.css += css_minero(sx, cx, cy, bx, by)


# ================================================================== portada
ALT_PORTADA = ("Santiago Rodríguez Jiménez, estudiante de Ingeniería de Software (7.º semestre) en la Universidad "
               "Cooperativa de Colombia, Medellín. Full stack y analítica de datos. Disponible para práctica empresarial.")


def pastilla(L, x, y, t, color, size=12):
    w = ancho(t, size, 500) + 30
    L.add(f'<rect x="{x + .5}" y="{y + .5}" width="{w}" height="25" rx="12.5" fill="none" stroke="{color}" stroke-opacity=".5"/>')
    L.add(f'<circle cx="{x + 13}" cy="{y + 13}" r="3.5" fill="{color}"><animate attributeName="opacity" values="1;.35;1" dur="2s" repeatCount="indefinite"/></circle>')
    L.texto(x + 23, y + 17, t, size, color, 500)
    return w


def portada():
    L = Lienzo(1000, 290, "Santiago Rodríguez Jiménez")
    L.defs = HAZ
    pastilla(L, 48, 50, "Disponible para práctica empresarial", VERDE)
    L.texto(48, 128, "Santiago Rodríguez Jiménez", 40, TEXTO, 600, extra=' letter-spacing="-.5"')
    L.texto(48, 166, "Ingeniería de Software · 7.º semestre", 18, SUAVE)
    L.texto(48, 192, "Universidad Cooperativa de Colombia · Medellín", 18, SUAVE)
    L.texto(48, 234, "Full stack · Analítica de datos", 18, ACENTO, 500)
    minero(L, 760, 236, "d")
    L.guardar("portada.svg", ALT_PORTADA)

    M = Lienzo(400, 400, "Santiago Rodríguez Jiménez")
    M.defs = HAZ
    minero(M, 130, 150, "m")
    pastilla(M, 28, 186, "Disponible para práctica", VERDE)
    M.texto(28, 254, "Santiago", 32, TEXTO, 600)
    M.texto(28, 292, "Rodríguez Jiménez", 32, TEXTO, 600)
    M.texto(28, 326, "Ingeniería de Software · 7.º semestre", 14, SUAVE)
    M.texto(28, 348, "U. Cooperativa de Colombia · Medellín", 14, SUAVE)
    M.texto(28, 376, "Full stack · Analítica de datos", 14, ACENTO, 500)
    M.guardar("movil/portada.svg", ALT_PORTADA)


# ================================================================== botones y chips
def icono(L, tipo, x, y, color):
    if tipo == "doc":
        L.add(f'<path d="M{x} {y}h8l4 4v12h-12z M{x + 8} {y}v4h4 M{x + 3} {y + 9}h6 M{x + 3} {y + 12}h6" fill="none" stroke="{color}" stroke-width="1.4" stroke-linejoin="round"/>')
    elif tipo == "correo":
        L.add(f'<path d="M{x} {y + 2}h15v11h-15z M{x} {y + 2}l7.5 6l7.5-6" fill="none" stroke="{color}" stroke-width="1.4" stroke-linejoin="round"/>')
    elif tipo == "codigo":
        L.add(f'<path d="M{x + 4} {y + 2}l-4 5l4 5 M{x + 10} {y + 2}l4 5l-4 5" fill="none" stroke="{color}" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>')
    elif tipo == "insignia":
        L.add(f'<circle cx="{x + 6}" cy="{y + 5}" r="4.5" fill="none" stroke="{color}" stroke-width="1.4"/>'
              f'<path d="M{x + 3} {y + 9}l-1 5l4-2l4 2l-1-5" fill="none" stroke="{color}" stroke-width="1.4" stroke-linejoin="round"/>')


def boton(nombre, etiqueta, tipo, color):
    w = int(ancho(etiqueta, 15, 500)) + 62
    L = Lienzo(w, 44, etiqueta, fondo=False)
    L.caja(0, 0, w, 44, 22, SUPERFICIE, BORDE)
    icono(L, tipo, 22, 14, color)
    L.texto(46, 27, etiqueta, 15, TEXTO, 500)
    L.guardar(nombre, etiqueta)


def chip(nombre, etiqueta, tipo="codigo", alt=None, color=ACENTO, rotulo=False):
    if rotulo:
        w = int(ancho(etiqueta, 13, 500)) + 12
        L = Lienzo(w, 32, etiqueta, fondo=False)
        L.texto(w - 4, 21, etiqueta, 13, TENUE, 500, "end")
    else:
        w = int(ancho(etiqueta, 13, 500)) + 50
        L = Lienzo(w, 32, etiqueta, fondo=False)
        L.caja(0, 0, w, 32, 16, FONDO, BORDE)
        icono(L, tipo, 16, 9, color)
        L.texto(38, 21, etiqueta, 13, "#c9d1d9", 500)
    L.guardar(nombre, alt or etiqueta)


# ================================================================== tarjetas de proyecto
COLOR_ESTADO = {"Cliente real": VERDE, "En vivo": VERDE, "En desarrollo": AMBAR, "Académico": ACENTO}


def tarjeta(nombre, titulo, estados, meta, desc, cifra_n, cifra_txt, rol, stack, movil=False):
    W, H = (400, 350) if movil else (490, 316)
    fs = 14
    cols = int((W - 56) / (fs * 0.54))
    alt = f"{titulo}, {', '.join(e.lower() for e in estados)}: {desc} {cifra_n} {cifra_txt}. Mi rol: {rol}"
    L = Lienzo(W, H, f"{titulo}: {desc}", fondo=False)
    L.caja(0, 0, W, H, 14, FONDO, BORDE)
    x = 28
    for e in estados:
        c = COLOR_ESTADO[e]
        L.add(f'<circle cx="{x + 4}" cy="38" r="3.5" fill="{c}"/>')
        L.texto(x + 13, 42, e, 12, c, 500)
        x += ancho(e, 12, 500) + 30
    L.texto(W - 28, 42, meta, 12, TENUE, 400, "end")
    L.texto(28, 84, titulo, 24, TEXTO, 600, extra=' letter-spacing="-.3"')
    y = 112
    for ln in partir(desc, cols):
        L.texto(28, y, ln, fs, SUAVE)
        y += 21
    y += 22
    L.texto(28, y + 10, cifra_n, 32, TEXTO, 600)
    xn = 28 + ancho(cifra_n, 32, 600) + 12
    yy = y - 4
    for ln in partir(cifra_txt, int((W - xn - 28) / (13 * 0.54))):
        L.texto(xn, yy + 6, ln, 13, SUAVE)
        yy += 18
    y = max(y + 44, yy + 22)
    for i, ln in enumerate(partir("Mi rol: " + rol, cols)):
        if i == 0:
            L.add(f'<text x="28" y="{y}" font-size="{fs}" fill="{SUAVE}"><tspan fill="{TEXTO}" font-weight="600">Mi rol:</tspan>{esc(ln[7:])}</text>')
        else:
            L.texto(28, y, ln, fs, SUAVE)
        y += 21
    L.add(f'<rect x="28" y="{H - 52}" width="{W - 56}" height="1" fill="{LINEA}"/>')
    L.texto(28, H - 26, "  ·  ".join(stack), 12, ACENTO, 500)
    L.guardar(("movil/" if movil else "") + f"proyecto-{nombre}.svg", alt)


PROYECTOS = [
    dict(nombre="casa-rendon", titulo="Casa Rendón", estados=["Cliente real", "En vivo"], meta="2026 · equipo",
         desc="Sitio web de una marca familiar de café y vino de Andes, Antioquia: historia, catálogo y reservas.",
         cifra_n="7", cifra_txt="secciones; reservas y reseñas llegan a WhatsApp",
         rol="HTML, CSS, JavaScript y componentes en React.", stack=["HTML", "CSS", "JavaScript", "React"]),
    dict(nombre="numi", titulo="Numi", estados=["En desarrollo"], meta="2026 · equipo de 4",
         desc="App educativa en Flutter para niños de 1.° a 5.° de primaria en zonas rurales de Medellín, sin internet.",
         cifra_n="15", cifra_txt="actividades en 5 materias, con asistente de IA offline",
         rol="pantallas de la app y diseño responsive.", stack=["Flutter", "Dart"]),
    dict(nombre="blackjack", titulo="BlackJack Royale", estados=["En vivo"], meta="2025 · equipo",
         desc="Casino web con BlackJack contra la máquina, multijugador en tiempo real y banco de fichas.",
         cifra_n="6", cifra_txt="módulos de JavaScript y un servidor de WebSockets",
         rol="front-end en HTML, CSS y JavaScript, y servidor en Python.", stack=["HTML", "CSS", "JavaScript", "Python"]),
    dict(nombre="cinex", titulo="CineX", estados=["Académico"], meta="2025 · equipo",
         desc="Sistema para gestionar un cine: películas, salas, funciones y reservas.",
         cifra_n="8", cifra_txt="clases de servicio sobre 4 entidades de la API REST",
         rol="capa de servicios con la lógica de negocio.", stack=["Java", "Spring Boot", "MySQL", "Bootstrap"]),
]


# ================================================================== trayectoria: vía y vagón
HITOS = [
    ("2023", ["Ingeniería de Software", "U. Cooperativa"], True),
    ("2024", ["Estructuras de datos", "en Python"], True),
    ("2025", ["BlackJack · CineX", "Computación Ubicua"], True),
    ("2026", ["Numi · Casa Rendón", "cliente real"], True),
    ("Sigue", ["Práctica empresarial", ""], False),
    ("2027", ["Fin de la carrera", "previsto"], False),
]
ALT_TRAY = ("Trayectoria: 2023 ingreso a Ingeniería de Software en la Universidad Cooperativa; 2024 estructuras de datos en "
            "Python; 2025 BlackJack, CineX y Computación Ubicua; 2026 Numi y Casa Rendón con cliente real. "
            "Siguiente: práctica empresarial. 2027: fin de la carrera, previsto.")
VAGON = [
    "SSSSSSSSSSSSSSSS",
    "sGGGGGGGGGGGGGGs",
    "sGRGGGGGGGGGGRGs",
    "sGGGgggggggggGGs",
    ".sGGGGGGGGGGGGs.",
    "..ssssssssssss..",
]
PAL_VAGON = {"S": "#c9d1d9", "s": "#3d4450", "G": "#6e7681", "g": "#5c636e", "R": "#e6edf3"}
RUEDA_A, RUEDA_B = ["KKK", "KWK", "KKK"], ["KWK", "WKW", "KWK"]
PAL_RUEDA = {"K": "#262c36", "W": "#9aa4b1"}
MOVER, PARAR = 1.1, 1.5


def css_viaje(n, eje, paso):
    total = n * (MOVER + PARAR) + 0.8
    marcas, t = [], 0.0
    for i in range(n):
        if i:
            t += MOVER
        marcas.append((t / total, (t + PARAR) / total))
        t += PARAR
    tr = (lambda d: f"translate({d}px,0)") if eje == "x" else (lambda d: f"translate(0,{d}px)")
    k = []
    for i, (a, b) in enumerate(marcas):
        k += [f"{a * 100:.2f}%{{transform:{tr(i * paso)};opacity:1}}", f"{b * 100:.2f}%{{transform:{tr(i * paso)};opacity:1}}"]
    k += [f"{min(99.5, marcas[-1][1] * 100 + 3):.2f}%{{transform:{tr((n - 1) * paso)};opacity:0}}", "100%{transform:translate(0,0);opacity:0}"]
    css = f".viaje{{animation:viaje {total:.1f}s linear infinite}}@keyframes viaje{{{''.join(k)}}}"
    for i, (a, b) in enumerate(marcas):
        css += (f".luz{i}{{opacity:0;animation:luz{i} {total:.1f}s steps(1) infinite}}"
                f"@keyframes luz{i}{{0%{{opacity:0}}{a * 100:.2f}%{{opacity:1}}{b * 100:.2f}%{{opacity:0}}100%{{opacity:0}}}}")
    css += (".rA{animation:rA .3s steps(1) infinite}.rB{animation:rB .3s steps(1) infinite}"
            "@keyframes rA{0%{opacity:1}50%{opacity:0}}@keyframes rB{0%{opacity:0}50%{opacity:1}}"
            ".saludo{transform-box:fill-box;transform-origin:50% 100%;animation:sal 1s ease-in-out infinite}"
            "@keyframes sal{0%,100%{transform:rotate(-12deg)}50%{transform:rotate(18deg)}}"
            "@media (prefers-reduced-motion:reduce){.viaje,.saludo,.rA,.rB{animation:none}"
            + ",".join(f".luz{i}" for i in range(n)) + "{animation:none;opacity:0}}")
    return css


def trayectoria():
    W, H = 1000, 262
    L = Lienzo(W, H, "Trayectoria")
    L.titulo_seccion(48, 52, "Trayectoria")
    x0, x1, riel = 110, 890, 178
    paso = round((x1 - x0) / (len(HITOS) - 1), 2)
    L.css = css_viaje(len(HITOS), "x", paso)
    for x in range(40, W - 40, 14):
        L.px(x, riel + 2, LINEA, 6, 5)
    L.add(f'<rect x="40" y="{riel - 1}" width="{W - 80}" height="2" fill="#3d4450"/>')
    for i, (anio, lineas, hecho) in enumerate(HITOS):
        x = x0 + i * paso
        color = ACENTO if hecho else TENUE
        L.add(f'<circle class="luz{i}" cx="{x}" cy="{riel}" r="11" fill="{ACENTO}" opacity="0" fill-opacity=".25"/>')
        if hecho:
            L.add(f'<circle cx="{x}" cy="{riel}" r="5" fill="{ACENTO}"/>')
        else:
            L.add(f'<circle cx="{x}" cy="{riel}" r="4.5" fill="{FONDO}" stroke="{TENUE}" stroke-dasharray="2 2"/>')
        L.texto(x, 96, anio, 13, color, 600, "middle")
        L.texto(x, riel + 38, lineas[0], 13, TEXTO if hecho else SUAVE, 500, "middle")
        if lineas[1]:
            L.texto(x, riel + 58, lineas[1], 12, TENUE, 400, "middle")
    # vagón con el minero
    xv, yv = x0 - 32, riel - 30
    L.add('<g class="viaje">')
    L.sprite(xv + 6, yv - 38, MINERO[:10], PAL_MINERO)
    L.add(f'<g class="saludo"><rect x="{xv + 46}" y="{yv - 14}" width="6" height="16" fill="#3b4256"/>'
          f'<rect x="{xv + 45}" y="{yv - 21}" width="8" height="8" fill="#8a6a4a"/></g>')
    L.sprite(xv, yv, VAGON, PAL_VAGON)
    for wx in (xv + 8, xv + 44):
        L.add('<g class="rA">')
        L.sprite(wx, riel - 9, RUEDA_A, PAL_RUEDA)
        L.add('</g><g class="rB">')
        L.sprite(wx, riel - 9, RUEDA_B, PAL_RUEDA)
        L.add('</g>')
    L.add('</g>')
    L.guardar("trayectoria.svg", ALT_TRAY)

    paso_m, y0 = 72, 104
    H = y0 + paso_m * (len(HITOS) - 1) + 50
    M = Lienzo(400, H, "Trayectoria")
    M.titulo_seccion(28, 48, "Trayectoria")
    M.css = css_viaje(len(HITOS), "y", paso_m)
    for y in range(80, H - 20, 12):
        M.px(36, y, LINEA, 24, 4)
    for rx in (40, 54):
        M.add(f'<rect x="{rx}" y="78" width="2" height="{H - 100}" fill="#3d4450"/>')
    for i, (anio, lineas, hecho) in enumerate(HITOS):
        y = y0 + i * paso_m
        M.add(f'<rect class="luz{i}" x="76" y="{y - 22}" width="300" height="52" rx="10" fill="{ACENTO}" opacity="0" fill-opacity=".1"/>')
        M.texto(88, y + 2, anio, 14, ACENTO if hecho else TENUE, 600)
        M.texto(150, y + 2, lineas[0], 14, TEXTO if hecho else SUAVE, 500)
        if lineas[1]:
            M.texto(150, y + 21, lineas[1], 12, TENUE)
    cx, cy = 48, y0 - 4
    M.add('<g class="viaje">')
    M.add(f'<rect x="{cx - 15}" y="{cy - 17}" width="30" height="34" rx="3" fill="#6e7681" stroke="#c9d1d9" stroke-width="2"/>')
    M.px(cx - 10, cy - 2, "#ff8a3d", 20, 10)
    M.px(cx - 7, cy - 11, "#f2c230", 14, 12)
    M.px(cx - 3, cy - 11, "#fff6b0", 6, 3)
    M.add('</g>')
    M.guardar("movil/trayectoria.svg", ALT_TRAY)


# ================================================================== stack
STACK = [
    ("HTML y CSS", "Estructura y estilos", "Casa Rendón · BlackJack"),
    ("JavaScript", "Lógica en el navegador", "Casa Rendón · BlackJack"),
    ("React", "Componentes de interfaz", "Casa Rendón"),
    ("Bootstrap", "Diseño responsive", "CineX (frontend)"),
    ("Flutter y Dart", "Apps móviles", "Numi"),
    ("Java", "Programación orientada a objetos", "CineX · POO en Java"),
    ("Spring Boot", "APIs REST", "CineX"),
    ("Python", "Servidores y scripts", "BlackJack · Estructuras"),
    ("MySQL", "Base de datos relacional", "CineX"),
    ("Git y GitHub", "Trabajo en equipo", "Todos los proyectos"),
    ("VS Code", "Editor", "Todos los proyectos"),
    ("Postman", "Probar APIs", "Académico"),
    ("Docker", "Contenedores", "Académico"),
]
ALT_STACK = "Stack: " + "; ".join(f"{n}, {u}, {p.lower() if p == 'Académico' else 'en ' + p}" for n, u, p in STACK) + "."


def etiqueta_academico(L, x, y):
    w = ancho("Académico", 11, 500) + 16
    L.add(f'<rect x="{x + .5}" y="{y - 13.5}" width="{w}" height="19" rx="9.5" fill="none" stroke="{TENUE}"/>')
    L.texto(x + 8, y, "Académico", 11, SUAVE, 500)


def stack():
    fila = 38
    H = 112 + len(STACK) * fila + 20
    L = Lienzo(1000, H, "Stack")
    L.titulo_seccion(48, 52, "Stack")
    for x, t in [(48, "Herramienta"), (300, "Para qué la uso"), (640, "Dónde la usé")]:
        L.texto(x, 96, t, 12, TENUE, 500)
    for i, (n, u, p) in enumerate(STACK):
        y = 112 + i * fila
        L.add(f'<rect x="48" y="{y}" width="904" height="1" fill="{LINEA}"/>')
        L.texto(48, y + 25, n, 14, TEXTO, 600)
        L.texto(300, y + 25, u, 14, SUAVE)
        if p == "Académico":
            etiqueta_academico(L, 640, y + 24)
        else:
            L.texto(640, y + 25, p, 14, ACENTO)
    L.guardar("stack.svg", ALT_STACK)

    fila = 58
    H = 80 + len(STACK) * fila + 16
    M = Lienzo(400, H, "Stack")
    M.titulo_seccion(28, 48, "Stack")
    for i, (n, u, p) in enumerate(STACK):
        y = 72 + i * fila
        M.add(f'<rect x="28" y="{y}" width="344" height="1" fill="{LINEA}"/>')
        M.texto(28, y + 24, n, 14, TEXTO, 600)
        M.texto(28, y + 44, u, 13, SUAVE)
        if p == "Académico":
            etiqueta_academico(M, 372 - ancho("Académico", 11, 500) - 16, y + 24)
        else:
            M.texto(372, y + 24, p, 12, ACENTO, 400, "end")
    M.guardar("movil/stack.svg", ALT_STACK)


# ================================================================== cierre
ALT_CIERRE = ("¿Tu equipo necesita un practicante? Full stack o analítica de datos, disponible para práctica empresarial. "
              "Escríbeme: santiago.rodriguezj12@gmail.com")
CORREO = "santiago.rodriguezj12@gmail.com"


def cierre():
    L = Lienzo(1000, 170, "Contacto")
    L.texto(48, 68, "¿Tu equipo necesita un practicante?", 26, TEXTO, 600, extra=' letter-spacing="-.3"')
    L.texto(48, 100, "Full stack o analítica de datos. Disponible para práctica empresarial.", 15, SUAVE)
    icono(L, "correo", 48, 120, ACENTO)
    L.texto(74, 133, CORREO, 15, ACENTO, 500)
    L.add(f'<rect x="74" y="139" width="{ancho(CORREO, 15, 500):.0f}" height="1" fill="{ACENTO}" opacity=".5"/>')
    L.guardar("cierre.svg", ALT_CIERRE)

    M = Lienzo(400, 200, "Contacto")
    M.texto(28, 56, "¿Tu equipo necesita", 22, TEXTO, 600)
    M.texto(28, 86, "un practicante?", 22, TEXTO, 600)
    M.texto(28, 116, "Full stack o analítica de datos.", 14, SUAVE)
    M.texto(28, 136, "Disponible para práctica empresarial.", 14, SUAVE)
    icono(M, "correo", 28, 156, ACENTO)
    M.texto(52, 169, CORREO, 14, ACENTO, 500)
    M.guardar("movil/cierre.svg", ALT_CIERRE)


# ================================================================== principal
def main():
    portada()
    boton("btn-cv.svg", "Hoja de vida (PDF)", "doc", ROSA)
    boton("btn-correo.svg", "Correo", "correo", ACENTO)
    for pr in PROYECTOS:
        tarjeta(**pr)
        tarjeta(**pr, movil=True)
    chip("chip-codigo.svg", "Código", rotulo=True)
    chip("chip-casa-rendon.svg", "Casa Rendón", alt="Código de Casa Rendón")
    chip("chip-numi.svg", "Numi", alt="Código de Numi")
    chip("chip-blackjack.svg", "BlackJack", alt="Código de BlackJack, proyecto en equipo")
    chip("chip-cinex.svg", "CineX", alt="Código del backend de CineX")
    chip("chip-ubicua.svg", "Computación Ubicua", alt="Código de Computación Ubicua: robot y sensores")
    chip("chip-poo-java.svg", "POO en Java", alt="Código de POO en Java")
    chip("chip-estructuras.svg", "Estructuras de datos", alt="Código de estructuras de datos en Python")
    chip("chip-credenciales.svg", "Credenciales", rotulo=True)
    for n, t in [("fundamentals", "Cloud Computing Fundamentals"), ("infra", "Infrastructure in Google Cloud"),
                 ("balancing", "Cloud Load Balancing"), ("appdev", "App Dev Environment")]:
        chip(f"chip-cred-{n}.svg", t, "insignia", f"Credencial: {t}", AMBAR)
    trayectoria()
    stack()
    cierre()
    print("Imágenes generadas en", DEST)


if __name__ == "__main__":
    main()
