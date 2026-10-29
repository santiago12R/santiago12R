"""Fuente JetBrains Mono (licencia OFL, ver fuentes/LICENSE-JetBrainsMono.txt) incrustada en los SVG.

Las imágenes del README no pueden cargar fuentes externas, así que se incrusta un subconjunto pequeño
(solo los caracteres que se usan) en pesos 400, 500 y 700.
"""
import base64
import os

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fuentes")
FUENTE = "'JetBrains Mono','Cascadia Mono',Consolas,'Liberation Mono',monospace"


def font_face():
    css = ""
    for peso in (400, 500, 700):
        with open(os.path.join(_DIR, f"jbmono-{peso}.woff2"), "rb") as f:
            datos = base64.b64encode(f.read()).decode()
        css += (f"@font-face{{font-family:'JetBrains Mono';font-weight:{peso};font-style:normal;"
                f"src:url(data:font/woff2;base64,{datos}) format('woff2')}}")
    return css
