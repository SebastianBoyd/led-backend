from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
socketio = SocketIO(app)

def color_to_number(hex_code):
    hex_code = hex_code.lstrip('#')
    num = int(hex_code, 16)
    return num

def zeros():
    return [ ["#000"]*40 for _ in range(20) ]

display = {}
display['pixels'] = zeros()
display['brightness'] = 255

@app.after_request
def add_header(response):
    response.cache_control.max_age = 60
    return response

@app.route('/')
def index():
    return render_template('index.html', **values)

@app.route('/display.js')
def display_json():
    return 'const display = ' + json.dumps(display)

@socketio.on('pixel changed')
def pixel_changed(x, y, color):
    if 0 <= x < 20 and 0 <= y < 40:
        display['pixels'][x][y] = color
        emit('sync pixel', (x, y, color), broadcast=True)

@socketio.on('brightness changed')
def brightness_changed(value):
    display['brightness'] = value;
    emit('sync brightness', value, broadcast=True)

@socketio.on('clear')
def clear():
    global display 
    display['pixels'] = zeros()
    emit('clear_sync', broadcast=True)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')