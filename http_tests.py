import unittest

import requests

from dog_api import PORT

"""Runs tests from an 'external' perspective on the api. The web server must be running independently
on localhost."""

ERROR_TEMPLATE = "<html><title>{status}: {message}</title><body>{status}: {message}</body></html>"


class RestAPITests(unittest.TestCase):

    def test_get(self):

        # Tests 2 dogs that should be on the website already.

        test_dog = {'name': 'Barton',
                    'breed': 'Anatolian',
                    'age': 8}

        r = requests.get('http://localhost:{port}/dogs/{name}'.format(port=PORT, name=test_dog['name']))
        return_json = r.json()

        self.assertEqual(200, r.status_code)
        self.assertEqual(test_dog, return_json)

        test_dog = {'name': 'Ellis',
                    'breed': 'Lab',
                    'age': 3}

        r = requests.get('http://localhost:{port}/dogs/{name}'.format(port=PORT, name=test_dog['name']))
        return_json = r.json()

        self.assertEqual(200, r.status_code)
        self.assertEqual(test_dog, return_json)

        # Tests what happens when a dog is requested that is not in the database.

        test_dog = {'name': 'MadeUpDog'}

        r = requests.get('http://localhost:{port}/dogs/{name}'.format(port=PORT, name=test_dog['name']))

        self.assertEqual(404, r.status_code)
        message = "We don't know a dog by that name."
        self.assertEqual(r.text, ERROR_TEMPLATE.format(status=404, message=message))

    def test_post(self):

        # Tests placing a new dog on the website

        new_dog = {'name': 'Parker',
                   'breed': 'Ridgeback',
                   'age': 5}

        r = requests.post('http://localhost:{port}/dogs/'.format(port=PORT), json=new_dog)
        self.assertEqual(r.status_code, 201)

        r = requests.get('http://localhost:{port}/dogs/{name}'.format(port=PORT, name=new_dog['name']))
        return_json = r.json()

        self.assertEqual(200, r.status_code)
        self.assertEqual(new_dog, return_json)

        # Cleanup the placement of that dog.
        requests.delete('http://localhost:{port}/dogs/{name}'.format(port=PORT, name=new_dog['name']))

        # Tests a request that does not use proper JSON

        r = requests.post('http://localhost:{port}/dogs/'.format(port=PORT), data=new_dog)
        self.assertEqual(r.status_code, 400)
        message = 'POST request expects JSON formatted data.'
        self.assertEqual(r.text, ERROR_TEMPLATE.format(status=400, message=message))


        # Tests adding a malformed dogs to the website.

        bad_dog = {'name': 'Rex',
                   'age': 8}

        r = requests.post('http://localhost:{port}/dogs/'.format(port=PORT), json=bad_dog)
        self.assertEqual(r.status_code, 400)
        message = 'Entering a dog requires a(n) breed.'
        self.assertEqual(r.text, ERROR_TEMPLATE.format(status=400, message=message))

        worse_dog = {'name': 'Rex',
                     'breed': 'Blue Heeler',
                     'coat': 'shiny',
                     'age': 8}

        r = requests.post('http://localhost:{port}/dogs/'.format(port=PORT), json=worse_dog)
        self.assertEqual(r.status_code, 400)
        message = 'Too many attributes passed for a dog.'
        self.assertEqual(r.text, ERROR_TEMPLATE.format(status=400, message=message))

        # Tests adding a dog that has already been added to the website.

        existing_dog = {'name': 'Barton',
                        'breed': 'Toy Poodle',
                        'age': 2}

        r = requests.post('http://localhost:{port}/dogs/'.format(port=PORT), json=existing_dog)
        self.assertEqual(r.status_code, 400)
        message = 'A dog already exists by that name. We only allow one dog per name.'
        self.assertEqual(r.text, ERROR_TEMPLATE.format(status=400, message=message))

    def test_put(self):

        update_dog = 'Barton'

        # (Save original dog state for later)

        r = requests.get('http://localhost:{port}/dogs/{name}'.format(port=PORT, name=update_dog))
        old_dog = r.json()

        def test_attribute(attribute, value):
            """Helper function for testing attributes"""
            change = {attribute: value}
            r = requests.put('http://localhost:{port}/dogs/{name}'.format(port=PORT, name=update_dog), json=change)
            self.assertEqual(r.status_code, 200, r.text)

            r = requests.get('http://localhost:{port}/dogs/{name}'.format(port=PORT, name=update_dog))
            self.assertEqual(r.json()[attribute], value)

        # Tests updating the breed of a dog.
        test_attribute('breed', 'Great Pyrenees')

        # Tests updating the age of a dog.
        test_attribute('age', 10)

        # (Change everything back)

        # (First try with the 'name' attribute still in the old_dog. This should throw an error)
        r = requests.put('http://localhost:{port}/dogs/{name}'.format(port=PORT, name=update_dog), json=old_dog)
        self.assertEqual(r.status_code, 400)
        message = 'Edit failed, you cannot change a dog\'s name.'
        self.assertEqual(r.text, ERROR_TEMPLATE.format(status=400, message=message))

        # (Now pop the name out and try again, this should work)
        old_dog_name = old_dog.pop('name')
        r = requests.put('http://localhost:{port}/dogs/{name}'.format(port=PORT, name=update_dog), json=old_dog)
        self.assertEqual(r.status_code, 200)

        # Tests a request that does not use proper JSON

        r = requests.put('http://localhost:{port}/dogs/{name}'.format(port=PORT, name=update_dog), data=old_dog)
        self.assertEqual(r.status_code, 400)
        message = 'PUT request expects JSON formatted data.'
        self.assertEqual(r.text, ERROR_TEMPLATE.format(status=400, message=message))

        # Tests updating a nonexistent attribute of a dog.
        change = {'coat': 'shaggy'}
        r = requests.put('http://localhost:{port}/dogs/{name}'.format(port=PORT, name=update_dog), json=change)
        self.assertEqual(r.status_code, 400)
        message = 'Edit failed, coat is not a recognized attribute.'
        self.assertEqual(r.text, ERROR_TEMPLATE.format(status=400, message=message))

        # Double Check that it has been fixed back (Also tests, multiple update)
        old_dog['name'] = old_dog_name
        r = requests.get('http://localhost:{port}/dogs/{name}'.format(port=PORT, name=old_dog_name))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(old_dog, r.json())

        # Test updating a nonexistent dog.
        nonexistent_dog_name = 'Petra'
        change = {'age': 2}
        r = requests.put('http://localhost:{port}/dogs/{name}'.format(port=PORT, name=nonexistent_dog_name), json=change)
        self.assertEqual(r.status_code, 404)
        message = 'We don\'t know a dog by that name. Edit was not completed.'
        self.assertEqual(r.text, ERROR_TEMPLATE.format(status=404, message=message))

    def test_delete(self):

        # Tests deleting a dog

        # (Add the dog first)
        new_dog = {'name': 'Comet',
                   'breed': 'Labrador',
                   'age': 11}

        requests.post('http://localhost:{port}/dogs/'.format(port=PORT), json=new_dog)

        r = requests.delete('http://localhost:{port}/dogs/{name}'.format(port=PORT, name=new_dog['name']), json=new_dog)
        self.assertEqual(r.status_code, 200)

        r = requests.get('http://localhost:{port}/dogs/{name}'.format(port=PORT, name=new_dog['name']))
        self.assertEqual(r.status_code, 404)

        # Tests deleting a nonexistent dog

        bad_dog = 'Barney'
        r = requests.delete('http://localhost:{port}/dogs/{name}'.format(port=PORT, name=bad_dog))
        self.assertEqual(r.status_code, 404)


if __name__ == '__main__':
    print("Make sure to start the web server first.")
    unittest.main()

