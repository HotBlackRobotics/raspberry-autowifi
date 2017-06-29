from flask import Flask, jsonify, Response, request
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS, cross_origin
from flask_json import JsonError, json_response, as_json
from datetime import datetime
import subprocess
from wifi import Cell, Scheme
from wifi.exceptions import ConnectionError
import re
from . import api

rest_api = Api(api)


class WifiCells(Resource):
    def get(self):
        cells = Cell.all('wlan0')
        wifi_info = []
        for c in cells:
            if c.ssid not in [wc['name'] for wc in wifi_info] + ["\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00"]:
                wifi_info.append({'name': c.ssid, 'encryption': c.encryption_type, 'encrypted': c.encrypted})
        return jsonify({'cells': wifi_info})

class WifiSchemes(Resource):
    def get(self):
        schemes = Scheme.all()
        pattern = re.compile("^scheme-\d*$")
        sc = [s.__dict__ for s in schemes if pattern.match(s)]
        return jsonify({'schemes': sorted(sc, key=lambda k: k[7:-1])})

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
            scheme = Scheme.for_cell('wlan0', sname, cells[0], args['password'])
            scheme.save()
            return jsonify({'scheme': scheme.__dict__})
        elif args["action"] == "clean":
            sname = scheme.name
            for s in Scheme.all():
                s.delete()
                if s.name == sname:
                    s = Scheme('wlan0', sname)
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

rest_api.add_resource(WifiCells, '/wifi/cells')
rest_api.add_resource(WifiSchemes, '/wifi/schemes')
rest_api.add_resource(WifiScheme, '/wifi/schemes/<name>')
