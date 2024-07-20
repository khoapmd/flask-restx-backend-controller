import os, re
from flask import request, jsonify, send_file, json
from flask_restx import Resource
from . import api
from .models import esp_data_model, sensor_data_model, LILYGOS3DATA, SENSORTEMPHUMIDATA, get_esp_firmware_parser, update_firm_ver_model
from database import db, redis_client
from sqlalchemy import func

# Directory where .bin files are stored
FIRMWARE_DIR = os.getenv('LILYGOS3_FIRMWARE_DIR')

@api.route('/data/all')
class DeviceList(Resource):
    @api.doc('list_lilygo_data')
    @api.doc(security='apikey')
    def get(self):
        try:         
            # Check cache first
            cache_key = 'lilygo_data_all'
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)  # Convert string back to list of dicts

            # Query the database
            esp_data = LILYGOS3DATA.query.all()
            data = [data.to_dict() for data in esp_data]
            
            # Cache the result
            redis_client.set(cache_key, json.dumps(data), ex=3600)  # Cache for 1 hour

            return data, 200
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
            sensor_id = data.get("sensor_id")
            firm_ver = data.get('firm_ver')

            new_esp_data = LILYGOS3DATA(
                org='org',
                dept='dept',
                room='room',
                line='line',
                display_name='display_name',
                u_id=u_id,
                device_type=device_type,
                firm_ver=firm_ver
            )
            new_sensor_data = SENSORTEMPHUMIDATA(
                u_id=u_id,
                h_slope=1.0126,
                t_slope=1.0056,
                h_intercept=-3.1109,
                t_intercept=-0.2008,
                temp_limit='20-30',
                humi_limit='60-90',
                sensor_id=sensor_id
            )

            db.session.add(new_esp_data)
            db.session.add(new_sensor_data)
            db.session.commit()

            # Invalidate the cache
            redis_client.delete('lilygo_data_all')

            return {'message': 'ESP data created successfully'}, 201
        except Exception as e:
            return {"error": str(e)}, 500

    @api.doc('get_device_data')
    @api.doc(security='apikey')
    @api.param('u_id', 'Device Unique Identify')
    def get(self):
        try:   
            u_id = request.args.get('u_id')
            cache_key = f'lilygo_data_{u_id}'
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data) # Convert string back to dict

            lilygo = LILYGOS3DATA.query.filter_by(u_id=u_id).first()
            sensor = SENSORTEMPHUMIDATA.query.filter_by(u_id=u_id).first()
            if lilygo and sensor:
                combined_data = {**lilygo.to_dict(), **sensor.to_dict()}
                
                # Cache the result
                redis_client.set(cache_key, json.dumps(combined_data), ex=3600)  # Cache for 1 hour

                return combined_data, 200
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
    @api.param('device_type', 'Device Type')
    def get(self):
        try:         
            u_id = request.args.get('u_id')
            device_type = request.args.get('device_type')
            # Try to get the data from Redis
            cache_key = f'lilygo_exist_{u_id}'
            result = redis_client.get(cache_key)
            if result:
                return json.loads(result)
            lily = LILYGOS3DATA.query.filter_by(u_id=u_id).first()
            if lily:
                sensor = SENSORTEMPHUMIDATA.query.filter_by(u_id=u_id).first()
                return {"exist": "Y", "sensor_id": sensor.sensor_id, "firm_ver": lily.firm_ver}, 200
            
            max_id = db.session.query(func.max(SENSORTEMPHUMIDATA.id)).scalar()
            next_id = max_id + 1 if max_id is not None else 1
            result = f"{device_type}{str(next_id).zfill(4)}"
            if result:
                response = {"exist": "Y", "firm_ver": result.firm_ver}
                redis_client.set(cache_key, json.dumps(response), ex=300)  # Cache for 5 minutes
                return response, 200
            return {"exist": "N"}, 204
        except Exception as e:
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
    @api.doc(security='apikey')
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
                firmware_path = os.path.join(FIRMWARE_DIR, firmware_file)
                if os.path.exists(firmware_path):
                    return send_file(firmware_path, as_attachment=True)
                else:
                    return {"error": "Firmware file not found"}, 404

            return {"hasnewversion": has_new_version}, 200
        except Exception as e:
            return {"error": str(e)}, 500

    @api.doc('update_firm_ver')
    @api.param('key', 'API Key', required=True)
    @api.param('u_id', 'Device Unique ID', required=True)
    @api.expect(update_firm_ver_model)
    def put(self):
        try:
            u_id = request.args.get('u_id')
            data = request.json
            firm_ver = data.get('firm_ver')

            esp_data = LILYGOS3DATA.query.filter_by(u_id=u_id).first()
            if not esp_data:
                return {"error": "Device not found"}, 404

            esp_data.firm_ver = firm_ver
            db.session.commit()

            cache_all_key = f'lilygo_data_all'
            cache_data_key = f'lilygo_data_{u_id}'
            cache_exist_key = f'lilygo_exist_{u_id}'
            redis_client.delete(cache_all_key)
            redis_client.delete(cache_data_key)
            redis_client.delete(cache_exist_key)

            return {'message': 'Firmware version updated successfully'}, 200
        except Exception as e:
            return {"error": str(e)}, 500