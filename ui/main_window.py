import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLabel, QFileDialog, QHBoxLayout,
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
        self.btn_previous = QPushButton("Previous")
        self.btn_next = QPushButton("Next")
        self.btn_play = QPushButton("Play")
        self.btn_stop = QPushButton("Stop")

        # Layout de controles - organiza los botones horizontalmente
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.btn_previous)
        controls_layout.addWidget(self.btn_play)
        controls_layout.addWidget(self.btn_stop)
        controls_layout.addWidget(self.btn_next)

        # Layout - organiza los widgets verticalmente
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label_song)
        main_layout.addWidget(self.btn_open)
        main_layout.addLayout(controls_layout)

        #Widget central - PyQt6 exige un widget central que contenga el layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Signals - conectamos cada botón con su metodo
        self.btn_open.clicked.connect(self.open_files)
        self.btn_play.clicked.connect(self.toggle_play)
        self.btn_stop.clicked.connect(self.stop)
        self.btn_next.clicked.connect(self.next_song)
        self.btn_previous.clicked.connect(self.previous_song)

    def open_files(self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Seleccionar canciones")
        dialog.setNameFilter("Audio (*.mp3 *.wav *.flac *.ogg)")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog)

        if dialog.exec():
            file_paths = dialog.selectedFiles()
            if file_paths:
                self.player.load_queue(file_paths)
                self.player.play()
                self.update_label()
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

    def next_song(self):
        self.player.next()
        self.update_label()
        self.btn_play.setText("Pause")

    def previous_song(self):
        self.player.previous()
        self.update_label()
        self.btn_play.setText("Play")

    def update_label(self):
        song = self.player.current_song()
        self.label_song.setText(os.path.basename(song))