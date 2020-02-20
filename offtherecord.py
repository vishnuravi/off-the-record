from flask import Flask, request, redirect, render_template
from pymongo import MongoClient
from twilio.twiml.messaging_response import Body, Message, Redirect, MessagingResponse
import time
import json
import secrets

app = Flask(__name__)

#load settings from config file
app.config.from_object("config.DevelopmentConfig")
base_url = app.config["SERVER_URL"]
sms_number = app.config["SMS_NUMBER"]
doctor_name = app.config["DOCTOR_NAME"]

#connect to database
client = MongoClient()
db = client.offtherecord

#make constants available globally to templates
@app.context_processor
def inject_constants():
    return dict(base_url=base_url, sms_number=sms_number, doctor_name=doctor_name)

#renders home page
@app.route("/")
def index_page():
    return render_template('home.html')
 
#recieves sms from Twilio and sends back link to compose message
@app.route("/process_sms", methods=['POST'])
def process_sms():
    phone_number = request.values.get('From', None)
    message = request.values.get('Body', None)
    resp = MessagingResponse()
    message = Message()
    
    #check if sender's phone number is registered
    valid_user = db.users.find_one({"phone_number" : phone_number})
    if valid_user is not None:
        #if registered, create new token and send compose message link
        token = secrets.token_urlsafe(8)
        db.tokens.insert_one({"token": token, "phone_number": phone_number, "time": int(time.time())})
        link = base_url + "/c/" + token
        message.body("Hey {}! Tap this link to send a secure message to {}. {}".format(valid_user['first_name'], doctor_name, link))
    else:
        #if not registered, send registration link
        message.body("Hi! Your number wasn't recognized as belonging to a current patient. Please register at this link: {}/register/{}".format(base_url, phone_number))
    resp.append(message)
    return str(resp)

#renders form to compose message
@app.route("/c/<token>", methods=['GET'])
def compose(token):
    #check if token is valid and render compose message page
    valid_token = db.tokens.find_one({"token": token})
    if valid_token is not None:
        phone_number = valid_token['phone_number']
        user = db.users.find_one({"phone_number" : phone_number})
        return render_template('compose.html', phone_number=phone_number, first_name=user['first_name'], last_name=user['last_name'],token=token)
    else:
        return render_template('expired.html')
	

#saves message to database
@app.route("/send", methods=['POST'])
def save():
    token = request.values.get('token', None)
    valid_token = db.tokens.find_one({"token": token})
    if valid_token is not None:
        message = request.values.get('message', None)
        phone_number = request.values.get('phone_number', None)
        db.messages.insert_one({"phone_number": phone_number, "message": message, "time": int(time.time())})
        db.tokens.remove({"token": token})
    else:
        return render_template('expired.html')
    return render_template('sent.html')
    
#register a new phone number
@app.route("/register", methods=['GET'])
@app.route("/register/<phone_number>", methods=['GET'])
def register(phone_number=''):
    return render_template('register.html', phone_number=phone_number)
	
#process new registration
@app.route("/create_user", methods=['POST'])
def process_registration():
    first_name = request.values.get('first_name', None)
    last_name = request.values.get('last_name', None)
    phone_number = request.values.get('phone_number', None)
    db.users.insert_one({"first_name": first_name, "last_name": last_name, "phone_number": phone_number})
    return render_template('registered.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
