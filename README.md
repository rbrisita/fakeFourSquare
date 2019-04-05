# fake Four Square
> Example Web Application

![ffs](https://drive.google.com/uc?export=view&id=1zc-xQoqIU7q2FBwLdEkZSwyaIKClXeZJ)

This is an example web application written using JS with a Python backend and MongoDB data store.
It finds the user's location or sets a default, then requests fake places or generates 10 new ones
with fake reviews (up to 5). The user can leave reviews or get directions for a selected place.
Generated data and saved reviews last for 10 minutes from creation. If places and reviews get deleted,
refresh browser.

## Run Locally
1. Install MongoDB

OS X:

```sh
brew install mongodb
mkdir -p data/db
```

2. Run MongoDB
```sh
mongod --fork --dbpath 'data/db' --bind_ip 127.0.0.1 --logpath '/usr/local/var/log/mongodb/mongo.log' --logappend --pidfilepath db.pid
```

3. Install dependencies
```sh
pip install -r requirements.txt
mkdir logs
touch logs/app.log
```

4. Get a Map Access Token

The example application uses [Mapbox](https://www.mapbox.com/signup/).

Either in an `.env` file enter:
```sh
MAP_ACCESS_TOKEN='{INSERT_YOUR_TOKEN}'
```

or

In the config.py file replace `{INSERT_YOUR_TOKEN}`

5. Run Server
Flask
```sh
FLASK_DEBUG=true FLASK_APP=app/main.py flask run
```

or

Gunicorn
```sh
gunicorn main:app --error-logfile logs/error.log --access-logfile logs/access.log --pid app.pid --daemon --chdir app && tail -f logs/app.log
```

6. Launch Browser

Either 127.0.0.1:5000 or 127.0.0.1:8000

1. Stop Services

Flask
Ctrl+C

or

Gunicorn
```sh
kill -s HUP $(cat app.pid) && kill -9 $(cat app.pid)
```

MongoDB
```sh
mongo --eval "db.getSiblingDB('admin').shutdownServer()"
```

## Colophon
* MongoDB
* Python ([dotenv](https://github.com/theskumar/python-dotenv), Flask, Jinja, PyMongo, [Faker](https://faker.readthedocs.io/en/master/index.html))
* jQuery
* Leaflet
* Bootstrap
* [Feather Icons](https://feathericons.com)
* [Spin Kit](http://tobiasahlin.com/spinkit/)

## Considerations for Improvement
* Sanitize input when leaving a review. As of now XSS is possible.
* Dependency injection for backend code to clean up global variables.
* Extract JS template strings to script tags with 'type="text/x-template"' to separate presentation and functionality.
