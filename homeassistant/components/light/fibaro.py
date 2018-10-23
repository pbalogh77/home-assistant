"""
Support for Fibaro lights.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/light.fibaro/
"""
import logging

from homeassistant.components.light import (
    ATTR_BRIGHTNESS, ATTR_HS_COLOR, ENTITY_ID_FORMAT,
    SUPPORT_BRIGHTNESS, SUPPORT_COLOR, Light)
import homeassistant.util.color as color_util
from homeassistant.components.fibaro import (
    FIBARO_CONTROLLER, FIBARO_DEVICES, FibaroDevice)

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['fibaro']


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Perform the setup for Fibaro controller devices."""
    add_entities(
        [FibaroLight(device, hass.data[FIBARO_CONTROLLER])
         for device in hass.data[FIBARO_DEVICES]['light']], True)


class FibaroLight(FibaroDevice, Light):
    """Representation of a Fibaro Light, including dimmable."""

    def __init__(self, fibaro_device, controller):
        """Initialize the light."""
        self._state = False
        self._color = None
        self._brightness = None
        FibaroDevice.__init__(self, fibaro_device, controller)
        self.entity_id = ENTITY_ID_FORMAT.format(self.fibaro_id)

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return self._brightness

    @property
    def hs_color(self):
        """Return the color of the light."""
        return self._color

    @property
    def supported_features(self):
        """Flag supported features."""
        if self._color:
            return SUPPORT_BRIGHTNESS | SUPPORT_COLOR
        return SUPPORT_BRIGHTNESS

    def turn_on(self, **kwargs):
        """Turn the light on."""
        # if ATTR_HS_COLOR in kwargs and self._color:
        #     rgb = color_util.color_hs_to_RGB(*kwargs[ATTR_HS_COLOR])
        #     self.vera_device.set_color(rgb)
        # elif ATTR_BRIGHTNESS in kwargs and self.vera_device.is_dimmable:
        #     self.vera_device.set_brightness(kwargs[ATTR_BRIGHTNESS])
        # else:
        #     self.vera_device.switch_on()

        self._state = True
        self.schedule_update_ha_state(True)

    def turn_off(self, **kwargs):
        """Turn the light off."""
#        self.fibaro_device.switch_off()
        self._state = False
        self.schedule_update_ha_state()

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    def update(self):
        """Call to update state."""
        self._state = (self.fibaro_device.properties.value is 'true') or (int(self.fibaro_device.properties.value) > 0)
        if 'levelChange' in self.fibaro_device.interfaces:
            # If it is dimmable, both functions exist. In case color
            # is not supported, it will return None
            if 'brightness' in self.fibaro_device.properties:
                self._brightness = int(self.fibaro_device.properties.brightness)
            else:
                self._brightness = int(self.fibaro_device.properties.value)
            if 'color' in self.fibaro_device.properties:
                rgbs = self.fibaro_device.properties.color
                rgb = [int(i) for i in rgbs.split(",")][:3]
                c = color_util.color_RGB_to_hs(*rgb) if rgb else None
                self._color = c
