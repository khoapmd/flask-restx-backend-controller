from dotenv import load_dotenv
import os
from flask import request
from flask_restx import Resource
from . import api
from .models import lilygos3_data_model, device_check_model, firmware_check_model, ESPTEMI1500Data
from auth import checkKEY
from database import db

load_dotenv()
# Directory where .bin files are stored
FIRMWARE_DIR = os.environ['TEMI1500_FIRMWARE_DIR']

@api.route('/esp_data/all')
class DeviceList(Resource):
    @api.doc('list_esp_data')
    @api.param('key', 'API Key')
    def get(self):
        try:
            checkKEY(request.args.get('key'))
            esp_data = ESPTEMI1500Data.query.all()
            return [data.to_dict() for data in esp_data], 200
        except Exception as e:
            # Handle exceptions
            return {"error": str(e)}, 500
    
@api.route('/esp_data')
class DeviceData(Resource):
    @api.doc('create_esp_data')
    @api.param('key', 'API Key')
    @api.expect(lilygos3_data_model)
    def post(self):
        try:
            checkKEY(request.args.get('key'))
            """Create a new ESP data entry"""
            # Extract data from request body
            data = request.json
            u_id = data.get('u_id')
            device_type = data.get('device_type')
            firm_ver = data.get('firm_ver')

            # Create a new ESPTEMI1500Data entry
            new_esp_data = ESPTEMI1500Data(
                org='org',
                dept='dept',
                room='room',
                line='line',
                display_name='display_name',
                u_id=u_id,
                device_type=device_type,
                firm_ver=firm_ver
            )

            # Save to database
            db.session.add(new_esp_data)
            db.session.commit()

            return {'message': 'ESP data created successfully'}, 201
        except Exception as e:
            # Handle exceptions
            return {"error": str(e)}, 500

    @api.doc('update_esp_data')
    @api.expect(lilygos3_data_model)
    def put(self, id):
        checkKEY(request.args.get('key'))
        """Update an ESP data entry"""
        # Implementation remains the same as update_esp_data()

    @api.doc('delete_esp_data')
    def delete(self, id):
        checkKEY(request.args.get('key'))
        """Delete an ESP data entry"""
        # Implementation remains the same as delete_esp_data()

@api.route('/checkexist')
class DeviceCheck(Resource):
    @api.doc('check_device_exist')
    @api.param('key', 'API Key')
    @api.param('u_id', 'Device UID')
    def get(self):
        try:
            checkKEY(request.args.get('key'))
            u_id = request.args.get('code')
            """Check if a device exists and provide device name"""
            result = ESPTEMI1500Data.query.filter_by(u_id=u_id).first()
            if result:
                return {"exist": "Y"}, 200

            return {"exist": "N"}, 204
        except Exception as e:
            # Handle exceptions
            return {"error": str(e)}, 500

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
        checkKEY(request.args.get('key'))
        """Get firmware information or download firmware"""
        # Implementation remains the same as get_esp_firmware()
