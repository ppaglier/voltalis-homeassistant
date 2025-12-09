# Intégration Voltalis pour Home Assistant

[![Stable][release-badge]][release-link]
[![Qualité de l'intégration][integration-quality-badge]][integration-quality-link]
[![Installations actives][integration-active-instalations-badge]][integration-active-instalations-link]
[![Tous les téléchargements][integration-all-downloads-badge]][integration-all-downloads-link]
[![Derniers téléchargements][integration-latest-downloads-badge]][integration-latest-downloads-link]

**Langues** : [English](README.md) | [Français](README.fr.md)

<!-- Latest release -->
[release-badge]: https://img.shields.io/github/v/release/ppaglier/voltalis-homeassistant?label=release&sort=semver&logo=github
[release-link]: https://github.com/ppaglier/voltalis-homeassistant/releases/latest
<!-- Integration quality -->
[integration-quality-badge]: https://img.shields.io/badge/quality-silver-c0c0c0
[integration-quality-link]: https://developers.home-assistant.io/docs/core/integration-quality-scale/#-silver
<!-- Integration active instalations -->
[integration-active-instalations-badge]: https://img.shields.io/badge/dynamic/json?url=https://analytics.home-assistant.io/custom_integrations.json&query=%24.voltalis.total&color=brightgreen&label=active%20instalations&logo=homeassistant
[integration-active-instalations-link]: https://analytics.home-assistant.io/custom_integrations.json
<!-- Integration all downloads -->
[integration-all-downloads-badge]: https://img.shields.io/github/downloads/ppaglier/voltalis-homeassistant/total?&color=blue&logo=github
[integration-all-downloads-link]: https://github.com/ppaglier/voltalis-homeassistant/releases
<!-- Integration latest downloads -->
[integration-latest-downloads-badge]: https://img.shields.io/github/downloads/ppaglier/voltalis-homeassistant/latest/total?&color=blue&logo=homeassistantcommunitystore
[integration-latest-downloads-link]: https://github.com/ppaglier/voltalis-homeassistant/releases/latest
<!-- HACS button -->
[hacs-badge]: https://my.home-assistant.io/badges/hacs_repository.svg
[hacs-link]: https://my.home-assistant.io/redirect/hacs_repository/?owner=ppaglier&repository=voltalis-homeassistant&category=integration



## À propos de Voltalis

Voltalis est une entreprise française qui fournit des solutions intelligentes de gestion énergétique pour aider les ménages et les entreprises à réduire leur consommation d'électricité et à soutenir la stabilité du réseau. Leur technologie innovante aide à optimiser l'utilisation de l'énergie tout en maintenant le confort, permettant aux utilisateurs de :

- Surveiller la consommation énergétique en temps réel de leurs appareils de chauffage et d'eau chaude
- Réduire les factures d'électricité grâce à une gestion intelligente de l'énergie
- Contribuer à la stabilité du réseau et à la durabilité environnementale
- Obtenir des informations sur leurs habitudes de consommation énergétique

Vous pouvez en savoir plus sur leurs solutions sur le site officiel : [https://www.voltalis.com](https://www.voltalis.com).

Cette intégration vous permet de connecter vos appareils Voltalis à Home Assistant, ce qui vous permet de surveiller votre consommation énergétique et l'état de connexion de vos appareils directement depuis votre tableau de bord Home Assistant.

## Fonctionnalités

Cette intégration fournit un contrôle et une surveillance complets de vos appareils Voltalis à travers plusieurs types d'entités :

### Contrôle du climat (pour les appareils de chauffage)
- Contrôle complet du thermostat avec modes HVAC (Arrêt, Chauffage, Automatique)
- Modes préset (Confort, Économie, Protection antigel, Température)
- Contrôle de la température cible
- Modes de programmation automatique et manuel
- Actions de service avancées pour accélération rapide et mode manuel temporisé

### Capteurs
- **Consommation énergétique** : Surveillez la consommation énergétique cumulée (en Wh)
- **État de connexion** : Vérifiez si les appareils sont en ligne et connectés
- **Mode actuel** : Consultez le mode de fonctionnement actif (Confort, Économie, Protection antigel, etc.)
- **Type de programmation** : Voir la programmation active (Manuel, Par défaut, Utilisateur, Rapide)

### Contrôles
- **Sélecteur de préset** : Changez rapidement le mode de l'appareil (Automatique, Confort, Économie, Protection antigel, Température, Activé, Arrêt)

## Installation

### Prérequis

Avant d'installer cette intégration, vous avez besoin de :

- Un compte Voltalis valide (l'email et le mot de passe que vous utilisez pour vous connecter à l'application mobile ou au site web Voltalis)
- Au moins un appareil Voltalis installé et configuré dans votre maison
- Home Assistant 2024.1.0 ou plus récent

### Installation via HACS (Recommandé)

[![Ouvrir votre instance Home Assistant et ouvrir un dépôt dans le Home Assistant Community Store.][hacs-badge]][hacs-link]

<details>
  <summary>Cliquez pour afficher les instructions d'installation</summary>

  1. Assurez-vous que [HACS](https://hacs.xyz/) est installé dans votre instance Home Assistant
  2. Dans Home Assistant, allez à **HACS** > **Intégrations**
  3. Cliquez sur le menu **⋮** dans le coin supérieur droit et sélectionnez **Dépôts personnalisés**
  4. Ajoutez cette URL de dépôt : `https://github.com/ppaglier/voltalis-homeassistant`
  5. Définissez la catégorie sur **Intégration**
  6. Cliquez sur **Ajouter**
  7. Recherchez « Voltalis » dans HACS et cliquez sur **Télécharger**
  8. Redémarrez Home Assistant
</details>

### Installation manuelle

<details>
  <summary>Cliquez pour afficher les instructions d'installation manuelle</summary>

  1. Téléchargez la dernière version depuis la [page des versions](https://github.com/ppaglier/voltalis-homeassistant/releases)
  2. Extrayez le dossier `custom_components/voltalis` de l'archive
  3. Copiez le dossier `voltalis` dans votre répertoire Home Assistant `custom_components` :
    - Si le répertoire `custom_components` n'existe pas, créez-le dans votre répertoire de configuration Home Assistant (où se trouve `configuration.yaml`)
    - Le chemin final doit être : `<config_dir>/custom_components/voltalis/`
  4. Redémarrez Home Assistant
</details>

## Configuration

### Ajout de l'intégration

<details>
  <summary>Cliquez pour voir les instructions de configuration</summary>

  1. Dans Home Assistant, allez à **Paramètres** > **Appareils et services**
  2. Cliquez sur le bouton **+ Ajouter une intégration**
  3. Recherchez « Voltalis » et sélectionnez-le
  4. Entrez vos identifiants Voltalis :
    - **Adresse email** : L'adresse email associée à votre compte Voltalis
    - **Mot de passe** : Votre mot de passe de compte Voltalis
  5. Cliquez sur **Envoyer**

  L'intégration validera vos identifiants et découvrira automatiquement tous vos appareils Voltalis.
</details>

### Reconfiguration

<details>
  <summary>Cliquez pour voir les instructions de reconfiguration en cas de mise à jour de vos identifiants</summary>

  1. Allez à **Paramètres** > **Appareils et services**
  2. Trouvez l'intégration Voltalis
  3. Cliquez sur le menu **⋮** et sélectionnez **Reconfigurer**
  4. Entrez vos nouveaux identifiants
  5. Cliquez sur **Envoyer**
</details>

## Important : Configuration du contrôle de température

<details>
  <summary>⚠️ Configuration requise pour le contrôle de température (Cliquez pour développer)</summary>

  ### Prérequis pour le mode Température

  Avant d'utiliser le **préset Température** ou le **contrôle de température de l'entité climatique**, vous devez correctement configurer le thermostat physique de votre radiateur dans MyVoltalis.

  **Important** : L'appareil Voltalis ne peut pas générer une température de chauffage plus élevée que celle définie sur votre radiateur. Pour que le contrôle de la température fonctionne correctement, assurez-vous que le thermostat de votre appareil est réglé sur une température plus élevée que celle définie dans l'application.

  ### Étapes de configuration

  1. Accédez au thermostat physique de votre radiateur (sur le radiateur lui-même)
  2. Réglez-le sur la température maximale que vous souhaitez autoriser (par exemple, 25°C ou 30°C)
  3. Utilisez ensuite l'intégration Voltalis ou l'application MyVoltalis pour contrôler la température cible dans cette plage

  ### Guide visuel

  Regardez ce guide vidéo de MyVoltalis pour une configuration correcte :

  <video controls src="https://myvoltalis.com/assets/A5-CAQOXgYD.mp4" title="guide"></video>

  *Source vidéo : [MyVoltalis](https://myvoltalis.com/assets/A5-CAQOXgYD.mp4)*

  ### Ce qui se passe si ce n'est pas configuré

  Si le thermostat physique de votre radiateur est réglé à une température inférieure à celle que vous souhaitez dans Home Assistant :
  - Le contrôle de la température ne fonctionnera pas comme prévu
  - Votre radiateur sera limité par le réglage de son thermostat physique
  - Vous n'atteindrez pas la température cible définie dans l'application

</details>


## Entités

L'intégration crée différentes entités selon le type d'appareil et ses capacités :

### Entité climatique

<details>
  <summary>Entité climatique (appareils de chauffage uniquement)</summary>

  - **ID d'entité** : `climate.<device_name>_climate`
  - **Type** : Climatisation (Thermostat)
  - **Modes HVAC** :
    - `Off` : Éteindre l'appareil
    - `Heat` : Mode de chauffage manuel
    - `Auto` : Mode de programmation automatique (suit le programme utilisateur ou par défaut)
  - **Modes préset** : Confort, Économie, Protection antigel, Température (selon les capacités de l'appareil)
  - **Contrôle de la température** : Définir la température cible (7-30°C, par pas de 0,5°C)
    - ⚠️ **Important** : Avant d'utiliser le contrôle de la température, assurez-vous que le thermostat physique de votre radiateur est réglé à une température plus élevée que celle que vous souhaitez. Consultez la section [Configuration du contrôle de température](#important--configuration-du-contrôle-de-température) ci-dessus.
  - **Fonctionnalités** :
    - Activer/désactiver
    - Changer le mode HVAC
    - Définir le mode préset
    - Ajuster la température cible (si supporté)
  - **Fréquence de mise à jour** : Chaque 1 minute
</details>

### Entité de chauffe-eau

<details>
  <summary>Entité de chauffe-eau (appareils de chauffage d'eau uniquement)</summary>

  - **ID d'entité** : `water_heater.<device_name>_water_heater`
  - **Type** : Chauffe-eau
  - **Modes de fonctionnement** :
    - `Off` : Le chauffe-eau est éteint (aucun chauffage autorisé)
    - `On` : Le chauffe-eau est autorisé à fonctionner (pas un mode de chauffage forcé). Si l'appareil est derrière un relais heures creuses/heures pleines (HC/HP), il ne chauffera que lorsque le relais le permet. Ce mode ne contourne pas le relais et ne force pas le chauffage.
    - `Auto` : Voltalis gère l'état marche/arrêt du chauffe-eau selon son propre calendrier. Cependant, si l'appareil est derrière un relais HC/HP, le relais a toujours la priorité : Voltalis ne peut que permettre ou empêcher le chauffage lorsque le relais est fermé (heures creuses). Voltalis ne peut pas forcer le chauffe-eau à chauffer pendant les heures pleines si le relais est ouvert.
    - `Away` : Le chauffe-eau est en mode absence (chauffage réduit ou arrêté, pour les périodes d'absence).
  - **Fonctionnalités** :
    - Activer/désactiver
    - Changer le mode de fonctionnement (y compris l'absence)
  - **Fréquence de mise à jour** : Chaque 1 minute
</details>


### Capteurs

<details>
  <summary>Capteur de consommation énergétique</summary>

  - **ID d'entité** : `sensor.<device_name>_device_consumption`
  - **Type** : Capteur d'énergie
  - **Unité** : Wh (Watt-heures)
  - **Classe de périphérique** : Énergie
  - **Classe d'état** : Total croissant
  - **Description** : Affiche la consommation énergétique cumulée de l'appareil
  - **Fréquence de mise à jour** : Chaque 1 minute
</details>

<details>
  <summary>Capteur d'état de connexion</summary>

  - **ID d'entité** : `sensor.<device_name>_device_connected`
  - **Type** : Capteur Enum
  - **Classe de périphérique** : Enum
  - **États** : `Connecté`, `Déconnecté`, `Test en cours`
  - **Description** : Indique l'état de connexion de l'appareil
  - **Fréquence de mise à jour** : Chaque 1 minute
</details>

<details>
  <summary>Capteur du mode actuel</summary>

  - **ID d'entité** : `sensor.<device_name>_device_current_mode`
  - **Type** : Capteur Enum
  - **Classe de périphérique** : Enum
  - **États** : `Confort`, `Économie`, `Protection antigel`, `Température`, `Activé`, `Arrêt`
  - **Description** : Affiche le mode de fonctionnement actuel de l'appareil
  - **Icône** : Change dynamiquement en fonction du mode actuel
  - **Fréquence de mise à jour** : Chaque 1 minute
</details>

<details>
  <summary>Capteur de programmation (désactivé par défaut)</summary>

  - **ID d'entité** : `sensor.<device_name>_device_programming`
  - **Type** : Capteur Enum
  - **Classe de périphérique** : Enum
  - **États** : `Manuel`, `Par défaut`, `Utilisateur`, `Rapide`
  - **Description** : Indique quel type de programmation est actuellement actif
  - **Icône** : Change dynamiquement en fonction du type de programmation
  - **Fréquence de mise à jour** : Chaque 1 minute
  - **Remarque** : Ce capteur est désactivé par défaut. Activez-le dans les paramètres de l'entité si nécessaire.
</details>

### Entité de sélection

<details>
  <summary>Sélecteur de préset</summary>

  - **ID d'entité** : `select.<device_name>_device_preset`
  - **Type** : Sélection
  - **Options** : Automatique, Activé (si disponible), Confort, Économie, Protection antigel, Température, Arrêt
  - **Description** : Permet de basculer rapidement entre différents modes de fonctionnement
  - **Icône** : Change dynamiquement en fonction du préset sélectionné
  - **Fonctionnalités** :
    - **Automatique** : Retourne l'appareil à la programmation automatique (gérée par Voltalis)
    - **Activé** : Active l'appareil en mode normal (si supporté)
    - **Confort/Économie/Protection antigel** : Active indéfiniment le mode préset sélectionné
    - **Température** : Utilise le paramètre de température cible actuel
      - ⚠️ **Important** : Avant d'utiliser ce préset, assurez-vous que le thermostat physique de votre radiateur est correctement configuré. Consultez la section [Configuration du contrôle de température](#important--configuration-du-contrôle-de-température) ci-dessus.
    - **Arrêt** : Éteint l'appareil
  - **Fréquence de mise à jour** : Chaque 1 minute
</details>

## Dépannage

### Erreurs d'authentification

Si vous rencontrez des erreurs d'authentification :

1. Vérifiez que vos identifiants sont corrects en vous connectant au [site web Voltalis](https://www.voltalis.com)
2. Essayez de reconfigurer l'intégration avec des identifiants à jour
3. Si le problème persiste, supprimez l'intégration et ajoutez-la à nouveau

### Les appareils n'apparaissent pas

Si vos appareils n'apparaissent pas :

1. Assurez-vous que vos appareils sont correctement configurés dans l'application mobile Voltalis
2. Vérifiez que vos appareils sont en ligne et connectés dans l'application Voltalis
3. Essayez de redémarrer Home Assistant
4. Si les problèmes persistent, consultez les journaux de Home Assistant pour les messages d'erreur

### Problèmes de connexion

Si vous rencontrez des problèmes de connexion :

1. Vérifiez votre connexion Internet
2. Vérifiez que Home Assistant peut accéder aux services externes
3. Vérifiez les journaux de Home Assistant pour les messages d'erreur spécifiques liés à Voltalis

### Affichage des journaux

Pour afficher les journaux détaillés à des fins de dépannage :

1. Allez à **Paramètres** > **Système** > **Journaux**
2. Recherchez « voltalis » pour filtrer les entrées pertinentes
3. Vous pouvez également activer la journalisation de débogage en ajoutant ceci à votre `configuration.yaml` :

```yaml
logger:
  default: info
  logs:
    custom_components.voltalis: debug
```

## Suppression

Pour supprimer l'intégration Voltalis :

1. Allez à **Paramètres** > **Appareils et services**
2. Trouvez l'intégration Voltalis
3. Cliquez sur le menu **⋮** et sélectionnez **Supprimer**
4. Confirmez la suppression

Toutes les entités et tous les appareils associés à l'intégration seront supprimés de Home Assistant.

Si vous souhaitez également supprimer les fichiers d'intégration :

1. Accédez à votre répertoire Home Assistant `custom_components`
2. Supprimez le dossier `voltalis`
3. Redémarrez Home Assistant

## Confidentialité des données

Cette intégration communique directement avec l'API Voltalis en utilisant vos identifiants. Vos identifiants sont stockés de manière sécurisée dans le stockage chiffré de Home Assistant. Aucune donnée n'est envoyée à des tiers autres que les serveurs officiels de Voltalis.

## Appareils pris en charge

Cette intégration prend en charge tous les appareils compatibles avec l'écosystème Voltalis, y compris :

- **Modulateur Voltalis (Fil)** : Modulateurs de chauffage connectés pour radiateurs contrôlés par fil
  - Fournit : Entité climatique, tous les capteurs, sélecteur de préset
- **Modulateur Voltalis (Relais)** : Modulateurs de chauffage connectés pour radiateurs contrôlés par relais
  - Fournit : Entité climatique, tous les capteurs, sélecteur de préset
- **Chauffe-eaux** : Appareils de chauffage d'eau avec modulateurs Voltalis
  - Fournit : Capteur de consommation, capteur d'état de connexion, sélecteur de préset

Tous les appareils fournissent une surveillance de la consommation énergétique et de l'état de connexion. Les appareils de chauffage fournissent en outre un contrôle climatique complet avec fonctionnalité de thermostat.

## Actions de service

L'intégration fournit des actions de service avancées pour les entités climatiques afin d'activer des automatisations sophistiquées :

### Définir le mode manuel

Service : `voltalis.set_manual_mode`

Définissez l'appareil en mode manuel avec un préset spécifique ou une température pour une durée définie ou indéfiniment.

**Paramètres :**
- `preset_mode` (optionnel) : Le mode préset à appliquer (confort, économie, protection_antigel, aucun)
- `temperature` (optionnel) : Température cible en Celsius. Si défini, l'appareil utilisera le mode température
- `duration_hours` (optionnel) : Combien de temps rester en mode manuel (en heures). Si non spécifié, reste en mode manuel jusqu'à nouvel ordre

**Exemples :**

```yaml
# Définir le mode confort pour 3 heures
service: voltalis.set_manual_mode
target:
  entity_id: climate.living_room_heater
data:
  preset_mode: comfort
  duration_hours: 3

# Définir à 21°C indéfiniment
service: voltalis.set_manual_mode
target:
  entity_id: climate.bedroom_heater
data:
  temperature: 21

# Définir le mode économie avec température personnalisée pour 5 heures
service: voltalis.set_manual_mode
target:
  entity_id: climate.kitchen_heater
data:
  preset_mode: eco
  temperature: 19.5
  duration_hours: 5
```

### Désactiver le mode manuel

Service : `voltalis.disable_manual_mode`

Retournez l'appareil au mode de programmation automatique (programme utilisateur ou par défaut).

**Exemple :**

```yaml
service: voltalis.disable_manual_mode
target:
  entity_id: climate.living_room_heater
```

### Définir l'accélération rapide

Service : `voltalis.set_quick_boost`

Accélérez rapidement le chauffage pour une courte période. Utile pour un chauffage rapide avant votre arrivée à la maison.

**Paramètres :**
- `temperature` (optionnel) : Température cible pour le mode accélération. Si non spécifié, utilise le mode confort avec une température augmentée
- `duration_hours` (optionnel) : Combien de temps accélérer le chauffage (en heures). Par défaut, 2 heures

**Exemples :**

```yaml
# Accélération rapide de 2 heures à température confort
service: voltalis.set_quick_boost
target:
  entity_id: climate.living_room_heater

# Accélération à 23°C pour 1 heure
service: voltalis.set_quick_boost
target:
  entity_id: climate.bathroom_heater
data:
  temperature: 23
  duration_hours: 1
```

### Utilisation dans les automatisations

Ces actions de service sont particulièrement utiles pour créer des automatisations :

```yaml
# Accélérer le chauffage à l'arrivée
automation:
  - alias: "Accélérer le chauffage à l'arrivée"
    trigger:
      - platform: zone
        entity_id: person.john
        zone: zone.home
        event: enter
    action:
      - service: voltalis.set_quick_boost
        target:
          entity_id: climate.living_room_heater
        data:
          duration_hours: 2

# Définir le mode économie la nuit
automation:
  - alias: "Mode économie la nuit"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: voltalis.set_manual_mode
        target:
          entity_id: climate.bedroom_heater
        data:
          preset_mode: eco
          duration_hours: 8

# Retour au mode automatique le matin
automation:
  - alias: "Mode automatique le matin"
    trigger:
      - platform: time
        at: "06:00:00"
    action:
      - service: voltalis.disable_manual_mode
        target:
          entity_id: climate.bedroom_heater
```

## Inspirations

Ce projet a été inspiré par et construit sur les travaux de :

- [ha-voltalis from jdelahayes](https://github.com/jdelahayes/ha-voltalis)
- [ha-addons from zaosoula](https://github.com/zaosoula/ha-addons)
- [flashbird-homeassistant from gorfo66](https://github.com/gorfo66/flashbird-homeassistant)

## Contribution

Les contributions sont bienvenues ! Veuillez vous assurer de suivre les [directives de contribution](CONTRIBUTING.md) pour ouvrir un problème ou soumettre une demande d'extraction. Les problèmes ne respectant pas les directives peuvent être fermés immédiatement.

## Licence

Ce projet est sous [licence MIT](LICENSE).
