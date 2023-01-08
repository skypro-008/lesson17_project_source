from flask import request
from flask_restx import Resource, Namespace

from app.database import db
from app.models import MovieSchema, Movie

movies_ns = Namespace('movies')

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


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
