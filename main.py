import pygame
import sys
import math
import subprocess

from elements import Nodo, Conexion
from mainPanel import MainPanel
from save import guardar_diagrama, cargar_diagrama

def obtener_portapapeles_mac():
    """Obtiene el texto del portapapeles nativo de macOS con fallback."""
    try:
        if sys.platform == "darwin":
            return subprocess.check_output('pbpaste', text=True, env={'LANG': 'en_US.UTF-8'})
        else:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            text = root.clipboard_get()
            root.destroy()
            return text
    except Exception:
        return ""

def guardar_portapapeles_mac(texto):
    """Guarda texto en el portapapeles nativo de macOS con fallback."""
    try:
        if sys.platform == "darwin":
            subprocess.run(['pbcopy'], input=texto, text=True, check=True)
        else:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(texto)
            root.update()
            root.destroy()
    except Exception:
        pass

def calcular_indice_click(obj, mouse_x, mouse_y, camara_x, camara_y, fuente):
    """Calcula el índice del caracter clickeado en un espacio multilínea basado en coordenadas píxel."""
    ox, oy = camara_x, camara_y
    if isinstance(obj, Nodo):
        rect_pantalla = obj.rect.move(-ox, -oy)
        if obj.forma == "linea":
            centro_ref = (rect_pantalla.centerx, rect_pantalla.bottom + 12)
        else:
            centro_ref = rect_pantalla.center
    else:
        puntos = obj.obtener_todos_los_puntos()
        if len(puntos) < 2: return 0
        p_origen = (puntos[0][0] - ox, puntos[0][1] - oy)
        p_destino = (puntos[1][0] - ox, puntos[1][1] - oy)
        centro_ref = ((p_origen[0] + p_destino[0]) // 2, (p_origen[1] + p_destino[1]) // 2 - 12)

    lineas = obj.texto.split("\n")
    altura_linea = fuente.get_linesize()
    alto_total = len(lineas) * altura_linea
    ancho_max = max([fuente.size(l)[0] for l in lineas]) if lineas else 0
    
    # Delimitamos la caja virtual que encierra a todas las líneas
    rect_texto = pygame.Rect(0, 0, ancho_max, alto_total)
    rect_texto.center = centro_ref

    # 1. Encontrar la línea vertical clickeada
    y_relativo = mouse_y - rect_texto.top
    line_idx = int(y_relativo // altura_linea)
    line_idx = max(0, min(line_idx, len(lineas) - 1))

    # 2. Encontrar el caracter dentro de la línea
    linea_target = lineas[line_idx] if line_idx < len(lineas) else ""
    ancho_linea = fuente.size(linea_target)[0]
    
    # El eje X de inicio de esta línea específica centrado
    x_inicio_linea = rect_texto.centerx - (ancho_linea // 2)
    x_relativo = mouse_x - x_inicio_linea
    
    col_idx = len(linea_target)
    if x_relativo > 0:
        ancho_acumulado = 0
        for i, char in enumerate(linea_target):
            ancho_char = fuente.size(char)[0]
            if x_relativo < ancho_acumulado + (ancho_char / 2):
                col_idx = i
                break
            ancho_acumulado += ancho_char
            
    # 3. Mapear columna y línea a un índice absoluto del string 1D con '\n'
    indice_abs = 0
    for i in range(line_idx):
        indice_abs += len(lineas[i]) + 1 # +1 por el '\n'
    indice_abs += col_idx
    return indice_abs

def borrar_seleccion(obj):
    """Borra el fragmento de texto seleccionado y reacomoda el cursor."""
    if hasattr(obj, 'indice_seleccion_inicio') and obj.indice_seleccion_inicio != obj.indice_cursor:
        idx_min = min(obj.indice_seleccion_inicio, obj.indice_cursor)
        idx_max = max(obj.indice_seleccion_inicio, obj.indice_cursor)
        obj.texto = obj.texto[:idx_min] + obj.texto[idx_max:]
        obj.indice_cursor = idx_min
        obj.indice_seleccion_inicio = obj.indice_cursor
        return True
    return False

def principal():
    pygame.font.init() 
    pygame.init()

    # VARIABLES DE CÁMARA PARA EL LIENZO INFINITO
    camara_x = 0
    camara_y = 0
    arrastrando_lienzo = False
    ultima_pos_mouse = (0, 0)

    ANCHO, ALTO = 1024, 768
    pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
    pygame.display.set_caption("Diagramador de Flujo Pro")

    fuente = pygame.font.Font(None, 24)
    reloj = pygame.time.Clock()

    panel = MainPanel(ANCHO, ALTO, grosor=200, posicion='izquierda')

    # Almacenamiento del lienzo de trabajo
    nodos = []
    conexiones = []
    
    # Estados de arrastre y redimensionamiento de Nodos
    nodo_arrastrado = None
    offset_x, offset_y = 0, 0
    pos_inicial_clic = (0, 0)
    
    nodo_redimensionando = None
    punto_redimension_nombre = None
    
    # Estado de control para rotación activa
    nodo_rotando = None 
    
    # 🌟 MEMORIA DEL ESTILO DE FLECHA ELEGIDO (recta o redondeada)
    estilo_conexion_global = "recta" 
    
    # Estados de lanzamiento de flechas
    nodo_origen_flecha = None
    llave_punto_origen = None
    flecha_origen_flecha = None 
    
    # Foco interactivo general
    conexion_seleccionada = None
    nodo_editando = None
    ultimo_clic_tiempo = 0
    archivo_actual = "" 
    
    # Estado para el arrastre de selección de texto
    estado_arrastrando_texto = False

    while True:
        pantalla.fill((245, 245, 245))

        # --- 🔄 BUCLE ÚNICO Y UNIFICADO DE EVENTOS DE PYGAME ---
        for evento in pygame.event.get():
            
            # 1. Salida del sistema
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # 2. Redimensión de la ventana
            elif evento.type == pygame.VIDEORESIZE:
                ANCHO, ALTO = evento.w, evento.h
                pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
                panel.redimensionar(ANCHO, ALTO)

            # 3. Teclado (Edición avanzada de texto)
            elif evento.type == pygame.KEYDOWN:
                conexion_editando = next((c for c in conexiones if c.editando), None)
                obj_edit = conexion_editando if conexion_editando else (nodo_editando if (nodo_editando and nodo_editando.editando) else None)
                
                if obj_edit:
                    if not hasattr(obj_edit, 'indice_seleccion_inicio'):
                        obj_edit.indice_seleccion_inicio = len(obj_edit.texto)
                    if not hasattr(obj_edit, 'indice_cursor'):
                        obj_edit.indice_cursor = len(obj_edit.texto)
                    
                    obj_edit.indice_cursor = max(0, min(len(obj_edit.texto), obj_edit.indice_cursor))
                    obj_edit.indice_seleccion_inicio = max(0, min(len(obj_edit.texto), obj_edit.indice_seleccion_inicio))

                    mods = pygame.key.get_mods()
                    is_cmd = (mods & pygame.KMOD_META) or (mods & pygame.KMOD_CTRL)
                    is_alt = (mods & pygame.KMOD_LALT) or (mods & pygame.KMOD_RALT)

                    # Navegación con flecha izquierda
                    if evento.key == pygame.K_LEFT:
                        if obj_edit.indice_seleccion_inicio != obj_edit.indice_cursor:
                            obj_edit.indice_cursor = min(obj_edit.indice_seleccion_inicio, obj_edit.indice_cursor)
                        else:
                            obj_edit.indice_cursor = max(0, obj_edit.indice_cursor - 1)
                        obj_edit.indice_seleccion_inicio = obj_edit.indice_cursor
                        continue
                    
                    # Navegación con flecha derecha
                    elif evento.key == pygame.K_RIGHT:
                        if obj_edit.indice_seleccion_inicio != obj_edit.indice_cursor:
                            obj_edit.indice_cursor = max(obj_edit.indice_seleccion_inicio, obj_edit.indice_cursor)
                        else:
                            obj_edit.indice_cursor = min(len(obj_edit.texto), obj_edit.indice_cursor + 1)
                        obj_edit.indice_seleccion_inicio = obj_edit.indice_cursor
                        continue

                    # Atajos de Cmd en macOS
                    if is_cmd:
                        if evento.key == pygame.K_a: # Seleccionar Todo
                            obj_edit.indice_seleccion_inicio = 0
                            obj_edit.indice_cursor = len(obj_edit.texto)
                            continue
                        elif evento.key == pygame.K_c: # Copiar
                            if obj_edit.indice_seleccion_inicio != obj_edit.indice_cursor:
                                idx_min = min(obj_edit.indice_seleccion_inicio, obj_edit.indice_cursor)
                                idx_max = max(obj_edit.indice_seleccion_inicio, obj_edit.indice_cursor)
                                guardar_portapapeles_mac(obj_edit.texto[idx_min:idx_max])
                            else:
                                guardar_portapapeles_mac(obj_edit.texto)
                            continue
                        elif evento.key == pygame.K_v: # Pegar
                            texto_pegar = obtener_portapapeles_mac()
                            if texto_pegar:
                                borrar_seleccion(obj_edit)
                                obj_edit.texto = obj_edit.texto[:obj_edit.indice_cursor] + texto_pegar + obj_edit.texto[obj_edit.indice_cursor:]
                                obj_edit.indice_cursor += len(texto_pegar)
                                obj_edit.indice_seleccion_inicio = obj_edit.indice_cursor
                            continue
                        elif evento.key == pygame.K_BACKSPACE: # Borrar toda la línea
                            obj_edit.texto = ""
                            obj_edit.indice_cursor = 0
                            obj_edit.indice_seleccion_inicio = 0
                            continue

                    # Option + Backspace (Borrar palabra completa)
                    elif is_alt and evento.key == pygame.K_BACKSPACE:
                        if not borrar_seleccion(obj_edit):
                            antes = obj_edit.texto[:obj_edit.indice_cursor].rstrip()
                            ultimo_espacio = antes.rfind(" ")
                            nuevo_antes = "" if ultimo_espacio == -1 else antes[:ultimo_espacio + 1]
                            obj_edit.texto = nuevo_antes + obj_edit.texto[obj_edit.indice_cursor:]
                            obj_edit.indice_cursor = len(nuevo_antes)
                            obj_edit.indice_seleccion_inicio = obj_edit.indice_cursor
                        continue

                    # ESCAPE: Confirma y sale del modo edición
                    if evento.key == pygame.K_ESCAPE:
                        obj_edit.editando = False
                        obj_edit.indice_seleccion_inicio = obj_edit.indice_cursor
                        if obj_edit == nodo_editando:
                            nodo_editando = None
                        continue
                    
                    # RETURN (ENTER): Inserta un salto de línea real (\n)
                    elif evento.key == pygame.K_RETURN:
                        borrar_seleccion(obj_edit)
                        obj_edit.texto = obj_edit.texto[:obj_edit.indice_cursor] + "\n" + obj_edit.texto[obj_edit.indice_cursor:]
                        obj_edit.indice_cursor += 1
                        obj_edit.indice_seleccion_inicio = obj_edit.indice_cursor
                        continue
                    
                    # Backspace simple
                    elif evento.key == pygame.K_BACKSPACE:
                        if not borrar_seleccion(obj_edit) and obj_edit.indice_cursor > 0:
                            obj_edit.texto = obj_edit.texto[:obj_edit.indice_cursor - 1] + obj_edit.texto[obj_edit.indice_cursor:]
                            obj_edit.indice_cursor -= 1
                            obj_edit.indice_seleccion_inicio = obj_edit.indice_cursor
                        continue

                    # Delete (Suprimir) hacia adelante
                    elif evento.key == pygame.K_DELETE:
                        if not borrar_seleccion(obj_edit) and obj_edit.indice_cursor < len(obj_edit.texto):
                            obj_edit.texto = obj_edit.texto[:obj_edit.indice_cursor] + obj_edit.texto[obj_edit.indice_cursor + 1:]
                        continue
                    
                    # Escritura de caracteres normales
                    else:
                        if evento.unicode and evento.unicode.isprintable():
                            borrar_seleccion(obj_edit)
                            obj_edit.texto = obj_edit.texto[:obj_edit.indice_cursor] + evento.unicode + obj_edit.texto[obj_edit.indice_cursor:]
                            obj_edit.indice_cursor += 1
                            obj_edit.indice_seleccion_inicio = obj_edit.indice_cursor
                                
                else:
                    # Borrado de elementos del lienzo
                    if evento.key == pygame.K_BACKSPACE or evento.key == pygame.K_DELETE:
                        if conexion_seleccionada:
                            if conexion_seleccionada in conexiones: conexiones.remove(conexion_seleccionada)
                            conexiones = [c for c in conexiones if c.origen_es_flecha != conexion_seleccionada]
                            conexion_seleccionada = None
                        else:
                            nodo_a_borrar = next((n for n in nodos if n.seleccionado), None)
                            if nodo_a_borrar:
                                nodos.remove(nodo_a_borrar)
                                conexiones = [c for c in conexiones if c.origen != nodo_a_borrar and c.destino != nodo_a_borrar]
                                if nodo_a_borrar == nodo_editando: nodo_editando = None
                                nodo_arrastrado = None

            # 4. Clic Inicial (Raton Abajo)
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                pos_mundo = (pos[0] + camara_x, pos[1] + camara_y)
                
                # Clic Derecho: Navegación de cámara
                if evento.button == 3:
                    if pos[0] > panel.rect.right:
                        arrastrando_lienzo = True
                        ultima_pos_mouse = pos

                # Clic Izquierdo: Selección e interacción
                elif evento.button == 1: 
                    clic_en_nodo = False
                    clic_en_linea = False
                    clic_en_rotacion = False
                    pos_inicial_clic = pos 

                    # CASO A: Click en el panel o acordeón lateral
                    if panel.verificar_clic_area(pos):
                        if panel.gestionar_clic(pos): continue 
                        
                        if panel.btn_guardar.collidepoint(pos):
                            archivo_actual = guardar_diagrama(nodos, conexiones, pantalla, archivo_actual)
                        elif panel.btn_cargar.collidepoint(pos):
                            n_nodos, n_conexiones, n_archivo = cargar_diagrama(pantalla)
                            if n_nodos is not None:
                                nodos, conexiones, archivo_actual = n_nodos, n_conexiones, n_archivo
                                nodo_arrastrado = nodo_redimensionando = nodo_origen_flecha = nodo_editando = None
                                flecha_origen_flecha = conexion_seleccionada = None
                        
                        color_elegido = panel.obtener_color_clickeado(pos)
                        if color_elegido:
                            for nodo in nodos:
                                if nodo.seleccionado: nodo.color_base = color_elegido
                            for c in conexiones:
                                if c.seleccionada: c.color_base = color_elegido
                        else:
                            item = panel.obtener_item_clickeado(pos)
                            if item:
                                forma_item = item.get("forma", "")
                                
                                # 🌟 NUEVO: Si tocan los botones de estilo, cambiar el modo en vez de crear nodo
                                if forma_item == "estilo_recta":
                                    estilo_conexion_global = "recta"
                                    if conexion_seleccionada:
                                        conexion_seleccionada.tipo = "recta"
                                        
                                elif forma_item == "estilo_curva":
                                    estilo_conexion_global = "redondeada"
                                    if conexion_seleccionada:
                                        conexion_seleccionada.tipo = "redondeada"
                                        
                                else:
                                    # Crear nodo normal
                                    nuevo_nodo = Nodo(pos_mundo[0], pos_mundo[1], f"{item['tipo']} {len(nodos) + 1}", forma=forma_item)
                                    nuevo_nodo.color_base = item.get("color", (200, 200, 200))
                                    for n in nodos: n.seleccionado = False
                                    nodos.append(nuevo_nodo)
                                    nodo_arrastrado = nuevo_nodo
                                    nuevo_nodo.seleccionado = True
                                    offset_x, offset_y = nuevo_nodo.rect.x - pos_mundo[0], nuevo_nodo.rect.y - pos_mundo[1]
                                    conexion_seleccionada = None
                    
                    # CASO B: Click en el lienzo de trabajo
                    else:
                        # Clic en puntas sueltas de flechas
                        for c in reversed(conexiones):
                            if c.verificar_clic_punta_suelta(pos_mundo):
                                flecha_origen_flecha = c
                                clic_en_linea = True
                                conexion_seleccionada = None
                                break

                        # Detectar clic en tirador de rotación (Lollipop)
                        if not flecha_origen_flecha:
                            for nodo in reversed(nodos):
                                if nodo.seleccionado:
                                    p_manija = nodo.obtener_punto_rotacion()
                                    if math.hypot(pos_mundo[0] - p_manija[0], pos_mundo[1] - p_manija[1]) <= 10:
                                        nodo_rotando = nodo
                                        dx = pos_mundo[0] - nodo.rect.centerx
                                        dy = pos_mundo[1] - nodo.rect.centery
                                        angulo_raton = math.degrees(math.atan2(dy, dx))
                                        nodo_rotando.angulo_offset = nodo.angulo - angulo_raton
                                        clic_en_rotacion = True
                                        clic_en_nodo = True
                                        conexion_seleccionada = None
                                        break

                        # Clic en puntos de anclaje
                        if not clic_en_rotacion and not flecha_origen_flecha:
                            for nodo in reversed(nodos):
                                if nodo.seleccionado:
                                    punto_nombre = nodo.verificar_clic_puntos(pos_mundo)
                                    if punto_nombre:
                                        clic_en_nodo = True
                                        conexion_seleccionada = None
                                        if nodo.modo_interaccion == "resize":
                                            nodo_redimensionando = nodo
                                            punto_redimension_nombre = punto_nombre
                                        else:
                                            nodo_origen_flecha = nodo
                                            llave_punto_origen = punto_nombre
                                        break
                        
                        # Clic en el cuerpo de un nodo
                        if not clic_en_nodo and not flecha_origen_flecha and not clic_en_rotacion:
                            for nodo in reversed(nodos):
                                if nodo.rect.collidepoint(pos_mundo):
                                    clic_en_nodo = True
                                    conexion_seleccionada = None
                                    tiempo_actual = pygame.time.get_ticks()
                                    
                                    if nodo == nodo_editando and nodo.editando:
                                        idx = calcular_indice_click(nodo, pos[0], pos[1], camara_x, camara_y, fuente)
                                        if tiempo_actual - ultimo_clic_tiempo < 400:
                                            nodo.indice_seleccion_inicio = 0
                                            nodo.indice_cursor = len(nodo.texto)
                                        else:
                                            nodo.indice_cursor = idx
                                            nodo.indice_seleccion_inicio = idx
                                            estado_arrastrando_texto = True
                                    else:
                                        if nodo_editando: 
                                            nodo_editando.editando = False
                                        nodo_editando = nodo
                                        
                                        if tiempo_actual - ultimo_clic_tiempo < 400: 
                                            nodo.editando = True
                                            nodo.indice_seleccion_inicio = 0
                                            nodo.indice_cursor = len(nodo.texto)
                                        else:
                                            nodo_arrastrado = nodo
                                            offset_x, offset_y = nodo.rect.x - pos_mundo[0], nodo.rect.y - pos_mundo[1]
                                        
                                        mods = pygame.key.get_mods()
                                        if not (mods & pygame.KMOD_SHIFT):
                                            if not nodo.seleccionado:
                                                for n in nodos: n.seleccionado = False
                                        nodo.seleccionado = True
                                        
                                    ultimo_clic_tiempo = tiempo_actual
                                    break 
                        
                        # Clic en el texto o trazado de una línea
                        if not clic_en_nodo and not clic_en_linea and not clic_en_rotacion:
                            mods = pygame.key.get_mods()
                            if not (mods & pygame.KMOD_SHIFT):
                                for n in nodos: n.seleccionado = False
                            if nodo_editando: 
                                nodo_editando.editando = False
                                nodo_editando = None
                                
                            conexion_seleccionada = None 
                            for c in reversed(conexiones):
                                if c.verificar_clic_linea(pos_mundo):
                                    conexion_seleccionada = c
                                    clic_en_linea = True
                                    
                                    for conn in conexiones:
                                        if conn != c:
                                            conn.seleccionada = False
                                            conn.editando = False
                                            
                                    tiempo_actual = pygame.time.get_ticks()
                                    if c.seleccionada and c.editando:
                                        idx = calcular_indice_click(c, pos[0], pos[1], camara_x, camara_y, fuente)
                                        if tiempo_actual - ultimo_clic_tiempo < 400:
                                            c.indice_seleccion_inicio = 0
                                            c.indice_cursor = len(c.texto)
                                        else:
                                            c.indice_cursor = idx
                                            c.indice_seleccion_inicio = idx
                                            estado_arrastrando_texto = True
                                    else:
                                        if tiempo_actual - ultimo_clic_tiempo < 400:
                                            c.editando = True
                                            c.indice_seleccion_inicio = 0
                                            c.indice_cursor = len(c.texto)
                                        else:
                                            c.indice_cursor = len(c.texto)
                                            c.indice_seleccion_inicio = len(c.texto)
                                            
                                    ultimo_clic_tiempo = tiempo_actual
                                    c.seleccionada = True
                                    break
                                        
                        # Clic en el vacío (Deseleccionar todo)
                        if not clic_en_nodo and not clic_en_linea and not clic_en_rotacion:
                            for n in nodos: n.seleccionado = False
                            for conn in conexiones: 
                                conn.seleccionada = False
                                conn.editando = False
                            conexion_seleccionada = None

            # 5. Soltar Clic (Raton Arriba)
            elif evento.type == pygame.MOUSEBUTTONUP:
                if evento.button == 3:
                    arrastrando_lienzo = False
                elif evento.button == 1:
                    pos = pygame.mouse.get_pos()
                    pos_mundo = (pos[0] + camara_x, pos[1] + camara_y)
                    distancia_arrastre = math.hypot(pos[0] - pos_inicial_clic[0], pos[1] - pos_inicial_clic[1])
                    
                    estado_arrastrando_texto = False
                    nodo_rotando = None 
                    
                    if panel.arrastrando_borde:
                        panel.arrastrando_borde = False
                        if distancia_arrastre < 6: panel.conmutar_colapso()
                        continue
                    
                    if nodo_arrastrado and distancia_arrastre < 5:
                        nodo_arrastrado.modo_interaccion = "arrow" if nodo_arrastrado.modo_interaccion == "resize" else "resize"
                    
                    # Conectar flecha nueva (NUEVO: Hereda el estilo global elegido)
                    if nodo_origen_flecha and llave_punto_origen:
                        flecha_anclada = False
                        for nodo_destino in reversed(nodos):
                            if nodo_destino != nodo_origen_flecha:
                                punto_destino_nombre = nodo_destino.verificar_clic_puntos(pos_mundo)
                                if not punto_destino_nombre and nodo_destino.rect.collidepoint(pos_mundo):
                                    punto_destino_nombre = "centro_izquierda" if pos_mundo[0] < nodo_destino.rect.centerx else "centro_derecha"
                                
                                if punto_destino_nombre:
                                    conexiones.append(Conexion(nodo_origen_flecha, llave_punto_origen, nodo_destino, punto_destino_nombre, tipo=estilo_conexion_global))
                                    flecha_anclada = True
                                    break
                        if not flecha_anclada:
                            nueva_c = Conexion(nodo_origen_flecha, llave_punto_origen, nodo_destino=None, punto_destino=None, tipo=estilo_conexion_global)
                            nueva_c.pos_vacio_final = pos_mundo
                            conexiones.append(nueva_c)
                        nodo_origen_flecha = llave_punto_origen = None

                    # Conectar flecha desde otra flecha suelta (NUEVO: Hereda el estilo)
                    elif flecha_origen_flecha:
                        flecha_anclada = False
                        for nodo_destino in reversed(nodos):
                            punto_destino_nombre = nodo_destino.verificar_clic_puntos(pos_mundo)
                            if not punto_destino_nombre and nodo_destino.rect.collidepoint(pos_mundo):
                                punto_destino_nombre = "centro_izquierda" if pos_mundo[0] < nodo_destino.rect.centerx else "centro_derecha"
                            if punto_destino_nombre:
                                nueva_c = Conexion(nodo_origen=None, punto_origen=None, nodo_destino=nodo_destino, punto_destino=punto_destino_nombre, tipo=estilo_conexion_global)
                                nueva_c.origen_es_flecha = flecha_origen_flecha
                                conexiones.append(nueva_c)
                                flecha_anclada = True
                                break
                        if not flecha_anclada:
                            nueva_c = Conexion(nodo_origen=None, punto_origen=None, nodo_destino=None, punto_destino=None, tipo=estilo_conexion_global)
                            nueva_c.origen_es_flecha = flecha_origen_flecha
                            nueva_c.pos_vacio_final = pos_mundo
                            conexiones.append(nueva_c)
                        flecha_origen_flecha = None

                    if nodo_arrastrado:
                        centro_pantalla = (nodo_arrastrado.rect.centerx - camara_x, nodo_arrastrado.rect.centery - camara_y)
                        if panel.rect.collidepoint(centro_pantalla):
                            nodos_a_remover = [n for n in nodos if n.seleccionado]
                            for n_rem in nodos_a_remover:
                                if n_rem in nodos: nodos.remove(n_rem)
                                conexiones = [c for c in conexiones if c.origen != n_rem and c.destino != n_rem]
                                if n_rem == nodo_editando: nodo_editando = None
                        nodo_arrastrado = None
                    
                    nodo_redimensionando = punto_redimension_nombre = None

            # 6. Movimiento Dinámico del Ratón
            elif evento.type == pygame.MOUSEMOTION:
                pos = evento.pos
                pos_mundo = (pos[0] + camara_x, pos[1] + camara_y)
                
                if arrastrando_lienzo:
                    dx = pos[0] - ultima_pos_mouse[0]
                    dy = pos[1] - ultima_pos_mouse[1]
                    camara_x -= dx
                    camara_y -= dy
                    ultima_pos_mouse = pos
                    
                elif panel.arrastrando_borde:
                    panel.actualizar_ancho(pos[0])

                elif estado_arrastrando_texto:
                    obj_edit = next((c for c in conexiones if c.editando), None) or (nodo_editando if (nodo_editando and nodo_editando.editando) else None)
                    if obj_edit:
                        idx = calcular_indice_click(obj_edit, pos[0], pos[1], camara_x, camara_y, fuente)
                        obj_edit.indice_cursor = idx

                elif nodo_rotando:
                    dx = pos_mundo[0] - nodo_rotando.rect.centerx
                    dy = pos_mundo[1] - nodo_rotando.rect.centery
                    angulo_raton = math.degrees(math.atan2(dy, dx))
                    nodo_rotando.angulo = (angulo_raton + nodo_rotando.angulo_offset) % 360

                elif nodo_redimensionando and punto_redimension_nombre:
                    r = nodo_redimensionando.rect
                    if "derecha" in punto_redimension_nombre or punto_redimension_nombre == "centro_derecha":
                        r.width = max(40, pos_mundo[0] - r.x)
                    elif "izquierda" in punto_redimension_nombre or punto_redimension_nombre == "centro_izquierda":
                        antiguo_right = r.right
                        r.x = min(pos_mundo[0], antiguo_right - 40)
                        r.width = antiguo_right - r.x
                    if "abajo" in punto_redimension_nombre or punto_redimension_nombre == "abajo_centro":
                        r.height = max(20, pos_mundo[1] - r.y)
                    elif "arriba" in punto_redimension_nombre or punto_redimension_nombre == "arriba_centro":
                        antiguo_bottom = r.bottom
                        r.y = min(pos_mundo[1], antiguo_bottom - 20)
                        r.height = antiguo_bottom - r.y

                elif nodo_arrastrado:
                    nueva_pos_x = pos_mundo[0] + offset_x
                    nueva_pos_y = pos_mundo[1] + offset_y
                    dx = nueva_pos_x - nodo_arrastrado.rect.x
                    dy = nueva_pos_y - nodo_arrastrado.rect.y
                    for nodo in nodos:
                        if nodo.seleccionado:
                            nodo.rect.x += dx
                            nodo.rect.y += dy

        # --- ORDEN DE CAPAS DE RENDERIZADO ---
        for conexion in conexiones: 
            if conexion == conexion_seleccionada:
                puntos_foco = conexion.obtener_todos_los_puntos()
                if len(puntos_foco) >= 2:
                    p0 = (puntos_foco[0][0] - camara_x, puntos_foco[0][1] - camara_y)
                    p1 = (puntos_foco[1][0] - camara_x, puntos_foco[1][1] - camara_y)
                    pygame.draw.line(pantalla, (255, 120, 0), p0, p1, 5)
            conexion.dibujar(pantalla, fuente, camara_offset=(camara_x, camara_y))

        if nodo_origen_flecha and llave_punto_origen:
            pos_raton = pygame.mouse.get_pos()
            ancla_world = nodo_origen_flecha.obtener_puntos_conexion()[llave_punto_origen]
            pos_ancla_pantalla = (ancla_world[0] - camara_x, ancla_world[1] - camara_y)
            pos_limitada = panel.limitar_linea_conexion(pos_raton)
            pygame.draw.line(pantalla, (50, 150, 255), pos_ancla_pantalla, pos_limitada, 2)
            pygame.draw.circle(pantalla, (50, 150, 255), pos_limitada, 4)

        elif flecha_origen_flecha:
            pos_raton = pygame.mouse.get_pos()
            pos_ancla_pantalla = (flecha_origen_flecha.pos_vacio_final[0] - camara_x, flecha_origen_flecha.pos_vacio_final[1] - camara_y)
            pos_limitada = panel.limitar_linea_conexion(pos_raton)
            pygame.draw.line(pantalla, (255, 165, 0), pos_ancla_pantalla, pos_limitada, 2)
            pygame.draw.circle(pantalla, (255, 165, 0), pos_limitada, 4)

        for nodo in nodos: 
            nodo.dibujar(pantalla, fuente, camara_offset=(camara_x, camara_y))
            
        pos_m = pygame.mouse.get_pos()
        pos_m_mundo = (pos_m[0] + camara_x, pos_m[1] + camara_y)
        for nodo in nodos:
            if nodo.seleccionado:
                p_manija = nodo.obtener_punto_rotacion()
                if math.hypot(pos_m_mundo[0] - p_manija[0], pos_m_mundo[1] - p_manija[1]) <= 12:
                    p_cursor = (pos_m[0], pos_m[1])
                    pygame.draw.circle(pantalla, (46, 204, 113), p_cursor, 14, 2)
                    pygame.draw.line(pantalla, (255, 255, 255), (p_cursor[0] - 5, p_cursor[1] - 5), (p_cursor[0] + 5, p_cursor[1] + 5), 1)

        panel.dibujar(pantalla, fuente)

        pygame.display.flip()
        reloj.tick(60)

if __name__ == "__main__":
    principal()