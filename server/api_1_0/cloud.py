from flask import Flask, jsonify, Response, request
from flask_restplus import Resource, Api, fields
from flask_cors import CORS, cross_origin
from flask_json import JsonError, json_response, as_json
from datetime import datetime
import subprocess
from wifi import Cell, Scheme
from wifi.exceptions import ConnectionError
import re
from . import api

rest_api = Api(api, version='1.0', title='WiFi RPi3 API',
    description='Simple WiFi API to manage RPi3 Connection',
)

wifi_cells_model = rest_api.model('Cells', {
    'ssid': fields.String(required=True, description='Wifi Cell SSID'),
    'encrypted': fields.String(required=True, description='Wifi is Encrypted'),
    'encryption': fields.String(required=True, description='Wifi Encryption Type')
})

@rest_api.route('/cells')
class Cells(Resource):
    @rest_api.marshal_list_with(wifi_cells_model)
    def get(self):
        cells = Cell.all('wlan0')
        wifi_cells = []
        for c in cells:
            if c.ssid not in [wc['name'] for wc in wifi_cells] + ["\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00"]:
                wifi_cells.append({'name': c.ssid, 'encryption': c.encryption_type, 'encrypted': c.encrypted})
        return wifi_cells

@rest_api.route('/schemes')
class WifiSchemes(Resource):
    def get(self):
        schemes = Scheme.all()
        pattern = re.compile("^scheme-\d*$")
        sc = [s.__dict__ for s in schemes if pattern.match(s.name)]
        sc = sorted(sc, key=lambda s: s['name'])
        return jsonify({'schemes': sc})

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        parser.add_argument('password')
        args = parser.parse_args()

        schemes = [s for s in Scheme.all()]
        cells = Cell.all('wlan0')

        newscheme = None
        for cell in cells:
            if cell.ssid == args['name']:
                if cell.encrypted is True:
                    newscheme = Scheme.for_cell('wlan0', 'scheme-'+str(len(schemes)), cell, args['password'])
                else:
                    newscheme = Scheme.for_cell('wlan0', 'scheme-'+str(len(schemes)), cell)
                break
        if newscheme is None:
            return jsonify({'response': "network non found"})
        else:
            newscheme.save()
            newscheme.activate()
            return jsonify({'response': "ok"})

@rest_api.route('/schemes/<name>')
class WifiScheme(Resource):
    def get(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument('action')
        args = parser.parse_args()
        s = [s for s in Scheme.all() if s.name == name]
        if len(s) == 0:
            return jsonify({'response': "non found"})
        scheme = s[0]
        return jsonify({'scheme': scheme.__dict__})

    def put(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument('action')
        parser.add_argument('ssid')
        parser.add_argument('password')
        args = parser.parse_args()
        s = [s for s in Scheme.all() if s.name == name]
        if len(s) == 0:
            return jsonify({'response': "non found"})
        scheme = s[0]
        if args["action"] == 'connect':
            try:
                scheme.activate()
            except ConnectionError:
                return  jsonify({"error": "Failed to connect to %s." % scheme.name})
            return jsonify({'scheme': scheme.__dict__, "connected": True})
        elif args["action"] == "configure":
            cells = [cell for cell in Cell.all("wlan0") if cell.ssid == args['ssid']]
            if len(cells) == 0:
                return jsonify({'error': 'wifi not found'})
            sname = scheme.name
            scheme.delete()
            if cell.encrypted is True:
                scheme = Scheme.for_cell('wlan0', sname, cells[0], args['password'])
            else:
                scheme = Scheme.for_cell('wlan0', sname, cells[0])
            scheme.save()
            return jsonify({'scheme': scheme.__dict__})

        elif args["action"] == "clean":
            sname = scheme.name
            for s in Scheme.all():
                if s.name == sname:
                    s = Scheme('wlan0', sname)
                    scheme.delete()
                    s.save()
        else:
            return jsonify({'scheme': scheme.__dict__})

    def delete(self, name):
        s = [s for s in Scheme.all() if s.name == name]
        if len(s) > 0:
            s[0].delete()
            return jsonify({'response': "ok"})
        else:
            return jsonify({'response': "non found"})
