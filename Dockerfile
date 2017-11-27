FROM armv7/armhf-ubuntu:16.04

RUN apt-get update
RUN apt-get install python-pip hostapd isc-dhcp-server -y

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
COPY ./scripts/autowifi.py /autowifi.py

COPY ./configs/interfaces /etc/network/interfaces
RUN echo "DAEMON_CONF=\"/etc/hostapd/hostapd.conf\"" >> /etc/default/hostapd
COPY ./configs/dhcpd.conf /etc/dhcp/dhcpd.conf
COPY ./configs/hostapd.conf /etc/hostapd/hostapd.conf

RUN apt install net-tools wireless-tools iw -y

CMD python /autowifi.py
