# Haptique RS90 - Intégration Home Assistant

[![Version](https://img.shields.io/badge/version-1.2.5-blue.svg)](https://github.com/daangel27/haptique_rs90/releases)
[![hacs](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Intégration Home Assistant pour la télécommande universelle **Haptique RS90** via MQTT.

[English](README.md) | **Français**

---

## 📸 Captures d'écran

<table>
<tr>
<td width="30%">
<img src="documentation/screenshots/device_info.png" alt="Informations appareil" />
<p align="center"><em>Informations et Contrôles</em></p>
</td>
<td width="30%">
<img src="documentation/screenshots/device_list.png" alt="Liste appareils" />
<p align="center"><em>Liste des appareils</em></p>
</td>
<td width="50%">
<img src="documentation/screenshots/device_commands.png" alt="Commandes appareil" />
<p align="center"><em>Liste des commandes</em></p>
</td>
</tr>
</table>

---

## ✨ Fonctionnalités

- 🎛️ **Switches pour macros** : Contrôlez vos macros avec état visible ON/OFF
- 🔋 **Capteur de batterie** : Surveillez le niveau de batterie de la télécommande
- 🔌 **État de connexion** : Détection en temps réel de l'état online/offline
- 🎮 **Détection des touches** : Capteur des dernières touches pressées
- 📱 **Liste des appareils** : Visualisation de tous les appareils configurés
- 📋 **Commandes des appareils** : Capteurs affichant les commandes disponibles pour chaque appareil
- 🔄 **100% piloté par MQTT** : Pas de polling, mises à jour événementielles pures
- 🎯 **QoS optimisé** : QoS 0 pour la surveillance, QoS 1 pour les commandes de contrôle
- 🚀 **Auto-découverte** : Détection automatique du Remote ID
- 🌍 **Multi-langue** : Anglais et Français

## 📋 Prérequis

- Home Assistant 2024.1.0 ou supérieur
- **Broker MQTT configuré** (Mosquitto recommandé)
- **Télécommande Haptique RS90 configurée et connectée à MQTT**

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

### Prérequis

Avant d'ajouter l'intégration, assurez-vous que :
1. ✅ **Le broker MQTT est configuré** dans Home Assistant
2. ✅ **Le RS90 est configuré** pour se connecter à votre broker MQTT (via l'application Haptique Config)
3. ✅ **Le RS90 est en ligne** et publie sur MQTT

### Auto-découverte

Une fois les prérequis remplis :

1. Allez dans **Paramètres** → **Appareils et services**
2. Cliquez sur **Ajouter une intégration**
3. Recherchez **Haptique RS90**
4. **L'intégration découvrira automatiquement votre télécommande** 🎉
5. Donnez-lui un nom (optionnel, par défaut : "RS90 {ID}")
6. Cliquez sur **Valider**

C'est tout ! L'intégration créera automatiquement toutes les entités.

### Topics MQTT

L'intégration s'abonne à ces topics (tous avec messages retained) :

```
Haptique/{RemoteID}/status                    # État online/offline
Haptique/{RemoteID}/battery_level             # Niveau de batterie (0-100)
Haptique/{RemoteID}/keys                      # Touches pressées
Haptique/{RemoteID}/macro/list                # Liste des macros (JSON)
Haptique/{RemoteID}/device/list               # Liste des appareils (JSON)
Haptique/{RemoteID}/device/{device}/commands  # Commandes de l'appareil (JSON)
Haptique/{RemoteID}/macro/{name}/trigger      # État de la macro (on/off)
```

## 📊 Entités créées

### Capteurs (Sensors)

| Entité | Description | Valeurs |
|--------|-------------|---------|
| `sensor.{name}_battery` | Niveau de batterie | 0-100% |
| `sensor.{name}_last_key_pressed` | Dernière touche pressée | Nom de la touche |
| `sensor.{name}_running_macro` | Macro en cours | Nom de la macro ou "Idle" |
| `sensor.{name}_device_list` | Liste des appareils | Nombre d'appareils |
| `sensor.commands_{device}` | Commandes disponibles | Liste des commandes (diagnostic) |

### Capteurs Binaires (Binary Sensors)

| Entité | Description | États |
|--------|-------------|-------|
| `binary_sensor.{name}_connection` | État de connexion | ON (online) / OFF (offline) |

### Interrupteurs (Switches)

| Entité | Description | Actions |
|--------|-------------|---------|
| `switch.macro_{macro_name}` | Contrôle de macro | ON / OFF / TOGGLE |

**Caractéristiques des switches :**
- ✅ État visible (ON = macro active, OFF = macro inactive)
- ✅ Toggle natif
- ✅ Icône dynamique (▶️ / ⏹️)
- ✅ Coloration bleue (ON) / grise (OFF)

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
  - entity: switch.macro_watch_tv
    name: Regarder la TV
  - entity: switch.macro_cinema_mode
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
        entity_id: switch.macro_watch_tv
        state: "off"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.macro_watch_tv
```

### Script

```yaml
script:
  cinema_scene:
    alias: "Scène Cinéma"
    sequence:
      - service: switch.turn_on
        target:
          entity_id: switch.macro_cinema_mode
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
  device_id: "6e99751e77b5a07de72d549143e2875a"  # ID de votre RS90
  macro_name: "Watch Movie"
```

### `haptique_rs90.trigger_device_command`

Envoie une commande à un appareil.

```yaml
service: haptique_rs90.trigger_device_command
data:
  device_id: "6e99751e77b5a07de72d549143e2875a"
  device_name: "Samsung TV"
  command_name: "POWER"
```

**Astuce :** Utilisez l'entité `sensor.commands_{device}` pour voir les commandes disponibles pour chaque appareil.

---

## 🎨 Templates de Dashboard

Vous voulez de belles cartes télécommande ? Consultez nos **templates de dashboard** !

### Template Carte Boutons Appareil

Générez automatiquement une carte télécommande complète avec toutes les commandes :

<table>
<tr>
<td width="60%">
<img src="documentation/screenshots/device_buttons_card.png" alt="Carte boutons appareil" />
</td>
<td width="40%">
<p><strong>Fonctionnalités :</strong></p>
<ul>
<li>✅ Boutons auto-générés</li>
<li>✅ Style 3D avec card-mod</li>
<li>✅ Grille responsive</li>
<li>✅ Fonctionne avec tout appareil</li>
</ul>
<p><strong><a href="templates/">📖 Voir les templates →</a></strong></p>
</td>
</tr>
</table>

---

## 🛠️ Dépannage

### La télécommande n'est pas détectée

1. Vérifiez que **le broker MQTT est configuré** dans Home Assistant (Paramètres > Appareils et services > MQTT)
2. Vérifiez que **le RS90 est configuré** pour se connecter à MQTT (application Haptique Config)
3. Vérifiez que **le RS90 est en ligne** (vérifiez dans l'application Haptique Config)
4. Utilisez **MQTT Explorer** pour vérifier que les messages sont publiés
5. Activez les logs de debug :

```yaml
logger:
  logs:
    custom_components.haptique_rs90: debug
```

### Les switches ne reflètent pas l'état correct

1. Vérifiez que la macro est correctement configurée dans le RS90
2. Vérifiez MQTT Explorer pour les topics `macro/{name}/trigger`
3. Redémarrez Home Assistant

### La batterie affiche toujours 0

Le niveau de batterie est mis à jour à la demande. Déclenchez une mise à jour manuellement ou attendez la prochaine mise à jour automatique.

## 📁 Structure des fichiers

```
custom_components/haptique_rs90/
├── __init__.py           # Point d'entrée de l'intégration
├── manifest.json         # Métadonnées de l'intégration
├── config_flow.py        # Interface de configuration
├── coordinator.py        # Coordinateur MQTT
├── const.py              # Constantes
├── sensor.py             # Capteurs
├── binary_sensor.py      # Capteurs binaires
├── switch.py             # Switches pour macros
├── services.yaml         # Définition des services
├── strings.json          # Traductions anglaises
├── icon.png              # Icône de l'intégration
└── translations/
    ├── en.json           # Traductions anglaises
    └── fr.json           # Traductions françaises
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

- [Cantata Communication Solutions](https://github.com/Cantata-Communication-Solutions) pour la création de la télécommande **Haptique RS90**
- L'équipe Home Assistant pour l'excellente plateforme
- La communauté Haptique pour le support

## 📞 Support

- 🐛 [Signaler un bug](https://github.com/daangel27/haptique_rs90/issues)
- 💡 [Demander une fonctionnalité](https://github.com/daangel27/haptique_rs90/issues)
- 💬 [Discussions](https://github.com/daangel27/haptique_rs90/discussions)

---

**Version :** 1.2.5  
**Auteur :** daangel27  
**Dernière mise à jour :** Décembre 2025  
**Langues :** English, Français
