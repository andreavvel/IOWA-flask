from database import Database, Movie, User
from flask import Flask, request, render_template, redirect, session

from icecream import ic

Database.verifyTables(2)

app = Flask("Flask - Lab")
app.secret_key = "secret"

@app.route("/", methods=["GET"])
def index():
    username = session.get("username")
    admin = session.get("admin") if session.get("admin") is not None else False
    logged = username is not None
    if username is None: username = "guest"
    database = Database()
    movies = database.getMovies()
    full_render = render_template("navbar.html", username=username, admin=admin, logged=logged)
    full_render += render_template("home.html", username=username, logged=logged, admin=admin, movies=movies)
    if admin: full_render += render_template("movie-form.html")
    return full_render

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET": return render_template("login.html")
    if request.method != "POST": return redirect("/")
    database = Database()
    
    username = request.form.get("username")
    password = request.form.get("password")
    maybeUser = database.getUser(username, password)
    if maybeUser is None: return render_template("login.html", error=True)

    session["username"] = maybeUser.username
    session["admin"] = maybeUser.admin
    session.permanent = True
    return redirect("/")

@app.route("/add-movie", methods=["POST"])
def addMovie():
    movie: Movie = Movie(
        id=None,
        name=request.form.get("name"),
        year=request.form.get("year"),
        director=request.form.get("director"),
        duration=request.form.get("duration"),
        poster=request.form.get("poster")
    )
    database = Database()
    database.addMovie(movie)
    return redirect("/")    

@app.route("/add-user", methods=["POST"])
def addUser():
    user: User = User(
        id=None,
        username=request.form.get("username"),
        password=request.form.get("password"),
        admin=request.form.get("admin") is not None
    )
    database = Database()
    database.createUser(user)
    return redirect("/users")

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username")
    session.pop("admin")
    return redirect("/")

@app.route("/users", methods=["GET"])
def users():
    if session.get("username") is None or session.get("admin") is False: return redirect("/")
    database = Database()
    users = database.getUsers()
    return render_template("navbar.html", username=session.get("username"), admin=session.get("admin"), logged=True) + render_template("users.html", users=users)

def getMovieTable(movies: list[tuple]) -> str:
    table = """
        <div class="table-container">
        <h1>Movie List</h1>
        <table>
        <tr>
            <th>Title</th>
            <th>Year</th>
            <th>Writer</th>
            <th>Pages</th>
            <th>Cover</th>
        </tr>
    """
    for movie in movies:
        table += f"""
            <tr>
                <td>{movie[1]}</td>
                <td>{movie[2]}</td>
                <td>{movie[3]}</td>
                <td>{movie[4]} min.</td>
                <td>
                <a target="_blank" rel="norreferer" href="{movie[5]}">
                    <img src={movie[5]} height=75 /> 
                </a>
                </td>
            </tr>
        """
    table += "</table></div>"
    return table

app.debug = True
app.run()