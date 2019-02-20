import json
from json.decoder import JSONDecodeError

import tornado.ioloop
import tornado.web

from dog_database import DogDatabase, DogDatabaseError, DogNotFoundError

"""A REST API that allows users to retrieve, add, update, and delete representations of dogs."""

PORT = 8888
DOG_ATTRIBUTES = ['name', 'breed', 'age']

# TODO: - Write API tests X
#       - Set up handler methods X
#       - Write DB tests X
#       - Set up database to store everything X
#       - Write additional tests to cover any other implementation X
#       - Play test on local server X
#       - Make sure everything is commenty clean.
#       - Dockerize X
#       - Add some documentation to this module.
#       - Consider loading on to AWS
#       - Test everything again!


class DogAPIError(tornado.web.HTTPError):
    pass


class BaseHandler(tornado.web.RequestHandler):
    """Handles requests piped to the /dogs URL without a specified dog."""
    def initialize(self, database):
        self.database = database

    def get(self):
        """Handles GET HTTP requests by pointing users to request a specific dog."""
        self.write('Request a dog by name using the URL. (Try Barton or Ellis)')

    def post(self):
        """Handles POST HTTP requests by creating a representation of the named dog.
        Expects payload to be in JSON format."""

        # Try converting the JSON
        try:
            dog = json.loads(self.request.body.decode('utf-8'))
        except (SyntaxError, JSONDecodeError):
            raise DogAPIError(400, reason='POST request expects JSON formatted data.')

        # Try entering the new dog.
        try:
            self.database.insert(dog)
        except DogDatabaseError as e:
            raise DogAPIError(400, reason=str(e))

        self.set_status(201)
        self.write('{name} was added to our records'.format(name=dog['name']))


class DogHandler(tornado.web.RequestHandler):
    """Handles  requests relating to specific dogs (/dogs/[dog_name])"""
    def initialize(self, database):
        self.database = database

    def get(self, dog_name):
        """Handles GET HTTP requests by returning a representation of the named dog."""
        try:
            dog = self.database.select(dog_name)
        except DogNotFoundError as e:
            raise DogAPIError(404, reason=str(e))

        # Relies on Tornado's built in JSON conversion.
        self.write(dog)

    def put(self, dog_name):
        """Handles PUT HTTP requests by updating the named dog's record on our website.
        Expects payload to be in JSON format."""

        # Try converting the JSON
        try:
            changes = json.loads(self.request.body.decode('utf-8'))
        except (SyntaxError, JSONDecodeError):
            raise DogAPIError(400, reason='PUT request expects JSON formatted data.')

        # Try to update the record
        try:
            self.database.update(dog_name, changes)
        except DogNotFoundError as e:
            raise DogAPIError(404, reason=str(e) + ' Edit was not completed.')
        except DogDatabaseError as e:
            raise DogAPIError(400, reason=str(e))

        self.write('Dog edit succeeded.')

    def delete(self, dog_name):
        """Handles DELETE HTTP requests by removing the named dog from our website."""
        try:
            self.database.delete(dog_name)
        except DogNotFoundError as e:
            raise DogAPIError(404, reason=str(e))

        self.write('{name} has been deleted.'.format(name=dog_name))


def make_app():
    database = DogDatabase()
    return tornado.web.Application([
        ("^\/dogs\/(.+)$", DogHandler, {'database': database}),
        ("/dogs/*", BaseHandler, {'database': database})
    ])


def run_test_server():
    app = make_app()
    app.listen(PORT)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    run_test_server()
