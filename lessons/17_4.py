from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    author = db.Column(db.String(100))
    year = db.Column(db.Integer)


class BookSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    author = fields.Str()
    year = fields.Int()


book_schema = BookSchema()
books_schema = BookSchema(many=True)

api = Api(app)
book_ns = api.namespace('')

book_1 = Book(id=1, name='Harry Potter', author='Joan Routing', year=2000)
book_2 = Book(id=2, name='Le Comte de Monte-Cristo', author='Alexandre Dumas', year=1844)


def init_database():
    with db.session.begin():
        db.create_all()
        db.session.add_all([book_1, book_2])


@book_ns.route('/books')
class BooksView(Resource):
    def get(self):
        all_books = db.session.query(Book).all()
        return books_schema.dump(all_books), 200

    def post(self):
        request_json = request.json
        new_book = Book(**request_json)
        with db.session.begin():
            db.session.add(new_book)
        return '', 201


@book_ns.route('/books/<int:book_id>')
class BookView(Resource):
    def get(self, book_id: int):
        try:
            book = db.session.query(Book).filter(Book.id == book_id).one()
            return book_schema.dump(book), 200
        except Exception as e:
            return str(e), 404

    def put(self, book_id):
        book = db.session.query(Book).get(book_id)
        request_json = request.json

        book.name = request_json.get('name')
        book.author = request_json.get('author')
        book.year = request_json.get('year')

        with db.session.begin():
            db.session.add(book)
        return '', 204

    def patch(self, book_id):
        book = db.session.query(Book).get(book_id)
        request_json = request.json

        if 'name' in request_json:
            book.name = request_json.get('name')
        if 'author' in request_json:
            book.author = request_json.get('author')
        if 'year' in request_json:
            book.year = request_json.get('year')

        with db.session.begin():
            db.session.add(book)
        return '', 204

    def delete(self, book_id):
        book = db.session.query(Book).get(book_id)

        with db.session.begin():
            db.session.delete(book)

        return '', 204


if __name__ == '__main__':
    with app.app_context():
        init_database()
    app.run(debug=True)
