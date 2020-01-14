from flask import Flask, request, redirect, render_template
from pymongo import MongoClient
from twilio.twiml.messaging_response import Body, Message, Redirect, MessagingResponse
import os, time, json

server_url = "http://apps.vishnu.io:5000"

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(variable_start_string='%%', variable_end_string='%%'))

client = MongoClient()
db = client.nyphack

app = CustomFlask(__name__)

@app.route("/")
def index_page():
    return "Hello"
 
#recieves sms from Twilio and sends back link to compose message
@app.route("/process_sms", methods=['GET', 'POST'])
def process_sms():
    phone_number = request.values.get('From', None)
    message = request.values.get('Body', None)
    resp = MessagingResponse()
    message = Message()
    
    #check if sender's phone number is registered
    valid_number = db.users.find_one({"phone_number" : phone_number})
    if valid_number is not None:
        token = os.urandom(8).encode('hex')
        db.tokens.insert_one({"token": token, "phone_number": phone_number, "time": int(time.time())})
        message.body("Hi! Tap the following link to send a secure message to your doctor. " + server_url + "/c/" + token)
    else:
        message.body("Your number was not recognized as belonging to a current patient. Register at the following link: " + server_url + "/register/" + phone_number)
    
    resp.append(message)
    return str(resp)

#renders form to compose message
@app.route("/c/<token>", methods=['GET', 'POST'])
def compose(token):
    valid_token = db.tokens.find_one({"token": token})
    if valid_token is not None:
        phone_number = valid_token['phone_number']
        db.tokens.remove({"token": token})
        return render_template('compose.html', phone_number=phone_number)
    else:
        return "<h1>This link has been used already or expired. Please try again.</h1>"
	

#saves message to database
@app.route("/send", methods=['GET', 'POST'])
def save():
    message = request.values.get('message', None)
    phone_number = request.values.get('phone_number', None)
    db.messages.insert_one({"phone_number": phone_number, "message": message, "time": int(time.time())})
    return "ok"
    
#register a new phone number
@app.route("/register/<phone_number>")
def register(phone_number):
    return render_template('register.html', phone_number=phone_number)
	
#process new registration
@app.route("/process_registration", methods=['GET', 'POST'])
def process_registration():
    first_name = request.values.get('first_name', None)
    last_name = request.values.get('last_name', None)
    phone_number = request.values.get('phone_number', None)
    db.users.insert_one({"first_name": first_name, "last_name": last_name, "phone_number": phone_number})
    return "ok"
    
#retrieve all messages
@app.route("/messages")
def retrieve_messages():
    cursor = db.messages.find()
    response = []
    for doc in cursor:
        response.append({'phone_number' : doc['phone_number'], 'message' : doc['message']})
    return json.dumps(response)

#doctor dashboard
@app.route("/dashboard")
def dashboard():
    return "Dashboard goes here"
 
if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
