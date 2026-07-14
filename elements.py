import pygame
import math

def rotar_punto(punto, centro, angulo_grados):
    """Rota un punto alrededor de un centro por un ángulo específico en grados."""
    angulo_rad = math.radians(angulo_grados)
    ox, oy = centro
    px, py = punto
    qx = ox + math.cos(angulo_rad) * (px - ox) - math.sin(angulo_rad) * (py - oy)
    qy = oy + math.sin(angulo_rad) * (px - ox) + math.cos(angulo_rad) * (py - oy)
    return (int(qx), int(qy))

def descifrar_indice(texto, indice_abs):
    """Traduce un índice absoluto 1D a coordenadas (linea_idx, columna_idx) para textos multilínea."""
    lineas = texto.split("\n")
    acumulado = 0
    for i, linea in enumerate(lineas):
        # +1 por el caracter '\n' que se pierde en el split (excepto en la última línea)
        longitud_linea = len(linea) + (1 if i < len(lineas) - 1 else 0)
        if indice_abs <= acumulado + longitud_linea:
            return i, min(indice_abs - acumulado, len(linea))
        acumulado += longitud_linea
    return len(lineas) - 1, len(lineas[-1]) if lineas else 0

def obtener_coordenadas_local(texto, indice_abs, fuente, ancho_t, pos_local_y, altura_linea):
    """Calcula la posición (X, Y) local de un cursor dentro de una superficie de texto multilínea centrada."""
    line_idx, col_idx = descifrar_indice(texto, indice_abs)
    lineas = texto.split("\n")
    linea_target = lineas[line_idx] if line_idx < len(lineas) else ""
    x_linea = (ancho_t - fuente.size(linea_target)[0]) // 2
    x_offset = fuente.size(linea_target[:col_idx])[0]
    y_offset = line_idx * altura_linea
    return x_linea + x_offset, pos_local_y + y_offset


