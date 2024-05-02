from PIL import ImageTk, Image
import os
import sys

def obtener_ruta_base():
    """Obtiene la ruta base para acceder a los recursos del sistema de archivos."""
    # Si APPDIR está establecido (por AppImage), usa esa ruta como base
    app_dir = os.getenv('APPDIR')
    if app_dir is not None:
        return os.path.join(app_dir, 'usr', 'bin')  # Ajusta esto según tu estructura de directorios específica dentro de AppDir

    # De lo contrario, utiliza el directorio del script principal como ruta base
    return os.path.dirname(os.path.abspath(sys.argv[0]))

def leer_imagen(path, size):
    """Lee una imagen desde una ruta relativa y la ajusta al tamaño especificado."""
    ruta_base = obtener_ruta_base()
    path_abs = os.path.join(ruta_base, path)
    return ImageTk.PhotoImage(Image.open(path_abs).resize(size, Image.Resampling.LANCZOS))  # Usa ANTIALIAS para un redimensionamiento de calidad