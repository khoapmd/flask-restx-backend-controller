import os, re
from flask import request, jsonify, send_file, json
from flask_restx import Resource
from . import api
from .models import versionfirmware_parser, uploadfirmware_parser, deletefirmware_parser
from werkzeug.utils import secure_filename

# Directory where .bin files are stored
LILYGOS3_FIRMWARE_DIR = os.getenv('LILYGOS3_FIRMWARE_DIR')
TEMI1500_FIRMWARE_DIR = os.getenv('TEMI1500_FIRMWARE_DIR')

def get_version(file_prefix, screen_size, FIRMWARE_DIR, filter):
    regex_pattern = re.compile(rf"{re.escape(file_prefix)}_{re.escape(screen_size)}_(\d+\.\d+)\.bin")
    versions = []
    
    for filename in os.listdir(FIRMWARE_DIR):
        match = regex_pattern.match(filename)
        if match:
            versions.append(match.group(1))
    
    if versions and filter == 'latest':
        return max(versions, key=lambda v: list(map(int, v.split('.'))))
    elif versions and filter == 'all':
        return versions
    return None

def upload_firmware(file_prefix, screen_size, FIRMWARE_DIR, version, uploaded_file):
    if not os.path.exists(FIRMWARE_DIR):
        os.makedirs(FIRMWARE_DIR)

    if uploaded_file.filename == '':
        return {"error": "No selected file"}, 400
    
    filename = f"{file_prefix}_{screen_size}_{version}.bin"
    uploaded_file.save(os.path.join(FIRMWARE_DIR, secure_filename(filename)))
    
    return {"message": "File uploaded successfully", "filename": filename}

def delete_version(file_prefix, screen_size, FIRMWARE_DIR, version):
    try:
        regex_pattern = re.compile(rf"{re.escape(file_prefix)}_{re.escape(screen_size)}_{re.escape(version)}\.bin")
        for filename in os.listdir(FIRMWARE_DIR):
            if regex_pattern.match(filename):
                os.remove(os.path.join(FIRMWARE_DIR, filename))
                return True
        return False
    except Exception as e:
        print(f"Error deleting version {version}: {e}")
        return False

def delete_all_versions(FIRMWARE_DIR):
    try:
        for filename in os.listdir(FIRMWARE_DIR):
            os.remove(os.path.join(FIRMWARE_DIR, filename))
        return True
    except Exception as e:
        print(f"Error deleting all version : {e}")
        return False
    
@api.route('/version')
class Firmware(Resource):
    @api.doc(parser=versionfirmware_parser)
    @api.doc(security='apikey')
    def get(self):
        try:
            args = versionfirmware_parser.parse_args()
            file_prefix = args['filePrefix']
            screen_size = args['screenSize']
            filter = args['filter']

            if file_prefix == 'tempSensorLily':
                FIRMWARE_DIR = LILYGOS3_FIRMWARE_DIR
            elif  file_prefix == 'temi1500ESP32':
                FIRMWARE_DIR = TEMI1500_FIRMWARE_DIR
            else: return {"error": "No firmware found"}

            version = get_version(file_prefix, screen_size, FIRMWARE_DIR, filter)
            if not version:
                return {"error": "No firmware found for the given prefix and screen size"}, 404

            return {"version": version}, 200
        except Exception as e:
            return {"error": str(e)}, 500
        
@api.route('/files')
class Firmware(Resource):
    @api.doc(parser=uploadfirmware_parser)
    @api.doc(security='apikey')
    def post(self):
        try:
            args = uploadfirmware_parser.parse_args()
            file_prefix = args['filePrefix']
            screen_size = args['screenSize']
            version = args['version']
            uploaded_file = request.files['in_file']

            if file_prefix == 'tempSensorLily':
                FIRMWARE_DIR = LILYGOS3_FIRMWARE_DIR
            elif  file_prefix == 'temi1500ESP32':
                FIRMWARE_DIR = TEMI1500_FIRMWARE_DIR
            else: return {"error": "Wrong firmware prefix"}
            result = upload_firmware(file_prefix, screen_size, FIRMWARE_DIR, version, uploaded_file)
            return result
        except Exception as e:
            return {"error": str(e)}, 500
    
    @api.doc(parser=deletefirmware_parser)
    @api.doc(security='apikey')
    def delete(self):
        try:
            args = deletefirmware_parser.parse_args()
            file_prefix = args.get('filePrefix')
            screen_size = args.get('screenSize')
            version = args.get('version')
            filter = args['filter']

            if file_prefix == 'tempSensorLily':
                FIRMWARE_DIR = LILYGOS3_FIRMWARE_DIR
            elif file_prefix == 'temi1500ESP32':
                FIRMWARE_DIR = TEMI1500_FIRMWARE_DIR
            else:
                return {"error": "Wrong firmware prefix"}, 400

            if filter == "one":
                deleted = delete_version(file_prefix, screen_size, FIRMWARE_DIR, version)
                if deleted:
                    return {"message": f"Version {version} deleted successfully"}, 200
                else:
                    return {"error": f"Version {version} not found or could not be deleted"}, 404
            else:
                deleted = delete_all_versions(FIRMWARE_DIR)
                if deleted:
                    return {"message": f"All versions deleted successfully"}, 200
                else:
                    return {"error": "Failed to delete all versions"}, 500

        except Exception as e:
            return {"error": str(e)}, 500


    