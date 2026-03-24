import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLabel, QFileDialog,
)
from core.player import Player

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__() # Llama al constuctor padre

        self.player = Player()

        # Configuración de la ventana
        self.setWindowTitle("Crown Music")
        self.setMinimumSize(400, 200)

        # Label que muestra la canción actual
        self.label_song = QLabel("Ninguna canción cargada")

        # Botones
        self.btn_open = QPushButton("Abrir archivo")
        self.btn_play = QPushButton("Play")
        self.btn_stop = QPushButton("Stop")

        # Layout - organiza los widgets verticalmente
        layout = QVBoxLayout()
        layout.addWidget(self.label_song)
        layout.addWidget(self.btn_open)
        layout.addWidget(self.btn_play)
        layout.addWidget(self.btn_stop)

        #Widget central - PyQt6 exige un widget central que contenga el layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Signals - conectamos cada botón con su metodo
        self.btn_open.clicked.connect(self.open_file)
        self.btn_play.clicked.connect(self.toggle_play)
        self.btn_stop.clicked.connect(self.stop)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar canción",
            "",
            "Audio (*.mp3 *.wav *.flac *.ogg)",
            options=QFileDialog.Option.DontUseNativeDialog  # ← esta línea
        )

        if file_path:
            self.player.load(file_path)
            self.player.play()
            self.label_song.setText(os.path.basename(file_path))
            self.btn_play.setText("Pause")

    def toggle_play(self):
        if self.player.is_playing():
            self.player.stop()
            self.btn_play.setText("Play")
        else:
            self.player.play()
            self.btn_play.setText("Pause")

    def stop(self):
        self.player.stop()
        self.btn_play.setText("Play")