from flask_restx import fields, reqparse
from . import api
from database import db

# Flask-Restx API models
esp_data_model = api.model('LILYGOS3DATA', {
    'org': fields.String(required=True, description='Organization'),
    'dept': fields.String(required=True, description='Department'),
    'room': fields.String(required=True, description='Room'),
    'line': fields.String(required=True, description='Line'),
    'display_name': fields.String(required=True, description='Display Name'),
    'u_id': fields.String(required=True, description='Unique ID'),
    'device_type': fields.String(required=True, description='Device Type'),
    'firm_ver': fields.String(required=True, description='Firmware Version')
})

# SQLAlchemy models
class LILYGOS3DATA(db.Model):
    __tablename__ = 'esp_data_lilygo_s3'

    id = db.Column(db.Integer, primary_key=True)
    org = db.Column(db.String(255), nullable=False)
    dept = db.Column(db.String(255), nullable=False)
    room = db.Column(db.String(255), nullable=False)
    line = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(255), nullable=False)
    u_id = db.Column(db.String(255), unique=True, nullable=False)  # Assuming this is unique in esp_data_lilygo_s3
    device_type = db.Column(db.String(255), nullable=False)
    firm_ver = db.Column(db.String(255), nullable=False)

    def __init__(self, org, dept, room, line, display_name, u_id, device_type, firm_ver):
        self.org = org
        self.dept = dept
        self.room = room
        self.line = line
        self.display_name = display_name
        self.u_id = u_id
        self.device_type = device_type
        self.firm_ver = firm_ver

    def __repr__(self):
        return f'<LILYGOS3DATA {self.u_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'org': self.org,
            'dept': self.dept,
            'room': self.room,
            'line': self.line,
            'display_name': self.display_name,
            'u_id': self.u_id,
            'device_type': self.device_type,
            'firm_ver': self.firm_ver
        }

sensor_data_model = api.model('SENSORDATATEMPHUMI', {
    'u_id': fields.String(required=True, description='Unique ID'),
    'hSlope': fields.Float(description='Humidity Slope'),
    'tSlope': fields.Float(description='Temperature Slope'),
    'hIntercept': fields.Float(description='Humidity Intercept'),
    'tIntercept': fields.Float(description='Temperature Intercept'),
    'temp_limit': fields.String(description='Temperature Limit'),
    'humi_limit': fields.String(description='Humidity Limit'),
    'sensor_id': fields.String(description='Sensor ID')
})

# SQLAlchemy models
class SENSORTEMPHUMIDATA(db.Model):
    __tablename__ = 'sensor_temphumi_data'

    id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.String(255), db.ForeignKey('esp_data_lilygo_s3.u_id'), unique=True, nullable=False)
    h_slope = db.Column(db.Float, nullable=True)
    t_slope = db.Column(db.Float, nullable=True)
    h_intercept = db.Column(db.Float, nullable=True)
    t_intercept = db.Column(db.Float, nullable=True)
    temp_limit = db.Column(db.String(255), nullable=True)
    humi_limit = db.Column(db.String(255), nullable=True)
    sensor_id = db.Column(db.String(255), nullable=False)

    esp_device = db.relationship('LILYGOS3DATA', backref='sensor_data')

    def __init__(self, u_id, h_slope, t_slope, h_intercept, t_intercept, sensor_id, temp_limit, humi_limit):
        self.u_id = u_id
        self.h_slope = h_slope
        self.t_slope = t_slope
        self.h_intercept = h_intercept
        self.t_intercept = t_intercept
        self.temp_limit = temp_limit
        self.humi_limit = humi_limit
        self.sensor_id = sensor_id

    def __repr__(self):
        return f'<SENSORTEMPHUMIDATA {self.u_id}>'

    def to_dict(self):
        return {
            'u_id': self.u_id,
            'h_slope': self.h_slope,
            't_slope': self.t_slope,
            'h_intercept': self.h_intercept,
            't_intercept': self.t_intercept,
            'temp_limit': self.temp_limit,
            'humi_limit': self.humi_limit,
            'sensor_id': self.sensor_id
        }
    
# Define the request parser
get_esp_firmware_parser = reqparse.RequestParser()
get_esp_firmware_parser.add_argument('key', type=str, required=True, help='The API key')
get_esp_firmware_parser.add_argument('filePrefix', type=str, required=True, help='The file prefix')
get_esp_firmware_parser.add_argument('screenSize', type=str, required=True, help='The screen size')
get_esp_firmware_parser.add_argument('version', type=str, required=True, help='The current firmware version')
get_esp_firmware_parser.add_argument('update', type=str, required=True, choices=['Y', 'N'], help='Whether to update the firmware')

update_firm_ver_model = api.model('UpdateFirmVer', {
    'firm_ver': fields.String(required=True, description='Firmware Version')
})
