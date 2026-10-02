from typing import cast

from homeassistant.helpers import device_registry, entity_registry

from custom_components.voltalis.apps.home_assistant.home_assistant_module import VoltalisHomeAssistantModule
from custom_components.voltalis.const import DOMAIN

# Suffix mapping: {"old_suffix": "new_suffix"}
CUSTOM_SUFFIX_MAPPING: dict[str, str] = {
    "device_daily_consumption_offpeak": "device_energy_daily_off-peak",
    "device_daily_consumption_peak": "device_energy_daily_peak",
    "device_daily_consumption": "device_energy_daily",
    "device_connected": "device_health_status",
    "energy_contract_current_mode": "energy_contract_current_tariff",
    "energy_contract_kwh_off_peak_cost": "energy_contract_kwh_off-peak_price",
    "energy_contract_kwh_peak_cost": "energy_contract_kwh_peak_price",
    "energy_contract_kwh_current_cost": "energy_contract_kwh_current_price",
    "daily_consumption_offpeak": "energy_daily_off-peak",
    "daily_consumption_peak": "energy_daily_peak",
    "daily_consumption": "energy_daily",
    "live_consumption": "live_power",
}

# Pre-sort by descending length of old suffixes to prevent partial substring matches
# (e.g. matching "daily_consumption" inside "device_daily_consumption")
SORTED_SUFFIX_MAPPING = sorted(
    CUSTOM_SUFFIX_MAPPING.items(),
    key=lambda item: len(item[0]),
    reverse=True,
)


async def migrate(*, home_assistant_module: VoltalisHomeAssistantModule) -> bool:
    """Migrate Voltalis devices and entities unique IDs."""
    hass = home_assistant_module.hass
    dev_reg = device_registry.async_get(hass)
    ent_reg = entity_registry.async_get(hass)
    logger = home_assistant_module.logger
    entry = home_assistant_module.entry
    site_id = cast(str, entry.data.get("site_id"))

    # 1. Device migration
    devices = home_assistant_module.device_coordinator.data or {}
    for device in devices.values():
        old_identifier = (DOMAIN, f"{device.id}")
        new_identifier = (DOMAIN, f"{site_id}_{device.id}")

        device_internal = dev_reg.async_get_device_by_identifier(
            identifier=old_identifier,
            config_entry_id=entry.entry_id,
        )
        if device_internal:
            logger.debug(
                "Migrating device %s (internal ID: %s) -> %s",
                device.name,
                device_internal.id,
                new_identifier[1],
            )

            # Cleanup if a duplicate device already exists with the new identifier
            existing_device = dev_reg.async_get_device_by_identifier(
                identifier=new_identifier,
                config_entry_id=entry.entry_id,
            )
            if existing_device and existing_device.id != device_internal.id:
                dev_reg.async_remove_device(existing_device.id)

            dev_reg.async_update_device(
                device_id=device_internal.id,
                new_identifiers={new_identifier},
            )

    # 2. Energy contracts migration
    energy_contracts = home_assistant_module.energy_contract_coordinator.data or {}
    for energy_contract in energy_contracts.values():
        old_identifier = (DOMAIN, f"{energy_contract.subscriber_id}")
        new_identifier = (DOMAIN, f"{site_id}_{energy_contract.subscriber_id}")

        energy_contract_internal = dev_reg.async_get_device_by_identifier(
            identifier=old_identifier,
            config_entry_id=entry.entry_id,
        )
        if energy_contract_internal:
            logger.debug(
                "Migrating energy contract %s (internal ID: %s) -> %s",
                energy_contract.name,
                energy_contract_internal.id,
                new_identifier[1],
            )

            # Cleanup if a duplicate device already exists with the new identifier
            existing_contract = dev_reg.async_get_device_by_identifier(
                identifier=new_identifier,
                config_entry_id=entry.entry_id,
            )
            if existing_contract and existing_contract.id != energy_contract_internal.id:
                dev_reg.async_remove_device(existing_contract.id)

            dev_reg.async_update_device(
                device_id=energy_contract_internal.id,
                new_identifiers={new_identifier},
            )

    # 3. Entity migration
    entries = entity_registry.async_entries_for_config_entry(ent_reg, entry.entry_id)

    for entity_entry in entries:
        old_unique_id = entity_entry.unique_id

        # Check if the entity has a suffix that needs updating (longest first)
        new_suffix = None
        for old_suffix, custom_new_suffix in SORTED_SUFFIX_MAPPING:
            if old_unique_id.endswith(old_suffix):
                base_id = old_unique_id[: -len(old_suffix)]
                new_suffix = f"{base_id}{custom_new_suffix}"
                break

        target_id = new_suffix or old_unique_id

        # Prepend site_id if not already present
        if not target_id.startswith(f"{site_id}_"):
            new_unique_id = f"{site_id}_{target_id}"
        else:
            new_unique_id = target_id

        if new_unique_id != old_unique_id:
            logger.debug(
                "Migrating entity %s -> %s",
                old_unique_id,
                new_unique_id,
            )

            # Remove existing entity if a collision occurs with the new unique_id
            existing_entity_id = ent_reg.async_get_entity_id(
                domain=entity_entry.domain,
                platform=DOMAIN,
                unique_id=new_unique_id,
            )
            if existing_entity_id and existing_entity_id != entity_entry.entity_id:
                ent_reg.async_remove(existing_entity_id)

            ent_reg.async_update_entity(
                entity_id=entity_entry.entity_id,
                new_unique_id=new_unique_id,
            )

    return True
