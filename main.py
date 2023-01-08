# main.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

from app.config import Config


def create_app(app_conf: Config) -> Flask:
    application = Flask(__name__)

    application.config.from_object(app_conf)
    application.app_context().push()

    return application


app_config = Config()

app = create_app(app_config)
api = Api(app)
db = SQLAlchemy(app)

movies_ns = api.namespace("movies")
directors_ns = api.namespace("directors")
genres_ns = api.namespace("genres")


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))

    genre = db.relationship("Genre")
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        """Возвращает список всех фильмов, разделенный по страницам
        Страница в параметре page.
        Размер страницы в параметре page_size
        Режиссер в параметре director_id.
        Жанр в параметре genre_id"""
        all_movies = db.session.query(Movie)

        # Сбор параметров
        page = request.args.get("page")
        page_size = request.args.get("page_size")
        director_id = request.args.get("director_id")
        genre_id = request.args.get("genre_id")

        if director_id:
            # curl -X GET "http://127.0.0.1:5000/movies/?director_id=3"
            all_movies = all_movies.filter(Movie.director_id == director_id)

        if genre_id:
            # curl -X GET "http://127.0.0.1:5000/movies/?genre_id=17"
            all_movies = all_movies.filter(Movie.genre_id == genre_id)

        if page_size and page:
            # curl -X GET "http://127.0.0.1:5000/movies/?page=2&page_size=3"
            all_movies = all_movies.limit(page_size).offset(int(page) * int(page_size))

        final_query = all_movies.all()
        # curl -X GET "http://127.0.0.1:5000/movies/?page=0&page_size=3&genre_id=18&director_id=7"

        if not final_query:
            return "", 404
            # curl -X GET "http://127.0.0.1:5000/movies/?page=1&page_size=3&genre_id=18&director_id=7"

        return movies_schema.dump(final_query), 200

    def post(self):
        request_json = request.json
        movie_ = movie_schema.load(request_json)
        new_movie = Movie(**movie_)
        with db.session.begin():
            db.session.add(new_movie)
        # curl -X POST "http://127.0.0.1:5000/movies/" -H "Content-Type: application/json" -d '{"title":"test",
        # "description":"test","year":2001,"genre_id":17,"director_id":3}'
        return '', 201


@movies_ns.route("/<int:movies_id>")
class MovieView(Resource):
    def get(self, movies_id: int):
        try:
            movie = db.session.query(Movie).get(movies_id)
            # curl -X GET "http://127.0.0.1:5000/movies/2"
            if not movie:
                # curl -X GET "http://127.0.0.1:5000/movies/2222"
                return "", 404
            return movie_schema.dump(movie), 200
        except Exception as e:
            return str(e), 404

    def put(self, movies_id: int):
        try:
            movie_select = db.session.query(Movie).filter(Movie.id == movies_id)
            request_json = request.json
            if not movie_select.first():
                # curl -X PUT "http://127.0.0.1:5000/movies/11111111111" -H "Content-Type: application/json" -d '{"title":"test","description":"test","year":2001,"genre_id":17}'
                return "", 404
            movie_select.update(request_json)
            db.session.commit()
            # curl -X PUT "http://127.0.0.1:5000/movies/1" -H "Content-Type: application/json" -d '{"title":"test","description":"test","year":2001,"genre_id":17}'
            return '', 204
        except Exception as e:
            return str(e), 404

    def delete(self, movies_id: int):
        try:
            movie_select = db.session.query(Movie).filter(Movie.id == movies_id)

            if not movie_select.first():
                return "", 404
            row_delete = movie_select.delete()

            if row_delete != 1:
                return "", 400
            db.session.commit()
            # curl -X DELETE "http://127.0.0.1:5000/movies/1"
            return '', 204
        except Exception as e:
            return str(e), 404


@directors_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        directors_all = db.session.query(Director).all()
        return directors_schema.dump(directors_all), 200

    def post(self):
        request_json = request.json
        director_ = director_schema.load(request_json)
        new_director = Director(**director_)

        with db.session.begin():
            db.session.add(new_director)

        return "", 201


@directors_ns.route("/<int:director_id>")
class DirectorView(Resource):
    def get(self, director_id: int):
        try:
            director = db.session.query(Director).get(director_id)
            if not director:
                return "", 404
            return movie_schema.dump(director), 200
        except Exception as e:
            return str(e), 404

    def put(self, director_id: int):
        try:
            director_select = db.session.query(Director).filter(Director.id == director_id)
            request_json = request.json
            if not director_select.first():
                return "", 404
            director_select.update(request_json)
            db.session.commit()
            return '', 204
        except Exception as e:
            return str(e), 404

    def delete(self, director_id: int):
        try:
            director_select = db.session.query(Director).filter(Director.id == director_id)

            if not director_select.first():
                return "", 404
            row_delete = director_select.delete()

            if row_delete != 1:
                return "", 400
            db.session.commit()
            return '', 204
        except Exception as e:
            return str(e), 404


@genres_ns.route("/")
class GenresView(Resource):
    def get(self):
        genre_all = db.session.query(Genre).all()
        return genres_schema.dump(genre_all), 200

    def post(self):
        request_json = request.json
        genre_ = director_schema.load(request_json)
        new_genre = Genre(**genre_)

        with db.session.begin():
            db.session.add(new_genre)

        return "", 201


@directors_ns.route("/<int:genre_id>")
class GenreView(Resource):
    def get(self, genre_id: int):
        try:
            genre = db.session.query(Genre).get(genre_id)
            if not genre:
                return "", 404
            return genre_schema.dump(genre), 200
        except Exception as e:
            return str(e), 404

    def put(self, genre_id: int):
        try:
            genre_select = db.session.query(Genre).filter(Genre.id == genre_id)
            request_json = request.json
            if not genre_select.first():
                return "", 404
            genre_select.update(request_json)
            db.session.commit()
            return '', 204
        except Exception as e:
            return str(e), 404

    def delete(self, genre_id: int):
        try:
            genre_select = db.session.query(Genre).filter(Genre.id == genre_id)

            if not genre_select.first():
                return "", 404
            row_delete = genre_select.delete()

            if row_delete != 1:
                return "", 400
            db.session.commit()
            return '', 204
        except Exception as e:
            return str(e), 404


if __name__ == '__main__':
    app.run(debug=True)
