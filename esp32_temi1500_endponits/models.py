from flask_restx import fields
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

device_check_model = api.model('DeviceCheck', {
    'deviceName': fields.String(description='Device Name'),
    'exist': fields.String(description='Existence Flag')
})

firmware_check_model = api.model('FirmwareCheck', {
    'hasnewversion': fields.String(description='New Version Flag')
})

