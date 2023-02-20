#/opt/conda/bin/python3
from flask import Flask, render_template
from flask_restful import Api, Resource
import json

import sqlalchemy
from models import User, House, HouseLease, HouseImage, db
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv
import os
import argparse
import sys

def create_app(dev):
	app = Flask(__name__, template_folder="templates")

	load_dotenv()
	if dev:
		user = os.getenv('DB_USERNAME')
		password = os.getenv('DEV_PASSWORD')
		DBNAME = os.getenv('DB_NAME')
		app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{user}:{password}@localhost:5432/{DBNAME}"
	else:
		# configuration
		USERNAME = os.getenv('DB_USERNAME')
		PASSWORD = os.getenv('DB_PASSWORD')
		DBNAME = os.getenv('DB_NAME')
		PUBLIC_IP_ADDRESS = os.getenv('DB_PUBLIC_IP_ADDRESS')
		PROJECT_ID = os.getenv('PROJECT_ID')
		INSTANCE_UNIX_SOCKET = os.getenv('INSTANCE_UNIX_SOCKET')

		
		uri = sqlalchemy.engine.url.URL(
            drivername="postgresql+psycopg2",
            username=USERNAME,
            password=PASSWORD,
            database=DBNAME,
            query={"host": INSTANCE_UNIX_SOCKET},
			host=None,
			port=None
        )

		app.config['SQLALCHEMY_DATABASE_URI'] = uri.render_as_string(hide_password=False)
		#app.config["SQLALCHEMY_DATABASE_URI"]= f"postgresql://{USERNAME}:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}?host=/cloudsql/{DB_INSTANCE_NAME}"
		app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= True
		user = os.getenv('DB_USER')
		password = os.getenv('DB_PASSWORD')
		#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{0}:{1}@localhost:5432/housenet'.format(user, password)
	db.init_app(app)

	with app.app_context():
		if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
			create_database(app.config['SQLALCHEMY_DATABASE_URI'])
		db.create_all()
	return app


dev = False
if len(sys.argv) > 1:
	dev = sys.argv[1] == 'dev'
app = create_app(dev)

api = Api(app)

# Return JSON of all users
@app.route('/users')
def users():
	users = User.query.all()
	user_list = []
	for user in users:
		user_list.append(user.to_dict())
	return json.dumps(user_list)

# Return JSON of all houses
@app.route('/houses')
def houses():
	houses = House.query.all()
	house_list = []
	for house in houses:
		house_list.append(house.to_dict())
	return json.dumps(house_list)

# Return JSON of all house leases
@app.route('/house_leases')
def house_leases():
	house_leases = HouseLease.query.all()
	lease_list = []
	for lease in house_leases:
		lease_list.append(lease.to_dict())
	return json.dumps(lease_list)

# Return JSON of all house images
@app.route('/house_images')
def house_images():
	house_images = HouseImage.query.all()
	image_list = []
	for image in house_images:
		image_list.append(image.to_dict())
	return json.dumps(image_list)

class HomeAPI(Resource):
	def get(self):
		return render_template('home.html')

api.add_resource(HomeAPI, '/')

if __name__ == '__main__':
	app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))