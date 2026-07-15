import pygame
import math

def rotar_punto(punto, centro, angulo_grados):
    angulo_rad = math.radians(angulo_grados)
    ox, oy = centro
    px, py = punto
    qx = ox + math.cos(angulo_rad) * (px - ox) - math.sin(angulo_rad) * (py - oy)
    qy = oy + math.sin(angulo_rad) * (px - ox) + math.cos(angulo_rad) * (py - oy)
    return (int(qx), int(qy))

def obtener_curva_bezier(p0, p1, p2):
    """
    Genera los puntos de una curva Bezier cuadrática adaptando el número
    de segmentos dinámicamente según la longitud física de la trayectoria.
    """
    # 📏 Calculamos la distancia aproximada de la curva siguiendo el polígono de control
    d1 = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    d2 = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    longitud_aprox = d1 + d2
    
    # 🎯 Ajuste dinámico: Queremos aproximadamente un segmento cada 8 píxeles.
    # Capamos entre 8 segmentos (mínimo de fluidez) y 150 (suavidad extrema sin ahogar la CPU).
    num_puntos = max(8, min(150, int(longitud_aprox / 8)))
    
    puntos = []
    for i in range(num_puntos + 1):
        t = i / num_puntos
        # Fórmula paramétrica de Bezier cuadrática
        x = (1-t)**2 * p0[0] + 2*(1-t)*t * p1[0] + t**2 * p2[0]
        y = (1-t)**2 * p0[1] + 2*(1-t)*t * p1[1] + t**2 * p2[1]
        puntos.append((x, y))
    return puntos

def obtener_ruta_redondeada(p1, p2, r=15, orientacion="horizontal"):
    x1, y1 = p1
    x2, y2 = p2
    if abs(x1 - x2) < 12 or abs(y1 - y2) < 12:
        return [p1, p2]
        
    dx = 1 if x2 > x1 else -1
    dy = 1 if y2 > y1 else -1
    
    if orientacion == "horizontal":
        x_mid = (x1 + x2) / 2
        r = min(r, abs(x_mid - x1) - 1, abs(y2 - y1) / 2 - 1)
        if r < 4: return [p1, (x_mid, y1), (x_mid, y2), p2]
        puntos = [p1]
        
        p0, p1_ctrl, p2_end = (x_mid - dx * r, y1), (x_mid, y1), (x_mid, y1 + dy * r)
        puntos.append(p0)
        for step in range(1, 6):
            t = step / 5.0
            bx = (1-t)**2 * p0[0] + 2*(1-t)*t * p1_ctrl[0] + t**2 * p2_end[0]
            by = (1-t)**2 * p0[1] + 2*(1-t)*t * p1_ctrl[1] + t**2 * p2_end[1]
            puntos.append((bx, by))
            
        q0, q1_ctrl, q2_end = (x_mid, y2 - dy * r), (x_mid, y2), (x_mid + dx * r, y2)
        puntos.append(q0)
        for step in range(1, 6):
            t = step / 5.0
            qx = (1-t)**2 * q0[0] + 2*(1-t)*t * q1_ctrl[0] + t**2 * q2_end[0]
            qy = (1-t)**2 * q0[1] + 2*(1-t)*t * q1_ctrl[1] + t**2 * q2_end[1]
            puntos.append((qx, qy))
            
        puntos.append(p2)
        return puntos
    else:
        y_mid = (y1 + y2) / 2
        r = min(r, abs(y_mid - y1) - 1, abs(x2 - x1) / 2 - 1)
        if r < 4: return [p1, (x1, y_mid), (x2, y_mid), p2]
        puntos = [p1]
        
        p0, p1_ctrl, p2_end = (x1, y_mid - dy * r), (x1, y_mid), (x1 + dx * r, y_mid)
        puntos.append(p0)
        for step in range(1, 6):
            t = step / 5.0
            bx = (1-t)**2 * p0[0] + 2*(1-t)*t * p1_ctrl[0] + t**2 * p2_end[0]
            by = (1-t)**2 * p0[1] + 2*(1-t)*t * p1_ctrl[1] + t**2 * p2_end[1]
            puntos.append((bx, by))
            
        q0, q1_ctrl, q2_end = (x2 - dx * r, y_mid), (x2, y_mid), (x2, y_mid + dy * r)
        puntos.append(q0)
        for step in range(1, 6):
            t = step / 5.0
            qx = (1-t)**2 * q0[0] + 2*(1-t)*t * q1_ctrl[0] + t**2 * q2_end[0]
            qy = (1-t)**2 * q0[1] + 2*(1-t)*t * q1_ctrl[1] + t**2 * q2_end[1]
            puntos.append((qx, qy))
            
        puntos.append(p2)
        return puntos