def obtener_ruta_redondeada(p1, p2, r=15, orientacion="horizontal"):
    """
    Genera una secuencia de puntos para una ruta ortogonal con esquinas redondeadas
    utilizando curvas Bezier en los codos para un acabado vectorial suave.
    """
    x1, y1 = p1
    x2, y2 = p2
    
    # Si están prácticamente alineados en algún eje, una línea recta basta
    if abs(x1 - x2) < 12 or abs(y1 - y2) < 12:
        return [p1, p2]
        
    dx = 1 if x2 > x1 else -1
    dy = 1 if y2 > y1 else -1
    
    if orientacion == "horizontal":
        x_mid = (x1 + x2) / 2
        # Limitar dinámicamente el radio de curvatura para evitar colapsos visuales si están muy cerca
        r = min(r, abs(x_mid - x1) - 1, abs(y2 - y1) / 2 - 1)
        if r < 4:
            return [p1, (x_mid, y1), (x_mid, y2), p2]
            
        puntos = [p1]
        
        # Esquina 1 (Bezier cuadrática: horizontal -> vertical)
        p0 = (x_mid - dx * r, y1)
        p1_ctrl = (x_mid, y1)
        p2_end = (x_mid, y1 + dy * r)
        
        puntos.append(p0)
        for step in range(1, 6):
            t = step / 5.0
            bx = (1-t)**2 * p0[0] + 2*(1-t)*t * p1_ctrl[0] + t**2 * p2_end[0]
            by = (1-t)**2 * p0[1] + 2*(1-t)*t * p1_ctrl[1] + t**2 * p2_end[1]
            puntos.append((bx, by))
            
        # Esquina 2 (Bezier cuadrática: vertical -> horizontal)
        q0 = (x_mid, y2 - dy * r)
        q1_ctrl = (x_mid, y2)
        q2_end = (x_mid + dx * r, y2)
        
        puntos.append(q0)
        for step in range(1, 6):
            t = step / 5.0
            qx = (1-t)**2 * q0[0] + 2*(1-t)*t * q1_ctrl[0] + t**2 * q2_end[0]
            qy = (1-t)**2 * q0[1] + 2*(1-t)*t * q1_ctrl[1] + t**2 * q2_end[1]
            puntos.append((qx, qy))
            
        puntos.append(p2)
        return puntos
    else:
        # Ruta vertical primero (viaja vertical -> horizontal -> vertical)
        y_mid = (y1 + y2) / 2
        r = min(r, abs(y_mid - y1) - 1, abs(x2 - x1) / 2 - 1)
        if r < 4:
            return [p1, (x1, y_mid), (x2, y_mid), p2]
            
        puntos = [p1]
        
        # Esquina 1 (Bezier cuadrática: vertical -> horizontal)
        p0 = (x1, y_mid - dy * r)
        p1_ctrl = (x1, y_mid)
        p2_end = (x1 + dx * r, y_mid)
        
        puntos.append(p0)
        for step in range(1, 6):
            t = step / 5.0
            bx = (1-t)**2 * p0[0] + 2*(1-t)*t * p1_ctrl[0] + t**2 * p2_end[0]
            by = (1-t)**2 * p0[1] + 2*(1-t)*t * p1_ctrl[1] + t**2 * p2_end[1]
            puntos.append((bx, by))
            
        # Esquina 2 (Bezier cuadrática: horizontal -> vertical)
        q0 = (x2 - dx * r, y_mid)
        q1_ctrl = (x2, y_mid)
        q2_end = (x2, y_mid + dy * r)
        
        puntos.append(q0)
        for step in range(1, 6):
            t = step / 5.0
            qx = (1-t)**2 * q0[0] + 2*(1-t)*t * q1_ctrl[0] + t**2 * q2_end[0]
            qy = (1-t)**2 * q0[1] + 2*(1-t)*t * q1_ctrl[1] + t**2 * q2_end[1]
            puntos.append((qx, qy))
            
        puntos.append(p2)
        return puntos

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
        
        # Atributos del modelo de selección nativa
        self.indice_cursor = len(self.texto)
        self.indice_seleccion_inicio = len(self.texto)
        
        # Atributos de rotación
        self.angulo = 0.0          
        self.angulo_offset = 0.0   

    def obtener_punto_rotacion(self):
        """Retorna las coordenadas de mundo del tirador de rotación superior."""
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
        
        # --- A. DIBUJAR CUERPO ROTADO ---
        if self.forma == "rectangulo":
            w, h = self.rect.width, self.rect.height
            surf_shape = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
            rect_local = pygame.Rect(4, 4, w, h)
            
            radio_redondeo = min(12, h // 2)
            
            pygame.draw.rect(surf_shape, color, rect_local, border_radius=radio_redondeo)
            pygame.draw.rect(surf_shape, self.color_borde, rect_local, 2, border_radius=radio_redondeo)
            
            surf_rotada = pygame.transform.rotate(surf_shape, -self.angulo)
            pos_dibujo = surf_rotada.get_rect(center=centro_pantalla)
            pantalla.blit(surf_rotada, pos_dibujo)
            
        elif self.forma == "rombo":
            puntos_rombo = [
                (self.rect.centerx, self.rect.top),
                (self.rect.right, self.rect.centery),
                (self.rect.centerx, self.rect.bottom),
                (self.rect.left, self.rect.centery)
            ]
            puntos_rotados = [rotar_punto(p, centro_mundo, self.angulo) for p in puntos_rombo]
            puntos_pantalla = [(p[0] - ox, p[1] - oy) for p in puntos_rotados]
            pygame.draw.polygon(pantalla, color, puntos_pantalla)
            pygame.draw.polygon(pantalla, self.color_borde, puntos_pantalla, 2)
            
        elif self.forma == "linea":
            p_inicio = rotar_punto((self.rect.centerx, self.rect.top + 5), centro_mundo, self.angulo)
            p_fin = rotar_punto((self.rect.centerx, self.rect.bottom - 5), centro_mundo, self.angulo)
            p_ini_p = (p_inicio[0] - ox, p_inicio[1] - oy)
            p_fin_p = (p_fin[0] - ox, p_fin[1] - oy)
            pygame.draw.line(pantalla, color, p_ini_p, p_fin_p, 4)
            pygame.draw.rect(pantalla, color, pygame.Rect(p_ini_p[0] - 4, p_ini_p[1] - 4, 8, 8))
            pygame.draw.rect(pantalla, color, pygame.Rect(p_fin_p[0] - 4, p_fin_p[1] - 4, 8, 8))
            
        elif self.forma == "texto" and (self.seleccionado or self.editando):
            esquinas = [self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft]
            esquinas_rotadas = [rotar_punto(p, centro_mundo, self.angulo) for p in esquinas]
            puntos_pantalla = [(p[0] - ox, p[1] - oy) for p in esquinas_rotadas]
            pygame.draw.polygon(pantalla, (200, 200, 200), puntos_pantalla, 1)

        # --- B. RENDERIZAR TEXTO MULTILÍNEA ROTADO ---
        color_letras = self.color_base if self.forma == "texto" else (30, 30, 30) 
        
        lineas = self.texto.split("\n")
        altura_linea = fuente.get_linesize()
        ancho_max_texto = max([fuente.size(l)[0] for l in lineas]) if lineas else 0
        alto_total_texto = len(lineas) * altura_linea
        
        ancho_t = max(20, ancho_max_texto + 20)
        alto_t = max(20, alto_total_texto + 10)
        surf_temp = pygame.Surface((ancho_t, alto_t), pygame.SRCALPHA)
        
        pos_local_y = 5
        
        # 1. Pintar selección azul segmentada por línea
        sel_inicio = getattr(self, 'indice_seleccion_inicio', self.indice_cursor)
        if self.editando and sel_inicio != self.indice_cursor:
            idx_min = min(sel_inicio, self.indice_cursor)
            idx_max = max(sel_inicio, self.indice_cursor)
            line_min, col_min = descifrar_indice(self.texto, idx_min)
            line_max, col_max = descifrar_indice(self.texto, idx_max)

            for i, linea in enumerate(lineas):
                y_linea = pos_local_y + i * altura_linea
                x_linea = (ancho_t - fuente.size(linea)[0]) // 2
                if line_min <= i <= line_max:
                    c_ini = col_min if i == line_min else 0
                    c_fin = col_max if i == line_max else len(linea)
                    if line_min < i < line_max:
                        c_ini = 0
                        c_fin = len(linea)
                    x_sel_inicio = x_linea + fuente.size(linea[:c_ini])[0]
                    ancho_sel_linea = fuente.size(linea[c_ini:c_fin])[0]
                    if ancho_sel_linea == 0 and i < line_max:
                        ancho_sel_linea = 6 
                    if ancho_sel_linea > 0:
                        rect_sel = pygame.Rect(x_sel_inicio, y_linea, ancho_sel_linea, altura_linea)
                        pygame.draw.rect(surf_temp, (180, 215, 255), rect_sel, border_radius=3)
        
        # 2. Renderizar y centrar cada línea individualmente
        for i, linea in enumerate(lineas):
            y_linea = pos_local_y + i * altura_linea
            x_linea = (ancho_t - fuente.size(linea)[0]) // 2
            superficie_linea = fuente.render(linea, True, color_letras)
            surf_temp.blit(superficie_linea, (x_linea, y_linea))
        
        # 3. Pintar cursor parpadeante en su línea respectiva
        if self.editando and sel_inicio == self.indice_cursor:
            if pygame.time.get_ticks() % 1000 < 500:
                cursor_x, cursor_y = obtener_coordenadas_local(self.texto, self.indice_cursor, fuente, ancho_t, pos_local_y, altura_linea)
                pygame.draw.line(surf_temp, color_letras, (cursor_x, cursor_y), (cursor_x, cursor_y + altura_linea), 2)
        
        # 4. Rotar el bloque completo
        surf_rotada = pygame.transform.rotate(surf_temp, -self.angulo)
        
        # 5. Dibujar en la pantalla
        if self.forma == "linea":
            desplazamiento = rotar_punto((centro_mundo[0], centro_mundo[1] + 12), centro_mundo, self.angulo)
            pos_texto = surf_rotada.get_rect(center=(desplazamiento[0] - ox, desplazamiento[1] - oy))
        else:
            pos_texto = surf_rotada.get_rect(center=centro_pantalla)
        
        pantalla.blit(surf_rotada, pos_texto)

        # --- C. DIBUJAR INTERFAZ DE CONTROL ---
        if self.seleccionado or self.editando:
            puntos = self.obtener_puntos_conexion()
            for pos in puntos.values():
                pos_entera = (int(pos[0] - ox), int(pos[1] - oy))
                pygame.draw.circle(pantalla, (255, 255, 255), pos_entera, int(self.radio_punto_conexion))
                pygame.draw.circle(pantalla, (50, 120, 240), pos_entera, int(self.radio_punto_conexion), 2)
            
            # 🌟 CORREGIDO: Eliminamos el 'and self.forma != "texto"' para que el texto sí dibuje sus flechitas
            if self.modo_interaccion == "arrow":
                direcciones = {
                    "arriba_izquierda": (-1, -1), "arriba_centro": (0, -1), "arriba_derecha": (1, -1),
                    "centro_izquierda": (-1, 0), "centro_derecha": (1, 0),
                    "abajo_izquierda": (-1, 1), "abajo_centro": (0, 1), "abajo_derecha": (1, 1)
                }
                r = self.rect
                puntos_originales = {
                    "arriba_izquierda": (r.left, r.top), "arriba_centro": (r.centerx, r.top), "arriba_derecha": (r.right, r.top),
                    "centro_izquierda": (r.left, r.centery), "centro_derecha": (r.right, r.centery),
                    "abajo_izquierda": (r.left, r.bottom), "abajo_centro": (r.centerx, r.bottom), "abajo_derecha": (r.right, r.bottom)
                }
                for nombre, pos_rotada in puntos.items():
                    dx, dy = direcciones[nombre]
                    pos_orig = puntos_originales[nombre]
                    destino_orig = (pos_orig[0] + dx * 16, pos_orig[1] + dy * 16)
                    destino_rotado = rotar_punto(destino_orig, centro_mundo, self.angulo)
                    
                    pos_pantalla = (pos_rotada[0] - ox, pos_rotada[1] - oy)
                    destino_pantalla = (destino_rotado[0] - ox, destino_rotado[1] - oy)
                    self._dibujar_flechita(pantalla, pos_pantalla, destino_pantalla)

            # DIBUJAR MANIJA DE ROTACIÓN "LOLLIPOP"
            p_base_manija = rotar_punto((self.rect.centerx, self.rect.top), centro_mundo, self.angulo)
            p_extremo_manija = self.obtener_punto_rotacion()
            
            p_base_p = (int(p_base_manija[0] - ox), int(p_base_manija[1] - oy))
            p_extremo_p = (int(p_extremo_manija[0] - ox), int(p_extremo_manija[1] - oy))
            
            pygame.draw.line(pantalla, (100, 100, 100), p_base_p, p_extremo_p, 2)
            pygame.draw.circle(pantalla, (255, 255, 255), p_extremo_p, 6)
            pygame.draw.circle(pantalla, (46, 204, 113), p_extremo_p, 6, 2)

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
        self.tipo = tipo  # 🌟 "recta" o "redondeada"
        
        # Atributos del modelo de selección nativa
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
        
        # 🌟 NUEVO: Ruteo inteligente basado en la dirección de salida del puerto
        orientacion = "horizontal"
        if self.punto_origen and ("arriba" in self.punto_origen or "abajo" in self.punto_origen):
            orientacion = "vertical"
            
        # 🌟 NUEVO: Generamos la ruta (recta o con curvas ortogonales de Bezier)
        if getattr(self, "tipo", "recta") == "redondeada":
            puntos_linea = obtener_ruta_redondeada(p_origen, p_destino, r=15, orientacion=orientacion)
        else:
            puntos_linea = [p_origen, p_destino]
            
        # Dibujar el trazado completo (soporta N segmentos curvados)
        if len(puntos_linea) >= 2:
            pygame.draw.lines(pantalla, COLOR_LINEA, False, puntos_linea, GROSOR)
        
        if self.pos_vacio_final and not self.seleccionada:
            pos_vacio_pantalla = (self.pos_vacio_final[0] - ox, self.pos_vacio_final[1] - oy)
            pygame.draw.circle(pantalla, (100, 100, 100), pos_vacio_pantalla, 4)
            pygame.draw.circle(pantalla, (245, 245, 245), pos_vacio_pantalla, 2)
            
        # --- RENDERIZAR TEXTO MULTILÍNEA EN LA FLECHA ---
        if fuente and (self.texto or self.editando):
            # Posición en el centro físico de la caja delimitadora
            centro_x, centro_y = (p_origen[0] + p_destino[0]) // 2, (p_origen[1] + p_destino[1]) // 2
            
            lineas = self.texto.split("\n")
            altura_linea = fuente.get_linesize()
            ancho_max_texto = max([fuente.size(l)[0] for l in lineas]) if lineas else 0
            alto_total_texto = len(lineas) * altura_linea
            
            ancho_t = max(20, ancho_max_texto + 20)
            alto_t = max(20, alto_total_texto + 10)
            surf_temp = pygame.Surface((ancho_t, alto_t), pygame.SRCALPHA)
            
            pos_local_y = 5
            
            # Pintar selección azul en la conexión
            sel_inicio = getattr(self, 'indice_seleccion_inicio', self.indice_cursor)
            if self.editando and sel_inicio != self.indice_cursor:
                idx_min = min(sel_inicio, self.indice_cursor)
                idx_max = max(sel_inicio, self.indice_cursor)
                line_min, col_min = descifrar_indice(self.texto, idx_min)
                line_max, col_max = descifrar_indice(self.texto, idx_max)

                for i, linea in enumerate(lineas):
                    y_linea = pos_local_y + i * altura_linea
                    x_linea = (ancho_t - fuente.size(linea)[0]) // 2
                    if line_min <= i <= line_max:
                        c_ini = col_min if i == line_min else 0
                        c_fin = col_max if i == line_max else len(linea)
                        if line_min < i < line_max:
                            c_ini = 0
                            c_fin = len(linea)
                        x_sel_inicio = x_linea + fuente.size(linea[:c_ini])[0]
                        ancho_sel_linea = fuente.size(linea[c_ini:c_fin])[0]
                        if ancho_sel_linea == 0 and i < line_max:
                            ancho_sel_linea = 6
                        if ancho_sel_linea > 0:
                            rect_sel = pygame.Rect(x_sel_inicio, y_linea, ancho_sel_linea, altura_linea)
                            pygame.draw.rect(surf_temp, (180, 215, 255), rect_sel, border_radius=3)
            
            # Renderizar las líneas de texto de la flecha
            for i, linea in enumerate(lineas):
                y_linea = pos_local_y + i * altura_linea
                x_linea = (ancho_t - fuente.size(linea)[0]) // 2
                superficie_linea = fuente.render(linea, True, self.color_base)
                surf_temp.blit(superficie_linea, (x_linea, y_linea))
                
            # Pintar cursor en su línea respectiva
            if self.editando and sel_inicio == self.indice_cursor:
                if pygame.time.get_ticks() % 1000 < 500:
                    cursor_x, cursor_y = obtener_coordenadas_local(self.texto, self.indice_cursor, fuente, ancho_t, pos_local_y, altura_linea)
                    pygame.draw.line(surf_temp, self.color_base, (cursor_x, cursor_y), (cursor_x, cursor_y + altura_linea), 2)
                    
            # Dibujar el fondo limpio de la conexión
            rect_texto_pantalla = surf_temp.get_rect(center=(centro_x, centro_y - 12))
            rect_fondo = rect_texto_pantalla.inflate(6, 4)
            pygame.draw.rect(pantalla, (245, 245, 245), rect_fondo)
            
            pantalla.blit(surf_temp, rect_texto_pantalla)
        
        # 🌟 NUEVO: Calculamos la orientación de la punta de la flecha usando el ÚLTIMO segmento
        p_penultimo = puntos_linea[-2]
        p_ultimo = puntos_linea[-1]
        dx = p_ultimo[0] - p_penultimo[0]
        dy = p_ultimo[1] - p_penultimo[1]
        
        angulo = math.atan2(dy, dx) if (dx != 0 or dy != 0) else 0
        LARGO_FLECHA, ANGULO_ALAS = 12, math.radians(25)
        
        flecha_ala1 = (p_ultimo[0] - LARGO_FLECHA * math.cos(angulo - ANGULO_ALAS), p_ultimo[1] - LARGO_FLECHA * math.sin(angulo - ANGULO_ALAS))
        flecha_ala2 = (p_ultimo[0] - LARGO_FLECHA * math.cos(angulo + ANGULO_ALAS), p_ultimo[1] - LARGO_FLECHA * math.sin(angulo + ANGULO_ALAS))
        pygame.draw.polygon(pantalla, COLOR_LINEA, [p_ultimo, flecha_ala1, flecha_ala2])