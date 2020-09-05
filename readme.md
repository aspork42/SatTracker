A simple app to publish satellite data to MQTT.
Uses the N2YO.com API to retrieve the next time a satellite will pass overhead.

This auto-detects your timezone to convert automatically since the API always returns the UTC time. MQTT data will be published every time this is run regardless of what may already exist in the broker. The suggestion is to run this as a CRON job ever 10-15 minutes or so since many LEO satellites orbit in about 90 minutes. This publishes the satellite name as returned from the API as well to MQTT.

If no results are returned from the API, then a message is published stating "Unknown NoradID or farther than x days in the future". The API limits the search to certain user-defined criteria; and sometimes no results are returned.

The user of this script will have to get their own API code by making an account at N2YO.com (this is free) and add it to the script.

https://www.n2yo.com/api/#radiopasses

MQTT Data will be published as per the following image.

![MQTT Data](/publishedSatelliteData.png)


Created 9/4/2020 by James O'Gorman

This uses the following libraries / imports that you will require:
  * import requests  # used for HTTP Get requests
  * from datetime import datetime
  * from dateutil import tz  # used for converting timezones
  * import paho.mqtt.client as mqtt

