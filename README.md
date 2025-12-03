# Haptique RS90 - Intégration Home Assistant

[![Version](https://img.shields.io/badge/version-1.1.5-blue.svg)](https://github.com/daangel27/haptique_rs90/releases)
[![hacs](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Intégration Home Assistant pour la télécommande universelle **Haptique RS90** via MQTT.

[English](README_EN.md) | **Français**

## ✨ Fonctionnalités

- 🎛️ **Switches pour macros** : Contrôlez vos macros avec état visible ON/OFF
- 🔋 **Capteur de batterie** : Surveillez le niveau de batterie de la télécommande
- 🔌 **État de connexion** : Détection en temps réel de l'état online/offline
- 🎮 **Détection des touches** : Capteur des dernières touches pressées
- 📱 **Liste des appareils** : Visualisation de tous les appareils configurés
- 💾 **États persistants** : Conservation des états après redémarrage de Home Assistant
- 🔄 **MQTT retained** : États disponibles immédiatement lors de la reconnexion
- 🚀 **Auto-découverte** : Détection automatique du Remote ID

## 📋 Prérequis

- Home Assistant 2024.1.0 ou supérieur
- Broker MQTT configuré (Mosquitto recommandé)
- Télécommande Haptique RS90 connectée au même réseau MQTT

## 🚀 Installation

### Via HACS (Recommandé)

1. Ouvrez HACS dans Home Assistant
2. Cliquez sur "Intégrations"
3. Cliquez sur les trois points en haut à droite
4. Sélectionnez "Dépôts personnalisés"
5. Ajoutez l'URL : `https://github.com/daangel27/haptique_rs90`
6. Catégorie : `Integration`
7. Cliquez sur "Ajouter"
8. Recherchez "Haptique RS90"
9. Cliquez sur "Télécharger"
10. Redémarrez Home Assistant

### Installation Manuelle

1. Téléchargez la dernière version depuis [Releases](https://github.com/daangel27/haptique_rs90/releases)
2. Extrayez le contenu dans `/config/custom_components/haptique_rs90/`
3. Redémarrez Home Assistant

## ⚙️ Configuration

### 1. Ajouter l'intégration

1. Allez dans **Paramètres** → **Appareils et services**
2. Cliquez sur **Ajouter une intégration**
3. Recherchez **Haptique RS90**
4. L'intégration détectera automatiquement votre télécommande
5. Donnez un nom (optionnel, par défaut : "Haptique RS90")
6. Cliquez sur **Valider**

### 2. Configuration MQTT

Assurez-vous que votre télécommande Haptique RS90 publie sur les topics suivants :

```
Haptique/{RemoteID}/status          # État online/offline
Haptique/{RemoteID}/battery_level   # Niveau de batterie (0-100)
Haptique/{RemoteID}/keys            # Touches pressées
Haptique/{RemoteID}/macro/list      # Liste des macros
Haptique/{RemoteID}/device/list     # Liste des appareils
Haptique/{RemoteID}/macro/{name}/trigger  # État macro (on/off)
```

## 📊 Entités créées

### Capteurs (Sensors)

| Entité | Description | Valeurs |
|--------|-------------|---------|
| `sensor.{name}_battery` | Niveau de batterie | 0-100% |
| `sensor.{name}_last_key_pressed` | Dernière touche pressée | Nom de la touche |
| `sensor.{name}_running_macro` | Macro en cours | Nom de la macro ou "Idle" |
| `sensor.{name}_device_list` | Liste des appareils | Nombre d'appareils |

### Capteurs Binaires (Binary Sensors)

| Entité | Description | États |
|--------|-------------|-------|
| `binary_sensor.{name}_connection` | État de connexion | ON (online) / OFF (offline) |

### Interrupteurs (Switches)

| Entité | Description | Actions |
|--------|-------------|---------|
| `switch.{name}_macro_{macro_name}` | Contrôle de macro | ON / OFF / TOGGLE |

**Caractéristiques des switches :**
- ✅ État visible (ON = macro active, OFF = macro inactive)
- ✅ Toggle natif
- ✅ Icône dynamique (▶️ / ⏹️)
- ✅ États persistants après redémarrage

## 🎯 Exemples d'utilisation

### Dashboard

```yaml
type: entities
title: Télécommande Salon
entities:
  - entity: binary_sensor.rs90_connection
    name: Connexion
  - entity: sensor.rs90_battery
    name: Batterie
  - entity: switch.rs90_macro_watch_tv
    name: Regarder la TV
  - entity: switch.rs90_macro_cinema_mode
    name: Mode Cinéma
```

### Automatisation

```yaml
automation:
  - alias: "TV auto au retour"
    trigger:
      - platform: state
        entity_id: person.moi
        to: "home"
    condition:
      - condition: state
        entity_id: binary_sensor.rs90_connection
        state: "on"
      - condition: state
        entity_id: switch.rs90_macro_watch_tv
        state: "off"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.rs90_macro_watch_tv
```

### Script

```yaml
script:
  cinema_scene:
    alias: "Scène Cinéma"
    sequence:
      - service: switch.turn_on
        target:
          entity_id: switch.rs90_macro_cinema_mode
      - service: light.turn_off
        target:
          entity_id: light.salon
      - delay:
          seconds: 2
      - service: media_player.play_media
        target:
          entity_id: media_player.tv
```

## 🔧 Services disponibles

### `haptique_rs90.trigger_macro`

Déclenche une macro manuellement.

```yaml
service: haptique_rs90.trigger_macro
data:
  device_id: "votre_device_id"
  macro_name: "Watch TV"
  action: "on"  # ou "off"
```

### `haptique_rs90.trigger_device_command`

Envoie une commande à un appareil.

```yaml
service: haptique_rs90.trigger_device_command
data:
  device_id: "votre_device_id"
  device_name: "TV Samsung"
  command_name: "power_on"
```

### `haptique_rs90.refresh_data`

Actualise manuellement les données.

```yaml
service: haptique_rs90.refresh_data
data:
  device_id: "votre_device_id"
```

### `haptique_rs90.get_diagnostics`

Affiche les diagnostics dans les logs.

```yaml
service: haptique_rs90.get_diagnostics
data:
  device_id: "votre_device_id"
```

## 🐛 Dépannage

### La télécommande n'est pas détectée

1. Vérifiez que MQTT est configuré et fonctionne
2. Vérifiez que la télécommande publie sur les topics MQTT
3. Utilisez MQTT Explorer pour voir les messages
4. Activez les logs de debug :

```yaml
logger:
  logs:
    custom_components.haptique_rs90: debug
```

### Les switches ne reflètent pas l'état correct

1. Vérifiez que les topics `macro/{name}/trigger` publient avec `retained=True`
2. Vérifiez le fichier `.storage/haptique_rs90_*_states.json`
3. Redémarrez Home Assistant

### La batterie affiche toujours 0

1. Vérifiez que la télécommande répond au topic `battery/status`
2. Activez les logs debug et cherchez "Battery level updated"
3. Testez manuellement :

```bash
mosquitto_pub -h localhost -t "Haptique/YOUR_ID/battery/status" -m ""
mosquitto_sub -h localhost -t "Haptique/YOUR_ID/battery_level"
```

## 📁 Structure des fichiers

```
custom_components/haptique_rs90/
├── __init__.py           # Point d'entrée de l'intégration
├── manifest.json         # Métadonnées de l'intégration
├── config_flow.py        # Interface de configuration
├── coordinator.py        # Coordinateur MQTT
├── const.py             # Constantes
├── sensor.py            # Capteurs
├── binary_sensor.py     # Capteurs binaires
├── switch.py            # Switches pour macros
├── services.yaml        # Définition des services
├── strings.json         # Traductions anglaises
└── translations/
    └── fr.json          # Traductions françaises
```

## 🤝 Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit vos changements (`git commit -m 'Ajout fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- L'équipe Home Assistant pour l'excellente plateforme
- La communauté Haptique pour le support

## 📞 Support

- 🐛 [Signaler un bug](https://github.com/daangel27/haptique_rs90/issues)
- 💡 [Demander une fonctionnalité](https://github.com/daangel27/haptique_rs90/issues)
- 💬 [Discussions](https://github.com/daangel27/haptique_rs90/discussions)

---

**Version:** 1.1.5  
**Auteur:** daangel27  
**Dernière mise à jour:** Décembre 2025
