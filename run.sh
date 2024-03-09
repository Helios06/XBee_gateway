#!/usr/bin/with-contenv bashio

device=$(bashio::config 'XBee_Device')
baud=$(bashio::config 'XBee_Baud')
d2s=$(bashio::config 'XBee_D2_State')
d2l=$(bashio::config 'XBee_D2_Level')

host=$(bashio::config 'MQTT_Host')
port=$(bashio::config 'MQTT_Port')
user=$(bashio::config 'MQTT_User')
password=$(bashio::config 'MQTT_Password')
send=$(bashio::config 'MQTT_Send')
recv=$(bashio::config 'MQTT_Receive')

logging=$(bashio::config 'ADDON_Logging')

echo "run.sh: launching sms_manager.py"
python3 /xbee_manager.py  \
  -d $device -b $baud \
  --d2s $d2s --d2l $d2l \
  --host $host --port $port -u $user -s $password --send $send --recv $recv \
  --log $logging
