import json
import os
import subprocess
from elements import Nodo, Conexion

def abrir_dialogo_nativo_macos(modo="guardar", nombre_defecto="diagrama.json"):
    """Usa el Finder de macOS de forma directa para forzar a la ventana nativa a saltar al frente."""
    if modo == "guardar":
        script = f'''
        tell application "Finder"
            activate
            set archivo to choose file name with prompt "Guardar Diagrama Como:" default name "{nombre_defecto}"
            return POSIX path of archivo
        end tell
        '''
    else:
        script = '''
        tell application "Finder"
            activate
            set archivo to choose file with prompt "Seleccionar Diagrama de Flujo (.json):" of type {"public.json"}
            return POSIX path of archivo
        end tell
        '''
    try:
        resultado = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        if resultado.returncode == 0 and resultado.stdout.strip():
            return resultado.stdout.strip()
    except Exception as e:
        print(f"Error al abrir diálogo nativo: {e}")
    return ""

def guardar_diagrama(nodos, conexiones, pantalla, archivo_actual):
    """Convierte los objetos del lienzo a un JSON flexible que soporta flechas sueltas y encadenadas."""
    nombre_defecto = os.path.basename(archivo_actual) if archivo_actual else "diagrama.json"
    ruta_archivo = abrir_dialogo_nativo_macos(modo="guardar", nombre_defecto=nombre_defecto)
    
    if not ruta_archivo:
        return archivo_actual

    try:
        lista_nodos = []
        for index, n in enumerate(nodos):
            lista_nodos.append({
                "id": index,
                "x": n.rect.x,
                "y": n.rect.y,
                "w": n.rect.width,
                "h": n.rect.height,
                "texto": getattr(n, "texto", ""),
                "forma": getattr(n, "forma", "rectangulo"),
                "color": list(getattr(n, "color_base", (173, 216, 230))),
                "angulo": getattr(n, "angulo", 0.0)  # Guarda la rotación de los nodos
            })
            
        lista_conexiones = []
        for index, c in enumerate(conexiones):
            id_origen = nodos.index(c.origen) if c.origen in nodos else -1
            id_destino = nodos.index(c.destino) if c.destino in nodos else -1
            id_flecha_madre = conexiones.index(c.origen_es_flecha) if c.origen_es_flecha in conexiones else -1

            lista_conexiones.append({
                "id": index,
                "id_origen": id_origen,
                "punto_origen": c.punto_origen,
                "id_destino": id_destino,
                "punto_destino": c.punto_destino,
                "pos_vacio_final": list(c.pos_vacio_final) if c.pos_vacio_final else None,
                "id_flecha_madre": id_flecha_madre,
                "texto": getattr(c, "texto", ""),
                "color": list(getattr(c, "color_base", (60, 60, 60))),
                "tipo": getattr(c, "tipo", "recta")  # 🌟 NUEVO: Guardamos si es recta o redondeada
            })

        datos = {"nodos": lista_nodos, "conexiones": lista_conexiones}
        
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        print(f"💾 Guardado avanzado exitoso en: {os.path.basename(ruta_archivo)}")
        return ruta_archivo

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO AL GUARDAR: {e}\n")
        return archivo_actual


def cargar_diagrama(pantalla):
    """Abre el panel nativo de macOS y reconstruye respetando la posición exacta original."""
    ruta_archivo = abrir_dialogo_nativo_macos(modo="cargar")
    if not ruta_archivo:
        return None, None, ""
        
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)
            
        n_nodos = []
        n_conexiones = []
        
        # 1. Reconstrucción de Nodos
        for n_data in datos.get("nodos", []):
            ancho = n_data.get("w", 120)
            alto = n_data.get("h", 60)
            x_guardada = n_data.get("x", 100)
            y_guardada = n_data.get("y", 100)
            
            nuevo = Nodo(x_guardada + ancho//2, y_guardada + alto//2, n_data.get("texto", ""), w=ancho, h=alto)
            nuevo.texto = n_data.get("texto", "")
            
            if "forma" in n_data: 
                nuevo.forma = n_data["forma"]
            if "color" in n_data: 
                nuevo.color_base = tuple(n_data["color"])
                
            nuevo.angulo = n_data.get("angulo", 0.0)
                
            n_nodos.append(nuevo)
            
        # 2. Primera pasada de Conexiones
        conexiones_temp_data = datos.get("conexiones", [])
        for c_data in conexiones_temp_data:
            id_origen = c_data.get("id_origen", -1)
            id_destino = c_data.get("id_destino", -1)
            
            nodo_origen = n_nodos[id_origen] if id_origen != -1 and id_origen < len(n_nodos) else None
            nodo_destino = n_nodos[id_destino] if id_destino != -1 and id_destino < len(n_nodos) else None
            
            # 🌟 NUEVO: Leemos el tipo de flecha (asume "recta" por defecto si es un JSON viejo)
            tipo_guardado = c_data.get("tipo", "recta")
            nueva_c = Conexion(nodo_origen, c_data.get("punto_origen"), nodo_destino, c_data.get("punto_destino"), tipo=tipo_guardado)
            
            nueva_c.texto = c_data.get("texto", "") 
            if "color" in c_data:
                nueva_c.color_base = tuple(c_data["color"])       

            pos_vacio = c_data.get("pos_vacio_final")
            if pos_vacio:
                nueva_c.pos_vacio_final = (pos_vacio[0], pos_vacio[1])
                
            n_conexiones.append(nueva_c)
            
        # 3. Segunda pasada para encadenamientos
        for i, c_data in enumerate(conexiones_temp_data):
            id_madre = c_data.get("id_flecha_madre", -1)
            if id_madre != -1 and id_madre < len(n_conexiones):
                n_conexiones[i].origen_es_flecha = n_conexiones[id_madre]
                
        print(f"✅ Cargado avanzado exitoso desde: {os.path.basename(ruta_archivo)}")
        return n_nodos, n_conexiones, ruta_archivo

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO AL CARGAR: {e}\n")
        return None, None, ""