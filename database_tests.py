import unittest

from dog_database import DogDatabase, DogDatabaseError, DogNotFoundError

"""Tests dog_database module"""


class DogDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.db = DogDatabase()

    def test_select(self):
        """Test the select method of DogDatabase"""

        # Test existing dog
        dog_to_test = {'name': 'Barton', 'breed': 'Anatolian', 'age': 8}
        dog = self.db.select(dog_to_test['name'])
        self.assertEqual(dog, dog_to_test)

        # Test nonexisting dog
        dog_to_test = {'name': 'Pinky', 'breed': 'Terrier', 'age': 4}
        with self.assertRaises(DogNotFoundError):
            self.db.select(dog_to_test['name'])

    def test_insert(self):

        dog_to_insert = {'name': 'Gracie', 'breed': 'Cocker', 'age': 13}
        self.db.insert(dog_to_insert)

        dog = self.db.select(dog_to_insert['name'])
        self.assertEqual(dog, dog_to_insert)

        # Clean up
        self.db.delete(dog_to_insert['name'])

        # Try inserting over an already existing dog.

        bad_dog = {'name': 'Barton', 'breed': 'Pug', 'age': 14}
        with self.assertRaises(DogDatabaseError):
            self.db.insert(bad_dog)

        # Double check that no changes were made:
        good_dog = {'name': 'Barton', 'breed': 'Anatolian', 'age': 8}
        self.assertEqual(good_dog, self.db.select(bad_dog['name']))

    def test_update(self):

        # Test changing two attributes
        test_dog = {'name': 'Barton', 'breed': 'Great Pyrenees', 'age': 9}
        changes = {'breed': test_dog['breed'], 'age': test_dog['age']}
        self.db.update(test_dog['name'], changes)

        check_dog = self.db.select(test_dog['name'])
        self.assertEqual(check_dog, test_dog)

        # Clean Up
        self.db.update(test_dog['name'], {'breed': 'Anatolian', 'age': 8})

    def test_delete(self):

        insert_dog = {'name': 'Santa\'s Lil Helper', 'breed': 'Greyhound', 'age': 35}
        self.db.insert(insert_dog)
        self.db.delete(insert_dog['name'])

        with self.assertRaises(DogNotFoundError):
            self.db.select(insert_dog['name'])

    def test_have_dog(self):
        self.assertTrue(self.db._have_dog('Barton'))
        self.assertFalse(self.db._have_dog('Fink'))

if __name__ == '__main__':
    unittest.main()
