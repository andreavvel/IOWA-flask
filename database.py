import sqlite3

from contextlib import closing
from icecream import ic
from pydantic import BaseModel

from typing import Optional

class User(BaseModel):
    id: Optional[int]
    username: str
    password: str
    admin: bool

class Movie(BaseModel):
    id: Optional[int]
    name: str
    year: int
    director: str
    duration: int
    poster: str

DATABASE_NAME = "movie-app.db"

class Database:
    @staticmethod
    def verifyTables(verbose=2):
        with closing(sqlite3.connect(DATABASE_NAME)) as connection:
            if verbose > 0: print("Connected to SQLite!")
            with closing(connection.cursor()) as cursor:
                cursor.execute("CREATE TABLE IF NOT EXISTS movies (id INTEGER PRIMARY KEY, name TEXT, year INTEGER, director TEXT, duration INTEGER, poster TEXT);")
                cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, admin INTEGER);")
                cursor.execute('INSERT OR IGNORE INTO users VALUES(1, "andrea", "secret", 1);')    
                tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
                if verbose > 0: print("Tables loaded: ", end="")
                if verbose > 1: print(tables)
            connection.commit()      
    
    def addMovie(self, movie: Movie):
        with closing(sqlite3.connect(DATABASE_NAME)) as connection:
            with closing(connection.cursor()) as cursor:
                values = f'NULL, "{movie.name}", "{movie.year}", "{movie.director}", "{movie.duration}", "{movie.poster}"'
                cursor.execute(f"INSERT INTO movies VALUES({values})")
            connection.commit()    

    def getMovies(self) -> list[Movie]:
        movie_list = []
        with closing(sqlite3.connect(DATABASE_NAME)) as connection:
            with closing(connection.cursor()) as cursor:
                movies_tuples = cursor.execute("SELECT * FROM movies").fetchall()
                for movie_tuple in movies_tuples:
                    movie_list.append(Movie(id=movie_tuple[0], name=movie_tuple[1], year=movie_tuple[2], director=movie_tuple[3], duration=movie_tuple[4], poster=movie_tuple[5]))
        return movie_list    

    def createUser(self, user:User):
        with closing(sqlite3.connect(DATABASE_NAME)) as connection:
                with closing(connection.cursor()) as cursor:
                    values = f'NULL, "{user.username}", "{user.password}", {1 if user.admin is True else 0}'
                    cursor.execute(f"INSERT INTO users VALUES({values})")
                connection.commit()

    def getUser(self, username: str, password:str) -> User | None:
        user = None
        with closing(sqlite3.connect(DATABASE_NAME)) as connection:
            with closing(connection.cursor()) as cursor:
                maybeUser = cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password,)).fetchone()
                if maybeUser is not None:
                    user = User(id=maybeUser[0], username=maybeUser[1], password=maybeUser[2], admin=maybeUser[3] > 0)
        return user
    
    def getUsers(self) -> list[User]:
        users = []
        with closing(sqlite3.connect(DATABASE_NAME)) as connection:
            with closing(connection.cursor()) as cursor:
                usersTuples = cursor.execute("SELECT * FROM users").fetchall()
                for userTuple in usersTuples:
                    users.append(User(id=userTuple[0], username=userTuple[1], password=userTuple[2], admin=userTuple[3] > 0))
        return users