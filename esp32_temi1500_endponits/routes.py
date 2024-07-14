from flask import request
from flask_restx import Resource
from . import api
from .models import lilygos3_data_model, device_check_model, firmware_check_model, ESPTEMI1500Data
from dotenv import load_dotenv
import os

load_dotenv()
VALID_KEY = os.environ['VALID_KEY']
# Directory where .bin files are stored
FIRMWARE_DIR = os.environ['TEMI1500_FIRMWARE_DIR']
@api.route('/esp_data')
class DeviceList(Resource):
    @api.doc('list_esp_data')
    @api.param('key', 'API Key')
    def get(self):
        key = request.args.get('key')
        if key != VALID_KEY:
            return {'message': 'Invalid API Key'}, 403
        esp_data = ESPTEMI1500Data.query.all()
        return [data.to_dict() for data in esp_data], 200
    
    @api.doc('create_esp_data')
    @api.expect(lilygos3_data_model)
    def post(self):
        key = request.args.get('key')
        code = request.args.get('code')
        """Create a new ESP data entry"""
        # Implementation remains the same as create_esp_data()

@api.route('/esp_data/<int:id>')
class ESPData(Resource):
    @api.doc('update_esp_data')
    @api.expect(lilygos3_data_model)
    def put(self, id):
        """Update an ESP data entry"""
        # Implementation remains the same as update_esp_data()

    @api.doc('delete_esp_data')
    def delete(self, id):
        """Delete an ESP data entry"""
        # Implementation remains the same as delete_esp_data()

@api.route('/checkexist')
class DeviceCheck(Resource):
    @api.doc('check_device_exist')
    @api.param('key', 'API Key')
    @api.param('code', 'Device Code')
    @api.param('devicetype', 'Device Type')
    @api.marshal_with(device_check_model)
    def get(self):
        """Check if a device exists and provide device name"""
        # Implementation remains the same as add_esp_device_data()

@api.route('/getESPFirm')
class Firmware(Resource):
    @api.doc('get_esp_firmware')
    @api.param('key', 'API Key')
    @api.param('filePrefix', 'File Prefix')
    @api.param('screenSize', 'Screen Size')
    @api.param('version', 'Current Version')
    @api.param('update', 'Update Flag')
    @api.marshal_with(firmware_check_model)
    def get(self):
        """Get firmware information or download firmware"""
        # Implementation remains the same as get_esp_firmware()
