from flask import Flask, render_template, jsonify, request
import socket
import os
import sys

# To import serverhandler (which is on the parent dir) as a module
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)
from serverhandler import Handler

app = Flask(__name__)

HOST = 'your server address'
CONTAINER = 'here it does not really matter, not used'
PORT = 12345 # A number, not a string

# This is the line of text to display on the web page
line_of_text = "Server status: closed"

handler = Handler(HOST,CONTAINER,600)

@app.route('/')
def index():
    return render_template('index.html', text=line_of_text)

@app.route('/update-text')
def update_text():
    global line_of_text
    global handler
    if handler.is_server_open():
        num_players = handler.get_server_players()
        line_of_text = "Server status: open, " + str(num_players) + " online"
    else:
        line_of_text = "Server status: closed"
    return jsonify({'text': line_of_text})

@app.route('/button-pressed', methods=['POST'])
def button_pressed():
    global line_of_text

    message = "Open the server"
    send_message_to_server(message)
    return jsonify({'status': 'Message sent', 'text': message})

def send_message_to_server(message):
    global HOST
    global PORT
    try:
        server_ip = socket.gethostbyname(HOST)  # Resolve the hostname to an IP address
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_ip,PORT))
            s.sendall(message.encode('utf-8'))
    except socket.gaierror:
        raise Exception(f"Could not resolve hostname {HOST}")

if __name__ == '__main__':
    app.run(debug=True)