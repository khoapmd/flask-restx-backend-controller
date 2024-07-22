from flask_restx import reqparse
import werkzeug

# Define the request parser
versionfirmware_parser = reqparse.RequestParser()
versionfirmware_parser.add_argument('filePrefix', type=str, required=True, choices=['tempSensorLily', 'temi1500ESP32'], help='The file prefix')
versionfirmware_parser.add_argument('screenSize', type=str, required=True, help='The screen size')
versionfirmware_parser.add_argument('filter', type=str, required=True, choices=['latest', 'all'])

uploadfirmware_parser = reqparse.RequestParser()
uploadfirmware_parser.add_argument('filePrefix', type=str, required=True, choices=['tempSensorLily', 'temi1500ESP32'], help='The file prefix')
uploadfirmware_parser.add_argument('screenSize', type=str, required=True, help='The screen size')
uploadfirmware_parser.add_argument('version', type=str, required=True, help='The current firmware version')
uploadfirmware_parser.add_argument('in_file', type=werkzeug.datastructures.FileStorage, location='files', required=True, help='The firmware file to upload')

deletefirmware_parser = reqparse.RequestParser()
deletefirmware_parser.add_argument('filePrefix', type=str, required=True, choices=['tempSensorLily', 'temi1500ESP32'], help='The file prefix')
deletefirmware_parser.add_argument('screenSize', type=str, required=True, help='The screen size')
deletefirmware_parser.add_argument('version', type=str, required=False, help='The firmware version to delete')
deletefirmware_parser.add_argument('filter', type=str, required=True, choices=['one', 'all'])

