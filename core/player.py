import pygame

class Player:
    def __init__(self):
        pygame.mixer.init()
        self._playing = False
        self.queue = [] # lista de rustas de archivos
        self.current_index = 0 #índice de la canción actual

    def load(self, file_path: str):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()  # ← libera el archivo actual antes de cargar el nuevo
        pygame.mixer.music.load(file_path)

    def load_queue(self, file_paths: list):
        self.queue = file_paths # guarda la lista completa
        self.current_index = 0 # arranca desde la primera
        self.load(self.queue[0]) # carga ña primera canción

    def play(self):
        if not self.queue:  # si no hay nada cargado, no hace nada
            return
        pygame.mixer.music.play()
        self._playing = True

    def pause(self):
        if self._playing:
            pygame.mixer.music.pause()
            self._playing = False
        else:
            pygame.mixer.music.unpause()
            self._playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self._playing = False

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