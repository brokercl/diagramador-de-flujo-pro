import pygame
from utils.macos_palette import MacColorPicker  

class ColorsPallet:
    def __init__(self, ancho_pantalla, alto_pantalla, grosor=200):
        self.rect = pygame.Rect(0, 0, grosor, alto_pantalla)
        
        # Botones inferiores responsivos
        self.btn_guardar = pygame.Rect(20, alto_pantalla - 120, 160, 40)
        self.btn_cargar = pygame.Rect(20, alto_pantalla - 60, 160, 40)
        
        # Paleta de colores pasteles base
        self.colores_opciones = [
            (173, 216, 230), (255, 200, 150), (230, 190, 255), (255, 255, 180),
            (180, 255, 180), (255, 180, 180), (220, 220, 220), (255, 150, 200)
        ]
        
        self.btn_personalizado = pygame.Rect(25, 350, 150, 40)
        self.bloques = []
        
        # Auto-configurar posiciones iniciales usando redimensionar
        self.redimensionar(grosor, alto_pantalla)

    def redimensionar(self, nuevo_grosor, nuevo_alto):
        """🌟 NUEVO: Reconstruye la grilla de colores de forma simétrica según el ancho del panel."""
        self.rect.height = nuevo_alto
        self.rect.width = nuevo_grosor
        
        # Reconstruir bloques de la grilla (2 columnas) adaptativos
        self.bloques = []
        ancho_bloque = 70
        alto_bloque = 45
        
        # Calculamos un espaciado horizontal dinámico
        espacio_x = max(5, (nuevo_grosor - 2 * ancho_bloque) // 3)
        
        for i, color in enumerate(self.colores_opciones):
            fila = i // 2
            columna = i % 2
            bx = self.rect.x + espacio_x + columna * (ancho_bloque + espacio_x)
            by = 100 + (fila * 60)
            self.bloques.append((pygame.Rect(bx, by, ancho_bloque, alto_bloque), color))
        
        # Botón personalizado dinámico
        ancho_btn_p = max(40, nuevo_grosor - 40)
        self.btn_personalizado = pygame.Rect(self.rect.x + (nuevo_grosor - ancho_btn_p)//2, 350, ancho_btn_p, 40)
        
        # Botones inferiores fijos dinámicos
        ancho_btn = max(40, nuevo_grosor - 40)
        self.btn_guardar = pygame.Rect(self.rect.x + (nuevo_grosor - ancho_btn)//2, nuevo_alto - 120, ancho_btn, 40)
        self.btn_cargar = pygame.Rect(self.rect.x + (nuevo_grosor - ancho_btn)//2, nuevo_alto - 60, ancho_btn, 40)

    def dibujar(self, pantalla, fuente):
        pygame.draw.rect(pantalla, (220, 220, 225), self.rect)
        pygame.draw.line(pantalla, (180, 180, 180), self.rect.topright, self.rect.bottomright, 2)
        
        # Dibujamos solo si hay espacio suficiente para no encimar textos
        if self.rect.width > 50:
            txt_titulo = fuente.render("Color de Elemento", True, (60, 60, 60))
            pantalla.blit(txt_titulo, (20, 65))
            
            pos_mouse = pygame.mouse.get_pos()
            
            # Dibujar grilla
            for rect, color in self.bloques:
                borde = 3 if rect.collidepoint(pos_mouse) else 1
                pygame.draw.rect(pantalla, color, rect, border_radius=6)
                pygame.draw.rect(pantalla, (50, 50, 50), rect, borde, border_radius=6)
                
            # Botón personalizado
            col_btn_p = (245, 245, 245) if not self.btn_personalizado.collidepoint(pos_mouse) else (235, 235, 240)
            borde_btn_p = 2 if self.btn_personalizado.collidepoint(pos_mouse) else 1
            pygame.draw.rect(pantalla, col_btn_p, self.btn_personalizado, border_radius=8)
            pygame.draw.rect(pantalla, (80, 80, 80), self.btn_personalizado, borde_btn_p, border_radius=8)
            
            txt_personalizado = fuente.render("+ Más Colores...", True, (40, 40, 40))
            pantalla.blit(txt_personalizado, txt_personalizado.get_rect(center=self.btn_personalizado.center))

            # Botón Guardar
            color_btn_g = (80, 180, 80) if not self.btn_guardar.collidepoint(pos_mouse) else (100, 200, 100)
            pygame.draw.rect(pantalla, color_btn_g, self.btn_guardar, border_radius=6)
            t_guardar = fuente.render("Guardar", True, (255, 255, 255))
            pantalla.blit(t_guardar, t_guardar.get_rect(center=self.btn_guardar.center))

            # Botón Cargar
            color_btn_c = (180, 130, 80) if not self.btn_cargar.collidepoint(pos_mouse) else (200, 150, 100)
            pygame.draw.rect(pantalla, color_btn_c, self.btn_cargar, border_radius=6)
            t_cargar = fuente.render("Cargar", True, (255, 255, 255))
            pantalla.blit(t_cargar, t_cargar.get_rect(center=self.btn_cargar.center))

    def obtener_color_clickeado(self, pos):
        for rect, color in self.bloques:
            if rect.collidepoint(pos):
                return color
                
        if self.btn_personalizado.collidepoint(pos):
            color_nativo = MacColorPicker.seleccionar_color()
            if color_nativo:
                return color_nativo
                
        return None