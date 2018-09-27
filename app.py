from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time, threading
import json
import main

app = Flask(__name__)
socketio = SocketIO(app)
screen = main.LedScreen(brightness=255)

values = {
    'slider1': 25,
    'slider2': 0,
}

def color_to_number(hex_code):
    hex_code = hex_code.lstrip('#')
    num = int(hex_code, 16)
    return num

def zeros():
    return [ ["#000"]*40 for _ in range(20) ]

def render_all():
    for x in range(20):
        for y in range(40):
            screen.set_pixel([x,y], color_to_number(display[x][y]))
    screen.render()

def render_timer():
    screen.render()
    threading.Timer(.5, render_timer).start()

display = zeros()

def update_screen(x, y, color):
    screen.set_pixel([x, y], color_to_number(color))
    screen.render()

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
        display[x][y] = color
        emit('sync pixel', (x, y, color), broadcast=True)
        update_screen(x, y, color)

@socketio.on('clear')
def clear():
    global display
    display = zeros()
    render_all()
    emit('clear_sync', broadcast=True)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')