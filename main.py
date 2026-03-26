import sys
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon  # <- IMPORTANTE: Necesitamos QIcon acá también
from ui.main_window import MainWindow

def main():
    # 1. INYECTAR IDENTIDAD (El paso que ya hicimos)
    if sys.platform == "win32":
        myappid = 'tu_nombre.crown_music.reproductor.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # 2. ARRANCAR EL MOTOR GLOBAL
    app = QApplication(sys.argv)

    # 3. EL GOLPE FINAL: Ícono global para la aplicación (Esto lo lee la barra de tareas)
    app.setWindowIcon(QIcon("assets/icon.png"))

    # 4. CREAR LA VENTANA
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()