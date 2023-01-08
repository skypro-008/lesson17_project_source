from flask import request
from flask_restx import Resource, Namespace

from app.database import db
from app.models import DirectorSchema
from create_data import Director

directors_ns = Namespace('directors')

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)


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
            return director_schema.dump(director), 200
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