def descifrar_indice(texto, indice_abs):
    lineas = texto.split("\n")
    acumulado = 0
    for i, linea in enumerate(lineas):
        longitud_linea = len(linea) + (1 if i < len(lineas) - 1 else 0)
        if indice_abs <= acumulado + longitud_linea:
            return i, min(indice_abs - acumulado, len(linea))
        acumulado += longitud_linea
    return len(lineas) - 1, len(lineas[-1]) if lineas else 0

def obtener_coordenadas_local(texto, indice_abs, fuente, ancho_t, pos_local_y, altura_linea):
    line_idx, col_idx = descifrar_indice(texto, indice_abs)
    lineas = texto.split("\n")
    linea_target = lineas[line_idx] if line_idx < len(lineas) else ""
    x_linea = (ancho_t - fuente.size(linea_target)[0]) // 2
    x_offset = fuente.size(linea_target[:col_idx])[0]
    y_offset = line_idx * altura_linea
    return x_linea + x_offset, pos_local_y + y_offset

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
        
        self.indice_cursor = len(self.texto)
        self.indice_seleccion_inicio = len(self.texto)
        
        self.angulo = 0.0          
        self.angulo_offset = 0.0   

    def obtener_punto_rotacion(self):
        pos_original = (self.rect.centerx, self.rect.top - 25)
        return rotar_punto(pos_original, self.rect.center, self.angulo)

    def obtener_puntos_conexion(self):
        r = self.rect
        centro = r.center
        puntos_originales = {
            "arriba_izquierda": (r.left, r.top), "arriba_centro": (r.centerx, r.top), "arriba_derecha": (r.right, r.top),
            "centro_izquierda": (r.left, r.centery), "centro_derecha": (r.right, r.centery),
            "abajo_izquierda": (r.left, r.bottom), "abajo_centro": (r.centerx, r.bottom), "abajo_derecha": (r.right, r.bottom)
        }
        puntos_rotados = {}
        for nombre, pos in puntos_originales.items():
            puntos_rotados[nombre] = rotar_punto(pos, centro, self.angulo)
        return puntos_rotados

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
        centro_mundo = self.rect.center
        centro_pantalla = (centro_mundo[0] - ox, centro_mundo[1] - oy)
        color = (255, 165, 0) if self.seleccionado else self.color_base
        
        if self.forma == "rectangulo":
            w, h = self.rect.width, self.rect.height
            surf_shape = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
            rect_local = pygame.Rect(4, 4, w, h)
            radio_redondeo = min(12, h // 2)
            pygame.draw.rect(surf_shape, color, rect_local, border_radius=radio_redondeo)
            pygame.draw.rect(surf_shape, self.color_borde, rect_local, 2, border_radius=radio_redondeo)
            surf_rotada = pygame.transform.rotate(surf_shape, -self.angulo)
            pantalla.blit(surf_rotada, surf_rotada.get_rect(center=centro_pantalla))
            
        elif self.forma == "rombo":
            puntos_rombo = [(self.rect.centerx, self.rect.top), (self.rect.right, self.rect.centery), (self.rect.centerx, self.rect.bottom), (self.rect.left, self.rect.centery)]
            puntos_pantalla = [(rotar_punto(p, centro_mundo, self.angulo)[0] - ox, rotar_punto(p, centro_mundo, self.angulo)[1] - oy) for p in puntos_rombo]
            pygame.draw.polygon(pantalla, color, puntos_pantalla)
            pygame.draw.polygon(pantalla, self.color_borde, puntos_pantalla, 2)
            
        elif self.forma == "linea":
            p_ini = rotar_punto((self.rect.centerx, self.rect.top + 5), centro_mundo, self.angulo)
            p_fin = rotar_punto((self.rect.centerx, self.rect.bottom - 5), centro_mundo, self.angulo)
            pygame.draw.line(pantalla, color, (p_ini[0]-ox, p_ini[1]-oy), (p_fin[0]-ox, p_fin[1]-oy), 4)
            pygame.draw.rect(pantalla, color, pygame.Rect(p_ini[0]-ox-4, p_ini[1]-oy-4, 8, 8))
            pygame.draw.rect(pantalla, color, pygame.Rect(p_fin[0]-ox-4, p_fin[1]-oy-4, 8, 8))
            
        elif self.forma == "texto" and (self.seleccionado or self.editando):
            esquinas = [self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft]
            puntos_pantalla = [(rotar_punto(p, centro_mundo, self.angulo)[0] - ox, rotar_punto(p, centro_mundo, self.angulo)[1] - oy) for p in esquinas]
            pygame.draw.polygon(pantalla, (200, 200, 200), puntos_pantalla, 1)

        color_letras = self.color_base if self.forma == "texto" else (30, 30, 30)
        
        lineas = self.texto.split("\n")
        altura_linea = fuente.get_linesize()
        ancho_t = max(20, max([fuente.size(l)[0] for l in lineas]) + 20) if lineas else 20
        alto_t = max(20, len(lineas) * altura_linea + 10)
        surf_temp = pygame.Surface((ancho_t, alto_t), pygame.SRCALPHA)
        pos_local_y = 5
        
        sel_inicio = getattr(self, 'indice_seleccion_inicio', self.indice_cursor)
        if self.editando and sel_inicio != self.indice_cursor:
            idx_min, idx_max = min(sel_inicio, self.indice_cursor), max(sel_inicio, self.indice_cursor)
            line_min, col_min = descifrar_indice(self.texto, idx_min)
            line_max, col_max = descifrar_indice(self.texto, idx_max)

            for i, linea in enumerate(lineas):
                if line_min <= i <= line_max:
                    c_ini = col_min if i == line_min else 0
                    c_fin = col_max if i == line_max else len(linea)
                    if line_min < i < line_max: c_ini, c_fin = 0, len(linea)
                    x_linea = (ancho_t - fuente.size(linea)[0]) // 2
                    x_sel = x_linea + fuente.size(linea[:c_ini])[0]
                    w_sel = fuente.size(linea[c_ini:c_fin])[0] or (6 if i < line_max else 0)
                    if w_sel > 0: pygame.draw.rect(surf_temp, (180, 215, 255), (x_sel, pos_local_y + i * altura_linea, w_sel, altura_linea), border_radius=3)
        
        for i, linea in enumerate(lineas):
            surf_temp.blit(fuente.render(linea, True, color_letras), ((ancho_t - fuente.size(linea)[0]) // 2, pos_local_y + i * altura_linea))
        
        if self.editando and sel_inicio == self.indice_cursor and pygame.time.get_ticks() % 1000 < 500:
            cx, cy = obtener_coordenadas_local(self.texto, self.indice_cursor, fuente, ancho_t, pos_local_y, altura_linea)
            pygame.draw.line(surf_temp, color_letras, (cx, cy), (cx, cy + altura_linea), 2)
        
        surf_rotada = pygame.transform.rotate(surf_temp, -self.angulo)
        
        if self.forma == "linea":
            desplazamiento = rotar_punto((centro_mundo[0], centro_mundo[1] + 12), centro_mundo, self.angulo)
            pos_texto = surf_rotada.get_rect(center=(desplazamiento[0] - ox, desplazamiento[1] - oy))
        else:
            pos_texto = surf_rotada.get_rect(center=centro_pantalla)
        pantalla.blit(surf_rotada, pos_texto)

        if self.seleccionado or self.editando:
            puntos = self.obtener_puntos_conexion()
            for pos in puntos.values():
                pygame.draw.circle(pantalla, (255, 255, 255), (int(pos[0] - ox), int(pos[1] - oy)), int(self.radio_punto_conexion))
                pygame.draw.circle(pantalla, (50, 120, 240), (int(pos[0] - ox), int(pos[1] - oy)), int(self.radio_punto_conexion), 2)
            
            if self.modo_interaccion == "arrow":
                direcciones = {"arriba_izquierda": (-1, -1), "arriba_centro": (0, -1), "arriba_derecha": (1, -1), "centro_izquierda": (-1, 0), "centro_derecha": (1, 0), "abajo_izquierda": (-1, 1), "abajo_centro": (0, 1), "abajo_derecha": (1, 1)}
                p_orig = {"arriba_izquierda": (self.rect.left, self.rect.top), "arriba_centro": (self.rect.centerx, self.rect.top), "arriba_derecha": (self.rect.right, self.rect.top), "centro_izquierda": (self.rect.left, self.rect.centery), "centro_derecha": (self.rect.right, self.rect.centery), "abajo_izquierda": (self.rect.left, self.rect.bottom), "abajo_centro": (self.rect.centerx, self.rect.bottom), "abajo_derecha": (self.rect.right, self.rect.bottom)}
                for nombre, pos_rotada in puntos.items():
                    dx, dy = direcciones[nombre]
                    dest = rotar_punto((p_orig[nombre][0] + dx * 16, p_orig[nombre][1] + dy * 16), centro_mundo, self.angulo)
                    self._dibujar_flechita(pantalla, (pos_rotada[0] - ox, pos_rotada[1] - oy), (dest[0] - ox, dest[1] - oy))

            p_base_manija = rotar_punto((self.rect.centerx, self.rect.top), centro_mundo, self.angulo)
            p_extremo_manija = self.obtener_punto_rotacion()
            pygame.draw.line(pantalla, (100, 100, 100), (int(p_base_manija[0] - ox), int(p_base_manija[1] - oy)), (int(p_extremo_manija[0] - ox), int(p_extremo_manija[1] - oy)), 2)
            pygame.draw.circle(pantalla, (255, 255, 255), (int(p_extremo_manija[0] - ox), int(p_extremo_manija[1] - oy)), 6)
            pygame.draw.circle(pantalla, (46, 204, 113), (int(p_extremo_manija[0] - ox), int(p_extremo_manija[1] - oy)), 6, 2)

class Conexion:
    def __init__(self, nodo_origen, punto_origen, nodo_destino=None, punto_destino=None, tipo="recta"):
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
        self.tipo = tipo  
        
        # 🌟 NUEVO: Offset de arrastre manual para deformar cualquier flecha
        self.desplazamiento_curva = [0, 0] 
        
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

    def verificar_clic_punto_control(self, pos_mundo):
        """🌟 NUEVO: Verifica si hiciste clic en la manija central de la flecha"""
        puntos = self.obtener_todos_los_puntos()
        if len(puntos) < 2: return False
        mid_x = (puntos[0][0] + puntos[1][0]) / 2
        mid_y = (puntos[0][1] + puntos[1][1]) / 2
        pc_x = mid_x + self.desplazamiento_curva[0]
        pc_y = mid_y + self.desplazamiento_curva[1]
        return math.hypot(pos_mundo[0] - pc_x, pos_mundo[1] - pc_y) <= 12

    def verificar_clic_linea(self, pos_mundo, margen_error=8):
        """Detección de colisión inteligente en líneas rectas o curvas"""
        puntos = self.obtener_todos_los_puntos()
        if len(puntos) < 2: return False
        
        p_origen, p_destino = puntos[0], puntos[1]
        mid_x = (p_origen[0] + p_destino[0]) / 2
        mid_y = (p_origen[1] + p_destino[1]) / 2
        p_control = (mid_x + self.desplazamiento_curva[0], mid_y + self.desplazamiento_curva[1])

        orientacion = "horizontal"
        if self.punto_origen and ("arriba" in self.punto_origen or "abajo" in self.punto_origen):
            orientacion = "vertical"

        # Ruteamos todos los segmentos
        if self.desplazamiento_curva != [0, 0]:
            puntos_ruta = obtener_curva_bezier(p_origen, p_control, p_destino)
        elif getattr(self, "tipo", "recta") == "redondeada":
            puntos_ruta = obtener_ruta_redondeada(p_origen, p_destino, r=15, orientacion=orientacion)
        else:
            puntos_ruta = [p_origen, p_destino]
            
        px, py = pos_mundo

        # Verificamos distancia a CADA segmento de la curva
        for i in range(len(puntos_ruta) - 1):
            p1, p2 = puntos_ruta[i], puntos_ruta[i+1]
            line_long = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            if line_long == 0:
                if math.hypot(px - p1[0], py - p1[1]) <= margen_error: return True
                continue
            u = ((px - p1[0]) * (p2[0] - p1[0]) + (py - p1[1]) * (p2[1] - p1[1])) / (line_long ** 2)
            u = max(0, min(1, u))
            proj_x = p1[0] + u * (p2[0] - p1[0])
            proj_y = p1[1] + u * (p2[1] - p1[1])
            if math.hypot(px - proj_x, py - proj_y) <= margen_error: return True
            
        return False

    def verificar_clic_punta_suelta(self, pos_raton, margen_error=10):
        if self.pos_vacio_final and self.destino is None:
            return math.hypot(pos_raton[0] - self.pos_vacio_final[0], pos_raton[1] - self.pos_vacio_final[1]) <= margen_error
        return False

    def dibujar(self, pantalla, fuente=None, camara_offset=(0, 0)):
        puntos = self.obtener_todos_los_puntos()
        if len(puntos) < 2: return
        
        ox, oy = camara_offset
        COLOR_LINEA = self.color_base
        GROSOR = 2
        
        p_origen = (puntos[0][0] - ox, puntos[0][1] - oy)
        p_destino = (puntos[1][0] - ox, puntos[1][1] - oy)
        
        mid_x_mundo = (puntos[0][0] + puntos[1][0]) / 2
        mid_y_mundo = (puntos[0][1] + puntos[1][1]) / 2
        p_control_mundo = (mid_x_mundo + self.desplazamiento_curva[0], mid_y_mundo + self.desplazamiento_curva[1])
        p_control_pantalla = (p_control_mundo[0] - ox, p_control_mundo[1] - oy)

        orientacion = "horizontal"
        if self.punto_origen and ("arriba" in self.punto_origen or "abajo" in self.punto_origen):
            orientacion = "vertical"
            
        # 🌟 NUEVO: Ruteo dinámico con la curva Bezier manual
        if self.desplazamiento_curva != [0, 0]:
            puntos_linea = obtener_curva_bezier(p_origen, p_control_pantalla, p_destino)
            centro_x = 0.25 * p_origen[0] + 0.5 * p_control_pantalla[0] + 0.25 * p_destino[0]
            centro_y = 0.25 * p_origen[1] + 0.5 * p_control_pantalla[1] + 0.25 * p_destino[1]
        elif getattr(self, "tipo", "recta") == "redondeada":
            puntos_linea = obtener_ruta_redondeada(p_origen, p_destino, r=15, orientacion=orientacion)
            centro_x, centro_y = (p_origen[0] + p_destino[0]) // 2, (p_origen[1] + p_destino[1]) // 2
        else:
            puntos_linea = [p_origen, p_destino]
            centro_x, centro_y = (p_origen[0] + p_destino[0]) // 2, (p_origen[1] + p_destino[1]) // 2
            
        # Dibujar resplandor naranja si está seleccionada
        if self.seleccionada and len(puntos_linea) >= 2:
            pygame.draw.lines(pantalla, (255, 140, 0), False, puntos_linea, GROSOR + 4)
            
        # Dibujar la línea principal
        if len(puntos_linea) >= 2:
            pygame.draw.lines(pantalla, COLOR_LINEA, False, puntos_linea, GROSOR)
        
        if self.pos_vacio_final and not self.seleccionada:
            pos_vacio_pantalla = (self.pos_vacio_final[0] - ox, self.pos_vacio_final[1] - oy)
            pygame.draw.circle(pantalla, (100, 100, 100), pos_vacio_pantalla, 4)
            pygame.draw.circle(pantalla, (245, 245, 245), pos_vacio_pantalla, 2)
            
        # --- RENDERIZAR TEXTO CENTRADO EN LA CURVA ---
        if fuente and (self.texto or self.editando):
            lineas = self.texto.split("\n")
            altura_linea = fuente.get_linesize()
            ancho_t = max(20, max([fuente.size(l)[0] for l in lineas]) + 20) if lineas else 20
            alto_t = max(20, len(lineas) * altura_linea + 10)
            surf_temp = pygame.Surface((ancho_t, alto_t), pygame.SRCALPHA)
            
            pos_local_y = 5
            sel_inicio = getattr(self, 'indice_seleccion_inicio', self.indice_cursor)
            if self.editando and sel_inicio != self.indice_cursor:
                idx_min, idx_max = min(sel_inicio, self.indice_cursor), max(sel_inicio, self.indice_cursor)
                line_min, col_min = descifrar_indice(self.texto, idx_min)
                line_max, col_max = descifrar_indice(self.texto, idx_max)
                for i, linea in enumerate(lineas):
                    if line_min <= i <= line_max:
                        c_ini = col_min if i == line_min else 0
                        c_fin = col_max if i == line_max else len(linea)
                        if line_min < i < line_max: c_ini, c_fin = 0, len(linea)
                        x_sel = (ancho_t - fuente.size(linea)[0]) // 2 + fuente.size(linea[:c_ini])[0]
                        w_sel = fuente.size(linea[c_ini:c_fin])[0] or (6 if i < line_max else 0)
                        if w_sel > 0: pygame.draw.rect(surf_temp, (180, 215, 255), (x_sel, pos_local_y + i * altura_linea, w_sel, altura_linea), border_radius=3)
            
            for i, linea in enumerate(lineas):
                surf_temp.blit(fuente.render(linea, True, self.color_base), ((ancho_t - fuente.size(linea)[0]) // 2, pos_local_y + i * altura_linea))
                
            if self.editando and sel_inicio == self.indice_cursor and pygame.time.get_ticks() % 1000 < 500:
                cursor_x, cursor_y = obtener_coordenadas_local(self.texto, self.indice_cursor, fuente, ancho_t, pos_local_y, altura_linea)
                pygame.draw.line(surf_temp, self.color_base, (cursor_x, cursor_y), (cursor_x, cursor_y + altura_linea), 2)
                
            rect_texto_pantalla = surf_temp.get_rect(center=(centro_x, centro_y - 12))
            pygame.draw.rect(pantalla, (245, 245, 245), rect_texto_pantalla.inflate(6, 4))
            pantalla.blit(surf_temp, rect_texto_pantalla)
        
        # Calcular punta de la flecha
        p_penultimo, p_ultimo = puntos_linea[-2], puntos_linea[-1]
        dx, dy = p_ultimo[0] - p_penultimo[0], p_ultimo[1] - p_penultimo[1]
        angulo = math.atan2(dy, dx) if (dx != 0 or dy != 0) else 0
        LARGO_FLECHA, ANGULO_ALAS = 12, math.radians(25)
        
        flecha_ala1 = (p_ultimo[0] - LARGO_FLECHA * math.cos(angulo - ANGULO_ALAS), p_ultimo[1] - LARGO_FLECHA * math.sin(angulo - ANGULO_ALAS))
        flecha_ala2 = (p_ultimo[0] - LARGO_FLECHA * math.cos(angulo + ANGULO_ALAS), p_ultimo[1] - LARGO_FLECHA * math.sin(angulo + ANGULO_ALAS))
        pygame.draw.polygon(pantalla, COLOR_LINEA, [p_ultimo, flecha_ala1, flecha_ala2])

        # 🌟 NUEVO: Dibujar el "puntito" interactivo si la flecha está seleccionada
        if self.seleccionada:
            pygame.draw.circle(pantalla, (46, 204, 113), (int(p_control_pantalla[0]), int(p_control_pantalla[1])), 6)
            pygame.draw.circle(pantalla, (255, 255, 255), (int(p_control_pantalla[0]), int(p_control_pantalla[1])), 4)