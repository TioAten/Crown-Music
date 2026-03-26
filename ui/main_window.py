import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStyle,
    QPushButton, QLabel, QFileDialog, QInputDialog, QListWidget, QMessageBox, QSlider
)
from PyQt6 import uic
from PyQt6.QtCore import QTimer, Qt
import qtawesome as qta

from core.player import Player
from core.database import Database

import sys
import ctypes

from PyQt6.QtGui import QIcon

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

        # 1. Ícono de la ventana principal
        self.setWindowIcon(QIcon("assets/icons/icon.png"))

        # Forzar modo oscuro en la barra de título nativa de Windows
        if sys.platform == "win32":
            hwnd = int(self.winId())
            # El atributo 20 funciona en Windows 11 y Windows 10 (versiones recientes)
            res = ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4)
            # Si el sistema operativo es un Windows 10 un poco más antiguo, el atributo es 19
            if res != 0:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 19, ctypes.byref(ctypes.c_int(1)), 4)

        #self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        uic.loadUi("ui/main_window.ui", self)

        self.player = Player()
        self.db = Database()
        self.playlist_ids = [] # ← guardamos los ID separados del texto visual
        self.current_viewing_paths = []  # ← Guarda las rutas reales de la lista visual

        self.load_playlists()

        # Recuperamos el volumen guardado (por defecto 100)
        saved_volume = int(self.db.get_setting("volume", "100"))
        self.slider_volume.setValue(saved_volume)
        #self.label_volume.setText(f"Vol: {saved_volume}%") # Ahora es un QLabel del .ui
        self.player.set_volume(saved_volume / 100)  # Aplicamos el volumen real al motor

        self.slider_progress.setEnabled(False)  # Se desactiva si no hay música
        self.label_song.setText("Ninguna canción cargada") # Ahora es un QLabel del .ui

        # --- CONFIGURACIÓN DE ÍCONOS VECTORIALES ---
        color_icono = "white"

        # 1. Botones de Gestión de Playlist (Conservamos el texto, sumamos ícono)
        self.btn_open.setIcon(qta.icon('fa5s.folder-open', color=color_icono))
        self.btn_open.setText(" Abrir")

        self.btn_save.setIcon(qta.icon('fa5s.save', color=color_icono))
        self.btn_save.setText(" Guardar")

        self.btn_rename.setIcon(qta.icon('fa5s.pen', color=color_icono))
        self.btn_rename.setText(" Renombrar")

        self.btn_delete.setIcon(qta.icon('fa5s.trash-alt', color=color_icono))
        self.btn_delete.setText(" Eliminar")

        # 2. Controles de Reproducción (Solo íconos, sin texto para que quede simétrico)
        self.btn_play.setIcon(qta.icon('fa5s.play', color=color_icono))
        self.btn_play.setText("")

        self.btn_stop.setIcon(qta.icon('fa5s.stop', color=color_icono))
        self.btn_stop.setText("")

        self.btn_previous.setIcon(qta.icon('fa5s.step-backward', color=color_icono))
        self.btn_previous.setText("")

        self.btn_next.setIcon(qta.icon('fa5s.step-forward', color=color_icono))
        self.btn_next.setText("")

        # 3. Opciones de Reproducción (Solo íconos)
        self.btn_shuffle.setIcon(qta.icon('fa5s.random', color=color_icono))
        self.btn_shuffle.setText("")

        self.btn_loop_song.setIcon(qta.icon('fa5s.redo', color=color_icono))
        self.btn_loop_song.setText(" 1")  # El "1" indica que repite la canción actual

        self.btn_loop_playlist.setIcon(qta.icon('fa5s.sync', color=color_icono))
        self.btn_loop_playlist.setText(" All")  # "All" indica que repite toda la lista

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

        # Conexión de tu slider promovido
        self.slider_progress.sliderMoved.connect(self.seek_position)

        # Temporizador para escuchar los events de Pygame
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_events)
        self.timer.start(500) # Revisa dos veces por segundo (500 ms)

    def toggle_shuffle_ui(self):
        self.player.toggle_shuffle()
        # Si está activo lo pintamos de morado claro, si no, vuelve a blanco
        color = "#5e3cf5" if self.player.shuffle else "white"
        self.btn_shuffle.setIcon(qta.icon('fa5s.random', color=color))

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
                self.actualizar_icono_play(True)
            else:
                self.stop()

    def seek_position(self):
        # Leemos dónde soltaste la bolita
        new_time = self.slider_progress.value()
        # Le ordenamos al motor interno que salte a ese segundo
        self.player.seek(new_time)
        # Actualizamos el texto inmediatamente para que no haya lag visual
        self.label_time_current.setText(self.format_time(new_time))
        self.actualizar_icono_play(True)

    def format_time(self, seconds: float) -> str:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}:{secs:02d}"

    def toggle_loop_song_ui(self):
        self.player.toggle_loop_song()
        color = "#5e3cf5" if self.player.loop_song else "white"
        self.btn_loop_song.setIcon(qta.icon('fa5s.redo', color=color))

        if self.player.loop_song:
            # Apagamos visualmente el otro loop si este se enciende
            self.btn_loop_playlist.setIcon(qta.icon('fa5s.sync', color='white'))

    def toggle_loop_playlist_ui(self):
        self.player.toggle_loop_playlist()
        color = "#5e3cf5" if self.player.loop_playlist else "white"
        self.btn_loop_playlist.setIcon(qta.icon('fa5s.sync', color=color))

        if self.player.loop_playlist:
            # Apagamos visualmente el loop de canción si este se enciende
            self.btn_loop_song.setIcon(qta.icon('fa5s.redo', color='white'))

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
        self.actualizar_icono_play(True)

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
                self.actualizar_icono_play(True)

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

        clicked_path = self.current_viewing_paths[selected_index]

        if self.player._original_queue != self.current_viewing_paths:
            self.player.load_queue(self.current_viewing_paths.copy())

        actual_index = self.player.queue.index(clicked_path)

        self.player.play_from_index(actual_index)
        self.update_label()
        self.actualizar_icono_play(True)

    def show_playlist_songs(self, index):
        if index == -1:
            return
        self.list_songs.clear()
        playlist_id = self.playlist_ids[index]
        songs = self.db.get_songs(playlist_id)

        self.current_viewing_paths = songs  # ← Sincronizamos la variable

        for path in songs:
            self.list_songs.addItem(os.path.basename(path))

    def actualizar_icono_play(self, is_playing):
        if is_playing:
            self.btn_play.setIcon(qta.icon('fa5s.pause', color='white'))
        else:
            self.btn_play.setIcon(qta.icon('fa5s.play', color='white'))

    def toggle_play(self):
        is_playing = self.player.toggle_playback()
        self.actualizar_icono_play(is_playing)

    def stop(self):
        self.player.stop()
        self.actualizar_icono_play(False)

    def next_song(self):
        self.player.next()
        self.update_label()
        self.actualizar_icono_play(True)

    def previous_song(self):
        self.player.previous()
        self.update_label()
        self.actualizar_icono_play(True)

    def update_label(self):
        song = self.player.current_song()
        # Solo actualiza si hay una canción cargada en el reproductor interno
        if song:
            self.label_song.setText(os.path.basename(song))
            # Configurar la barra de progreso para la nueva canción
            total_length = self.player.get_total_length()
            if total_length > 0:
                self.slider_progress.setMaximum(int(total_length))
                self.label_time_total.setText(self.format_time(total_length))
                self.slider_progress.setEnabled(True)

    def closeEvent(self, event):
        # Guardamos la configuración antes de cerrar la conexión
        current_volume = self.slider_volume.value()
        self.db.save_setting("volume", str(current_volume))
        self.db.close()  # cierra la conexión a la DB
        event.accept()