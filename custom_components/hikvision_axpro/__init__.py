"""The hikvision_axpro integration."""
import asyncio
import logging
import hikaxpro

from async_timeout import timeout

from homeassistant.components.alarm_control_panel import SCAN_INTERVAL
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DATA_COORDINATOR, DOMAIN

PLATFORMS: list[Platform] = [Platform.ALARM_CONTROL_PANEL]
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up hikvision_axpro from a config entry."""
    host = entry.data[CONF_HOST]
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    axpro = hikaxpro.HikAxPro(host, username, password)

    try:
        async with timeout(10):
            mac = await hass.async_add_executor_job(axpro.get_interface_mac_address, 1)
    except (asyncio.TimeoutError, ConnectionError) as ex:
        raise ConfigEntryNotReady from ex

    coordinator = HikAxProDataUpdateCoordinator(hass, axpro, mac)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {DATA_COORDINATOR: coordinator}

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class HikAxProDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching ax pro data."""

    def __init__(self, hass, axpro, mac):
        self.axpro = axpro
        self.state = None
        self.host = axpro.host
        self.mac = mac

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    def _update_data(self) -> None:
        """Fetch data from axpro via sync functions."""
        status = self.axpro.get_area_arm_status(1)
        _LOGGER.debug("Axpro status: %s", status)

        self.state = status

    async def _async_update_data(self) -> None:
        """Fetch data from Axpro."""
        try:
            async with timeout(10):
                await self.hass.async_add_executor_job(self._update_data)
        except ConnectionError as error:
            raise UpdateFailed(error) from error

    async def async_arm_home(self):
        """Arm alarm panel in home state."""
        is_success = await self.hass.async_add_executor_job(self.axpro.arm_home)

        if is_success:
            await self._async_update_data()
            await self.async_request_refresh()

    async def async_arm_away(self):
        """Arm alarm panel in away state"""
        is_success = await self.hass.async_add_executor_job(self.axpro.arm_away)

        if is_success:
            await self._async_update_data()
            await self.async_request_refresh()

    async def async_disarm(self):
        """Disarm alarm control panel."""
        is_success = await self.hass.async_add_executor_job(self.axpro.disarm)

        if is_success:
            await self._async_update_data()
            await self.async_request_refresh()