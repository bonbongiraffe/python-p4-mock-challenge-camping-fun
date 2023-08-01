#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/activities', methods=["GET"])
def activities():
    #returns all activities
    if request.method == "GET":
        activity_dicts = [a.to_dict() for a in Activity.query.all()]
        return make_response( activity_dicts, 200 )

@app.route('/activities/<int:id>', methods=["DELETE"])
def activities_by_id(id=id):
    #finds activity with provided id
    activity = Activity.query.filter_by(id=id).first()
    if not activity:
        return make_response( {"error": "Activity not found"}, 404 )

    #deletes an activity
    if request.method == "DELETE":
        db.session.delete(activity)
        db.session.commit()
        return make_response( {}, 204 )

@app.route('/campers', methods=["GET", "POST"])
def campers():
    #returns all campers
    if request.method == "GET":
        camper_dicts = [c.to_dict() for c in Camper.query.all()]
        return make_response( camper_dicts, 200 ) 
    
    #create new camper
    if request.method == "POST":
        data = request.get_json()
        try:
            new_camper = Camper(
                name = data["name"],
                age = data["age"]
            )
        except ValueError as v_error:
            return make_response({"errors": "validation errors"}, 400)
        db.session.add(new_camper)
        db.session.commit()
        return make_response(new_camper.to_dict(), 200)

@app.route('/campers/<int:id>', methods=["GET", "PATCH"])
def campers_by_id(id=id):
    #finds camper with provided id
    camper = Camper.query.filter_by(id=id).first()
    if not camper:
        return make_response( {"error": "Camper not found"}, 404 )

    #returns camper dictionary
    if request.method == "GET":
        signup_dicts = []
        for signup in camper.signups:
            signup_dict = signup.to_dict()
            del signup_dict["camper"]
            signup_dicts.append(signup_dict)
        camper_dict = {
            **camper.to_dict(),
            "signups": signup_dicts
        }
        return make_response( camper_dict, 200 )

    #updates existing camper
    if request.method == "PATCH":
        data = request.get_json()
        try: 
            for attr in data:
                setattr( camper, attr, data[attr] )
        except ValueError as v_error:
            return make_response({"errors": ["validation errors"]}, 400 )
        db.session.commit()
        return make_response( camper.to_dict(), 202 )

@app.route('/signups', methods=["POST"])
def signups():
    #create new signup
    if request.method == "POST":
        data = request.get_json()
        try:
            new_signup = Signup(
                camper_id = data["camper_id"],
                activity_id = data["activity_id"],
                time = data["time"]
            )
        except ValueError as v_error:
            return make_response( {"errors": ["validation errors"]}, 400 )
        db.session.add(new_signup)
        db.session.commit()
        return make_response( new_signup.to_dict(), 200 )

if __name__ == '__main__':
    app.run(port=5555, debug=True)
