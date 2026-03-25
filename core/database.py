import os
import sqlite3

DB_PATH = "crown_music.db" # Archivo de base de satos en la raíz del proyecto

class Database:
    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS playlists ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name TEXT NOT NULL)"
        )

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS songs ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "playlist_id INTEGER NOT NULL,"
            "path TEXT NOT NULL,"
            "position INTEGER NOT NULL,"
            "FOREIGN KEY (playlist_id) REFERENCES playlists(id))"
        )

        # NUEVA TABLA: Configuración general de la app
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS settings ("
            "key TEXT PRIMARY KEY,"
            "value TEXT NOT NULL)"
        )

        self.connection.commit()

        # NUEVOS MÉTODOS PARA SETTINGS
    def save_setting(self, key: str, value: str):
        # INSERT OR REPLACE actualiza el valor si la clave ya existe
        self.cursor.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
        self.connection.commit()

    def get_setting(self, key: str, default: str) -> str:
        self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = self.cursor.fetchone()
        return row[0] if row else default

    def save_playlist(self, name: str, file_paths: list) -> int:
        # Inserta la playlist y obtiene su id
        self.cursor.execute("INSERT INTO playlists (name) VALUES (?)", (name, ))
        playlist_id = self.cursor.lastrowid

        # Insertar cada canción con su posición
        for position, path in enumerate(file_paths):
            self.cursor.execute("""
                INSERT INTO songs (playlist_id, path, position)
                VALUES (?, ?, ?)
            """, (playlist_id, path, position))

        self.connection.commit()
        return playlist_id

    def rename_playlist(self, playlist_id: int, new_name: str):
        self.cursor.execute(
            "UPDATE playlists SET name = ? WHERE id = ?",
            (new_name, playlist_id)
        )
        self.connection.commit()

    def get_playlists(self) -> list:
        self.cursor.execute("SELECT id, name FROM playlists")
        return self.cursor.fetchall() #retorna lista de tuplas (id, name)

    def get_songs(self, playlist_id: int) -> list:
        self.cursor.execute(
            "SELECT path FROM songs WHERE playlist_id = ? ORDER BY position",
            (playlist_id,)
        )
        return [row[0] for row in self.cursor.fetchall()] # Retorna lista de rutas

    def delete_playlist(self, playlist_id: int):
        self.cursor.execute("DELETE FROM songs WHERE playlist_id = ?", (playlist_id,))
        self.cursor.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))
        self.connection.commit()

    def close(self):
        self.connection.close()