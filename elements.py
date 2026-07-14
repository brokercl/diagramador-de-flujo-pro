import pygame
import math

class Nodo:
    def __init__(self, x, y, texto="Nodo", forma="rectangulo", w=120, h=60):
        self.rect = pygame.Rect(x - w//2, y - h//2, w, h) 
        self.color_borde = (50, 50, 50)
        self.texto = texto 
        self.color_base = (173, 216, 230) 
        self.seleccionado = False
        self.forma = forma
        self.editando = False
        self.radio_punto_conexion = 6 
        self.modo_interaccion = "resize" 
        
        # 🌟 Atributos del modelo de selección nativa
        self.indice_cursor = len(self.texto)
        self.indice_seleccion_inicio = len(self.texto)

    def obtener_puntos_conexion(self):
        if self.forma == "texto": return {}
        r = self.rect
        return {
            "arriba_izquierda": (int(r.left), int(r.top)), "arriba_centro": (int(r.centerx), int(r.top)), "arriba_derecha": (int(r.right), int(r.top)),
            "centro_izquierda": (int(r.left), int(r.centery)), "centro_derecha": (int(r.right), int(r.centery)),
            "abajo_izquierda": (int(r.left), int(r.bottom)), "abajo_centro": (int(r.centerx), int(r.bottom)), "abajo_derecha": (int(r.right), int(r.bottom))
        }

    def verificar_clic_puntos(self, pos_raton):
        puntos = self.obtener_puntos_conexion()
        for nombre, pos in puntos.items():
            if math.hypot(pos_raton[0] - pos[0], pos_raton[1] - pos[1]) <= self.radio_punto_conexion + 6:
                return nombre
        return None

    def _dibujar_flechita(self, pantalla, origen, destino):
        color_flecha = (50, 120, 240)
        pygame.draw.line(pantalla, color_flecha, origen, destino, 3)
        angulo = math.atan2(destino[1] - origen[1], destino[0] - origen[0])
        largo = 8
        apertura = math.pi / 6
        p1 = (destino[0] - largo * math.cos(angulo - apertura), destino[1] - largo * math.sin(angulo - apertura))
        p2 = (destino[0] - largo * math.cos(angulo + apertura), destino[1] - largo * math.sin(angulo + apertura))
        pygame.draw.polygon(pantalla, color_flecha, [destino, p1, p2])

    def dibujar(self, pantalla, fuente, camara_offset=(0, 0)):
        ox, oy = camara_offset
        rect_pantalla = self.rect.move(-ox, -oy)
        
        color = (255, 165, 0) if self.seleccionado else self.color_base
        
        if self.forma == "rectangulo":
            pygame.draw.rect(pantalla, color, rect_pantalla, border_radius=8)
            pygame.draw.rect(pantalla, self.color_borde, rect_pantalla, 2, border_radius=8)
        elif self.forma == "rombo":
            puntos_rombo = [(rect_pantalla.centerx, rect_pantalla.top), (rect_pantalla.right, rect_pantalla.centery), (rect_pantalla.centerx, rect_pantalla.bottom), (rect_pantalla.left, rect_pantalla.centery)]
            pygame.draw.polygon(pantalla, color, puntos_rombo)
            pygame.draw.polygon(pantalla, self.color_borde, puntos_rombo, 2)
        elif self.forma == "linea":
            cx, y_inicio, y_fin = rect_pantalla.centerx, rect_pantalla.top + 5, rect_pantalla.bottom - 5
            pygame.draw.line(pantalla, color, (cx, y_inicio), (cx, y_fin), 4)
            pygame.draw.rect(pantalla, color, pygame.Rect(cx - 4, y_inicio - 4, 8, 8))
            pygame.draw.rect(pantalla, color, pygame.Rect(cx - 4, y_fin - 4, 8, 8))
        elif self.forma == "texto" and (self.seleccionado or self.editando):
            pygame.draw.rect(pantalla, (200, 200, 200), rect_pantalla, 1)

        color_letras = self.color_base if self.forma == "texto" else (10, 10, 10)
        superficie_texto = fuente.render(self.texto, True, color_letras)
        
        pos_texto = superficie_texto.get_rect(center=(rect_pantalla.centerx, rect_pantalla.bottom + 12) if self.forma == "linea" else rect_pantalla.center)
            
        # 🌟 1. RENDERIZAR SELECCIÓN AZUL (Parcial o Total)
        sel_inicio = getattr(self, 'indice_seleccion_inicio', self.indice_cursor)
        if self.editando and sel_inicio != self.indice_cursor:
            idx_min = max(0, min(sel_inicio, self.indice_cursor, len(self.texto)))
            idx_max = max(0, min(max(sel_inicio, self.indice_cursor), len(self.texto)))
            
            x_inicio = pos_texto.left + fuente.size(self.texto[:idx_min])[0]
            ancho_seleccion = fuente.size(self.texto[idx_min:idx_max])[0]
            
            rect_sel = pygame.Rect(x_inicio, pos_texto.top, ancho_seleccion, pos_texto.height)
            rect_sel.inflate_ip(4, 4)
            pygame.draw.rect(pantalla, (180, 215, 255), rect_sel, border_radius=3)

        pantalla.blit(superficie_texto, pos_texto)

        # 🌟 2. RENDERIZAR CURSOR PARPADEANTE (Solo si NO hay texto seleccionado)
        if self.editando and sel_inicio == self.indice_cursor:
            if pygame.time.get_ticks() % 1000 < 500:
                idx = max(0, min(len(self.texto), self.indice_cursor))
                cursor_x = pos_texto.left + fuente.size(self.texto[:idx])[0]
                pygame.draw.line(pantalla, color_letras, (cursor_x, pos_texto.top), (cursor_x, pos_texto.bottom), 2)

        if self.seleccionado or self.editando:
            puntos = self.obtener_puntos_conexion()
            for pos in puntos.values():
                pos_entera = (int(pos[0] - ox), int(pos[1] - oy))
                pygame.draw.circle(pantalla, (255, 255, 255), pos_entera, int(self.radio_punto_conexion))
                pygame.draw.circle(pantalla, (50, 120, 240), pos_entera, int(self.radio_punto_conexion), 2)
            
            if self.modo_interaccion == "arrow" and self.forma != "texto":
                direcciones = {
                    "arriba_izquierda": (-1, -1), "arriba_centro": (0, -1), "arriba_derecha": (1, -1),
                    "centro_izquierda": (-1, 0), "centro_derecha": (1, 0),
                    "abajo_izquierda": (-1, 1), "abajo_centro": (0, 1), "abajo_derecha": (1, 1)
                }
                for nombre, pos in puntos.items():
                    dx, dy = direcciones[nombre]
                    pos_pantalla = (pos[0] - ox, pos[1] - oy)
                    destino_pantalla = (pos_pantalla[0] + dx * 16, pos_pantalla[1] + dy * 16)
                    self._dibujar_flechita(pantalla, pos_pantalla, destino_pantalla)


class Conexion:
    def __init__(self, nodo_origen, punto_origen, nodo_destino=None, punto_destino=None):
        self.origen = nodo_origen          
        self.punto_origen = punto_origen   
        self.destino = nodo_destino        
        self.punto_destino = punto_destino 
        self.seleccionada = False 
        self.pos_vacio_final = None
        self.origen_es_flecha = None
        
        self.texto = ""  
        self.editando = False 
        self.color_base = (60, 60, 60)
        
        # 🌟 Atributos del modelo de selección nativa
        self.indice_cursor = 0
        self.indice_seleccion_inicio = 0

    def obtener_todos_los_puntos(self):
        p_origen = p_destino = None
        if self.origen and self.punto_origen:
            p_origen = self.origen.obtener_puntos_conexion().get(self.punto_origen)
        elif self.origen_es_flecha:
            puntos_flecha = self.origen_es_flecha.obtener_todos_los_puntos()
            if puntos_flecha: p_origen = puntos_flecha[-1]

        if self.destino and self.punto_destino:
            p_destino = self.destino.obtener_puntos_conexion().get(self.punto_destino)
        elif self.pos_vacio_final:
            p_destino = self.pos_vacio_final

        return [p_origen, p_destino] if (p_origen and p_destino) else []

    def verificar_clic_linea(self, pos_raton, margen_error=8):
        puntos = self.obtener_todos_los_puntos()
        if len(puntos) < 2: return False
        p1, p2, px, py = puntos[0], puntos[-1], pos_raton[0], pos_raton[1]
        linea_longitud = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        if linea_longitud == 0: return math.hypot(px - p1[0], py - p1[1]) <= margen_error
        u = ((px - p1[0]) * (p2[0] - p1[0]) + (py - p1[1]) * (p2[1] - p1[1])) / (linea_longitud ** 2)
        if u < 0 or u > 1: return False
        return math.hypot(px - (p1[0] + u * (p2[0] - p1[0])), py - (p1[1] + u * (p2[1] - p1[1]))) <= margen_error

    def verificar_clic_punta_suelta(self, pos_raton, margen_error=10):
        if self.pos_vacio_final and self.destino is None:
            return math.hypot(pos_raton[0] - self.pos_vacio_final[0], pos_raton[1] - self.pos_vacio_final[1]) <= margen_error
        return False

    def dibujar(self, pantalla, fuente=None, camara_offset=(0, 0)):
        puntos = self.obtener_todos_los_puntos()
        if len(puntos) < 2: return
        
        ox, oy = camara_offset
        COLOR_LINEA = (255, 140, 0) if self.seleccionada else self.color_base
        GROSOR = 3 if self.seleccionada else 2
        
        p_origen = (puntos[0][0] - ox, puntos[0][1] - oy)
        p_destino = (puntos[1][0] - ox, puntos[1][1] - oy)
        pygame.draw.line(pantalla, COLOR_LINEA, p_origen, p_destino, GROSOR)
        
        if self.pos_vacio_final and not self.seleccionada:
            pos_vacio_pantalla = (self.pos_vacio_final[0] - ox, self.pos_vacio_final[1] - oy)
            pygame.draw.circle(pantalla, (100, 100, 100), pos_vacio_pantalla, 4)
            pygame.draw.circle(pantalla, (245, 245, 245), pos_vacio_pantalla, 2)
            
        if fuente and (self.texto or self.editando):
            centro_x, centro_y = (p_origen[0] + p_destino[0]) // 2, (p_origen[1] + p_destino[1]) // 2
            surf_texto = fuente.render(self.texto, True, self.color_base)
            rect_texto = surf_texto.get_rect(center=(centro_x, centro_y - 12)) 
            
            rect_fondo = rect_texto.inflate(6, 4)
            pygame.draw.rect(pantalla, (245, 245, 245), rect_fondo)
            
            # 🌟 1. RENDERIZAR SELECCIÓN AZUL EN LA CONEXIÓN
            sel_inicio = getattr(self, 'indice_seleccion_inicio', self.indice_cursor)
            if self.editando and sel_inicio != self.indice_cursor:
                idx_min = max(0, min(sel_inicio, self.indice_cursor, len(self.texto)))
                idx_max = max(0, min(max(sel_inicio, self.indice_cursor), len(self.texto)))
                x_inicio = rect_texto.left + fuente.size(self.texto[:idx_min])[0]
                ancho_seleccion = fuente.size(self.texto[idx_min:idx_max])[0]
                rect_sel = pygame.Rect(x_inicio, rect_texto.top, ancho_seleccion, rect_texto.height)
                pygame.draw.rect(pantalla, (180, 215, 255), rect_sel, border_radius=3)
            
            pantalla.blit(surf_texto, rect_texto)

            # 🌟 2. RENDERIZAR CURSOR INTERMEDIO
            if self.editando and sel_inicio == self.indice_cursor:
                if pygame.time.get_ticks() % 1000 < 500:
                    idx = max(0, min(len(self.texto), self.indice_cursor))
                    cursor_x = rect_texto.left + fuente.size(self.texto[:idx])[0]
                    pygame.draw.line(pantalla, self.color_base, (cursor_x, rect_texto.top), (cursor_x, rect_texto.bottom), 2)
        
        dx, dy = p_destino[0] - p_origen[0], p_destino[1] - p_origen[1]
        angulo = math.atan2(dy, dx) if (dx != 0 or dy != 0) else 0
        LARGO_FLECHA, ANGULO_ALAS = 12, math.radians(25)
        
        flecha_ala1 = (p_destino[0] - LARGO_FLECHA * math.cos(angulo - ANGULO_ALAS), p_destino[1] - LARGO_FLECHA * math.sin(angulo - ANGULO_ALAS))
        flecha_ala2 = (p_destino[0] - LARGO_FLECHA * math.cos(angulo + ANGULO_ALAS), p_destino[1] - LARGO_FLECHA * math.sin(angulo + ANGULO_ALAS))
        pygame.draw.polygon(pantalla, COLOR_LINEA, [p_destino, flecha_ala1, flecha_ala2])