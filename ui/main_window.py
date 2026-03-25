import os

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStyle,
    QPushButton, QLabel, QFileDialog, QInputDialog, QListWidget, QMessageBox, QSlider
)
from PyQt6.QtCore import QTimer, Qt

from core.player import Player
from core.database import Database

# Agrega la clase ClickableSlider
class ClickableSlider(QSlider):
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            val = QStyle.sliderValueFromPosition(
                self.minimum(),
                self.maximum(),
                event.pos().x(),
                self.width()
            )
            self.setValue(val)
            self.sliderMoved.emit(val)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__() # Llama al constructor padre

        self.player = Player()
        self.db = Database()
        self.playlist_ids = [] # ← guardamos los ID separados del texto visual
        self.current_viewing_paths = []  # ← Guarda las rutas reales de la lista visual

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
        self.btn_shuffle = QPushButton("Shuffle: OFF")

        # Slider de volumen
        self.slider_volume = QSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setMinimum(0)
        self.slider_volume.setMaximum(100)
        self.slider_volume.setValue(100)  # volumen máximo por defecto
        self.slider_volume.setFixedWidth(100)

        # Recuperamos el volumen guardado (por defecto 100)
        saved_volume = int(self.db.get_setting("volume", "100"))

        self.slider_volume.setValue(saved_volume)
        self.label_volume = QLabel(f"Vol: {saved_volume}%")
        self.player.set_volume(saved_volume / 100)  # Aplicamos el volumen real al motor

        # Barra de progreso (Timeline)
        # Reemplaza el QSlider estándar por tu nuevo ClickableSlider
        # Antes tenías algo como: self.progress_bar = QSlider(Qt.Orientation.Horizontal)
        # Instanciamos tu clase personalizada usando el nombre de variable que ya tenías
        self.slider_progress = ClickableSlider(Qt.Orientation.Horizontal)
        self.slider_progress.setEnabled(False)  # Se desactiva si no hay música

        self.label_time_current = QLabel("0:00")
        self.label_time_total = QLabel("0:00")

        # Conectamos la señal 'sliderMoved' de tu nuevo ClickableSlider a la función 'seek_position'
        # Nota: Pygame necesita un salto inmediato, 'sliderMoved' es más preciso aquí que 'sliderReleased'
        self.slider_progress.sliderMoved.connect(self.seek_position)

        # Conecta la señal 'sliderMoved' al método que maneja el "seek" en Pygame
        self.slider_progress.sliderMoved.connect(self.seek_position)

        # Layout para la barra de progreso y sus tiempos
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(self.label_time_current)
        self.slider_progress.setRange(0, 100)  # Rango por defecto (se actualiza en update_label)
        progress_layout.addWidget(self.slider_progress)  # Usamos self.slider_progress aquí
        progress_layout.addWidget(self.label_time_total)

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
        controls_layout.addWidget(self.btn_shuffle)
        controls_layout.addWidget(self.label_volume)
        controls_layout.addWidget(self.slider_volume)

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
        main_layout.addLayout(progress_layout)
        main_layout.addLayout(controls_layout)

        #Widget central - PyQt6 exige un widget central que contenga el layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Signals - conectamos cada botón con su método
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
        self.btn_shuffle.clicked.connect(self.toggle_shuffle_ui)
        self.slider_volume.valueChanged.connect(self.change_volume)
        self.slider_progress.sliderReleased.connect(self.seek_position)

        # Temporizador para escuchar los events de Pygame
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_events)
        self.timer.start(500) # Revisa dos veces por segundo (500 ms)

    def toggle_shuffle_ui(self):
        self.player.toggle_shuffle()
        estado = "ON" if self.player.shuffle else "OFF"
        self.btn_shuffle.setText(f"Shuffle: {estado}")
        # Eliminamos el código que redibujaba la lista para que quede estática

    def change_volume(self, value: int):
        self.player.set_volume(value / 100)  # convertimos 0-100 a 0.0-1.0
        self.label_volume.setText(f"Vol: {value}%")

    def check_events(self):
        # 1. ACTUALIZAR LA BARRA DE PROGRESO (Solo si el usuario NO la está arrastrando)
        if self.player.is_playing() and not self.slider_progress.isSliderDown():
            current_sec = self.player.get_current_time()
            self.slider_progress.setValue(int(current_sec))
            self.label_time_current.setText(self.format_time(current_sec))

        # 2. LÓGICA DE FIN DE CANCIÓN
        if self.player.check_song_end():
            if self.player.loop_song:
                self.player.play_from_index(self.player.current_index)
            elif self.player.current_index < len(self.player.queue) - 1:
                self.next_song()
            elif self.player.loop_playlist:
                self.player.play_from_index(0)
                self.update_label()
                self.btn_play.setText("Pause")
            else:
                self.stop()

    def cambiar_posicion_cancion(self, valor):
        # Aquí calculas los segundos exactos según el 'valor' del slider
        # y la duración total de tu pista actual.
        # Luego usas pygame.mixer.music.set_pos() (o rewind/play según el formato)
        print(f"Pygame seek: Saltando a la posición {valor}")

    def seek_position(self):
        # Leemos dónde soltaste la bolita
        new_time = self.slider_progress.value()

        # Le ordenamos al motor interno que salte a ese segundo
        self.player.seek(new_time)

        # Actualizamos el texto inmediatamente para que no haya lag visual
        self.label_time_current.setText(self.format_time(new_time))
        self.btn_play.setText("Pause")

    # Debe tener 'self' como primer argumento porque es un método de la clase
    def format_time(self, seconds: float) -> str:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}:{secs:02d}"

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

        # Dibujamos siempre la lista en su orden original, ignorando el shuffle
        self.list_songs.clear()
        self.current_viewing_paths = self.player._original_queue.copy()
        for path in self.current_viewing_paths:
            self.list_songs.addItem(os.path.basename(path))

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

                # Dibujamos siempre la lista en su orden original
                self.list_songs.clear()
                self.current_viewing_paths = self.player._original_queue.copy()
                for path in self.current_viewing_paths:
                    self.list_songs.addItem(os.path.basename(path))

    def save_playlist(self):
        if not self.player._original_queue:
            QMessageBox.warning(self, "Aviso", "No hay canciones cargadas para guardar.")
            return
        name, ok = QInputDialog.getText(self, "Guardar playlist", "Nombre de la playlist:")
        if ok and name:
            self.db.save_playlist(name, self.player._original_queue)  # ← orden original
            self.load_playlists()

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

        # Obtenemos la ruta exacta de la canción que tocaste en la lista visual ordenada
        clicked_path = self.current_viewing_paths[selected_index]

        # Si el reproductor interno no tiene la misma cola que estamos viendo, se la cargamos
        if self.player._original_queue != self.current_viewing_paths:
            self.player.load_queue(self.current_viewing_paths.copy())

        # Buscamos en qué índice exacto quedó esa canción dentro del reproductor (esté barajado o no)
        actual_index = self.player.queue.index(clicked_path)

        # Le decimos al reproductor que arranque desde ese índice interno
        self.player.play_from_index(actual_index)
        self.update_label()
        self.btn_play.setText("Pause")

    def show_playlist_songs(self, index):
        if index == -1:
            return
        self.list_songs.clear()
        playlist_id = self.playlist_ids[index]
        songs = self.db.get_songs(playlist_id)

        self.current_viewing_paths = songs  # ← Sincronizamos la variable

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

        # Configurar la barra de progreso para la nueva canción
        total_length = self.player.get_total_length()
        self.slider_progress.setMaximum(int(total_length))
        self.label_time_total.setText(self.format_time(total_length))
        self.slider_progress.setEnabled(True)

    def closeEvent(self, event):
        # Guardamos la configuración antes de cerrar la conexión
        current_volume = self.slider_volume.value()
        self.db.save_setting("volume", str(current_volume))

        self.db.close()  # cierra la conexión a la DB
        event.accept()