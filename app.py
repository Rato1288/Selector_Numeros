import pygame
import pandas as pd
import time
from datetime import datetime
import os

# --- CONFIGURACIÓN ---
ANCHO, ALTO = 1100, 850
FPS = 60
COLOR_FONDO = (15, 15, 15)
COLOR_PANEL_LAT = (25, 25, 25)
COLOR_PANEL_INF = (35, 35, 35)
VERDE, ROJO, AMARILLO = (46, 204, 113), (231, 76, 60), (241, 196, 15)
BLANCO, GRIS = (240, 240, 240), (120, 120, 120)

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("⚽ Futsal Pro - Analizador Portero")
reloj = pygame.time.Clock()

# FUENTES PROFESIONALES
fuente_l = pygame.font.SysFont("Verdana", 38, bold=True)
fuente_m = pygame.font.SysFont("Verdana", 20, bold=True)
fuente_s = pygame.font.SysFont("Verdana", 15, bold=True)
fuente_tiny = pygame.font.SysFont("Verdana", 14)

# --- RECURSOS ---
IMG_PATH = "marco.png"


def cargar_arco():
    if os.path.exists(IMG_PATH):
        try:
            img = pygame.image.load(IMG_PATH).convert()
            return pygame.transform.scale(img, (800, 500))
        except:
            pass
    img = pygame.Surface((800, 500));
    img.fill((50, 50, 50))
    pygame.draw.rect(img, BLANCO, (0, 0, 800, 500), 4)
    return img


img_arco = cargar_arco()
rect_arco = img_arco.get_rect(topleft=(50, 120))

# --- VARIABLES DE ESTADO ---
tiros = []
nombre_portero = ""
fase = "INICIO"
modo_activo = "Detenido"
tiempo_transcurrido = 0
momento_inicio = 0
pausado = False

botones = [
    {"pos": (130, 730), "tipo": "Detenido", "color": VERDE},
    {"pos": (330, 730), "tipo": "Gol", "color": ROJO},
    {"pos": (530, 730), "tipo": "Fuera", "color": AMARILLO}
]


def escribir(txt, f, c, x, y):
    pantalla.blit(f.render(txt, True, c), (x, y))


def guardar_reporte():
    if tiros:
        df = pd.DataFrame(tiros)
        if 'Pos' in df.columns: df.drop(columns=['Pos', 'Color'], inplace=True)
        fecha_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f"reporte_{nombre_portero}_{fecha_str}.csv"
        df.to_csv(nombre_archivo, index=False)
        return nombre_archivo
    return None


