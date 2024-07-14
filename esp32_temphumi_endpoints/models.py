from flask_restx import fields
from . import api
from database import db

# Models
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

class LILYGOS3DATA(db.Model):
    __tablename__ = 'esp_data_lilygo_s3'

    id = db.Column(db.Integer, primary_key=True)
    org = db.Column(db.String(255), nullable=False)
    dept = db.Column(db.String(255), nullable=False)
    room = db.Column(db.String(255), nullable=False)
    line = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(255), nullable=False)
    u_id = db.Column(db.String(255), db.ForeignKey('esp_data_lilygo_s3.u_id'), unique=True, nullable=False)
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
    sensor_data = db.relationship('SENSORTEMPHUMIDATA', backref='esp_device', uselist=False)

sensor_data_model = api.model('SENSORDATATEMPHUMI', {
    'hSlope': fields.Float(description='Humidity Slope'),
    'tSlope': fields.Float(description='Temperature Slope'),
    'hIntercept': fields.Float(description='Humidity Intercept'),
    'tIntercept': fields.Float(description='Temperature Intercept'),
    'sensor_id': fields.String(description='Sensor ID')
})

class SENSORTEMPHUMIDATA(db.Model):
    __tablename__ = 'sensor_temphumi_data'

    id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.String(255), db.ForeignKey('sensor_temphumi_data.u_id'), unique=True, nullable=False)
    h_slope = db.Column(db.Float, nullable=True)
    t_slope = db.Column(db.Float, nullable=True)
    h_intercept = db.Column(db.Float, nullable=True)
    t_intercept = db.Column(db.Float, nullable=True)
    sensor_id = db.Column(db.String(255), nullable=True)

    def __init__(self, u_id, humidity, temperature, h_slope, t_slope, h_intercept, t_intercept, device_name):
        self.u_id = u_id
        self.humidity = humidity
        self.temperature = temperature
        self.h_slope = h_slope
        self.t_slope = t_slope
        self.h_intercept = h_intercept
        self.t_intercept = t_intercept
        self.device_name = device_name

    def __repr__(self):
        return f'<SENSORTEMPHUMIDATA {self.u_id}>'

    def to_dict(self):
        return {
            'Hum': self.humidity,
            'Tem': self.temperature,
            'hSlope': self.h_slope,
            'tSlope': self.t_slope,
            'hIntercept': self.h_intercept,
            'tIntercept': self.t_intercept,
            'sensor_id': self.u_id
        }
    esp_device = db.relationship('LILYGOS3DATA', back_populates='sensor_temphumi_data')

device_check_model = api.model('DeviceCheck', {
    'deviceName': fields.String(description='Device Name'),
    'exist': fields.String(description='Existence Flag')
})

firmware_check_model = api.model('FirmwareCheck', {
    'hasnewversion': fields.String(description='New Version Flag')
})

