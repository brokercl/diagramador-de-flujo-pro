import pygame
import math
from utils.macos_palette import MacColorPicker  

class MainPanel:
    def __init__(self, ancho_pantalla, alto_pantalla, grosor=200, posicion='izquierda'):
        self.posicion = posicion
        self.rect = pygame.Rect(0, 0, grosor, alto_pantalla)
        self.ancho_original = grosor
        self.contraido = False
        self.arrastrando_borde = False
        
        # 📂 ESTADOS DE EXPANSIÓN DE CADA SECCIÓN
        self.expandida_flujo = True
        self.expandida_datos = False
        self.expandida_color = False
        
        # 📦 DEFINICIÓN DE ITEMS DE CADA SECCIÓN
        self.items_flujo = [
            {"tipo": "Proceso", "forma": "rectangulo", "color": (173, 216, 230)},
            {"tipo": "Decisión", "forma": "rombo", "color": (255, 200, 150)},
            {"tipo": "F. Recta", "forma": "estilo_recta", "color": (50, 120, 240)},
            {"tipo": "F. Curva", "forma": "estilo_curva", "color": (50, 120, 240)},
            {"tipo": "Texto", "forma": "texto", "color": (30, 30, 30)}
        ]
        self.items_datos = [
            {"tipo": "Base Datos", "forma": "rectangulo", "color": (230, 190, 255)},
            {"tipo": "Documento", "forma": "rectangulo", "color": (255, 255, 180)}
        ]
        self.colores_opciones = [
            (173, 216, 230), (255, 200, 150), (230, 190, 255), (255, 255, 180),
            (180, 255, 180), (255, 180, 180), (220, 220, 220), (255, 150, 200)
        ]

        # Inicializadores de rectángulos de control
        self.btn_toggle = pygame.Rect(0, 0, 0, 0)
        self.btn_guardar = pygame.Rect(0, 0, 0, 0)
        self.btn_cargar = pygame.Rect(0, 0, 0, 0)
        self.btn_personalizado = pygame.Rect(0, 0, 0, 0)
        
        # Cabeceras del Acordeón (Botones de colapso)
        self.header_flujo = pygame.Rect(0, 0, 0, 0)
        self.header_datos = pygame.Rect(0, 0, 0, 0)
        self.header_color = pygame.Rect(0, 0, 0, 0)
        self.bloques_color = []
        
        # Calculamos la distribución inicial
        self.actualizar_ancho(grosor)

    @property
    def panel_actual(self):
        """Le indica a main.py que el objeto contenedor es su propio panel de renderizado."""
        return self

    def conmutar_colapso(self):
        """Alterna entre colapsar el panel izquierdo a 0px o expandirlo."""
        self.contraido = not self.contraido
        nuevo_ancho = 0 if self.contraido else self.ancho_original
        self.actualizar_ancho(nuevo_ancho)

    def actualizar_ancho(self, nuevo_ancho):
        """Calcula de forma matemática la posición vertical de cada botón según qué secciones estén abiertas."""
        if nuevo_ancho < 50:
            self.contraido = True
            self.rect.width = 0
        else:
            self.contraido = False
            nuevo_ancho = max(100, min(400, nuevo_ancho))
            self.ancho_original = nuevo_ancho
            self.rect.width = nuevo_ancho
            
        self.recalcular_layout()

    def redimensionar(self, nuevo_ancho, nuevo_alto):
        """Ajusta la altura del panel al estirar la ventana de Pygame."""
        self.rect.height = nuevo_alto
        self.recalcular_layout()

    def recalcular_layout(self):
        """Mete la tijera matemática a las coordenadas de cada elemento para que se desplacen solos."""
        grosor = self.rect.width
        alto = self.rect.height
        
        by = alto // 2
        if self.contraido:
            self.btn_toggle = pygame.Rect(self.rect.right, by - 40, 25, 80)
        else:
            self.btn_toggle = pygame.Rect(self.rect.right - 25, by - 40, 25, 80)
            
        if self.contraido:
            return

        # Botones de Guardar y Cargar fijos al fondo responsivos
        ancho_btn = max(40, grosor - 40)
        self.btn_guardar = pygame.Rect(self.rect.x + (grosor - ancho_btn)//2, alto - 110, ancho_btn, 35)
        self.btn_cargar = pygame.Rect(self.rect.x + (grosor - ancho_btn)//2, alto - 60, ancho_btn, 35)
        
        # --- CÁLCULO DINÁMICO DE ALTURAS DEL ACORDEÓN ---
        y_actual = 25
        
        # 1. Grupo Flujo
        self.header_flujo = pygame.Rect(15, y_actual, grosor - 30, 28)
        y_actual += 45
        
        if self.expandida_flujo:
            for item in self.items_flujo:
                item["rect"] = pygame.Rect(self.rect.x + (grosor // 2) - 60, y_actual, 120, 50)
                y_actual += 62
            y_actual += 10
            
        # 2. Grupo Datos
        self.header_datos = pygame.Rect(15, y_actual, grosor - 30, 28)
        y_actual += 45
        
        if self.expandida_datos:
            for item in self.items_datos:
                item["rect"] = pygame.Rect(self.rect.x + (grosor // 2) - 60, y_actual, 120, 50)
                y_actual += 62
            y_actual += 10
            
        # 3. Grupo Color
        self.header_color = pygame.Rect(15, y_actual, grosor - 30, 28)
        y_actual += 45
        
        if self.expandida_color:
            self.bloques_color = []
            ancho_bloque = 65
            alto_bloque = 40
            espacio_x = max(5, (grosor - 2 * ancho_bloque) // 3)
            
            y_grid_start = y_actual
            for i, color in enumerate(self.colores_opciones):
                fila = i // 2
                columna = i % 2
                bx = self.rect.x + espacio_x + columna * (ancho_bloque + espacio_x)
                by = y_grid_start + fila * 48
                self.bloques_color.append((pygame.Rect(bx, by, ancho_bloque, alto_bloque), color))
            
            y_actual += 4 * 48
            
            # Botón "+ Más Colores..." adaptativo
            ancho_btn_p = max(40, grosor - 40)
            self.btn_personalizado = pygame.Rect(self.rect.x + (grosor - ancho_btn_p)//2, y_actual, ancho_btn_p, 35)

    def verificar_clic_area(self, pos):
        """Verifica si un clic del ratón ocurrió dentro de los límites del menú izquierdo."""
        return self.rect.collidepoint(pos) or self.btn_toggle.collidepoint(pos)

    def limitar_linea_conexion(self, pos_raton):
        """Evita que el usuario dibuje líneas de conexión cruzando el panel izquierdo."""
        x, y = pos_raton
        return max(x, self.rect.right), y

    def dibujar(self, pantalla, fuente):
        # Dibujar el panel contenedor
        pygame.draw.rect(pantalla, (220, 220, 225), self.rect)
        pygame.draw.line(pantalla, (180, 180, 180), self.rect.topright, self.rect.bottomright, 2)
        
        pos_mouse = pygame.mouse.get_pos()
        
        if not self.contraido:
            # --- DIBUJAR ACORDEÓN ---
            self.dibujar_seccion_cabecera(pantalla, fuente, "Flujo", self.header_flujo, self.expandida_flujo, pos_mouse)
            if self.expandida_flujo:
                for item in self.items_flujo:
                    self.dibujar_item_icono(pantalla, fuente, item, pos_mouse)
                    
            self.dibujar_seccion_cabecera(pantalla, fuente, "Datos", self.header_datos, self.expandida_datos, pos_mouse)
            if self.expandida_datos:
                for item in self.items_datos:
                    self.dibujar_item_icono(pantalla, fuente, item, pos_mouse)
                    
            self.dibujar_seccion_cabecera(pantalla, fuente, "Color", self.header_color, self.expandida_color, pos_mouse)
            if self.expandida_color:
                for rect, color in self.bloques_color:
                    borde = 3 if rect.collidepoint(pos_mouse) else 1
                    pygame.draw.rect(pantalla, color, rect, border_radius=6)
                    pygame.draw.rect(pantalla, (50, 50, 50), rect, borde, border_radius=6)
                
                # Botón "+ Más Colores..."
                col_btn_p = (245, 245, 245) if not self.btn_personalizado.collidepoint(pos_mouse) else (235, 235, 240)
                borde_btn_p = 2 if self.btn_personalizado.collidepoint(pos_mouse) else 1
                pygame.draw.rect(pantalla, col_btn_p, self.btn_personalizado, border_radius=8)
                pygame.draw.rect(pantalla, (80, 80, 80), self.btn_personalizado, borde_btn_p, border_radius=8)
                txt_personalizado = fuente.render("+ Más Colores...", True, (40, 40, 40))
                pantalla.blit(txt_personalizado, txt_personalizado.get_rect(center=self.btn_personalizado.center))

            # Botones Guardar y Cargar al fondo
            color_btn_g = (80, 180, 80) if not self.btn_guardar.collidepoint(pos_mouse) else (100, 200, 100)
            pygame.draw.rect(pantalla, color_btn_g, self.btn_guardar, border_radius=6)
            t_guardar = fuente.render("Guardar", True, (255, 255, 255))
            pantalla.blit(t_guardar, t_guardar.get_rect(center=self.btn_guardar.center))

            color_btn_c = (180, 130, 80) if not self.btn_cargar.collidepoint(pos_mouse) else (200, 150, 100)
            pygame.draw.rect(pantalla, color_btn_c, self.btn_cargar, border_radius=6)
            t_cargar = fuente.render("Cargar", True, (255, 255, 255))
            pantalla.blit(t_cargar, t_cargar.get_rect(center=self.btn_cargar.center))

        # Dibujar Tirador Triangular responsivo (Boceto)
        self.dibujar_toggle(pantalla, pos_mouse)

    def dibujar_seccion_cabecera(self, pantalla, fuente, nombre, rect, expandida, pos_mouse):
        """Dibuja un botón de cabecera de acordeón y el triángulo indicador de tu dibujo."""
        color_cabecera = (165, 165, 170) if rect.collidepoint(pos_mouse) else (180, 180, 185)
        pygame.draw.rect(pantalla, color_cabecera, rect, border_radius=4)
        
        # Etiqueta de la cabecera
        t_surf = fuente.render(nombre, True, (255, 255, 255))
        pantalla.blit(t_surf, t_surf.get_rect(center=rect.center))
        
        # El triángulo gris de colapso centrado abajo de la cabecera
        tx, ty = rect.centerx, rect.bottom + 8
        if expandida:
            puntos = [(tx - 8, ty - 4), (tx + 8, ty - 4), (tx, ty + 6)]
        else:
            puntos = [(tx - 4, ty - 8), (tx - 4, ty + 8), (tx + 6, ty)]
        pygame.draw.polygon(pantalla, (120, 120, 125), puntos)

    def dibujar_item_icono(self, pantalla, fuente, item, pos_mouse):
        """Dibuja con precisión el icono de cada elemento de dibujo."""
        r = item["rect"]
        grosor_borde = 3 if r.collidepoint(pos_mouse) else 2
        color = item["color"]
        forma = item["forma"]
        tipo = item["tipo"]
        
        if forma == "rectangulo":
            pygame.draw.rect(pantalla, color, r, border_radius=8)
            pygame.draw.rect(pantalla, (50, 50, 50), r, grosor_borde, border_radius=8)
        elif forma == "rombo":
            puntos_rombo = [
                (r.centerx, r.top), (r.right, r.centery), (r.centerx, r.bottom), (r.left, r.centery)
            ]
            pygame.draw.polygon(pantalla, color, puntos_rombo)
            pygame.draw.polygon(pantalla, (50, 50, 50), puntos_rombo, grosor_borde)
            
        # 🌟 NUEVO: ICONO PARA FLECHA RECTA
        elif forma == "estilo_recta":
            # Fondo de botón interactivo (tipo "herramienta" y no nodo)
            pygame.draw.rect(pantalla, (245, 245, 245), r, border_radius=8)
            pygame.draw.rect(pantalla, (180, 180, 185) if grosor_borde == 2 else (100, 150, 250), r, 2, border_radius=8)
            
            cx = r.centerx
            y_inicio = r.top + 10
            y_fin = r.bottom - 22
            pygame.draw.line(pantalla, color, (cx, y_inicio), (cx, y_fin), 3)
            # Dibujar la punta de flecha
            pygame.draw.polygon(pantalla, color, [(cx, y_fin), (cx-5, y_fin-7), (cx+5, y_fin-7)])
            
        # 🌟 NUEVO: ICONO PARA FLECHA CURVA (BEZIER)
        elif forma == "estilo_curva":
            # Fondo de botón interactivo
            pygame.draw.rect(pantalla, (245, 245, 245), r, border_radius=8)
            pygame.draw.rect(pantalla, (180, 180, 185) if grosor_borde == 2 else (100, 150, 250), r, 2, border_radius=8)
            
            cx = r.centerx
            y_inicio = r.top + 10
            y_fin = r.bottom - 22
            
            # Dibujar una curva en forma de S muy suave
            puntos = []
            for i in range(20):
                t = i / 19.0
                x = cx - 12 * math.cos(t * math.pi)
                y = y_inicio + t * (y_fin - y_inicio)
                puntos.append((x, y))
                
            pygame.draw.lines(pantalla, color, False, puntos, 3)
            # Punta de flecha apuntando hacia abajo
            px, py = puntos[-1]
            pygame.draw.polygon(pantalla, color, [(px, py), (px-5, py-7), (px+5, py-7)])
            
        elif forma == "texto":
            pygame.draw.rect(pantalla, (255, 255, 255), r, border_radius=8)
            pygame.draw.rect(pantalla, (160, 160, 165), r, 1, border_radius=8)
            
            fuente_t = pygame.font.SysFont("Arial", 24, bold=True)
            t_surf = fuente_t.render("T", True, (50, 120, 240))
            pantalla.blit(t_surf, t_surf.get_rect(center=(r.centerx, r.centery - 4)))

        # Etiqueta de texto del botón
        superficie_texto = fuente.render(tipo, True, (10, 10, 10))
        # Desplazamos el texto hacia abajo para los botones de configuración y texto
        if forma in ["linea", "texto", "estilo_recta", "estilo_curva"]:
            text_rect = superficie_texto.get_rect(center=(r.centerx, r.bottom - 10))
        else:
            text_rect = superficie_texto.get_rect(center=r.center)
        pantalla.blit(superficie_texto, text_rect)

    def dibujar_toggle(self, pantalla, pos_mouse):
        """El tirador triangular gigante del borde del panel."""
        self.btn_toggle.x = self.rect.right if self.contraido else self.rect.right - 25
        
        color_fondo = (160, 160, 165) if self.btn_toggle.collidepoint(pos_mouse) else (140, 140, 145)
        
        bx = self.rect.right
        by = self.rect.height // 2
        
        if self.contraido:
            puntos_toggle = [(bx, by - 40), (bx, by + 40), (bx + 20, by)]
        else:
            puntos_toggle = [(bx, by - 40), (bx, by + 40), (bx - 20, by)]
            
        pygame.draw.polygon(pantalla, color_fondo, puntos_toggle)
        pygame.draw.polygon(pantalla, (60, 60, 65), puntos_toggle, 1)

    def gestionar_clic(self, pos):
        """Detecta si hicieron clic en los headers para abrirlos/cerrarlos, o en el tirador."""
        if self.btn_toggle.collidepoint(pos):
            self.arrastrando_borde = True
            self.pos_inicio_clic = pos
            return "toggle"
            
        if self.contraido:
            return None
            
        # Toggles de Acordeón (Headers)
        if self.header_flujo.collidepoint(pos):
            self.expandida_flujo = not self.expandida_flujo
            self.recalcular_layout()
            return "header"
        elif self.header_datos.collidepoint(pos):
            self.expandida_datos = not self.expandida_datos
            self.recalcular_layout()
            return "header"
        elif self.header_color.collidepoint(pos):
            self.expandida_color = not self.expandida_color
            self.recalcular_layout()
            return "header"
            
        return None

    def obtener_item_clickeado(self, pos):
        """Retorna el item sobre el cual se hizo clic si su sección está expandida."""
        if self.contraido:
            return None
            
        if self.expandida_flujo:
            for item in self.items_flujo:
                if item["rect"].collidepoint(pos):
                    return item
                    
        if self.expandida_datos:
            for item in self.items_datos:
                if item["rect"].collidepoint(pos):
                    return item
                    
        return None

    def obtener_color_clickeado(self, pos):
        """Retorna el color sobre el cual se hizo clic si la sección de Color está expandida."""
        if self.contraido or not self.expandida_color:
            return None
            
        for rect, color in self.bloques_color:
            if rect.collidepoint(pos):
                return color
                
        if self.btn_personalizado.collidepoint(pos):
            color_nativo = MacColorPicker.seleccionar_color()
            if color_nativo:
                return color_nativo
                
        return None