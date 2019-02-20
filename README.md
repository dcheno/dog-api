# Dog API
An exercise using the Tornado library to create a simple Dog API in Python. Supports finding, adding, updating, and removing representations of dogs from a website.

### Requirements:
Tornado
```bash
pip install tornado
```
### Starting the Application:
```bash
python3 dog_api.py &
```
By default, the dog API will run on port 8888.

### Finding a Dog:
Append the name of the dog to the end of the URL and send an HTTP GET request.

For example:
http://localhost:8888/dogs/Barton
will return Barton

### Adding a Dog:
Send an HTTP POST request with a JSON representation of your dog to the root url (http://localhost:8888/dogs)

Expected format:
```python
{'name': [Dog's Name (string)], 'age': [Dog's age (int)], 'breed': [Dog's breed (string)]}
```

### Updating A Dog

In an HTTP PUT request, send a JSON object with key value pairs of the attributes and values you want to change to the URL for the dog you want to update.

For example:
If you wanted to update Barton's age, you might send the JSON object:
```python
{'age': 10}
```
To the URL http://localhost:8888/dogs/Barton

You are not allowed to change the name of a dog. You are allowed to change more than one attribute at a time.

### Deleting a Dog
Send an HTTP DELETE request to the URL for the dog that you need to remove.
