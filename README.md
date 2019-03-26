Example application using the Python language, MongoDB data store, Flask framework with Jinga2 for templating.

Originally created to work with Heroku.

Install
mongod --dbpath data/db/ --bind_ip 127.0.0.1
python setup.py
gunicorn main:app --log-file errors.log -p app.pid -D
kill -9 $(cat app.pid)
