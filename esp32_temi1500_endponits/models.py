from flask_restx import fields, reqparse
from . import api
from database import db

# Models
esp_data_model = api.model('ESPTEMI1500Data', {
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
class ESPTEMI1500Data(db.Model):
    __tablename__ = 'esp_temi1500_data'

    id = db.Column(db.Integer, primary_key=True)
    org = db.Column(db.String(255), nullable=False)
    dept = db.Column(db.String(255), nullable=False)
    room = db.Column(db.String(255), nullable=False)
    line = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(255), nullable=False)
    u_id = db.Column(db.String(255), unique=True, nullable=False)
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
        return f'<ESPTEMI1500Data {self.u_id}>'

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

# Define the request parser
get_esp_firmware_parser = reqparse.RequestParser()
get_esp_firmware_parser.add_argument('filePrefix', type=str, required=True, choices=['tempSensorLily', 'temi1500ESP32'], help='The file prefix')
get_esp_firmware_parser.add_argument('screenSize', type=str, required=True, help='The screen size')
get_esp_firmware_parser.add_argument('version', type=str, required=True, help='The current firmware version')
get_esp_firmware_parser.add_argument('update', type=str, required=True, choices=['Y', 'N'], help='Whether to update the firmware')

update_firm_ver_model = api.model('UpdateFirmVer', {
    'firm_ver': fields.String(required=True, description='Firmware Version')
})