from flask import request
from flask_restx import Resource, reqparse
from . import api
from database import redis_client

parser = reqparse.RequestParser()
parser.add_argument('key', type=str, required=False, help='Cached key to delete')
parser.add_argument('filter', type=str, required=True, choices=['one', 'all'])

@api.route('/keys')
class Cache(Resource):
    @api.doc(security='apikey')
    def get(self):
        try:
            cursor = 0
            all_keys = []

            while True:
                cursor, keys = redis_client.scan(cursor=cursor, match='*', count=100)
                all_keys.extend(keys)
                if cursor == 0:
                    break
            if all_keys:
                return {'keys': all_keys}
            else:
                return {'message': 'no cached keys found'}
        except Exception as e:
            return {"error": str(e)}, 500
    
    @api.doc(security='apikey')
    @api.expect(parser)
    def delete(self):
        args = parser.parse_args()
        key = args['key']
        filter_type = args['filter'] 
        try:
            if filter_type == 'all':
                res = redis_client.flushall()
                if res:
                    return {'message': "All cached keys deleted"}
                else:
                    return {'message': "Cached keys not found or could not be deleted"}
            elif filter_type == 'one':
                if key:
                    res = redis_client.delete(key)
                    if res:
                        return {'message': f"Key '{key}' deleted"}
                    else:
                        return {'message': f"Key '{key}' not found or could not be deleted"}
                else:
                    return {'message': 'no input cached key'}
        except Exception as e:
            return {"error": str(e)}, 500
