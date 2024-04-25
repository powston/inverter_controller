"""The inverter_controller integration."""
from __future__ import annotations
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from powston.inverter import InverterSensor
from paho.mqtt import client as mqtt_client
import random
import json
import logging
logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
client_external = mqtt_client.Client("HA-MQTT-" + str(random.random()).split(".")[1])

from .const import DOMAIN

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.LIGHT]

def on_connect(client, user_data, flags, rc):
    if rc == 0:
        entry = user_data.data["entry"]
        mqtt_username = entry.data["username"]
        client.subscribe(f"{mqtt_username}/homeassistant/#")
        logger.info("Connected to MQTT Broker mon-mqtt")
    else:
        logger.info("Failed to connect, return code %d\n", rc)

def on_message(client, user_data, msg):
    topic = msg.topic
    hass = user_data.data["hass"]
    entry = user_data.data["entry"]
    packet = msg.payload.decode()
    logger.info(f"Received `{packet}` from `{topic}` topic")
    if topic == f"{entry.data['username']}/homeassistant/sensor":
        data = json.loads(packet)
        sensor = InverterSensor(data['site_name'], data['inverter_id'], data['model_name'], data['serial_number'])
        if sensor.unique_id not in hass.data[DOMAIN]:
            hass.data[DOMAIN][sensor.unique_id] = sensor
        else:
            sensor = hass.data[DOMAIN][sensor.unique_id]
        sensor.last_interval = data['last_interval']
        for key in sensor._attr_native_values.keys():
            if key in data:
                sensor.set_value(key, data[key])
        sensor.schedule_update_ha_state()

def on_disconnect(client, user_data, rc):
    if rc != 0:
        logger.info("Unexpected disconnection: %d. Attempt reconnect", rc)
        client.reconnect()
    else:
        logger.info("Disconnected from MQTT Broker")
        

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up inverter_controller from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    try:
        mqtt_username = entry.data["username"]
        mqtt_password = entry.data["password"]
        client_external.username_pw_set(mqtt_username, mqtt_password)
        client_external.user_data_set({'hass': hass, 'entry': entry})
        client_external.on_connect = on_connect
        client_external.on_message = on_message
        mqtt_host = entry.data["host"]
        mqtt_port = entry.data["port"]
        client_external.connect(mqtt_host, mqtt_port)
        client_external.on_disconnect = on_disconnect
        client_external.loop_start()

    except Exception as e:
        logger.info(f"Failed to connect to MQTT Broker: {e}", exc_info=True)
        return False
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)


    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    client_external.disconnect()
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
