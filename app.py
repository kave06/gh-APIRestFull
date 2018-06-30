from flask import Flask, jsonify, abort, make_response
from flask_httpauth import HTTPBasicAuth
from flask_socketio import SocketIO, emit, send
from ghTools import *

auth = HTTPBasicAuth()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app)


@auth.get_password
def get_password(username):
    if username == 'kave':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/get_sensor/<int:sensor_id>/<int:days>', methods=['GET'])
# @auth.login_required
def get_sensor(sensor_id, days):
    model = Model()
    list = ({
        'sensor': 1,
        'data': {
            'temp' : 25,
            'humi' : 45
        }
    })

    if list.items() == 0:
        abort(404)

    # list = model.select_ambient(1,1)

    return jsonify(list)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

# @socketio.on('my event', namespace='/test')
# def test_message(message):
#     emit('my response', {'data': message['data']})


if __name__ == '__main__':
    app.run(debug=True)
    # socketio.run(app)
