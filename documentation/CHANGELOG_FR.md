# Journal des modifications

Tous les changements notables de ce projet seront documentés dans ce fichier.

## [1.2.5] - 2024-12-10

### 🎉 Changements majeurs depuis v1.2.0

#### ✨ Nouvelles fonctionnalités
- **Capteurs de commandes d'appareils** : Ajout de capteurs de diagnostic affichant les commandes disponibles pour chaque appareil
  - Capteurs créés comme `sensor.commands_{nom_appareil}`
  - Triés alphabétiquement pour faciliter la navigation
  - Catégorisés comme entités de diagnostic
- **Logs MQTT améliorés** : Ajout de logs DEBUG complets pour toutes les opérations MQTT
  - Opérations Subscribe/Unsubscribe avec topics
  - Tous les messages reçus avec payloads
  - Tous les messages publiés avec QoS et flags retain
  - Utile pour le dépannage et la surveillance

#### 🔧 Améliorations techniques
- **100% piloté par événements** : Suppression de tout polling périodique
  - Plus de configuration `scan_interval`
  - Mises à jour uniquement via messages MQTT
  - Trafic réseau réduit et réactivité améliorée
- **Optimisation QoS** : Alignement avec les meilleures pratiques MQTT Haptique
  - QoS 0 pour la surveillance (status, batterie, touches, listes)
  - QoS 1 pour les commandes de contrôle (déclencheurs macro/appareil)
- **Protocole de déclenchement de macro** : Correction de la gestion des messages MQTT retained
  - Changement de `retain=True` à `retain=False` pour les déclencheurs de macro
  - Désabonnement approprié lors de la suppression de macros
  - Nettoyage automatique des messages retained lors de la suppression
- **Gestion dynamique des entités** : Amélioration de l'ajout/suppression d'entités
  - Nettoyage approprié lors de la suppression de macros/appareils
  - Correction des conditions de concurrence dans la gestion des abonnements
  - Entités mises à jour en temps réel

#### 🗑️ Fonctionnalités supprimées
- **Services supprimés** :
  - `haptique_rs90.refresh_data` (plus nécessaire avec mises à jour événementielles)
  - `haptique_rs90.get_diagnostics` (utilisez les logs DEBUG à la place)
- **Entités supprimées** :
  - Bouton Actualiser les données
  - Curseur Intervalle de scrutation

#### 🎨 Améliorations UI/UX
- **Switches de macros** :
  - Coloration Bleu (ON) / Gris (OFF) via device_class
  - Meilleur retour visuel
- **Capteur de connexion** :
  - Icônes dynamiques : `mdi:connection` (connecté) / `mdi:close-network-outline` (déconnecté)
- **Capteur de macro en cours** :
  - Icônes dynamiques : `mdi:play-circle` (actif) / `mdi:circle-outline` (inactif)
- **Entité Number** (supprimée) :
  - Avant : Curseur d'intervalle de scrutation (5-60 min)

#### 🌍 Internationalisation
- **Support multilingue** :
  - Anglais (par défaut)
  - Français
- **Descriptions de services** : Clarté améliorée
  - Meilleure explication du `device_id` (ID Home Assistant vs ID MQTT)
  - Instructions claires : "trouvez-la dans Paramètres > Appareils et services"
  - Exemples avec IDs réels
- **Chaînes traduites** : Traductions complètes pour :
  - Flux de configuration
  - Noms et descriptions de services
  - Libellés et descriptions de champs

#### 🐛 Corrections de bugs
- **Gestion des abonnements MQTT** :
  - Correction de la condition de concurrence empêchant le désabonnement correct des macros
  - Suivi approprié des états d'abonnement
  - Synchronisation des dictionnaires `_subscribed_macros` et `_macro_subscriptions`
  - Désabonnement approprié lors de la suppression de macros
- **Persistance d'état** :
  - Suppression de la persistance basée sur fichiers `.storage` (causait des déclenchements aléatoires)
  - S'appuie maintenant uniquement sur les messages MQTT retained du RS90 (source de vérité unique)

#### 📚 Documentation
- **README amélioré** :
  - Anglais comme langue par défaut
  - Explication claire de l'auto-découverte
  - Section des prérequis ajoutée
  - Meilleurs exemples de captures d'écran
  - Remerciements à Cantata Communication Solutions
- **Documentation des services** :
  - Distinction claire entre l'ID MQTT et le device_id Home Assistant
  - Guide étape par étape pour trouver le device_id
  - Meilleurs exemples

#### 🔒 Conformité protocolaire
- **100% conforme au MQTT Haptique** :
  - Vérifié par rapport à la documentation officielle
  - Niveaux QoS corrects pour toutes les opérations
  - Gestion appropriée des messages retained
  - Pattern Subscribe-once implémenté

### Détails techniques

#### Topics MQTT
- **Surveillance** (QoS 0, Retained) :
  - `status`, `battery_level`, `keys`, `device/list`, `macro/list`, `device/{name}/commands`
- **Contrôle** (QoS 1, Non Retained) :
  - `macro/{name}/trigger`, `device/{name}/trigger`

#### Changements de structure de fichiers
```diff
- button.py (supprimé - bouton refresh)
- number.py (supprimé - curseur scan interval)
+ coordinator.py amélioré (piloté par événements, pas de polling)
+ services.yaml amélioré (traductions EN/FR)
+ Nouveau translations/en.json
+ Nouveau translations/fr.json
```

---

## [1.2.0] - 2024-12-XX

### Fonctionnalités initiales
- Intégration MQTT avec Haptique RS90
- Capteurs de base (batterie, dernière touche, macro en cours, liste d'appareils)
- Capteur binaire pour l'état de connexion
- Switches de macro avec états ON/OFF
- Services pour déclencher des macros et des commandes d'appareil
- Intervalle de scrutation configurable (60s-3600s)
- Bouton de rafraîchissement manuel
- Service de diagnostic

---

## Guide de migration : 1.2.0 → 1.2.5

### Changements incompatibles
- ⚠️ **Entités supprimées** : `button.{name}_refresh_data` et `number.{name}_scan_interval`
- ⚠️ **Services supprimés** : `haptique_rs90.refresh_data` et `haptique_rs90.get_diagnostics`

### Ce que vous devez faire
1. **Supprimer les automatisations/scripts** qui utilisent les services supprimés
2. **Mettre à jour les dashboards** pour supprimer le bouton refresh et l'entité scan interval
3. **Activer les logs DEBUG** si vous utilisiez le service `get_diagnostics` :
   ```yaml
   logger:
     logs:
       custom_components.haptique_rs90: debug
   ```

### Ce qui reste identique
- ✅ Tous les switches de macro fonctionnent à l'identique
- ✅ Tous les capteurs continuent de fonctionner
- ✅ Services `trigger_macro` et `trigger_device_command` inchangés
- ✅ Aucune modification de configuration nécessaire

### Avantages de la mise à niveau
- 🚀 Temps de réponse plus rapides (piloté par événements vs polling)
- 📉 Trafic réseau réduit
- 🐛 Plus de déclenchements aléatoires de macros
- 🎨 Meilleur retour visuel (couleurs, icônes)
- 🌍 Support multilingue
- 📋 Capteurs de commandes d'appareil pour une découverte facile des commandes
