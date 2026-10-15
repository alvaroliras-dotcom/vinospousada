"""Bodegón de la cabecera de /licores/ (15/10/2026): las seis garrafas Pousada con alfa (recursos/producto/) en fila
escalonada sobre FONDO BLANCO de estudio. Va en blanco a propósito (Álvaro, 15/10/2026): los recortes de las garrafas
traen blanco dentro de las asas y en la base; sobre un fondo oscuro se veían como parches, sobre blanco desaparecen.
Solo lleva una sombra de contacto gris suave bajo cada garrafa. Sale recursos/fotos/licores-gallegos-bodegon-garrafas.jpg.
Uso: python3 herramientas/bodegon_licores.py"""
import pathlib
from PIL import Image, ImageDraw, ImageFilter

R = pathlib.Path(__file__).resolve().parent.parent / "recursos"
SAL = R / "fotos" / "licores-gallegos-bodegon-garrafas.jpg"
W, H = 1800, 900
BLANCO = (255, 255, 255)


def garrafa(nombre):
    im = Image.open(R / "producto" / f"{nombre}-garrafa-3-litros.png").convert("RGBA")
    return im.crop(im.getbbox())


def colocar(lienzo, im, cx, base_y, alto):
    k = alto / im.height
    im = im.resize((int(im.width * k), int(alto)), Image.LANCZOS)
    x, y = int(cx - im.width / 2), int(base_y - im.height)
    # sombra de contacto: elipse gris muy difuminada bajo la base (nunca negra: el fondo sigue siendo blanco)
    s = Image.new("L", lienzo.size, 0)
    ImageDraw.Draw(s).ellipse((x + im.width * 0.06, base_y - 18, x + im.width * 0.94, base_y + 16), fill=150)
    s = s.filter(ImageFilter.GaussianBlur(18))
    lienzo.paste(Image.new("RGB", lienzo.size, (150, 146, 138)), (0, 0), s)
    lienzo.paste(im, (x, y), im)


def main():
    lienzo = Image.new("RGB", (W, H), BLANCO)
    # fila escalonada: las de atrás un poco más pequeñas y más altas, alternando claro y oscuro
    orden = [("orujo-blanco-gallego", 0), ("pacharan-gallego", 1), ("crema-de-orujo-gallega", 0),
             ("licor-de-cafe-gallego", 1), ("limoncino-licor-de-limon-gallego", 0), ("aguardiente-de-hierbas-gallego", 1)]
    paso = W * 0.152
    xs = [W / 2 + (i - 2.5) * paso for i in range(6)]
    base_delante, base_atras = int(H * 0.93), int(H * 0.83)
    for (n, atras), cx in zip(orden, xs):
        if atras:
            colocar(lienzo, garrafa(n), cx, base_atras, 580)
    for (n, atras), cx in zip(orden, xs):
        if not atras:
            colocar(lienzo, garrafa(n), cx, base_delante, 660)
    lienzo.save(SAL, quality=90, optimize=True, progressive=True)
    print("hecho", SAL, lienzo.size)


if __name__ == "__main__":
    main()
