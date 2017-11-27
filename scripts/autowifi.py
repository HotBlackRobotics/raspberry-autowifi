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

def get_cpu_id():
    cpuserial = "0000000000000000"
    try:
      f = open('/proc/cpuinfo','r')
      for line in f:
        if line[0:6]=='Serial':
          cpuserial = line[10:26]
      f.close()
    except:
      cpuserial = "ERROR000000000"
    return cpuserial


if __name__=='__main__':
    import time
    import os
    net_name = os.environ.get('SSID_NAME') or 'hbr.demo'
    with open('/etc/hostapd/hostapd.conf', 'w') as hostapd_file:
        hostapd_file.write("interface=wlan0\n")
        hostapd_file.write("hw_mode=g\n")
        hostapd_file.write("channel=6\n")
        hostapd_file.write("ssid=%s.%s\n"%(net_name, get_cpu_id()[7:]))
    autoconnect_command('wlan0')
    while True:
        time.sleep(10)
