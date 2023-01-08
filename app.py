# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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


if __name__ == '__main__':
    app.run(debug=True)
