import pygame
import random

class Player:
    def __init__(self):
        pygame.mixer.init()
        self._playing = False
        self._paused = False # <- nueva adición del gemini
        self.queue = [] # lista de rustas de archivos
        self.current_index = 0 #índice de la canción actual
        self.shuffle = False # ← nuevo
        self._original_queue = [] # ← guarda el orden original

        # Nuevos estados booleanos para los buvles
        self.loop_song = False
        self.loop_playlist = False

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle

        if not self.queue:
            return  # Cambiamos el estado (ON/OFF), pero si no hay lista cortamos acá.

        if self.shuffle:
            self._original_queue = self.queue.copy()
            current_song = self.queue[self.current_index]

            random.shuffle(self.queue)  # Mezcla toda la lista (incluyendo la primera)

            # Buscamos dónde quedó la canción actual en la lista mezclada para no interrumpirla
            self.current_index = self.queue.index(current_song)
        else:
            current_song = self.queue[self.current_index]
            self.queue = self._original_queue.copy()
            self.current_index = self.queue.index(current_song)

    def set_volume(self, value: float):
        # value va de 0.0 a 1.0
        pygame.mixer.music.set_volume(value)

    def toggle_loop_song(self):
        self.loop_song = not self.loop_song
        if self.loop_song:
            self.loop_playlist = False  # Son mutuamente excluyentes

    def toggle_loop_playlist(self):
        self.loop_playlist = not self.loop_playlist
        if self.loop_playlist:
            self.loop_song = False

    def load(self, file_path: str):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()  # ← libera el archivo actual antes de cargar el nuevo
        pygame.mixer.music.load(file_path)
        self._paused = False

    def load_queue(self, file_paths: list):
        self._original_queue = file_paths.copy()  # Guardamos siempre la original

        if self.shuffle:
            self.queue = file_paths.copy()
            random.shuffle(self.queue)  # Mezcla total inmediata si el shuffle está ON
        else:
            self.queue = file_paths.copy()

        self.current_index = 0
        self.load(self.queue[0])

    def play(self):
        if not self.queue:  # si no hay nada cargado, no hace nada
            return
        pygame.mixer.music.play()
        self._playing = True
        self._paused = False

    def toggle_playback(self) -> bool:
        # Si está sonando, pausa
        if self._playing:
            pygame.mixer.music.pause()
            self._playing = False
            self._paused = True
        # Si estaba pausado, reanuda (esto arregla tu problema)
        elif self._paused:
            pygame.mixer.music.unpause()
            self._playing = True
            self._paused = False
        # Si estaba detenido por completo, arranca de cero
        else:
            self.play()

        return self._playing

    def play_from_index(self, index: int):
        if 0 <= index < len(self.queue):
            self.current_index = index
            self.load(self.queue[self.current_index])
            self.play()

    def pause(self):
        if self._playing:
            pygame.mixer.music.pause()
            self._playing = False
            self._paused = True # <- nueva adición del gemini

    def stop(self):
        pygame.mixer.music.stop()
        self._playing = False
        self._paused = False

    def next(self):
        if self.current_index < len(self.queue) - 1:
            self.current_index += 1
            self.load(self.queue[self.current_index])
            self.play()

    def previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load(self.queue[self.current_index])
            self.play()

    def current_song(self) -> str:
        if self.queue:
            return self.queue[self.current_index]
        return ""

    def is_playing(self) -> bool:
        return self._playing

    def check_song_end(self) -> bool:
        # get_busy() da False si la canción terminó o si se pausó.
        # Si nuestra variable _playing es True y _paused es False,
        # y get_busy() da False, es porque la canción terminó sola.
        if self._playing and not self._paused and not pygame.mixer.music.get_busy():
            return True
        return False