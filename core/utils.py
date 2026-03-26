import sys
import os


def get_resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, compatible con desarrollo y PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # Si es un ejecutable compilado, PyInstaller guarda los archivos acá
        base_path = sys._MEIPASS
    else:
        # En desarrollo, utils.py está en /core, así que subimos un nivel para llegar a la raíz
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)