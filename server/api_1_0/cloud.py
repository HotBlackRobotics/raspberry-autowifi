from flask import Flask, jsonify, Response, request, abort
from flask_restplus import Resource, Api, fields, reqparse
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

cell_model = rest_api.model('Cell', {
    'ssid': fields.String(required=True, description='Wifi Cell SSID'),
    'encrypted': fields.Boolean(required=True, description='Wifi is Encrypted'),
    'encryption': fields.String(required=True, description='Wifi Encryption Type')
})


scheme_model = rest_api.model('Scheme', {
    'interface': fields.String(required=True, description='Interfaced of network'),
    'name': fields.String(required=True, description='Wifi Scheme Name'),
    'options': fields.Raw(required=True, description='Scheme info')
})

connect_model = rest_api.model('Connection', {
    'ssid': fields.String(required=True, description='Network SSID'),
    'password': fields.String(required=False, description='Network Password'),
})


@rest_api.route('/cells')
class Cells(Resource):
    @rest_api.marshal_list_with(cell_model)
    def get(self):
        cells = Cell.all('wlan0')
        wifi_cells = []
        for c in cells:
            if c.ssid not in [wc['name'] for wc in wifi_cells] + ["\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00"]:
                wifi_cells.append({'ssid': c.ssid, 'encryption': c.encryption_type, 'encrypted': c.encrypted})
        return wifi_cells

@rest_api.route('/schemes')
class Schemes(Resource):
    @rest_api.marshal_list_with(scheme_model)
    def get(self):
        schemes = Scheme.all()
        pattern = re.compile("^scheme-\d*$")
        sc = [s.__dict__ for s in schemes if pattern.match(s.name)]
        sc = sorted(sc, key=lambda s: s['name'])
        return sc

@rest_api.route('/schemes/<name>')
class WifiScheme(Resource):

    def find_scheme(self, name):
        try:
            scheme = next(s for s in Scheme.all() if s.name == name)
        except StopIteration:
            abort(404, "scheme not found")
        return scheme

    @rest_api.marshal_with(scheme_model)
    def get(self, name):
        return self.find_scheme(name).__dict__

    @rest_api.marshal_with(scheme_model)
    def delete(self, name):
        scheme = self.find_scheme(name)
        scheme.delete()
        scheme = Scheme('wlan0', name)
        scheme.save()
        return scheme.__dict__

    @rest_api.expect(connect_model)
    @rest_api.marshal_with(scheme_model)
    def post(self, name):
        scheme = self.find_scheme(name)
        args = rest_api.payload
        try:
            cell = next(cell for cell in Cell.all("wlan0") if cell.ssid == args['ssid'])
        except StopIteration:
            abort(404, "Cell not found")
        scheme.delete()
        if cell.encrypted is True:
            scheme = Scheme.for_cell('wlan0', name, cells[0], args['password'])
        else:
            scheme = Scheme.for_cell('wlan0', name, cells[0])
        scheme.save()
        return scheme.__dict__

    @rest_api.marshal_with(scheme_model)
    def put(self, name):
        scheme = self.find_scheme(name)
        try:
            scheme.activate()
        except ConnectionError:
            abort(404, "Failed to connect to {}.".format(name))
        return jsonify({'scheme': scheme.__dict__, "connected": True})

    @rest_api.marshal_with(scheme_model)
    def delete(self, name):
        s = [s for s in Scheme.all() if s.name == name]
        if len(s) > 0:
            s[0].delete()
            return jsonify({'response': "ok"})
        else:
            return jsonify({'response': "non found"})
