import pygame

class Player:
    def __init__(self):
        pygame.mixer.init()
        self._playing = False
        self._paused = False # <- nueva adición del gemini
        self.queue = [] # lista de rustas de archivos
        self.current_index = 0 #índice de la canción actual

    def load(self, file_path: str):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()  # ← libera el archivo actual antes de cargar el nuevo
        pygame.mixer.music.load(file_path)
        self._paused = False

    def load_queue(self, file_paths: list):
        self.queue = file_paths # guarda la lista completa
        self.current_index = 0 # arranca desde la primera
        self.load(self.queue[0]) # carga ña primera canción

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
        """else:
            pygame.mixer.music.unpause()
            self._playing = True"""

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