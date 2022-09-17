# purpleair

A library for working with the Purple Air APIs. See https://api.purpleair.com for API info.

# License

This is provided via the MIT License.

# APIs

Currently the following APIs are implemented:

- Check an API Key
  - `check_key()`
- Check Sensor Data
  - `get_sensor_data()`
- Check Sensors Data
  - `get_sensors_data()`

Currently the following APIs are in alpha and not tested:
- Check Sensor History
  - `get_sensor_history()`

See the docstrings and API docs for information on these functions.

# How to Get Sensor Id
Go to the https://purpleair.com map. Find your sensor and click it. Look at the url. Here is an example:

```
https://map.purpleair.com/1/mHUMIDITY/a10/p604800/cC0?select=63217#11.24/38.5924/-121.2715

This is the sensor id:                                       ^^^^^
 = 63217
```

# How to Get API Keys
Send an email to contact@purpleair.com requesting API keys.

# Examples

## Getting Single Sensor Data
```
In [1]: from purpleair import PurpleAir

In [2]: p = PurpleAir('READ_KEY_HERE')

# See help(p.get_sensor_data) for param names, and see https://api.purpleair.com for API info.

In [3]: p.get_sensor_data('99999')
Out[3]:
{'api_version': 'V1.0.10-0.0.17',
 'time_stamp': 1657577251,
 'data_time_stamp': 1657577238,
 'sensor': {'sensor_index': 99999,
  'last_modified': 1628736055,
  'date_created': 1624389476,
  'last_seen': 1657577216,
  'private': 0,
  'is_owner': 0,
  'name': '99999',
  'icon': 0,
  'location_type': 0,
  'model': 'PA-II',
  'hardware': '2.0+BME280+PMSX003-B+PMSX003-A',
  'led_brightness': 35,
  'firmware_version': '7.00',
  'rssi': -63,
  'uptime': 2571,
  'pa_latency': 251,
  'memory': 15272,
  'position_rating': 5,
  'latitude': 99999,
  'longitude': 99999,
  'altitude': 99999,
  'channel_state': 3,
  'channel_flags': 0,
  'channel_flags_manual': 0,
  'channel_flags_auto': 0,
  'confidence': 100,
  'confidence_auto': 100,
  'confidence_manual': 100,
  'humidity': 13,
  'humidity_a': 13,
  'temperature': 103,
  'temperature_a': 103,
  'pressure': 1000.2,
  'pressure_a': 1000.16,
  'analog_input': 0.01,
  'pm1.0': 6.1,
  'pm1.0_a': 6.1,
  'pm1.0_b': 6.1,
  'pm1.0_atm': 6.1,
  'pm1.0_cf_1': 6.1,
  'pm2.5': 9.5,
  'pm2.5_a': 9.2,
  'pm2.5_b': 9.8,
  'pm2.5_atm': 9.5,
  'pm2.5_cf_1': 9.5,
  'pm2.5_alt': 7.0,
  'pm2.5_alt_a': 7.4,
  'pm2.5_alt_b': 6.6,
  'pm10.0': 9.9,
  'pm10.0_a': 9.7,
  'pm10.0_b': 10.2,
  'pm10.0_atm': 9.9,
  'pm10.0_cf_1': 9.9,
  'scattering_coefficient': 21.3,
  'scattering_coefficient_a': 22.6,
  'scattering_coefficient_b': 20.0,
  'deciviews': 12.7,
  'deciviews_a': 13.1,
  'deciviews_b': 12.2,
  'visual_range': 109.8,
  'visual_range_a': 105.0,
  'visual_range_b': 114.6,
  '0.3_um_count': 1421,
  '0.3_um_count_a': 1508,
  '0.3_um_count_b': 1335,
  '0.5_um_count': 388,
  '0.5_um_count_a': 416,
  '0.5_um_count_b': 361,
  '1.0_um_count': 72,
  '1.0_um_count_a': 74,
  '1.0_um_count_b': 70,
  '2.5_um_count': 2,
  '2.5_um_count_a': 1,
  '2.5_um_count_b': 4,
  '5.0_um_count': 0,
  '5.0_um_count_a': 0,
  '5.0_um_count_b': 0,
  '10.0_um_count': 0,
  '10.0_um_count_a': 0,
  '10.0_um_count_b': 0,
  'pm1.0_atm_a': 6.08,
  'pm2.5_atm_a': 9.19,
  'pm10.0_atm_a': 9.71,
  'pm1.0_cf_1_a': 6.08,
  'pm2.5_cf_1_a': 9.19,
  'pm10.0_cf_1_a': 9.71,
  'pm1.0_atm_b': 6.11,
  'pm2.5_atm_b': 9.82,
  'pm10.0_atm_b': 10.18,
  'pm1.0_cf_1_b': 6.11,
  'pm2.5_cf_1_b': 9.82,
  'pm10.0_cf_1_b': 10.18,
  'primary_id_a': 1423249,
  'primary_key_a': '1BEFQX60DUFTLDA8',
  'primary_id_b': 1423251,
  'primary_key_b': '1Q1AIWD7K2I3ACJM',
  'secondary_id_a': 1423250,
  'secondary_key_a': 'P39SSA1REDNK6EW3',
  'secondary_id_b': 1423252,
  'secondary_key_b': 'SGQY235BUUIQ2SW4',
  'stats': {'pm2.5': 9.5,
   'pm2.5_10minute': 8.0,
   'pm2.5_30minute': 6.6,
   'pm2.5_60minute': 6.6,
   'pm2.5_6hour': 6.1,
   'pm2.5_24hour': 3.8,
   'pm2.5_1week': 3.1,
   'time_stamp': 1657577216},
  'stats_a': {'pm2.5': 9.2,
   'pm2.5_10minute': 8.1,
   'pm2.5_30minute': 6.7,
   'pm2.5_60minute': 6.7,
   'pm2.5_6hour': 6.2,
   'pm2.5_24hour': 3.9,
   'pm2.5_1week': 3.2,
   'time_stamp': 1657577216},
  'stats_b': {'pm2.5': 9.8,
   'pm2.5_10minute': 8.0,
   'pm2.5_30minute': 6.5,
   'pm2.5_60minute': 6.4,
   'pm2.5_6hour': 5.9,
   'pm2.5_24hour': 3.8,
   'pm2.5_1week': 3.0,
   'time_stamp': 1657577216}}}
```

## Getting Multiple Sensors Data via location_id and modified_since

See https://api.purpleair.com for what the parameters mean and how they're used.

```
In [1]: from purpleair import PurpleAir

In [2]: p = PurpleAir('READ_KEY_HERE')

# See help(p.get_sensors_data) for param names, and see https://api.purpleair.com for API info.

# Pull temperature/humidity from all sensors that are outside and have been modified today
# location_type=0 per api docs means outdoor sensors
# Use modified_since with a datetime corresponding with the first moment of today

In [3]: p.get_sensors_data(fields=('temperature', 'humidity', ), location_type=0, modified_since=datetime(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day))
Out[3]:
{'api_version': 'V1.0.11-0.0.40',
 'time_stamp': 1663454033,
 'data_time_stamp': 1663454012,
 'location_type': 0,
 'modified_since': 1663428833,
 'max_age': 604800,
 'firmware_default_version': '7.00',
 'fields': ['sensor_index', 'humidity', 'temperature'],
 'data': [[131075, 35, 90],
  [131079, 53, 71],
  [131077, 35, 78],
  [131083, 36, 77],
  [131087, 23, 76],
  [131085, 12, 85],
  [131091, 16, 101],
  ...
