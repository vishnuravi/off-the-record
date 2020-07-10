from flask import Flask, request, redirect, render_template, jsonify
from pymongo import MongoClient
from twilio.twiml.messaging_response import Body, Message, Redirect, MessagingResponse
from marshmallow import ValidationError
from schemas import UserSchema, MessageSchema
import time
import json
import secrets
import os


class CustomFlask(Flask):
    """Defines custom delimiters for Jinja to avoid conflict with Vue.js"""
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(
        dict(variable_start_string='[[', variable_end_string=']]'))


app = CustomFlask(__name__)

# Load settings from config file
if os.environ['FLASK_ENV'] == 'production':
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

base_url = app.config["SERVER_URL"]
sms_number = app.config["SMS_NUMBER"]
doctor_name = app.config["DOCTOR_NAME"]

# Connect to database
client = MongoClient(host=app.config['MONGODB_HOST'])
db = client.offtherecord


@app.context_processor
def inject_constants():
    """Make constants available globally to templates"""
    return dict(base_url=base_url, sms_number=sms_number, doctor_name=doctor_name)


@app.route("/")
def index_page():
    """Renders home page"""
    return render_template('home.html')


@app.route("/process_sms", methods=['POST'])
def process_sms():
    """Recieves incoming SMS from Twilio and responds with a link to compose a message"""
    phone_number = request.values.get('From', None)
    message = request.values.get('Body', None)
    resp = MessagingResponse()
    message = Message()

    valid_user = db.users.find_one({"phone_number": phone_number})
    if valid_user is not None:
        token = secrets.token_urlsafe(8)
        db.tokens.insert_one(
            {"token": token, "phone_number": phone_number, "time": int(time.time())})
        link = base_url + "/c/" + token
        message.body("Hey {}! Tap this link to send a secure message to {}. {}".format(
            valid_user['first_name'], doctor_name, link))
    else:
        message.body("Hi! Your number wasn't recognized as belonging to a current patient. Please register at this link: {}/register/{}".format(base_url, phone_number))
    resp.append(message)
    return str(resp)


@app.route("/c/<token>", methods=['GET'])
def compose(token):
    """Renders form to compose a new message"""
    valid_token = db.tokens.find_one({"token": token})
    if valid_token is not None:
        phone_number = valid_token['phone_number']
        user = db.users.find_one({"phone_number": phone_number})
        return render_template('compose.html', phone_number=phone_number, first_name=user['first_name'], last_name=user['last_name'], token=token)
    else:
        return render_template('expired.html')


@app.route("/send", methods=['POST'])
def save_message():
    """Saves a message to the database"""
    data = request.get_json()

    try:
        result = MessageSchema().load(data)
    except ValidationError as err:
        return err.messages, 400

    token = data['token']
    valid_token = db.tokens.find_one({"token": token})
    if valid_token is not None:
        db.messages.insert_one(
            {"phone_number": data['phone_number'], "message": data['message'], "time": int(time.time())})
        db.tokens.remove({"token": token})
        return jsonify(success=True)
    else:
        return jsonify(error="Invalid token"), 401


@app.route("/register/", methods=['GET'])
@app.route("/register/<phone_number>", methods=['GET'])
def register(phone_number=''):
    """Renders form to register a new user"""
    return render_template('register.html', phone_number=phone_number)


@app.route("/create_user", methods=['POST'])
def create_user():
    """Creates a new user"""
    data = request.get_json()

    try:
        result = UserSchema().load(data)
    except ValidationError as err:
        return err.messages, 400

    if db.users.find_one({"phone_number": data['phone_number']}) is None:
        db.users.insert_one({"first_name": data['first_name'], "last_name": data['last_name'],
                             "date_of_birth": data['date_of_birth'], "phone_number": data['phone_number']})
        return jsonify(success=True), 201
    else:
        return jsonify(error="Phone number already registered."), 409


if __name__ == "__main__":
    app.run(host='0.0.0.0')
