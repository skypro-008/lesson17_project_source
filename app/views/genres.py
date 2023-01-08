from flask import request
from flask_restx import Resource, Namespace

from app.database import db
from app.models import GenreSchema
from create_data import Genre

genres_ns = Namespace('genres')

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@genres_ns.route("/")
class GenresView(Resource):
    def get(self):
        genre_all = db.session.query(Genre).all()
        return genres_schema.dump(genre_all), 200

    def post(self):
        request_json = request.json
        genre_ = genre_schema.load(request_json)
        new_genre = Genre(**genre_)

        with db.session.begin():
            db.session.add(new_genre)

        return "", 201


@genres_ns.route("/<int:genre_id>")
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
