import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QInputDialog, QListWidget, QMessageBox
)
from PyQt6.QtCore import QTimer
from core.player import Player
from core.database import Database

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__() # Llama al constructor padre

        self.player = Player()
        self.db = Database()
        self.playlist_ids = [] # ← guardamos los IDs separados del texto visual

        # Configuración de la ventana
        self.setWindowTitle("Crown Music")
        self.setMinimumSize(600, 400)

        # Label que muestra la canción actual
        self.label_song = QLabel("Ninguna canción cargada")

        # Lista de playlists
        self.list_playlists = QListWidget()
        self.list_songs = QListWidget()
        self.load_playlists()

        #Botones de Playlists
        self.btn_open = QPushButton("Abrir archivo")
        self.btn_save = QPushButton("Guardar playlist")
        self.btn_rename = QPushButton("Renombrar playlist")
        self.btn_delete = QPushButton("Eliminar playlist")

        # Botones de control
        self.btn_previous = QPushButton("⏮")
        self.btn_next = QPushButton("⏭")
        self.btn_play = QPushButton("Play")
        self.btn_stop = QPushButton("Stop")
        self.btn_loop_song = QPushButton("Repetir Canción: OFF")
        self.btn_loop_playlist = QPushButton("Repetir Playlist: OFF")

        #Layout de las dos listas lado a lado
        lists_layout = QHBoxLayout()
        lists_layout.addWidget(self.list_playlists)
        lists_layout.addWidget(self.list_songs)

        # Layout de controles - organiza los botones horizontalmente
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.btn_previous)
        controls_layout.addWidget(self.btn_play)
        controls_layout.addWidget(self.btn_stop)
        controls_layout.addWidget(self.btn_next)
        controls_layout.addWidget(self.btn_loop_song)
        controls_layout.addWidget(self.btn_loop_playlist)

        # Layout de botones de playlist
        playlist_buttons_layout = QHBoxLayout()
        playlist_buttons_layout.addWidget(self.btn_open)
        playlist_buttons_layout.addWidget(self.btn_save)
        playlist_buttons_layout.addWidget(self.btn_rename)
        playlist_buttons_layout.addWidget(self.btn_delete)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addLayout(lists_layout)
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
        self.btn_rename.clicked.connect(self.rename_playlist)
        self.btn_delete.clicked.connect(self.delete_playlist)
        self.btn_play.clicked.connect(self.toggle_play)
        self.btn_stop.clicked.connect(self.stop)
        self.btn_next.clicked.connect(self.next_song)
        self.btn_previous.clicked.connect(self.previous_song)
        self.list_playlists.currentRowChanged.connect(self.show_playlist_songs)
        self.list_playlists.itemDoubleClicked.connect(self.load_playlist)
        self.list_songs.itemDoubleClicked.connect(self.play_song_from_list)
        self.btn_loop_song.clicked.connect(self.toggle_loop_song_ui)
        self.btn_loop_playlist.clicked.connect(self.toggle_loop_playlist_ui)

        # Temporizador para escuchar los events de Pygame
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_events)
        self.timer.start(500) # Revisa dos veces por segundo (500 ms)

    def check_events(self):
        if self.player.check_song_end():
            # 1. Prioridad máxima: ¿Repetir la misma canción?
            if self.player.loop_song:
                self.player.play_from_index(self.player.current_index)

            # 2. Si no repite canción, ¿quedan canciones en la playlist?
            elif self.player.current_index < len(self.player.queue) - 1:
                self.next_song()

            # 3. Si se acabó la playlist, ¿está activo repetir playlist?
            elif self.player.loop_playlist:
                self.player.play_from_index(0)  # Vuelve a la primera
                self.update_label()
                self.btn_play.setText("Pause")

            # 4. Si nada de lo anterior se cumple, se terminó la música
            else:
                self.stop()

    def toggle_loop_song_ui(self):
        self.player.toggle_loop_song()
        # Actualizamos la UI según los estados internos del player
        estado = "ON" if self.player.loop_song else "OFF"
        self.btn_loop_song.setText(f"Repetir Canción: {estado}")
        if self.player.loop_song:
            self.btn_loop_playlist.setText("Repetir Playlist: OFF")

    def toggle_loop_playlist_ui(self):
        self.player.toggle_loop_playlist()
        estado = "ON" if self.player.loop_playlist else "OFF"
        self.btn_loop_playlist.setText(f"Repetir Playlist: {estado}")
        if self.player.loop_playlist:
            self.btn_loop_song.setText("Repetir Canción: OFF")

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

    def rename_playlist(self):
        selected_index = self.list_playlists.currentRow()
        if selected_index == -1:
            QMessageBox.warning(self, "Aviso", "Seleccioná una playlist de la lista.")
            return
        current_name = self.list_playlists.currentItem().text()
        new_name, ok = QInputDialog.getText(self, "Renombrar playlist", "Nuevo nombre:", text=current_name)
        if ok and new_name:
            playlist_id = self.playlist_ids[selected_index]
            self.db.rename_playlist(playlist_id, new_name)
            self.load_playlists()

    def play_song_from_list(self):
        selected_index = self.list_songs.currentRow()
        if selected_index == -1:
            return

        # Asegurarnos de que el reproductor tenga la cola de la playlist actual
        playlist_index = self.list_playlists.currentRow()
        if playlist_index != -1:
            playlist_id = self.playlist_ids[playlist_index]
            self.player.queue = self.db.get_songs(playlist_id)

        self.player.play_from_index(selected_index)
        self.update_label()
        self.btn_play.setText("Pause")

    def show_playlist_songs(self, index):
        if index == -1:
            return
        self.list_songs.clear()  # ← limpiar la lista
        playlist_id = self.playlist_ids[index]
        songs = self.db.get_songs(playlist_id)
        for path in songs:
            self.list_songs.addItem(os.path.basename(path))

    def toggle_play(self):
        # El reproductor decide internamente si pausar, reanudar o reiniciar
        is_playing = self.player.toggle_playback()

        if is_playing:
            self.btn_play.setText("Pause")
        else:
            self.btn_play.setText("Play")

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