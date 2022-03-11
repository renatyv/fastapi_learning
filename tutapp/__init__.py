import os
from flask import Flask

from tutapp.db import get_db_connection


def create_app(test_config=None):
	"""Flask application factory"""
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
		SECRET_KEY='dev',
		DATABASE=os.path.join(app.instance_path,'tutapp.sqlite')
		)
	if test_config is None:
		# load the instance config, if it exists, when not testing
		app.config.from_pyfile('config.py', silent=True)
	else:
		# load the test config if passed in
		app.config.from_mapping(test_config)

	print(app.instance_path)
	# ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	# add routes
	@app.route('/hello')
	def hello():
		get_db_connection()
		return 'Hello world!'

	# init database
	from . import db
	db.init_app(app)

	return app