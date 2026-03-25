import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QInputDialog, QListWidget, QMessageBox
)
from core.player import Player
from core.database import Database

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__() # Llama al constuctor padre

        self.player = Player()
        self.db = Database()
        self.playlist_ids = [] # ← guardamos los IDs separados del texto visual

        # Configuración de la ventana
        self.setWindowTitle("Crown Music")
        self.setMinimumSize(500, 400)

        # Label que muestra la canción actual
        self.label_song = QLabel("Ninguna canción cargada")

        # Lista de playlists
        self.list_playlists = QListWidget()
        self.load_playlists()

        #Botones de Playlists
        self.btn_open = QPushButton("Abrir archivo")
        self.btn_save = QPushButton("Guardar playlist")
        self.btn_load = QPushButton("Cargar playlist")
        self.btn_delete = QPushButton("Eliminar playlist")

        # Botones de control
        self.btn_previous = QPushButton("⏮")
        self.btn_next = QPushButton("⏭")
        self.btn_play = QPushButton("Play")
        self.btn_stop = QPushButton("Stop")

        # Layout de controles - organiza los botones horizontalmente
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.btn_previous)
        controls_layout.addWidget(self.btn_play)
        controls_layout.addWidget(self.btn_stop)
        controls_layout.addWidget(self.btn_next)

        # Layout de botones de playlist
        playlist_buttons_layout = QHBoxLayout()
        playlist_buttons_layout.addWidget(self.btn_open)
        playlist_buttons_layout.addWidget(self.btn_save)
        playlist_buttons_layout.addWidget(self.btn_load)
        playlist_buttons_layout.addWidget(self.btn_delete)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("Playlists guardadas:"))
        main_layout.addWidget(self.list_playlists)
        main_layout.addLayout(playlist_buttons_layout)
        main_layout.addWidget(self.label_song)
        main_layout.addLayout(controls_layout)

        #Widget central - PyQt6 exige un widget central que contenga el layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Signals - conectamos cada botón con su metodo
        self.btn_open.clicked.connect(self.open_files)
        self.btn_save.clicked.connect(self.save_playlist)
        self.btn_load.clicked.connect(self.load_playlist)
        self.btn_delete.clicked.connect(self.delete_playlist)
        self.btn_play.clicked.connect(self.toggle_play)
        self.btn_stop.clicked.connect(self.stop)
        self.btn_next.clicked.connect(self.next_song)
        self.btn_previous.clicked.connect(self.previous_song)
        self.list_playlists.currentRowChanged.connect(self.show_playlist_songs)

    def load_playlist(self):
        selected_index = self.list_playlists.currentRow()
        if selected_index == -1:
            QMessageBox.warning(self, "Aviso", "Seleccioná una playlist de la lista.")
            return
        playlist_id = self.playlist_ids[selected_index]
        file_paths = self.db.get_songs(playlist_id)
        self.player.load_queue(file_paths)
        self.player.play()
        self.update_label()
        self.btn_play.setText("Pause")

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

    def save_playlist(self):
        if not self.player.queue:
            QMessageBox.warning(self, "Aviso", "No hay canciones cargadas para guardar.")
            return

        name, ok = QInputDialog.getText(self, "Guardar playlist", "Nombre de la playlist:")
        if ok and name:
            self.db.save_playlist(name, self.player.queue)
            self.load_playlists()  # actualiza la lista visual

    def load_playlists(self):
        self.list_playlists.clear()
        self.playlist_ids = []
        for playlist_id, name in self.db.get_playlists():
            self.list_playlists.addItem(name)
            self.playlist_ids.append(playlist_id)

    def delete_playlist(self):
        selected_index = self.list_playlists.currentRow()
        if selected_index == -1:
            QMessageBox.warning(self, "Aviso", "Seleccioná una playlist de la lista.")
            return
        playlist_id = self.playlist_ids[selected_index]
        self.db.delete_playlist(playlist_id)
        self.load_playlists()

    def show_playlist_songs(self, index):
        if index == -1:
            return
        playlist_id = self.playlist_ids[index]
        songs = self.db.get_songs(playlist_id)
        song_names = [os.path.basename(path) for path in songs]
        self.label_song.setText(" | ".join(song_names))

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

    def closeEvent(self, event):
        self.db.close()  # cierra la conexión a la DB al cerrar la ventana
        event.accept()