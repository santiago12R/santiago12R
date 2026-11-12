"""Genera el banner de LinkedIn (1584x396) con el mismo estilo pixel del README.

Uso: python3 tools/banner_linkedin.py  ->  assets/linkedin/banner.svg
Para LinkedIn hay que subir un PNG: rsvg-convert assets/linkedin/banner.svg -o banner.png
"""
import os

import generar_readme as g

W, H, GY = 1584, 396, 340


def banner():
    L = g.Lienzo(W, H, "Santiago Rodriguez Jimenez — Ingeniería de Software · Full Stack y Datos")
    # sin estrellas sobre el texto ni donde LinkedIn pone la foto (abajo a la izquierda)
    L.fondo(46, 5, evitar=[(520, 60, 1250, 290), (0, 200, 420, H)])
    g.nubes(L, [(140, 30), (430, 54), (900, 26), (1180, 300 - 250)])
    g.luna(L, 1500, 30)
    L.add('<g transform="translate(40,10)">' + open(os.path.join(g.HERE, "s_letra.svgfrag")).read() + "</g>")
    x = 560
    L.texto(x, 128, "Santiago Rodriguez Jimenez", 46, g.CREMA, 700, extra=' letter-spacing="-1"')
    L.px(x, 142, g.ROSA, 692, 4)
    L.texto(x, 182, "Ingeniería de Software · Full Stack & Datos", 25, g.ROSA, 500)
    L.texto(x, 224, "> Java · Spring Boot · Python · React · Flutter", 19, g.CIAN, 400)
    L.texto(x, 254, "> Disponible para práctica empresarial · Medellín", 19, g.CIAN, 400)
    L.texto(x, 290, "github.com/santiago12R", 17, g.GRIS, 700)
    g.suelo(L, GY, W)
    L.css = g.escena_minero(L, 1360, GY, "d")
    L.o.insert(0, f"<defs>{g.BEAM}</defs>")
    g.DEST = os.path.join(g.RAIZ, "assets", "linkedin")
    return L.guardar("banner.svg", "Banner de LinkedIn de Santiago Rodriguez Jimenez")


if __name__ == "__main__":
    print(banner())
