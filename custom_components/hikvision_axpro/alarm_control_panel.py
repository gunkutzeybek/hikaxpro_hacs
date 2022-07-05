from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
)

from .const import DATA_COORDINATOR, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up a Hikvision ax pro alarm control panel based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    async_add_entities([HikAxProPanel(coordinator)], False)


class HikAxProPanel(CoordinatorEntity, AlarmControlPanelEntity):
    """Representation of Hikvision Ax Pro alarm panel."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_AWAY
    )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for this device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            manufacturer="Hikvision - Ax Pro",
            name=self.name,
        )

    @property
    def unique_id(self):
        """Return a unique id."""
        return self.coordinator.mac

    @property
    def name(self):
        """Return the name."""
        return "HikvisionAxPro"

    @property
    def state(self):
        """Return the state of the device."""
        return self.coordinator.state

    async def async_alarm_disarm(self, code=None):
        """Send disarm command."""
        await self.coordinator.async_disarm()

    async def async_alarm_arm_home(self, code=None):
        """Send arm home command."""
        await self.coordinator.async_arm_home()

    async def async_alarm_arm_away(self, code=None):
        """Send arm away command."""
        await self.coordinator.async_arm_away()