# --- BUCLE PRINCIPAL ---
ejecutando = True
while ejecutando:
    pantalla.fill(COLOR_FONDO)
    eventos = pygame.event.get()

    for e in eventos:
        if e.type == pygame.QUIT: ejecutando = False

        if fase == "INICIO":
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and len(nombre_portero) > 1:
                    fase = "ANALISIS"
                    momento_inicio = time.time()
                    tiros = []
                    tiempo_transcurrido = 0
                elif e.key == pygame.K_BACKSPACE:
                    nombre_portero = nombre_portero[:-1]
                else:
                    nombre_portero += e.unicode

        elif fase == "ANALISIS":
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_p:
                    pausado = not pausado
                    if not pausado: momento_inicio = time.time() - tiempo_transcurrido

                # --- NUEVA OPCIÓN: REINICIO [X] ---
                if e.key == pygame.K_x:
                    tiros = []
                    tiempo_transcurrido = 0
                    momento_inicio = time.time()
                    pausado = False

                if e.key == pygame.K_c:
                    guardar_reporte()
                    nombre_portero = "";
                    fase = "INICIO"
                if e.key == pygame.K_r: fase = "RESUMEN"

            if e.type == pygame.MOUSEBUTTONDOWN and not pausado:
                m_pos = pygame.mouse.get_pos()
                clic_menu = False
                for b in botones:
                    dist = ((m_pos[0] - b["pos"][0]) ** 2 + (m_pos[1] - b["pos"][1]) ** 2) ** 0.5
                    if dist < 30:
                        modo_activo = b["tipo"];
                        clic_menu = True

                if not clic_menu and rect_arco.collidepoint(m_pos):
                    color = VERDE if modo_activo == "Detenido" else (ROJO if modo_activo == "Gol" else AMARILLO)
                    m, s = divmod(int(tiempo_transcurrido), 60)
                    tiros.append({
                        "Portero": nombre_portero, "Min": f"{m:02d}:{s:02d}",
                        "Res": modo_activo, "Pos": m_pos, "Color": color
                    })

        elif fase == "RESUMEN":
            if e.type == pygame.KEYDOWN:
                guardar_reporte()
                ejecutando = False

    # --- DIBUJO ---
    if fase == "INICIO":
        escribir("CONTROL TÁCTICO DE PORTEROS", fuente_l, BLANCO, 230, 250)
        escribir("Nombre del Portero:", fuente_m, GRIS, 440, 350)
        pygame.draw.rect(pantalla, COLOR_PANEL_INF, (350, 400, 400, 45), border_radius=8)
        escribir(nombre_portero + "|", fuente_m, VERDE, 370, 410)

    elif fase == "ANALISIS":
        if not pausado: tiempo_transcurrido = time.time() - momento_inicio

        pygame.draw.rect(pantalla, COLOR_PANEL_LAT, (880, 0, 220, ALTO))
        pygame.draw.rect(pantalla, COLOR_PANEL_INF, (0, 670, 880, 180))
        pantalla.blit(img_arco, rect_arco)
        pygame.draw.rect(pantalla, BLANCO, rect_arco, 2)

        m, s = divmod(int(tiempo_transcurrido), 60)
        escribir(f"PORTERO: {nombre_portero.upper()}", fuente_m, GRIS, 50, 30)
        escribir(f"TIEMPO: {m:02d}:{s:02d}", fuente_l, VERDE, 50, 60)

        if pausado:
            escribir("[ EN PAUSA ]", fuente_m, AMARILLO, 260, 75)

        # BOTONES DE SELECCIÓN
        for b in botones:
            radio_esfera = 25
            if modo_activo == b["tipo"]:
                pygame.draw.circle(pantalla, BLANCO, b["pos"], radio_esfera + 4, 2)
            pygame.draw.circle(pantalla, b["color"], b["pos"], radio_esfera)
            escribir(b["tipo"], fuente_s, BLANCO, b["pos"][0] - 35, b["pos"][1] + 35)

        # Estadísticas
        p, g, f = len([t for t in tiros if t['Res'] == 'Detenido']), len([t for t in tiros if t['Res'] == 'Gol']), len(
            [t for t in tiros if t['Res'] == 'Fuera'])
        escribir("ESTADÍSTICAS", fuente_m, BLANCO, 900, 50)
        escribir(f"TIROS: {len(tiros)}", fuente_m, BLANCO, 900, 110)
        escribir(f"PARADAS: {p}", fuente_m, VERDE, 900, 170)
        escribir(f"GOLES:   {g}", fuente_m, ROJO, 900, 230)
        escribir(f"FUERA:   {f}", fuente_m, AMARILLO, 900, 290)

        escribir("[P] PAUSA", fuente_m, AMARILLO, 910, 640)
        escribir("[X] REINICIAR", fuente_m, BLANCO, 910, 680)
        escribir("[C] CAMBIO", fuente_m, VERDE, 910, 720)
        escribir("[R] RESUMEN", fuente_m, ROJO, 910, 760)

        for t in tiros:
            pygame.draw.circle(pantalla, t["Color"], t["Pos"], 10)
            pygame.draw.circle(pantalla, BLANCO, t["Pos"], 10, 2)

    elif fase == "RESUMEN":
        pygame.draw.rect(pantalla, COLOR_PANEL_LAT, (250, 150, 600, 550), border_radius=20)
        escribir("RESUMEN DE DESEMPEÑO", fuente_l, BLANCO, 330, 200)
        p, g, f = len([t for t in tiros if t['Res'] == 'Detenido']), len([t for t in tiros if t['Res'] == 'Gol']), len(
            [t for t in tiros if t['Res'] == 'Fuera'])
        total = max(1, len(tiros));
        efic = (p / (total - f) * 100) if (total - f) > 0 else 0
        escribir(f"Portero: {nombre_portero}", fuente_m, AMARILLO, 300, 300)
        escribir(f"Tiros a Puerta: {total - f}", fuente_m, BLANCO, 300, 350)
        escribir(f"Goles: {g}", fuente_m, ROJO, 300, 400)
        escribir(f"Efectividad: {int(efic)}%", fuente_l, VERDE if efic > 70 else ROJO, 300, 550)
        escribir("CUALQUIER TECLA PARA GUARDAR Y SALIR", fuente_tiny, GRIS, 420, 660)

    pygame.display.flip()
    reloj.tick(FPS)

pygame.quit()
