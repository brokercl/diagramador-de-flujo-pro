import pygame

def oscurecer_fondo(pantalla, ancho, alto):
    """Guarda el fondo actual y aplica una capa semitransparente."""
    fondo_guardado = pantalla.copy()
    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120)) # Un poco más oscuro para resaltar
    pantalla.blit(overlay, (0, 0))
    return fondo_guardado

def pedir_texto_pygame(pantalla, titulo, texto_defecto=""):
    """Pop-up para ingresar texto."""
    fuente_titulo = pygame.font.Font(None, 28)
    fuente_texto = pygame.font.Font(None, 32)
    
    texto = texto_defecto
    ancho, alto = pantalla.get_size()
    caja_w, caja_h = 400, 150
    caja_x, caja_y = (ancho - caja_w) // 2, (alto - caja_h) // 2
    
    caja_rect = pygame.Rect(caja_x, caja_y, caja_w, caja_h)
    input_rect = pygame.Rect(caja_x + 20, caja_y + 60, caja_w - 40, 40)
    
    fondo_guardado = oscurecer_fondo(pantalla, ancho, alto)
    
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    return texto.strip()
                elif evento.key == pygame.K_ESCAPE:
                    return None
                elif evento.key == pygame.K_BACKSPACE:
                    texto = texto[:-1]
                else:
                    texto += evento.unicode

        pantalla.blit(fondo_guardado, (0, 0))
        oscurecer_fondo(pantalla, ancho, alto)
        
        # Dibujar UI
        pygame.draw.rect(pantalla, (240, 240, 245), caja_rect, border_radius=10)
        pygame.draw.rect(pantalla, (100, 100, 100), caja_rect, 2, border_radius=10)
        pantalla.blit(fuente_titulo.render(titulo, True, (10, 10, 10)), (caja_x + 20, caja_y + 20))
        
        pygame.draw.rect(pantalla, (255, 255, 255), input_rect, border_radius=5)
        pygame.draw.rect(pantalla, (50, 150, 255), input_rect, 2, border_radius=5)
        
        cursor = "|" if pygame.time.get_ticks() % 1000 < 500 else ""
        pantalla.blit(fuente_texto.render(texto + cursor, True, (10, 10, 10)), (input_rect.x + 10, input_rect.y + 10))
        pygame.display.flip()
        pygame.time.delay(30)

def pedir_color_pygame(pantalla, titulo):
    """Pop-up que muestra una grilla de opciones de colores para el nodo."""
    fuente_titulo = pygame.font.Font(None, 28)
    
    ancho, alto = pantalla.get_size()
    caja_w, caja_h = 360, 180
    caja_x, caja_y = (ancho - caja_w) // 2, (alto - caja_h) // 2
    caja_rect = pygame.Rect(caja_x, caja_y, caja_w, caja_h)
    
    # Lista de colores pasteles/bonitos para elegir
    colores_opciones = [
        (173, 216, 230), (255, 200, 150), (230, 190, 255), 
        (255, 255, 180), (180, 255, 180), (255, 180, 180),
        (220, 220, 220), (255, 150, 200)
    ]
    
    # Generar los rectángulos de la paleta (2 filas de 4 columnas)
    bloques = []
    for i, color in enumerate(colores_opciones):
        fila = i // 4
        columna = i % 4
        bx = caja_x + 30 + (columna * 75)
        by = caja_y + 60 + (fila * 55)
        bloques.append((pygame.Rect(bx, by, 60, 40), color))
        
    fondo_guardado = oscurecer_fondo(pantalla, ancho, alto)
    
    while True:
        pos_mouse = pygame.mouse.get_pos()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return None
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    # Si hace clic en un color, lo devuelve de inmediato
                    for rect, color in bloques:
                        if rect.collidepoint(pos_mouse):
                            return color
                    # Si hace clic fuera de la caja, cancela
                    if not caja_rect.collidepoint(pos_mouse):
                        return None

        pantalla.blit(fondo_guardado, (0, 0))
        oscurecer_fondo(pantalla, ancho, alto)
        
        # Dibujar UI de la caja
        pygame.draw.rect(pantalla, (240, 240, 245), caja_rect, border_radius=10)
        pygame.draw.rect(pantalla, (100, 100, 100), caja_rect, 2, border_radius=10)
        pantalla.blit(fuente_titulo.render(titulo, True, (10, 10, 10)), (caja_x + 20, caja_y + 20))
        
        # Dibujar los botones de colores
        for rect, color in bloques:
            borde = 3 if rect.collidepoint(pos_mouse) else 1
            pygame.draw.rect(pantalla, color, rect, border_radius=5)
            pygame.draw.rect(pantalla, (50, 50, 50), rect, borde, border_radius=5)
            
        pygame.display.flip()
        pygame.time.delay(30)