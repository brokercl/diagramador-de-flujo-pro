import pygame

class PanelUI:
    def __init__(self, ancho_pantalla, alto_pantalla, grosor=200, posicion='izquierda'):
        self.posicion = posicion
        self.ancho_pantalla = ancho_pantalla
        self.alto_pantalla = alto_pantalla
        
        self.rect = pygame.Rect(0, 0, grosor, alto_pantalla)
        self.items_paleta = []
        self._configurar_paleta(grosor)
        
        # Inicialización de botones responsivos
        self.btn_guardar = pygame.Rect(20, alto_pantalla - 120, 160, 40)
        self.btn_cargar = pygame.Rect(20, alto_pantalla - 60, 160, 40)
        self.redimensionar(grosor, alto_pantalla)

    def _configurar_paleta(self, grosor):
        x_base = self.rect.x + (grosor // 2) - 60

        self.items_paleta = [
            {
                "rect": pygame.Rect(x_base, 90, 120, 60), # 🌟 Incluye espacio de 50px para las pestañas
                "tipo": "Proceso",
                "forma": "rectangulo",
                "color": (173, 216, 230)
            },
            {
                "rect": pygame.Rect(x_base, 170, 120, 60),
                "tipo": "Decisión",
                "forma": "rombo",
                "color": (255, 200, 150)
            },
            {
                "rect": pygame.Rect(x_base, 250, 120, 60),
                "tipo": "Flecha",
                "forma": "linea",
                "color": (50, 120, 240)
            },
            {
                "rect": pygame.Rect(x_base, 330, 120, 60),
                "tipo": "Texto",
                "forma": "texto",
                "color": (250, 250, 250)
            }
        ]

    def redimensionar(self, nuevo_grosor, nuevo_alto):
        """🌟 NUEVO: Re-centra los ítems y adapta el ancho de los botones dinámicamente."""
        self.rect.height = nuevo_alto
        self.rect.width = nuevo_grosor
        self.alto_pantalla = nuevo_alto
        
        # Centrar los bloques de proceso, decisión, etc.
        x_base = self.rect.x + (nuevo_grosor // 2) - 60
        for item in self.items_paleta:
            item["rect"].x = x_base
            
        # Ajustar el ancho de los botones de Guardar/Cargar al espacio disponible
        ancho_btn = max(40, nuevo_grosor - 40)
        self.btn_guardar = pygame.Rect(self.rect.x + (nuevo_grosor - ancho_btn)//2, nuevo_alto - 120, ancho_btn, 40)
        self.btn_cargar = pygame.Rect(self.rect.x + (nuevo_grosor - ancho_btn)//2, nuevo_alto - 60, ancho_btn, 40)

    def dibujar(self, pantalla, fuente):
        pygame.draw.rect(pantalla, (220, 220, 225), self.rect)
        
        color_linea = (180, 180, 180)
        pygame.draw.line(pantalla, color_linea, self.rect.topright, self.rect.bottomright, 2)

        # Solo renderizamos los elementos si el panel tiene un ancho visible prudente
        if self.rect.width > 50:
            pos_mouse = pygame.mouse.get_pos()
            for item in self.items_paleta:
                grosor_borde = 3 if item["rect"].collidepoint(pos_mouse) else 2
                
                if item["forma"] == "rectangulo":
                    pygame.draw.rect(pantalla, item["color"], item["rect"], border_radius=8)
                    pygame.draw.rect(pantalla, (50, 50, 50), item["rect"], grosor_borde, border_radius=8)
                elif item["forma"] == "rombo":
                    puntos_rombo = [
                        (item["rect"].centerx, item["rect"].top),
                        (item["rect"].right, item["rect"].centery),
                        (item["rect"].centerx, item["rect"].bottom),
                        (item["rect"].left, item["rect"].centery)
                    ]
                    pygame.draw.polygon(pantalla, item["color"], puntos_rombo)
                    pygame.draw.polygon(pantalla, (50, 50, 50), puntos_rombo, grosor_borde)

                elif item["forma"] == "linea":
                    r = item["rect"]
                    cx = r.centerx
                    y_inicio = r.top + 8
                    y_fin = r.bottom - 22 
                    
                    pygame.draw.line(pantalla, item["color"], (cx, y_inicio), (cx, y_fin), 3)
                    
                    tam = 7
                    rect_sup = pygame.Rect(cx - tam//2, y_inicio - tam//2, tam, tam)
                    rect_inf = pygame.Rect(cx - tam//2, y_fin - tam//2, tam, tam)
                    
                    pygame.draw.rect(pantalla, item["color"], rect_sup)
                    pygame.draw.rect(pantalla, item["color"], rect_inf)

                elif item["forma"] == "texto":
                    r = item["rect"]
                    pygame.draw.rect(pantalla, (255, 255, 255), r, border_radius=8)
                    pygame.draw.rect(pantalla, (160, 160, 160), r, 1, border_radius=8)
                    
                    fuente_t = pygame.font.SysFont("Arial", 28, bold=True)
                    t_surf = fuente_t.render("T", True, (50, 120, 240))
                    pantalla.blit(t_surf, t_surf.get_rect(center=(r.centerx, r.centery - 6)))

                # Texto de etiqueta del botón
                superficie_texto = fuente.render(item["tipo"], True, (10, 10, 10))
                if item["forma"] in ["linea", "texto"]:
                    text_rect = superficie_texto.get_rect(center=(item["rect"].centerx, item["rect"].bottom - 8))
                else:
                    text_rect = superficie_texto.get_rect(center=item["rect"].center)
                pantalla.blit(superficie_texto, text_rect)

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

    def obtener_item_clickeado(self, pos):
        for item in self.items_paleta:
            if item["rect"].collidepoint(pos):
                return item
        return None