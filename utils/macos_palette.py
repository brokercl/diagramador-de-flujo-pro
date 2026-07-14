# macos_palette.py
import subprocess

class MacColorPicker:
    """Clase utilitaria independiente para invocar el selector de colores nativo de macOS."""
    
    @staticmethod
    def seleccionar_color():
        """Abre el System Color Picker de macOS y devuelve un tuple (R, G, B) o None si se cancela."""
        script = '''
        tell application "Finder"
            activate
            set el_color to choose color
            return el_color
        end tell
        '''
        try:
            resultado = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            if resultado.returncode == 0 and resultado.stdout.strip():
                # El sistema devuelve "R_16bit, G_16bit, B_16bit" (escala 0-65535)
                valores_16bit = [int(x.strip()) for x in resultado.stdout.strip().split(",")]
                
                # Conversión perfecta a 8 bits (0-255)
                r = int(round(valores_16bit[0] / 257))
                g = int(round(valores_16bit[1] / 257))
                b = int(round(valores_16bit[2] / 257))
                return (r, g, b)
        except Exception as e:
            print(f"Error en MacColorPicker: {e}")
        return None