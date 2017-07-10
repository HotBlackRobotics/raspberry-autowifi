#! env/bin/python

from wifi import Scheme, Cell
from wifi.exceptions import ConnectionError
import sys

def autoconnect_command(interface):
    ssids = [cell.ssid for cell in Cell.all(interface)]
    connected = False
    for scheme in [Scheme.find('wlan0', s) for s in ['scheme-'+str(x) for x in range(1,6)]]:

        ssid = scheme.options.get('wpa-ssid', scheme.options.get('wireless-essid'))
        if ssid in ssids:
            sys.stderr.write('Connecting to "%s".\n' % ssid)
            try:
                scheme.activate()
                connected = True
            except ConnectionError:
                print "Failed to connect to %s." % scheme.name
                continue
            connected = True
            break

    if not connected:
	try:
            s = Scheme.find('wlan0', 'hotspot')
            s.activate()
        except ConnectionError:
            print "hotspot is created."
        

if __name__=='__main__':
    autoconnect_command('wlan0')
