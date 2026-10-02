from homeassistant.helpers import device_registry, entity_registry

from custom_components.voltalis.apps.home_assistant.home_assistant_module import VoltalisHomeAssistantModule
from custom_components.voltalis.const import DOMAIN

# Mapping éventuel si certains suffixes ont changé : {"ancien_suffixe": "nouveau_suffixe"}
CUSTOM_SUFFIX_MAPPING: dict[str, str] = {
    "device_daily_consumption": "device_energy_daily",
    "device_daily_consumption_peak": "device_energy_daily_peak",
    "device_daily_consumption_offpeak": "device_energy_daily_off-peak",
    "device_connected": "device_health_status",
    "energy_contract_current_mode": "energy_contract_current_tariff",
    "daily_consumption": "energy_daily",
    "daily_consumption_peak": "energy_daily_peak",
    "daily_consumption_offpeak": "energy_daily_off-peak",
    "energy_contract_kwh_current_cost": "energy_contract_kwh_current_price",
    "energy_contract_kwh_peak_cost": "energy_contract_kwh_peak_price",
    "energy_contract_kwh_off_peak_cost": "energy_contract_kwh_off-peak_price",
    "live_consumption": "live_power",
}


async def migrate(*, home_assistant_module: VoltalisHomeAssistantModule) -> bool:
    """Effectue les migrations d'identifiants d'appareils et entités Voltalis."""
    hass = home_assistant_module.hass
    dev_reg = device_registry.async_get(hass)
    ent_reg = entity_registry.async_get(hass)
    logger = home_assistant_module.logger

    # 1. Migration des appareils (Devices)
    devices = home_assistant_module.device_coordinator.data or {}
    for device in devices.values():
        old_identifier = (DOMAIN, f"{device.id}")
        new_identifier = (DOMAIN, f"{device.site_id}_{device.id}")

        device_internal = dev_reg.async_get_device_by_identifier(
            identifier=old_identifier,
            config_entry_id=home_assistant_module.entry.entry_id,
        )
        if device_internal:
            logger.debug(
                "Migration de l'appareil %s (ID interne: %s) -> %s",
                device.name,
                device_internal.id,
                new_identifier[1],
            )

            # Nettoyage si un doublon existe déjà avec le nouvel identifiant
            existing_device = dev_reg.async_get_device_by_identifier(
                identifier=new_identifier,
                config_entry_id=home_assistant_module.entry.entry_id,
            )
            if existing_device and existing_device.id != device_internal.id:
                dev_reg.async_remove_device(existing_device.id)

            dev_reg.async_update_device(
                device_id=device_internal.id,
                new_identifiers={new_identifier},
            )

    # 2. Migration des contrats d'énergie
    energy_contracts = home_assistant_module.energy_contract_coordinator.data or {}
    for energy_contract in energy_contracts.values():
        old_identifier = (DOMAIN, f"{energy_contract.subscriber_id}")
        new_identifier = (DOMAIN, f"{energy_contract.site_id}_{energy_contract.subscriber_id}")

        energy_contract_internal = dev_reg.async_get_device_by_identifier(
            identifier=old_identifier,
            config_entry_id=home_assistant_module.entry.entry_id,
        )
        if energy_contract_internal:
            logger.debug(
                "Migration du contrat d'énergie %s (ID interne: %s) -> %s",
                energy_contract.name,
                energy_contract_internal.id,
                new_identifier[1],
            )

            existing_contract = dev_reg.async_get_device_by_identifier(
                identifier=new_identifier,
                config_entry_id=home_assistant_module.entry.entry_id,
            )
            if existing_contract and existing_contract.id != energy_contract_internal.id:
                dev_reg.async_remove_device(existing_contract.id)

            dev_reg.async_update_device(
                device_id=energy_contract_internal.id,
                new_identifiers={new_identifier},
            )

    # 3. Migration des entités (Entities)
    # Récupération de toutes les entités associées à cette Config Entry
    entries = entity_registry.async_entries_for_config_entry(ent_reg, home_assistant_module.entry.entry_id)

    for entity_entry in entries:
        old_unique_id = entity_entry.unique_id

        # Recherche si l'entité possède un suffixe personnalisé
        new_suffix = None
        for old_suffix, custom_new_suffix in CUSTOM_SUFFIX_MAPPING.items():
            if old_unique_id.endswith(old_suffix):
                # Remplace l'ancien suffixe par le nouveau
                base_id = old_unique_id[: -len(old_suffix)]
                new_suffix = f"{base_id}{custom_new_suffix}"
                break

        # Si un suffixe personnalisé est identifié, on se base sur lui
        target_id = new_suffix or old_unique_id

        # Détermination du site_id correspondant
        # Vérification si le unique_id ne commence pas déjà par un site_id
        site_id = None
        for device in devices.values():
            if str(device.site_id) in target_id:
                site_id = str(device.site_id)
                break

        if not site_id and energy_contracts:
            first_contract = next(iter(energy_contracts.values()))
            site_id = str(first_contract.site_id)

        # Si le unique_id ne commence pas déjà par le site_id, on l'ajoute
        if site_id and not target_id.startswith(f"{site_id}_"):
            new_unique_id = f"{site_id}_{target_id}"
        else:
            new_unique_id = target_id

        if new_unique_id != old_unique_id:
            logger.debug(
                "Migration de l'entité %s -> %s",
                old_unique_id,
                new_unique_id,
            )

            # Supression si collision avec un unique_id existant
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
