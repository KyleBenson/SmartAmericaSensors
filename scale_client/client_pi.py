#!/usr/bin/python

import threading
import time
import urllib2
import socket
from threading import Thread
from Queue import Queue
from device_descriptor import DeviceDescriptor
from event_reporter import EventReporter
from publisher import Publisher
from mqtt_publisher import MQTTPublisher
from virtual_sensor import VirtualSensor
from gpio_virtual_sensor import GPIOVirtualSensor
from analog_virtual_sensor import AnalogVirtualSensor
from heartbeat_virtual_sensor import HeartbeatVirtualSensor as HBVirtualSensor
from pir_virtual_sensor import PIRVirtualSensor 
from light_virtual_sensor import LightVirtualSensor
from gas_virtual_sensor import GasVirtualSensor

QUEUE_SIZE = 4096
MQTT_HOSTNAME = "m10.cloudmqtt.com"
MQTT_HOSTPORT = 11094
MQTT_USERNAME = "vbjsfwul"
MQTT_PASSWORD = "xottyHH5j9v2"
CEL_DAEMON_PATH = "temprature-streams"

# Check Network Accessibility
"""
hasNetwork = False
while(hasNetwork != True):
	try:
		response = urllib2.urlopen('http://www.google.com', timeout = 2)
		hasNetwork = True 
	except urllib2.URLError:
		time.sleep(5)
		continue 
"""

# Create message queue
queue = Queue(QUEUE_SIZE)

# Create and start event reporter
reporter = EventReporter(queue)
reporter.daemon = True
reporter.start()

# Create publishers
#file_hostname = open("/etc/hostname", "r")
#str_hostname = file_hostname.readline().rstrip()
#file_hostname.close()
pb_mqtt = MQTTPublisher(
	topic_prefix = "scale/test/" + socket.gethostname()
)
if pb_mqtt.connect(MQTT_HOSTNAME, MQTT_HOSTPORT, MQTT_USERNAME, MQTT_PASSWORD):
	reporter.append_publisher(pb_mqtt)

# Create and start virtual sensors
# Create Heartbeat "Sensor"
ls_vs = []
vs_heartbeat = HBVirtualSensor(
	queue,
	DeviceDescriptor("hb0"),
	interval = 10
)
if vs_heartbeat.connect():
	ls_vs.append(vs_heartbeat)

#Create PIR Motion Virtual Sensor
vs_pir = PIRVirtualSensor(
	queue,
	DeviceDescriptor("pir0"),
	gpio_pin = 17
)
if vs_pir.connect():
	ls_vs.append(vs_pir)

#Create Light Virtual Sensor
vs_light = LightVirtualSensor(
	queue,
	DeviceDescriptor("light0"),
	analog_port = 3,
	threshold = 400
)
if vs_light.connect():
	ls_vs.append(vs_light)

#Create Gas Virtual Sensor
vs_gas = GasVirtualSensor(
	queue,
	DeviceDescriptor("gas0"),
	analog_port = 0,
	threshold = 500
)
if vs_gas.connect():
	ls_vs.append(vs_gas)

# Start all the sensors
for vs_j in ls_vs:
	vs_j.daemon = True
	vs_j.start()

# Loop forever
while True:
	time.sleep(1)
