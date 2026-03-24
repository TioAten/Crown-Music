import pygame

class Player:
    def __init__(self):
        pygame.mixer.init()
        self._playing = False

    def load(self, file_path: str):
        pygame.mixer.music.load(file_path)

    def play(self):
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

    def is_playing(self) -> bool:
        return self._playing