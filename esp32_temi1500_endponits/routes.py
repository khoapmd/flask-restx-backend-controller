import os, re
from flask import request, send_file, json
from flask_restx import Resource
from . import api
from .models import esp_data_model, ESPTEMI1500Data, get_esp_firmware_parser, update_firm_ver_model
from database import db, redis_client
from config import TEMI1500_FIRMWARE_DIR, REDIS_EX

@api.route('/data/all')
class DeviceList(Resource):
    @api.doc(security='apikey')
    @api.doc('list_esp_data')
    def get(self):
        try:
            # Try to get the data from Redis
            esp_data = redis_client.get('temi1500_data_all')
            
            if esp_data:
                return json.loads(esp_data)

            # If not found in Redis, get it from PostgreSQL
            esp_data = ESPTEMI1500Data.query.all()
            esp_data_list = [data.to_dict() for data in esp_data]
            
            # Store the data in Redis
            redis_client.set('temi1500_data_all', json.dumps(esp_data_list), ex=REDIS_EX)

            return esp_data_list, 200
        except Exception as e:
            return {"error": str(e)}, 500

@api.route('/data')
class DeviceData(Resource):
    @api.doc('create_esp_data')
    @api.doc(security='apikey')
    @api.expect(esp_data_model)
    def post(self):
        try:
            data = request.json
            u_id = data.get('u_id')
            device_type = data.get('device_type')
            firm_ver = data.get('firm_ver')

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

            db.session.add(new_esp_data)
            db.session.commit()

            # Invalidate the Redis cache
            redis_client.delete('temi1500_data_all')

            return {'message': 'ESP data created successfully'}, 201
        except Exception as e:
            return {"error": str(e)}, 500
        
    @api.doc('get_device_data')
    @api.doc(security='apikey')
    @api.param('u_id', 'Device Unique Identify')
    def get(self):
        try:
            u_id = request.args.get('u_id')
            cache_key = f'temi1500_data_{u_id}'
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data) # Convert string back to dict

            temi1500 = ESPTEMI1500Data.query.filter_by(u_id=u_id).first()
            if temi1500:
                # Cache the result
                redis_client.set(cache_key, json.dumps(temi1500.to_dict()), ex=REDIS_EX)

                return temi1500.to_dict(), 200
            else:
                return {'message': 'No data found for the given u_id'}, 404
        except Exception as e:
            return {"error": str(e)}, 500

    @api.doc('update_esp_data')
    @api.doc(security='apikey')
    @api.expect(esp_data_model)
    def put(self, id):
        return {'message': 'nothing'}, 403
        # Implementation remains the same as update_esp_data()

    @api.doc('delete_esp_data')
    @api.doc(security='apikey')
    def delete(self, id):
        return {'message': 'nothing'}, 403
        # Implementation remains the same as delete_esp_data()

@api.route('/checkexist')
class DeviceCheck(Resource):
    @api.doc('check_device_exist')
    @api.doc(security='apikey')
    @api.param('u_id', 'Device UID')
    def get(self):
        try:
            u_id = request.args.get('u_id')

            # Try to get the data from Redis
            cache_key = f'temi1500_exist_{u_id}'
            result = redis_client.get(cache_key)
            if result:
                return json.loads(result)

            result = ESPTEMI1500Data.query.filter_by(u_id=u_id).first()
            if result:
                response = {"exist": "Y", "firm_ver": result.firm_ver}
                redis_client.set(cache_key, json.dumps(response), ex=REDIS_EX)
                return response, 200

            return {"exist": "N"}, 204
        except Exception as e:
            return {"error": str(e)}, 500

def get_latest_version(file_prefix, screen_size):
    regex_pattern = re.compile(rf"{re.escape(file_prefix)}_{re.escape(screen_size)}_(\d+\.\d+)\.bin")
    versions = []
    
    for filename in os.listdir(TEMI1500_FIRMWARE_DIR):
        match = regex_pattern.match(filename)
        if match:
            versions.append(match.group(1))
    
    if versions:
        return max(versions, key=lambda v: list(map(int, v.split('.'))))
    return None

@api.route('/firmware')
class GetESPFirmware(Resource):
    @api.doc(security='apikey')
    @api.doc(parser=get_esp_firmware_parser)
    def get(self):
        try:
            args = get_esp_firmware_parser.parse_args()

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
                firmware_path = os.path.join(TEMI1500_FIRMWARE_DIR, firmware_file)
                if os.path.exists(firmware_path):
                    return send_file(firmware_path, as_attachment=True)
                else:
                    return {"error": "Firmware file not found"}, 404

            return {"hasnewversion": has_new_version}, 200
        except Exception as e:
            return {"error": str(e)}, 500

    @api.doc('update_firm_ver')
    @api.doc(security='apikey')
    @api.param('u_id', 'Device Unique ID', required=True)
    @api.expect(update_firm_ver_model)
    def put(self):
        try:
            u_id = request.args.get('u_id')
            data = request.json
            firm_ver = data.get('firm_ver')

            esp_data = ESPTEMI1500Data.query.filter_by(u_id=u_id).first()
            if not esp_data:
                return {"error": "Device not found"}, 404

            esp_data.firm_ver = firm_ver
            db.session.commit()

            cache_all_key = 'temi1500_data_all'
            cache_data_key = f'temi1500_data_{u_id}'
            cache_exist_key = f'temi1500_exist_{u_id}'
            redis_client.delete(cache_all_key)
            redis_client.delete(cache_data_key)
            redis_client.delete(cache_exist_key)

            return {'message': 'Firmware version updated successfully'}, 200
        except Exception as e:
            return {"error": str(e)}, 500