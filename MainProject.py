# Simple application to fetch satellite data and publish the next overhead pass (radio contact) to MQTT
# Created 9/4/2020 by James O'Gorman
# Written in Python 3.7


import requests  # used for HTTP Get requests
from datetime import datetime
from dateutil import tz  # used for converting timezones http://niemeyer.net/python-dateutil
import paho.mqtt.client as mqtt  # https://pypi.org/project/paho-mqtt/


#  Replace the next 7 values with ones appropriate for your needs.

# Also update your MQTT broker ID listed down below.

API_Key = "nnnnnn-vvvvvv-dddddd-wwww"  # Create free account with N2YO.com and get an API key
NoradID = [28654, 41287, 33591, 25338, 90864]  # Norad ID of satellites wanted to be observed
observer_lat = 43.42528  # Float.  Observer's latitude (decimal degrees format)
observer_lng = -88.18343  # Float. Observer's longitude (decimal degrees format)
observer_alt = 500  # Float. Observer's altitude above sea level in meters
days = 10  # Integer. Number of days of prediction (max 10)
min_elevation = 40  # Integer. The minimum elevation acceptable for the highest altitude point of the pass (degrees)


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code "+str(rc))


client = mqtt.Client()
client.on_connect = on_connect

print("Connecting to MQTT Broker... ")
client.connect("192.168.n.n", 1883, 60)

client.loop_start()  # background thread to maintain MQTT connection.

BaseURL = "https://www.n2yo.com/rest/v1/satellite/radiopasses"

# Convert from UTC timestamp to local
from_zone = tz.gettz('UTC')  # The returned values are always UTC
to_zone = tz.tzlocal()  # convert to the local timezone

# subroutine to convert UTC into local time
def convertTime(UTC_TZ):
    print("Time string to convert: " + str(UTC_TZ))
    time_string = datetime.utcfromtimestamp(UTC_TZ)
    print(" UTC Converted: " + str(time_string))
    time_string.replace(tzinfo=from_zone)
    converted_time_string = time_string.astimezone(to_zone)
    print(" more converted: " + str(converted_time_string))

    return str(converted_time_string)


# loop through all the NoradIDs in the list and publish to MQTT
for n in NoradID:
    PARAMS = {
        'apiKey': API_Key
    }
    print("Current index: " + str(n) + " Norad ID: " + str(n))

    MyURL = BaseURL + '/' + str(n) \
               + '/' + str(observer_lat) \
               + '/' + str(observer_lng) \
               + '/' + str(observer_alt) \
               + '/' + str(days) \
               + '/' + str(min_elevation)

    r = requests.get(MyURL, PARAMS)
    print(r.url)  # print out the URL to use (debug)
    data = r.json()  # var to hold the returned data
    print(data)
    if 'passes' not in data:
        client.publish("Sat/" + str(n) + "/NextPass",
                       "Unknown NoradID or farther than " + str(days) +
                       " days in the future.")

    else:
        client.publish("Sat/" + str(n) + "/NextPass", convertTime(data['passes'][0]['startUTC']))

        client.publish("Sat/" + str(n) + "/Name", data['info']['satname'])
        client.publish("Sat/" + str(n) + "/SatID", data['info']['satid'])
        client.publish("Sat/" + str(n) + "/PassesCount", data['info']['passescount'])
        client.publish("Sat/" + str(n) + "/startAZ", data['passes'][0]['startAz'])
        client.publish("Sat/" + str(n) + "/startAZCompass", data['passes'][0]['startAzCompass'])
        client.publish("Sat/" + str(n) + "/MaxAz", data['passes'][0]['maxAz'])
        client.publish("Sat/" + str(n) + "/MaxAZCompass", data['passes'][0]['maxAzCompass'])
        client.publish("Sat/" + str(n) + "/MaxElevation", data['passes'][0]['maxEl'])
        client.publish("Sat/" + str(n) + "/MaxUTC", convertTime(data['passes'][0]['maxUTC']))
        client.publish("Sat/" + str(n) + "/endAz", data['passes'][0]['endAz'])
        client.publish("Sat/" + str(n) + "/endAzCompass", data['passes'][0]['endAzCompass'])
        client.publish("Sat/" + str(n) + "/endUTC", convertTime(data['passes'][0]['endUTC']))

# end of for-loop

client.loop_stop()  # stop the MQTT background thread
