# Haptique RS90 - Intégration Home Assistant

## Contribution Standard MQTT (brouillon)

Ajoute les macros réelles, les séquences, l’interrogation des états mémorisés et
l’actualisation de la découverte, les boutons d’ouverture des applications et
un capteur indiquant la dernière application signalée. Les identités des interrupteurs existants sont
conservées lors de la migration. Seul le retour du firmware confirme l’état.
Voir le [guide Standard MQTT](documentation/STANDARD_MQTT.md), notamment les
vérifications encore nécessaires sur une télécommande réelle.


[![Version](https://img.shields.io/badge/version-1.7.0-blue.svg)](https://github.com/daangel27/haptique_rs90/releases)
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

### Fonctionnalités principales
- 🎛️ **Switches pour macros** : Contrôlez vos macros avec état visible ON/OFF
- 📋 **Capteur de batterie** : Surveillez le niveau avec rafraîchissement optimisé
- 📌 **État de connexion** : Détection en temps réel online/offline
- 🎮 **Détection des touches** : Événements à chaque appui (même répétés)
- 🎯 **Déclencheurs d'appareil** : Support natif UI Home Assistant (24 boutons)
- 🔄 **Anneau RGB** : Bouton et service pour déclencher l'animation

### Fonctionnalités avancées
- 📱 **Liste des appareils** : Visualisation avec capteurs de commandes
- 📊 **Capteur Info Summary** : Tous les IDs au même endroit
- 🔄 **100% piloté par MQTT** : Pas de polling, mises à jour événementielles
- 🎯 **QoS optimisé** : QoS 0 pour surveillance, QoS 1 pour contrôle
- 🚀 **Auto-découverte** : Détection automatique du Remote ID
- 🌐 **Multi-langue** : Anglais et Français

### Nouveautés v1.7.0
- ⚡ **Événements sur chaque appui** : Tous les appuis déclenchent un événement
- 🎮 **Déclencheurs d'appareil** : 24 boutons dans l'UI (pas de YAML)
- 🔄 **Sync état macros** : État correct même depuis télécommande (nécessite MAJ firmware)
- 🔋 **Rafraîchissement intelligent** : Auto sur reconnexion + protection anti-spam
- 📍 **RemoteID MQTT exposé** : Accès facile pour débogage

---

## 📋 Prérequis

- Home Assistant 2024.1.0 ou supérieur
- **Broker MQTT configuré** (Mosquitto recommandé)
- **Télécommande Haptique RS90 configurée et connectée à MQTT**
- **Firmware RS90** : Dernière version recommandée pour toutes les fonctionnalités
  - Sync état macros nécessite MAJ firmware à venir (contacter support Haptique)

---

## 🚀 Installation

### Via HACS (Recommandé)

[![Ouvrir votre instance Home Assistant et ouvrir un dépôt dans le Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=daangel27&repository=haptique_rs90&category=integration)

**Étapes manuelles** (si le bouton ne fonctionne pas) :

1. Ouvrez **HACS** dans Home Assistant
2. Cliquez sur **Intégrations**
3. Cliquez sur **⋮** (trois points) → **Dépôts personnalisés**
4. Ajoutez le dépôt :
   - **URL** : `https://github.com/daangel27/haptique_rs90`
   - **Catégorie** : `Integration`
5. Cliquez sur **Ajouter**
6. Recherchez **"Haptique RS90"**
7. Cliquez sur **Télécharger**
8. Redémarrez Home Assistant

### Installation manuelle

1. Téléchargez la [dernière version](https://github.com/daangel27/haptique_rs90/releases)
2. Extrayez dans `/config/custom_components/haptique_rs90/`
3. Redémarrez Home Assistant

---

## ⚙️ Configuration

### Prérequis

Avant d'ajouter l'intégration :
1. ✅ **Broker MQTT configuré** dans Home Assistant
2. ✅ **RS90 configuré** pour se connecter à MQTT (app Haptique Config)
3. ✅ **RS90 en ligne** et publiant sur MQTT

### Configuration rapide

1. Allez dans **Paramètres** → **Appareils et services**
2. Cliquez sur **Ajouter une intégration**
3. Recherchez **Haptique RS90**
4. **L'intégration découvrira automatiquement votre télécommande** 🎉
5. Donnez-lui un nom (optionnel, défaut : "RS90 {ID}")
6. Cliquez sur **Valider**

C'est tout ! Toutes les entités sont créées automatiquement.

---

## 📊 Entités créées

### Capteurs (Sensors)

| Entité | Description | Fréquence de mise à jour |
|--------|-------------|--------------------------|
| `sensor.rs90_battery` | Niveau de batterie (0-100%) | Toutes les 30 min + reconnexion |
| `sensor.rs90_info_summary` | Tous les IDs en un endroit | Statique |

### Capteurs binaires (Binary Sensors)

| Entité | Description | États |
|--------|-------------|-------|
| `binary_sensor.rs90_connection` | État de connexion | ON (online) / OFF (offline) |
| `binary_sensor.rs90_last_key_pressed` | Dernière touche pressée | Numéro de bouton |

### Interrupteurs (Switches)

| Entité | Description | Actions |
|--------|-------------|---------|
| `switch.macro_{nom}` | Contrôle de macro | ON / OFF / TOGGLE |

**Caractéristiques :**
- ✅ État visible (ON = active, OFF = inactive)
- ✅ État synchronisé depuis télécommande (avec MAJ firmware)
- ✅ Icône dynamique (▶️ / ⏹️)

### Boutons (Buttons)

| Entité | Description | Action |
|--------|-------------|--------|
| `button.rgb_ring_light` | Déclenchement animation RGB | Active 5 secondes |

---

## 🎯 Nouveau v1.7.0 : Automatisations basées sur événements

### Utilisation des événements (Avancé)

Chaque appui de bouton déclenche un événement :

```yaml
automation:
  - alias: "Bouton 13 - Toggle lumières"
    trigger:
      - platform: event
        event_type: haptique_rs90_key_pressed
        event_data:
          button: 13
    action:
      - service: light.toggle
        target:
          entity_id: light.salon
```

**Données de l'événement :**
- `remote_id` : RemoteID MQTT
- `device_id` : ID appareil Home Assistant
- `button` : Numéro de bouton (1-24)
- `timestamp` : Horodatage de l'appui

### Utilisation des déclencheurs d'appareil (Facile - UI seulement)

**Pas de YAML nécessaire !** Créez des automatisations directement dans l'interface :

1. **Ajouter une automatisation** → **Ajouter un déclencheur** → **Appareil**
2. Sélectionnez **RS90 Remote**
3. Choisissez **Button pressed**
4. Sélectionnez le numéro de bouton (1-24)
5. Ajoutez des actions
6. Enregistrez

**YAML généré :**
```yaml
trigger:
  - platform: device
    device_id: [votre_rs90_id]
    domain: haptique_rs90
    type: button_pressed
    button: 13
```

**Avantages :**
- ✅ Déclenche à chaque appui (même répétés)
- ✅ Fonctionne simultanément avec les macros RS90
- ✅ Compatible avec le constructeur visuel

---

## 🔧 Services disponibles

### `haptique_rs90.trigger_macro`

Déclencher une macro on/off.

```yaml
service: haptique_rs90.trigger_macro
data:
  rs90_id: "9b974dab9a7649e13baeb921d4c9bb85"  # Depuis page appareil ou Info Summary
  rs90_macro_id: "692eb1561bddd5814022960c"     # Depuis attributs switch ou Info Summary
  action: "on"
```

**Trouver les IDs :**
- `rs90_id` : URL page appareil ou attribut `sensor.rs90_info_summary`
- `rs90_macro_id` : Attributs `switch.macro_{nom}` ou Info Summary

### `haptique_rs90.trigger_device_command`

Envoyer une commande à un appareil.

```yaml
service: haptique_rs90.trigger_device_command
data:
  rs90_id: "9b974dab9a7649e13baeb921d4c9bb85"
  rs90_device_id: "692ead781bddd58140228e33"  # Depuis attributs sensor ou Info Summary
  command_name: "POWER"
```

### `haptique_rs90.refresh_lists`

Forcer le rafraîchissement des appareils, macros et batterie.

```yaml
service: haptique_rs90.refresh_lists
data:
  rs90_id: "9b974dab9a7649e13baeb921d4c9bb85"
```

### `haptique_rs90.trigger_rgb_light`

Déclencher l'animation de l'anneau RGB.

```yaml
service: haptique_rs90.trigger_rgb_light
data:
  rs90_id: "9b974dab9a7649e13baeb921d4c9bb85"
  duration: 5  # 1-10 secondes
```

---

## 🛠️ Dépannage

### La télécommande n'est pas détectée

1. Vérifiez que **le broker MQTT est configuré** (Paramètres > Appareils et services > MQTT)
2. Vérifiez que **le RS90 est configuré** pour MQTT (app Haptique Config)
3. Vérifiez que **le RS90 est en ligne** (app Haptique Config)
4. Activez les logs de debug :

```yaml
logger:
  logs:
    custom_components.haptique_rs90: debug
```

### Les switches ne reflètent pas l'état correct

**Si firmware sans topic `/status` :**
- L'état se met à jour uniquement depuis Home Assistant
- Déclenchement depuis RS90 ne synchronise pas
- **Solution :** Mettre à jour le firmware quand disponible (contacter support Haptique)

**Si firmware mis à jour :**
- Vérifiez MQTT Explorer pour les topics `macro/{nom}/status`
- Vérifiez que le topic publie "ON"/"OFF" (majuscules)

### La batterie affiche 0 ou est obsolète

La batterie se rafraîchit :
- Toutes les 30 minutes (périodique)
- À la reconnexion du RS90 (réveil)
- Via service `refresh_lists` (manuel)

Si le RS90 se déconnecte fréquemment (<5 min), le rafraîchissement est limité à une fois par 5 minutes.

---

## 📚 Documentation

- **[CHANGELOG_FR.md](CHANGELOG_FR.md)** - Historique des versions
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Instructions détaillées
- **[Templates](templates/)** - Templates de cartes dashboard

---

## 🤝 Contribuer

Les contributions sont les bienvenues !

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit les changements (`git commit -m 'Ajout fonctionnalité'`)
4. Push (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- [Cantata Communication Solutions](https://github.com/Cantata-Communication-Solutions) pour la création de la télécommande **Haptique RS90**
- **Support Haptique** pour l'excellente collaboration sur les fonctionnalités firmware
- Communauté Home Assistant pour les retours et tests

---

## 📞 Support

- 🐛 [Signaler un bug](https://github.com/daangel27/haptique_rs90/issues)
- 💡 [Demander une fonctionnalité](https://github.com/daangel27/haptique_rs90/issues)
- 💬 [Discussions](https://github.com/daangel27/haptique_rs90/discussions)

---

**Version :** 1.7.0  
**Auteur :** daangel27  
**Dernière mise à jour :** Janvier 2026  
**Langues :** English, Français
