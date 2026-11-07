# Journal des modifications - Intégration Haptique RS90 pour Home Assistant

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.9.0] - Non publiée

### ✨ Nouvelles fonctionnalités
- **Tableau de bord Haptique RS90** (stratégie de tableau de bord fournie par l'intégration, listée sous *Community dashboards* dans Home Assistant 2026.5+) :
  - Onglet RS90 : macros en boutons ON/OFF (vert = ON), séquences, applications et état
  - Un onglet par appareil RS90, commandes regroupées comme sur une télécommande (alimentation, croix de navigation, volume et chaînes, lecture, pavé numérique, entrées, autres), style 3D avec card-mod
  - Reconstruit à chaque ouverture : les appareils, macros et applications ajoutés, renommés ou supprimés suivent tout seuls ; les macros et applications supprimées n'apparaissent plus
- **Réveiller la RS90** : saisissez son adresse IP dans les options pour obtenir un bouton **Réveiller**, et éventuellement la réveiller automatiquement avant les macros, applications et commandes (paquets UDP vers son IP jusqu'à ce qu'elle repasse en ligne, 20 s au maximum ; fonctionne avec l'adresse MAC aléatoire de la RS90)
- Avec le réveil automatique, les boutons de l'anneau RGB et **Synchroniser** réveillent aussi la RS90, et **Last Reported App** garde sa dernière valeur pendant la veille
- Bouton **Synchroniser** (entité de configuration) : demande à la RS90 de republier ses appareils, commandes, macros, séquences et applications, ainsi que la batterie et l'état des macros, sans passer par une action
- Au réveil de la RS90, l'intégration lui redemande ses listes (au plus toutes les 5 minutes) : les changements faits pendant sa veille sont rattrapés
- Les **options de l'intégration** deviennent un menu : renommer la télécommande, ou choisir les boutons de commandes affichés pour chaque appareil (tous par défaut, aucun masque l'appareil)

### 🐛 Corrections
- Renommer la télécommande n'efface plus les autres options
- L'adresse du script du tableau de bord contient une empreinte du fichier : les navigateurs chargent la nouvelle version après une mise à jour

---

## [1.8.1] - 2026-11-07

Version de maintenance : aucun changement de comportement.

### 🐛 Corrections
- Suppression de la dépendance inutilisée `aiomqtt` (Home Assistant ne l'installe plus)
- Version minimale de Home Assistant fixée à **2024.8** (plus ancienne version sur laquelle les tests passent)

### 📚 Documentation
- Modèle de carte « boutons d'un appareil » réécrit : seul le capteur est à remplacer, identifiants de la RS90 et de l'appareil trouvés automatiquement, commandes en double supprimées, syntaxe `perform-action`, procédure corrigée en 4 étapes (calcul dans Outils de développement → Modèle, puis collage du résultat dans une carte Manuel), nouvel exemple KODI
- Installation via le **Marketplace** de Home Assistant (2026.11+), avec la procédure HACS conservée pour les versions plus anciennes
- README : nouvelles captures, identifiants à retrouver avec le capteur Info Summary, badge de version minimale de Home Assistant

---

## [1.8.0] - 2026-11-07

Nécessite le firmware **Standard MQTT** de la RS90 (testé en 4.1.2 / 4.2).

### ✨ Nouvelles fonctionnalités

#### Macros et séquences Standard MQTT (PR #38, merci @ccs777)
- Les macros et les séquences sont découvertes séparément (`macro/list`, `sequence/list`) et déclenchées par **identifiant stable**
- L'état des macros (ON/OFF/UNKNOWN) vient du retour du firmware (`macro/<id>/status`), sans état supposé
- Nouvelles actions : `haptique_rs90.trigger_sequence`, `haptique_rs90.query_status`
- Les interrupteurs de macros existants gardent leur entity ID quand une macro devient une séquence ou est renommée

#### Applications installées (PR #39, merci @ccs777)
- Un bouton de lancement par application installée sur la RS90 (`app/list`), **désactivé par défaut**
- Nouvelle action : `haptique_rs90.launch_app`
- Nouveau capteur **Last Reported App** : affiche le nom de l'application (ex. `Kore`), package dans `app_package_id`
  - Reconnaît aussi les applications ouvertes depuis l'écran de la RS90, que le firmware signale par leur nom au lieu du package

#### Capteur et événement Last Macro Result
- Nouveau capteur **Last Macro Result**, ex. `CANAL · OFF · skipped (already_in_requested_state)`
  - Attributs : `target_name`, `target_id`, `target_kind`, `action`, `status`, `error`, `timestamp`
  - Chaque résultat a sa propre ligne dans le journal, même identique au précédent, rattachée à l'interrupteur de la macro/séquence
  - Dernière valeur restaurée après un redémarrage de Home Assistant
- Nouvel événement `haptique_rs90_macro_result` avec les mêmes données, pour les automatisations (ex. notification sur `skipped` / `failed`)
- Les résultats retenus renvoyés à la reconnexion ne sont pas comptés comme de nouvelles exécutions

#### Icône et logo de l'intégration
- Nouvelle icône et nouveau logo (clair et sombre), dans `brand/` pour que Home Assistant 2026.3+ les affiche ; l'ancien `icon.png` à la racine n'a jamais été utilisé par Home Assistant

### 🐛 Corrections
- Remplacement de `DeviceEntry.config_entries`, déprécié, par `config_entry_id` (cassé en HA 2027.10), avec repli pour les anciennes versions de HA
- Suppression du `sw_version: 1.0` codé en dur (la page de l'appareil affichait « Firmware : 1.0 » quelle que soit la version de la RS90)
- `• RGB Ring Light` renommé en `RGB Ring Light`
- Les paramètres de traduction (`{name}`) ne cassent plus les descriptions des actions
- Suppression de l'appel déprécié `device_registry.async_get_device` dans le capteur Info Summary (cassé en HA 2027.8), corrige #37

### 🙏 Remerciements
- @ccs777 pour les PR #38 et #39
- Claude (Anthropic), binôme IA sur cette version

---

## [1.7.0] - 2026-01-27

### ✨ Nouvelles fonctionnalités

#### Détection des appuis de touches basée sur les événements
- **Déclenche des événements à chaque appui de bouton**, y compris les appuis répétés du même bouton
- Nouvel événement : `haptique_rs90_key_pressed` avec données : `remote_id`, `device_id`, `button`, `timestamp`
- Active la **double fonctionnalité** : exécution macro RS90 + automatisation Home Assistant depuis un seul appui
- Résout le problème où appuyer deux fois sur le même bouton ne déclenchait pas les automatisations

**Exemple d'utilisation :**
```yaml
automation:
  trigger:
    - platform: event
      event_type: haptique_rs90_key_pressed
      event_data:
        button: 13
```

#### Déclencheurs d'appareil pour l'interface native
- **24 déclencheurs de boutons** (1-24) disponibles dans l'interface d'automatisation Home Assistant
- Pas besoin de YAML manuel - entièrement compatible avec le constructeur visuel
- Sélectionnez l'appareil RS90 et le bouton directement depuis les menus déroulants

**Exemple (généré par l'interface) :**
```yaml
trigger:
  - platform: device
    device_id: [votre_rs90]  # Depuis sensor.rs90_info_summary → rs90_id
    domain: haptique_rs90
    type: button_pressed
    button: 13
```

#### Synchronisation de l'état des macros
- **Nouveau topic MQTT** : Abonnement à `macro/{NomMacro}/status` pour le retour d'état
  - ⚠️ **Nécessite un firmware RS90 mis à jour** (version à venir de Haptique - contactez le support Haptique pour la disponibilité)
- **Suivi d'état correct** lorsque les macros sont déclenchées depuis la télécommande RS90
- Les entités switch reflètent maintenant fidèlement l'état des macros quelle que soit la source de déclenchement
- Architecture MQTT propre : Commandes (`/trigger`) séparées de l'état (`/status`)

**Détails techniques :**
- Topic commande : `macro/{NomMacro}/trigger` (retain=False, éphémère)
- Topic état : `macro/{NomMacro}/status` (retain=True par RS90, état autoritaire)
- Pas de boucles de synchronisation ni de commandes dupliquées

#### Exposition du RemoteID MQTT
- Ajout de l'attribut `rs90_remote_id` dans `sensor.rs90_info_summary`
- Facilite la découverte du RemoteID MQTT pour le débogage et les opérations MQTT manuelles

**Exemple d'attributs :**
```yaml
sensor.rs90_info_summary:
  rs90_id: "9b974dab9a7649e13baeb921d4c9bb85"  # ID Appareil HA
  rs90_remote_id: "3d5d95aa3a7f7b20"  # RemoteID MQTT (nouveau !)
  rs90_device_name: "RS90"
  devices: {...}
  macros: {...}
```

### 🔧 Améliorations

#### Optimisations du rafraîchissement de la batterie
- **Rafraîchissement automatique à la reconnexion** : Niveau de batterie demandé immédiatement quand la RS90 se réveille
- **Optimisé pour les cycles veille/réveil** : Jusqu'à 6x plus de mises à jour fréquentes quand la RS90 n'est pas sur le socle
- **Protection anti-spam** : Minimum 5 minutes entre les rafraîchissements pour éviter le spam lors de connexions instables
- **Intervalle du timer réduit** : Rafraîchissement périodique toutes les 30 minutes (au lieu de 60 minutes)

**Fréquence de rafraîchissement :**
- Sur le socle (toujours en ligne) : Toutes les 30 minutes
- Hors socle (veille/réveil ~10 min) : Toutes les ~10 minutes au réveil
- Connexion instable (<5 min déco/reco) : Limité à max 1 rafraîchissement par 5 minutes

#### Rafraîchissement batterie dans le service `refresh_lists`
- Le service `refresh_lists` demande maintenant aussi une mise à jour du niveau de batterie
- Utile pour un rafraîchissement manuel sans attendre les intervalles automatiques

### 🐛 Corrections de bugs

- Corrigé l'état des macros qui ne se mettait pas à jour lorsque déclenchées depuis la télécommande RS90
- Corrigé les potentielles boucles de publication MQTT lors de la synchronisation de l'état des macros
- Corrigé le niveau de batterie qui ne se mettait pas à jour pendant les cycles veille/réveil de la RS90

### 📝 Documentation

- Ajout d'exemples complets pour les automatisations basées sur les événements
- Documentation de l'utilisation des déclencheurs d'appareil dans l'interface d'automatisation
- Explication de l'architecture de synchronisation de l'état des macros
- Ajout de la documentation sur le comportement du rafraîchissement de la batterie

### ⚠️ Changements incompatibles

**Aucun** - Cette version est entièrement rétrocompatible avec la v1.5.1.

### 🙏 Remerciements

- **Synchronisation de l'état des macros** : Merci tout particulièrement au **Support Haptique** pour l'implémentation du topic `/status` et l'excellente collaboration !
- **Problème de détection d'événements** : Rapporté et validé par @Benz63Amg dans l'issue #35

### 📋 Prérequis

- **Firmware RS90** : La synchronisation de l'état des macros nécessite un firmware RS90 mis à jour avec support du topic `/status`
  - Cette fonctionnalité sera disponible dans une prochaine version du firmware
  - Contactez le support Haptique pour connaître la disponibilité et les instructions de mise à jour du firmware
  - Toutes les autres fonctionnalités fonctionnent avec les versions actuelles du firmware
- **Home Assistant** : 2024.1.0 ou plus récent
- **MQTT** : Configuré et fonctionnel

---

## [1.5.1] - 2025-12-27

### Version stable précédente

Voir les releases GitHub pour les détails : https://github.com/daangel27/haptique_rs90/releases

---

## Liens

- [Dépôt GitHub](https://github.com/daangel27/haptique_rs90)
- [Suivi des problèmes](https://github.com/daangel27/haptique_rs90/issues)
- [Documentation](https://github.com/daangel27/haptique_rs90/blob/main/README_FR.md)
