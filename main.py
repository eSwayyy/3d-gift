"""Visor 3D para Pygbag: rotación táctil sin botones en pantalla."""

import asyncio
import math
import os

import pygame


W, H = 600, 600
FPS = 60
NEAR = 0.1
COLOR = (0, 143, 57)

# Arrastrar de un extremo al otro de la pantalla gira aprox. 225 grados.
SENSIBILIDAD_TACTIL = math.pi * 1.25


def cargar_figuras():
    carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
    figuras = []

    for nombre in sorted(os.listdir(carpeta)):
        if not nombre.lower().endswith(".txt"):
            continue

        vertices = []
        aristas = []
        color = COLOR

        with open(os.path.join(carpeta, nombre), encoding="utf-8") as archivo:
            for linea in archivo:
                datos = linea.split()
                if not datos:
                    continue
                if datos[0] == "c":
                    color = tuple(map(int, datos[1:4]))
                elif datos[0] == "v":
                    vertices.append(tuple(map(float, datos[1:4])))
                elif datos[0] == "e":
                    aristas.append(tuple(map(int, datos[1:3])))

        figuras.append((vertices, aristas, color))

    return figuras


figuras = cargar_figuras()

pygame.init()
ventana = pygame.display.set_mode((W, H))
pygame.display.set_caption("3D desde cero")
reloj = pygame.time.Clock()


def a_pantalla(p):
    return ((p[0] + 1) * W / 2, (1 - p[1]) * H / 2)


def proyectar(p):
    return (p[0] / p[2], p[1] / p[2])


def trasladar(p, dx, dy, dz):
    return (p[0] + dx, p[1] + dy, p[2] + dz)


def rotar(p, angulo_xz, angulo_yz):
    c = math.cos(angulo_xz)
    s = math.sin(angulo_xz)
    p = (p[0] * c - p[2] * s, p[1], p[0] * s + p[2] * c)

    c = math.cos(angulo_yz)
    s = math.sin(angulo_yz)
    return (p[0], p[1] * c - p[2] * s, p[1] * s + p[2] * c)


def rotacion_auto(i, angulo_xz, angulo_yz, dt):
    paso = math.pi / 2 * dt
    if i % 4 == 1:
        return angulo_xz + paso, angulo_yz
    if i % 4 == 2:
        return angulo_xz, angulo_yz + paso
    if i % 4 == 3:
        return angulo_xz + paso, angulo_yz + paso
    return angulo_xz, angulo_yz


def punto(p, color=COLOR, tamaño=5):
    if p[2] < NEAR:
        return
    x, y = a_pantalla(proyectar(p))
    pygame.draw.rect(
        ventana, color, (int(x - tamaño / 2), int(y - tamaño / 2), tamaño, tamaño)
    )


def linea(p1, p2, color=COLOR):
    if p1[2] < NEAR and p2[2] < NEAR:
        return
    if p1[2] < NEAR:
        t = (NEAR - p1[2]) / (p2[2] - p1[2])
        p1 = tuple(p1[k] + t * (p2[k] - p1[k]) for k in range(3))
    if p2[2] < NEAR:
        t = (NEAR - p2[2]) / (p1[2] - p2[2])
        p2 = tuple(p2[k] + t * (p1[k] - p2[k]) for k in range(3))
    pygame.draw.line(
        ventana, color, a_pantalla(proyectar(p1)), a_pantalla(proyectar(p2)), 2
    )


async def main():
    dx, dy, dz = 0.0, 0.0, 0.5
    angulo_xz, angulo_yz = 0.0, 0.0
    mostrar_vertices = True
    rotacion_i = 0

    # Solo el primer dedo controla la rotación; los demás no interfieren.
    dedo_activo = None
    mouse_arrastrando = False
    corriendo = True

    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False

            elif evento.type == pygame.FINGERDOWN:
                if dedo_activo is None:
                    dedo_activo = evento.finger_id

            elif evento.type == pygame.FINGERMOTION:
                if evento.finger_id == dedo_activo:
                    # FINGER* entrega desplazamientos normalizados entre 0 y 1.
                    angulo_xz -= evento.dx * SENSIBILIDAD_TACTIL
                    angulo_yz += evento.dy * SENSIBILIDAD_TACTIL

            elif evento.type == pygame.FINGERUP:
                if evento.finger_id == dedo_activo:
                    dedo_activo = None

            # También se puede probar arrastrando con el mouse en el PC.
            # Ignoramos los eventos mouse que el propio toque puede generar.
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1 and not getattr(evento, "touch", False):
                    mouse_arrastrando = True

            elif evento.type == pygame.MOUSEMOTION:
                if mouse_arrastrando and not getattr(evento, "touch", False):
                    angulo_xz -= evento.rel[0] / W * SENSIBILIDAD_TACTIL
                    angulo_yz += evento.rel[1] / H * SENSIBILIDAD_TACTIL

            elif evento.type == pygame.MOUSEBUTTONUP:
                if evento.button == 1:
                    mouse_arrastrando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_q:
                    mostrar_vertices = not mostrar_vertices
                elif evento.key == pygame.K_e:
                    rotacion_i += 1

        dt = min(reloj.get_time() / 1000.0, 0.05)
        teclas = pygame.key.get_pressed()

        # Los controles clásicos permanecen disponibles en el PC.
        if teclas[pygame.K_s]:
            dz += dt
        if teclas[pygame.K_w]:
            dz -= dt
        if teclas[pygame.K_a]:
            dx += dt
        if teclas[pygame.K_d]:
            dx -= dt
        if teclas[pygame.K_SPACE]:
            dy -= dt
        if teclas[pygame.K_LCTRL]:
            dy += dt
        if teclas[pygame.K_LEFT]:
            angulo_xz -= math.pi * dt
        if teclas[pygame.K_RIGHT]:
            angulo_xz += math.pi * dt
        if teclas[pygame.K_UP]:
            angulo_yz += math.pi * dt
        if teclas[pygame.K_DOWN]:
            angulo_yz -= math.pi * dt

        if rotacion_i % 4:
            angulo_xz, angulo_yz = rotacion_auto(
                rotacion_i, angulo_xz, angulo_yz, dt
            )

        ventana.fill((0, 0, 0))
        for vertices, aristas, color in figuras:
            movidos = [
                trasladar(rotar(p, angulo_xz, angulo_yz), dx, dy, dz)
                for p in vertices
            ]
            for i, j in aristas:
                linea(movidos[i], movidos[j], color)
            if mostrar_vertices:
                for p in movidos:
                    punto(p, color)

        pygame.display.flip()
        reloj.tick(FPS)
        await asyncio.sleep(0)

    pygame.quit()  # Dentro de main(), nunca después de asyncio.run().


asyncio.run(main())
