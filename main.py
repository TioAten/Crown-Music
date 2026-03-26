import sys
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow

# Importamos la función desde el nuevo archivo neutral
from core.utils import get_resource_path
def main():
    # 1. INYECTAR IDENTIDAD
    if sys.platform == "win32":
        myappid = 'tu_nombre.crown_music.reproductor.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # 2. ARRANCAR EL MOTOR GLOBAL
    app = QApplication(sys.argv)

    # 3. EL GOLPE FINAL: Ícono global para la aplicación
    icon_path = get_resource_path("assets/icons/icon.png")
    app.setWindowIcon(QIcon(icon_path))  # <- CORREGIDO: app en vez de self

    # 4. CREAR LA VENTANA
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()