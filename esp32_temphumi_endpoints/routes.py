from flask import request
from flask_restx import Resource
from . import api
from .models import esp_data_model, device_check_model, firmware_check_model, sensor_data_model
from dotenv import load_dotenv
import os

load_dotenv()
VALID_KEY = os.environ['VALID_KEY']
# Directory where .bin files are stored
FIRMWARE_DIR = os.environ['LILYGOS3_FIRMWARE_DIR']
   
@api.route('/esp_data')
class ESPDataList(Resource):
    @api.doc('list_esp_data')
    def get(self):
        """List all ESP data"""
        # Implementation remains the same as get_esp_data()

    @api.doc('create_esp_data')
    @api.expect(esp_data_model)
    def post(self):
        """Create a new ESP data entry"""
        # Implementation remains the same as create_esp_data()

@api.route('/esp_data/<int:id>')
class ESPData(Resource):
    @api.doc('update_esp_data')
    @api.expect(esp_data_model)
    def put(self, id):
        """Update an ESP data entry"""
        # Implementation remains the same as update_esp_data()

    @api.doc('delete_esp_data')
    def delete(self, id):
        """Delete an ESP data entry"""
        # Implementation remains the same as delete_esp_data()

@api.route('/getExtInfo')
class ExtInfo(Resource):
    @api.doc('get_ext_info')
    @api.param('key', 'API Key')
    @api.param('code', 'Device Code')
    @api.marshal_with(sensor_data_model)
    def get(self):
        """Get extended info for a device"""
        # Implementation remains the same as get_esp_data_by_uid()

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
