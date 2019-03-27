Example application using the Python language, MongoDB data store, Flask framework with Jinga2 for templating.

Originally created to work with Heroku.

Install
mongod --dbpath data/db/ --bind_ip 127.0.0.1
python setup.py
gunicorn main:_app --error-logfile error.log --access-logfile access.log --pid app.pid --daemon --chdir app && tail -f app.log
kill -s HUP $(cat app.pid) && kill -9 $(cat app.pid)
