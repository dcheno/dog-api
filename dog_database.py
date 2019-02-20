import sqlite3

DATABASE_NAME = 'dog.db'
DOG_ATTRIBUTES = ['name', 'breed', 'age']


class DogDatabaseError(Exception):
    pass


class DogNotFoundError(DogDatabaseError):
    def __init__(self):
        super().__init__('We don\'t know a dog by that name.')


class DogDatabase:
    def __init__(self, conn_name=DATABASE_NAME):
        self._connection = sqlite3.connect(conn_name)
        self._cursor = self._connection.cursor()

    def insert(self, dog):
        """Creates a record for the given dog in the database with the
        given attributes. Expects dog as a dictionary."""
        for attribute in DOG_ATTRIBUTES:
            if attribute not in dog:
                raise DogDatabaseError('Entering a dog requires a(n) {atr}.'.format(atr=attribute))

        if len(dog) > len(DOG_ATTRIBUTES):
            raise DogDatabaseError('Too many attributes passed for a dog.')

        template = 'INSERT INTO dogs ({atrs}) VALUES (?, ?, ?)'.format(atrs=', '.join(DOG_ATTRIBUTES))
        params = [dog[attribute] for attribute in DOG_ATTRIBUTES]

        try:
            self._cursor.execute(template, params)
        except sqlite3.IntegrityError:
            raise DogDatabaseError('A dog already exists by that name. We only allow one dog per name.')

        self._connection.commit()

    def select(self, dog_name):
        """Returns a dictionary with the attributes for the given dog"""
        template = 'SELECT {atrs} FROM dogs WHERE name=?'.format(atrs=', '.join(DOG_ATTRIBUTES))
        self._cursor.execute(template, (dog_name,))

        db_dog = self._cursor.fetchone()

        if not db_dog:
            raise DogNotFoundError()

        dog = dict(zip(DOG_ATTRIBUTES, db_dog))

        return dog

    def update(self, dog_name, changes):
        """Updates the values for the given dog for the key value pairs
        provided in the changes parameter"""

        # Validate the changes
        for attribute in changes:
            if attribute not in DOG_ATTRIBUTES:
                raise DogDatabaseError('Edit failed, {atr} is not a recognized attribute.'.format(atr=attribute))

            if attribute == 'name':
                raise DogDatabaseError('Edit failed, you cannot change a dog\'s name.')

        # Make sure this is a dog we know.
        if not self._have_dog(dog_name):
            raise DogNotFoundError()

        for change in changes:
            try:
                # Be cautious of this if above validation code changes -> could allow for injection.
                template = 'UPDATE dogs SET {}=? WHERE name=?'.format(change)
                params = (changes[change], dog_name)
                self._cursor.execute(template, params)
            except sqlite3.Error:
                error_template = 'Update Not Completed for {atr}, {val} and following attributes'
                raise DogDatabaseError(error_template.format(atr=change, val=changes[change]))

        self._connection.commit()

    def delete(self, dog_name):
        """Removes the given dog from the database"""

        # Make sure this is a dog we know.
        if not self._have_dog(dog_name):
            raise DogNotFoundError()

        template = 'DELETE FROM dogs WHERE name=?'
        self._cursor.execute(template, (dog_name,))
        self._connection.commit()

    def close(self):
        """Close out the database connection"""
        self._connection.close()

    def _have_dog(self, dog_name):
        """Checks if we have a dog in the database."""
        template = 'SELECT name FROM dogs WHERE name=?'
        self._cursor.execute(template, (dog_name,))
        name = self._cursor.fetchone()

        return True if name else False
