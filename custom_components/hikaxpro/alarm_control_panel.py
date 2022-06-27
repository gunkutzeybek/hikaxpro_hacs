from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
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

    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_AWAY
    )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for this device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            manufacturer="Antifurto365 - Meian",
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

    def alarm_disarm(self, code=None):
        """Send disarm command."""
        self.coordinator.axpro.disarm()

    def alarm_arm_home(self, code=None):
        """Send arm home command."""
        self.coordinator.axpro.arm_home()

    def alarm_arm_away(self, code=None):
        """Send arm away command."""
        self.coordinator.axpro.arm_away()
