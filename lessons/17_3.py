from flask import Flask, request
from flask_restx import Api, Resource

app = Flask(__name__)
api = Api(app)
book_ns = api.namespace('')

books = {
    1: {
        'name': 'Harry Potter',
        'year': 2000,
        'author': 'Joan Routing'
    },
    2: {
        'name': 'Le Comte de Monte-Cristo',
        'year': 1844,
        'author': 'Alexandre Dumas'
    }
}


@book_ns.route('/books')
class BooksView(Resource):
    def get(self):
        return books

    def post(self):
        request_json = request.json()
        books[len(books) + 1] = request_json
        return '', 201


@book_ns.route('/books/<int: book_id>')
class BookView(Resource):
    def get(self, book_id):
        return books[book_id], 200

    def delete(self, book_id):
        del books[book_id]
        return '', 204


if __name__ == '__main__':
    app.run(debug=True)
