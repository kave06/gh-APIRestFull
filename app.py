from datetime import datetime, timedelta
from flask import Flask, jsonify, abort, make_response, request
from flask_httpauth import HTTPBasicAuth
from flask_script import Manager
from threading import Thread, ThreadError

from ghTools.irrigation import Irrigation
from ghTools.sensor import Sensor
from ghTools.logger import Logger
import logging

auth = HTTPBasicAuth()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
manager = Manager(app)

logger = Logger().init_logger()
logger.info('Init API Restfull')


@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello World!'


@app.route('/last_value/temp/<int:sensor_id>', methods=['GET'])
# @auth.login_required
def get_last_temp(sensor_id):
    sensor = Sensor(id=sensor_id)
    rs = sensor.get_last_temperature()
    if rs == None:
        abort(404)
    logger.debug(rs)
    return jsonify(rs)


@app.route('/last_value/humi/<int:sensor_id>', methods=['GET'])
# @auth.login_required
def get_last_humi(sensor_id):
    sensor = Sensor(id=sensor_id)
    rs = sensor.get_last_humidity()
    if rs == None:
        abort(404)
    logger.debug(rs)
    return jsonify(rs)


@app.route('/get_sensor/<int:sensor_id>/<int:days>', methods=['GET'])
# @auth.login_required
def get_sensor(sensor_id, days):
    sensor = Sensor(sensor_id)
    rs = sensor.get_last_climate(days)  # type: list

    if len(rs) == 0:
        abort(404)

    logger.debug(rs)
    return jsonify(rs)


@app.route('/insert_irrigation', methods=['POST'])
def insert_irrigation():
    if not request.json:
        abort(400)

    logger.debug(request.json)
    format = '%Y-%m-%d %H:%M:%S.%f'

    start = datetime.strptime(request.json['start'], format)
    duration = float(request.json['duration'])
    id_relay = int(request.json['id_relay'])
    liters = int(request.json['liters'])

    ir = Irrigation(id_relay=id_relay, start=start, duration=duration, liters=liters)
    insert = ir.insert_irrigation()
    logger.debug('insert:{}'.format(insert))
    if insert:
        t = Thread(target=ir.add_scheduler)
        t.start()
        return 'Irrigation inserted correctly'
    else:
        return 'There is irrigation scheduled at the same time'


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@auth.get_password
def get_password(username):
    if username == 'kave':
        return 'python'
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)


if __name__ == '__main__':
    manager.run()
