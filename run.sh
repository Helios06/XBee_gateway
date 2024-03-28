#!/usr/bin/with-contenv bashio

device=$(bashio::config 'XBee_Device')
baud=$(bashio::config 'XBee_Baud')
l0=$(bashio::config 'XBee_DIO0_Level')
l1=$(bashio::config 'XBee_DIO1_Level')
l2=$(bashio::config 'XBee_DIO2_Level')
l3=$(bashio::config 'XBee_DIO3_Level')

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
  --l0 $l0 --l1 $l1 --l2 $l2 --l3 $l3 \
  --host $host --port $port -u $user -s $password --send $send --recv $recv \
  --log $logging
