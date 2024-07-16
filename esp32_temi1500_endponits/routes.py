from dotenv import load_dotenv
import os, re
from flask import request, jsonify, send_file
from flask_restx import Resource
from . import api
from .models import esp_data_model, ESPTEMI1500Data, get_esp_firmware_parser, update_firm_ver_model
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
    @api.expect(esp_data_model)
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
    @api.expect(esp_data_model)
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
            u_id = request.args.get('u_id')
            """Check if a device exists and provide device name"""
            result = ESPTEMI1500Data.query.filter_by(u_id=u_id).first()
            if result:
                return {"exist": "Y", "firm_ver": result.firm_ver}, 200

            return {"exist": "N"}, 204
        except Exception as e:
            # Handle exceptions
            return {"error": str(e)}, 500

def get_latest_version(file_prefix, screen_size):
    regex_pattern = re.compile(rf"{re.escape(file_prefix)}_{re.escape(screen_size)}_(\d+\.\d+)\.bin")
    versions = []
    
    for filename in os.listdir(FIRMWARE_DIR):
        match = regex_pattern.match(filename)
        if match:
            versions.append(match.group(1))
    
    if versions:
        return max(versions, key=lambda v: list(map(int, v.split('.'))))
    return None

@api.route('/firmware')
class GetESPFirmware(Resource):
    @api.doc(parser=get_esp_firmware_parser)
    def get(self):
        try:
            args = get_esp_firmware_parser.parse_args()

            checkKEY(args['key'])
            file_prefix = args['filePrefix']
            screen_size = args['screenSize']
            version = args['version']
            update = args['update']

            latest_version = get_latest_version(file_prefix, screen_size)
            if not latest_version:
                return {"error": "No firmware found for the given prefix and screen size"}, 404

            has_new_version = 'Y' if version < latest_version else 'N'

            if update == 'Y' and has_new_version == 'Y':
                firmware_file = f"{file_prefix}_{screen_size}_{latest_version}.bin"
                firmware_path = os.path.join(FIRMWARE_DIR, firmware_file)
                if os.path.exists(firmware_path):
                    # return {"OK": "Test"}, 200
                    return send_file(firmware_path, as_attachment=True) #Do NOT ADD 200 or any code here, it would cause JSON return error
                else:
                    return {"error": "Firmware file not found"}, 404

            return {"hasnewversion": has_new_version}, 200
        
        except Exception as e:
            # Handle exceptions
            return {"error": str(e)}, 500

    #update firmware version info in Database
    @api.doc('update_firm_ver')
    @api.param('key', 'API Key', required=True)
    @api.param('u_id', 'Device Unique ID', required=True)
    @api.expect(update_firm_ver_model)
    def put(self):
        try:
            checkKEY(request.args.get('key'))
            u_id = request.args.get('u_id')
            data = request.json
            firm_ver = data.get('firm_ver')

            # Find the ESP data entry by u_id
            esp_data = ESPTEMI1500Data.query.filter_by(u_id=u_id).first()
            if not esp_data:
                return {"error": "Device not found"}, 404

            # Update the firmware version
            esp_data.firm_ver = firm_ver
            db.session.commit()

            return {'message': 'Firmware version updated successfully'}, 200
        except Exception as e:
            return {"error": str(e)}, 500