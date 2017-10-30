FROM armv7/armhf-ubuntu

RUN apt-get update -y && apt-get install -y hostapd isc-dchp-sever && update-rc.d -f isc-dhcp-server remove && update-rc.d -f hostapd remove && echo "DAEMON_CONF=\"/etc/hostapd/hostapd.conf\"" >> /etc/default/hostapd
COPY ./configs/interfaces /etc/network/interfaces
COPY ./configs/dhcpd.conf /etc/dhcp/dhcpd.conf
COPY ./configs/hostapd.conf /etc/hostapd/hostapd.conf
COPY ./ /autowifi
COPY ./requirements /requirements.txt
RUN pip install -r requirements.txt

CMD python /autowifi/manage.py runserver -h 0.0.0.0
