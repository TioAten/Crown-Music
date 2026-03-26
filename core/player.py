import pygame
import random
import time  # <- El motor de nuestro nuevo cronómetro de precisión


class Player:
    def __init__(self):
        pygame.mixer.init()
        self._playing = False
        self._paused = False
        self.queue = []
        self.current_index = 0
        self.shuffle = False
        self._original_queue = []

        self.loop_song = False
        self.loop_playlist = False

        # --- NUEVO SISTEMA DE CRONÓMETRO ABSOLUTO ---
        self._accumulated_time = 0.0
        self._last_start_time = 0.0

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle

        if not self.queue:
            return

        if self.shuffle:
            self._original_queue = self.queue.copy()
            current_song = self.queue[self.current_index]
            random.shuffle(self.queue)
            self.current_index = self.queue.index(current_song)
        else:
            current_song = self.queue[self.current_index]
            self.queue = self._original_queue.copy()
            self.current_index = self.queue.index(current_song)

    def get_total_length(self) -> float:
        if not self.queue:
            return 0.0
        try:
            sound = pygame.mixer.Sound(self.queue[self.current_index])
            return sound.get_length()
        except Exception:
            return 0.0

    def get_current_time(self) -> float:
        # Lógica matemática precisa, sin depender del buffer de Pygame
        if self._playing:
            # Tiempo real = lo que ya venía sonando + lo que pasó desde el último play/unpause
            return self._accumulated_time + (time.time() - self._last_start_time)
        elif self._paused:
            # Si está en pausa, el tiempo queda exactamente congelado donde lo dejamos
            return self._accumulated_time
        return 0.0

    def set_volume(self, value: float):
        pygame.mixer.music.set_volume(value)

    def toggle_loop_song(self):
        self.loop_song = not self.loop_song
        if self.loop_song:
            self.loop_playlist = False

    def toggle_loop_playlist(self):
        self.loop_playlist = not self.loop_playlist
        if self.loop_playlist:
            self.loop_song = False

    def load(self, file_path: str):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.music.load(file_path)
        self._paused = False

    def load_queue(self, file_paths: list):
        self._original_queue = file_paths.copy()
        if self.shuffle:
            self.queue = file_paths.copy()
            random.shuffle(self.queue)
        else:
            self.queue = file_paths.copy()

        self.current_index = 0
        self.load(self.queue[0])

    def play(self):
        if not self.queue:
            return
        pygame.mixer.music.play()
        self._playing = True
        self._paused = False

        # Reiniciamos nuestro cronómetro desde cero
        self._accumulated_time = 0.0
        self._last_start_time = time.time()

    def seek(self, seconds: float):
        if not self.queue:
            return
        pygame.mixer.music.play(start=seconds)
        self._playing = True
        self._paused = False

        # Le decimos al cronómetro que el tiempo acumulado ahora es exactamente el segundo donde saltamos
        self._accumulated_time = seconds
        self._last_start_time = time.time()

    def toggle_playback(self) -> bool:
        if self._playing:
            pygame.mixer.music.pause()
            self._playing = False
            self._paused = True
            # Al pausar, guardamos exactamente el tiempo que transcurrió hasta este milisegundo
            self._accumulated_time += (time.time() - self._last_start_time)
        elif self._paused:
            pygame.mixer.music.unpause()
            self._playing = True
            self._paused = False
            # Al reanudar, reseteamos el punto de partida del reloj a este instante
            self._last_start_time = time.time()
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
            self._paused = True
            self._accumulated_time += (time.time() - self._last_start_time)

    def stop(self):
        pygame.mixer.music.stop()
        self._playing = False
        self._paused = False
        self._accumulated_time = 0.0

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
        if self._playing and not self._paused and not pygame.mixer.music.get_busy():
            return True
        return False