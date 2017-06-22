# auto-wifi
The auto-wifi project provides a set of useful tools to manage the wifi connection for a Raspberry Pi 3, its functioning is illustrated in details below.

Once the Raspberry is switched on, it automatically searches for known wifi networks and connects to them. If no known networks are detected, the Raspberry builds its own wifi network (with SSID name and password specified in the hostapd.conf file) so that you can connect to it through an external device, see all the available wifi networks that can be spotted by the Raspberry and choose the one you are interested in by typing also the password. From that moment on, the Raspberry will maintain the configuration saved and it will automatically connect to it at each boot.

Up to now, the server of the Raspberry must be build up manually through the following command:
```/root/raspberry-autowifi/env/bin/python /root/raspberry-autowifi/manage.py runserver -h 0.0.0.0```

and then the list of all available networks can be found at the following address:
192.168.42.1:5000/wifi/schemes

But we are currently working on that, in order to make the Raspberry building the server autonomously and, through a captive portal, connect to the previous address when the external device connects to the Raspberry wifi network.

## Getting Started

To make things work, the following step must be followed for the correct installation.

- install hostapd and isc-dhcp-server services
	- ```sudo apt-get install hostapd isc-dchp-sever```

- disable the activation of both services during the boot procedure
	- ```sudo update-rc.d -f isc-dhcp-server remove```
	- ```update-rc.d -f hostapd remove```

- specify which is the file containing the hostapd configuration
	- ```echo "DAEMON_CONF=\"/etc/hostapd/hostapd.conf\"" >> /etc/default/hostapd```
	
- download the configuration files of hostapd, isc-dhcp-server and the network interfaces file
	- ```git clone https://github.com/HotBlackRobotics/raspberry-autowifi.git```

- from the downloaded folder, copy the files in the right destination
	- ```cp -f configs/interfaces /etc/network/interfaces```
	- ```cp -f configs/dhcpd.conf /etc/dhcp/dhcpd.conf```
	- ```cp configs/hostapd.conf /etc/hostapd/```

- set the auto-wifi script to be run at the boot time
	- ```crontab -l > mycron```
	- ```echo "@reboot /root/raspberry-autowifi/env/bin/python /root/raspberry-autowifi/scripts/autowifi.py >> /var/log/wifi_auto.log" >> mycron```
	- ```crontab mycron```
	- ```rm mycron```
	- ```update-rc.d cron defaults```
	
## Usage

if no known networks are detected, run the following command from the Raspberry to build up the server:

```/root/raspberry-autowifi/env/bin/python /root/raspberry-autowifi/manage.py runserver -h 0.0.0.0```

then, once you are connected to the Raspberry wifi network, go to this page:

192.168.42.1:5000/wifi/schemes

## Authors

* **HotBlackRobotics** - [HotBlackRobotics](https://github.com/HotBlackRobotics)

## License

This project is licensed under the GNU General Public License - see the [LICENSE.md](LICENSE.md) file for details


