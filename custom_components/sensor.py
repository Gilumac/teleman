"""Platform for sensor integration."""
import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib import request

#import asyncio
#import async_timeout

import requests
import json
import re
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import PLATFORM_SCHEMA
from homeassistant.const import *


DEFAULT_NAME = "teleman"
SCAN_INTERVAL = timedelta(minutes=30)



PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
#    vol.Required(CONF_TOKEN): cv.string,
#    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.string,
#    vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
#    vol.Optional(CONF_PROTOCOL, default=DEFAULT_PROTO): cv.string,
#    vol.Optional(CONF_MAXIMUM, default=DEFAULT_LIMIT): cv.string,
#    vol.Optional(CONF_STATE, default=DEFAULT_STATE): cv.string,
     vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
#    vol.Optional(CONF_SORTING, default=DEFAULT_SORTING): cv.string
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([telemansensor(config)], True)



class telemansensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, config):
        self._state = None
        self._name = config.get(CONF_NAME)
        #self.token = config.get(CONF_TOKEN)
        #self.host = config.get(CONF_HOST)
        #self.protocol = config.get(CONF_PROTOCOL)
        #self.port = config.get(CONF_PORT)
        self.data = None
        #self.state_movies = config.get(CONF_STATE)
        #self.limit = config.get(CONF_MAXIMUM)
        #self.sort = config.get(CONF_SORTING)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.data

    def update(self):
    #async def async_update(self):

        attributes = {}
        card_json = []
        movie_tab = []
        init = {}
        """Initialized JSON Object"""
        init['title_default'] = '$title'
        init['line1_default'] = '$studio'
        init['line2_default'] = '$release'
        init['line3_default'] = '$number - $rating - $runtime'
        init['line4_default'] = '$genres'
        init['icon'] = 'mdi:eye-off'
        card_json.append(init)
        
        page_url = 'https://m.teleman.pl/highlights'
        page = requests.get(page_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        suggestions_div= soup.find(class_="suggestions")
        
        for link in suggestions_div.find_all('a'):
            href_link = link.get('href')
            inner_url = href_link.replace("/", "https://m.teleman.pl/", 1)
            #data_movie = link.find('div', class_="time").get_text().strip().split(":")
            #propper_hour = int(data_movie[0])
            #propper_minute = int(data_movie[1])
            
            channel = link.find('div', class_="station").get_text().strip()
            
            #zaglądam do linku
            page_inner = requests.get(inner_url)
            soup_inner = BeautifulSoup(page_inner.content, 'html.parser')
            titlemovie = soup_inner.find('h2').get_text().strip()
            genre = soup_inner.find('div', class_="genre").get_text().strip()
            short_description = soup_inner.find('p', class_='show-desc').get_text().strip()
            image = soup_inner.find('img', itemprop="image").get('src')
            image_propper = image.replace("//", "https://", 1)
            data_movie = soup_inner.find('div', class_="prog").get_text().strip().replace("\n", " " ).split(" ", 3)
            propper_day = int(data_movie[1].split(".")[0])
            propper_month = int(data_movie[1].split(".")[1])
            propper_hour = int(data_movie[2].split(":")[0])
            propper_minute = int(data_movie[2].split(":")[1])
            
            card_items = {}
            #card_items['airdate'] = datetime.today().replace(microsecond=0).isoformat() +"Z"
            card_items['airdate'] = datetime.now().replace(day=propper_day, month=propper_month, hour=propper_hour, minute=propper_minute, microsecond=0).isoformat() +"Z"
            card_items['poster'] = image_propper
            card_items['title'] = titlemovie
            card_items['studio'] = channel
            card_items['release'] = "$day $time"
            movie_tab.append(card_items)
            
            #if self.sort == "date":
        movie_tab.sort(key=lambda x: x.get('airdate'))

        card_json = card_json + movie_tab
        attributes['data'] = json.dumps(card_json)
        self.data = attributes

