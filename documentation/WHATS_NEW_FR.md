# Nouveautés de la v1.2.5

## 🎉 Mise à jour majeure : Du polling au 100% piloté par événements

Le plus gros changement dans la v1.2.5 est la suppression complète du polling périodique. Votre intégration réagit maintenant **instantanément** à chaque changement via MQTT !

---

## ✨ Points clés

### 🚀 Performance & Réactivité
- **Mises à jour instantanées** : Plus d'attente du prochain cycle de polling
- **Trafic réseau réduit** : Mises à jour uniquement lorsque quelque chose change
- **Usage CPU réduit** : Pas de tâches périodiques en arrière-plan

### 📋 Nouveau : Capteurs de commandes d'appareils
- Voir toutes les commandes disponibles pour chaque appareil d'un coup d'œil
- Situés dans la catégorie Diagnostic
- Triés alphabétiquement pour faciliter la navigation
- Exemple : `sensor.commands_samsung_tv` affiche toutes les commandes TV

### 🎨 Améliorations visuelles
- **Switches de macros** : Affichent maintenant bleu quand ON, gris quand OFF
- **Capteur de connexion** : Icônes dynamiques (connecté/déconnecté)
- **Macro en cours** : Icônes dynamiques (lecture/inactif)

### 🌍 Support multilingue
- **English** (par défaut)
- **Français**
- Traductions complètes pour tous les services et éléments d'interface

### 🔧 Meilleure documentation des services
- Distinction claire entre l'ID MQTT et le device_id Home Assistant
- Instructions étape par étape intégrées dans l'UI
- Exemples concrets avec des IDs réels

---

## 🗑️ Ce qui est supprimé (et pourquoi)

### Entités supprimées
- ❌ **Bouton Actualiser les données** → Plus nécessaire avec mises à jour événementielles
- ❌ **Curseur Intervalle de scrutation** → Plus de polling !

### Services supprimés
- ❌ **`haptique_rs90.refresh_data`** → Les mises à jour se font automatiquement
- ❌ **`haptique_rs90.get_diagnostics`** → Utilisez les logs DEBUG à la place

**Pas d'inquiétude !** Les services essentiels (`trigger_macro` et `trigger_device_command`) restent inchangés.

---

## 🐛 Corrections de bugs critiques

### Corrigé : Déclenchements aléatoires de macros
**Problème** : Les macros se déclenchaient parfois aléatoirement sans action de l'utilisateur.
**Cause** : La gestion duale d'état (fichier + MQTT) créait des conflits.
**Solution** : Utilise maintenant les messages MQTT retained comme source de vérité unique.

### Corrigé : Fuites d'abonnements
**Problème** : Les macros supprimées restaient abonnées à MQTT.
**Cause** : Condition de concurrence dans la gestion asynchrone des abonnements.
**Solution** : Suivi synchronisé des abonnements et nettoyage approprié lors de la suppression.

---

## 📚 Améliorations de la documentation

### Auto-découverte expliquée
Documentation claire sur les prérequis :
1. ✅ Broker MQTT configuré dans Home Assistant
2. ✅ RS90 configuré pour se connecter à MQTT (application Haptique Config)
3. ✅ RS90 en ligne et publiant

Une fois ces conditions remplies, l'intégration découvre automatiquement votre télécommande !

### Exemples de captures d'écran
Le README inclut maintenant des emplacements pour les captures d'écran :
- Processus d'installation
- Liste des entités
- Exemples de dashboard

### Remerciements
Merci spécial à [Cantata Communication Solutions](https://github.com/Cantata-Communication-Solutions) pour la création du Haptique RS90.

---

## 🔒 Conformité protocolaire

### 100% conforme au MQTT Haptique
Chaque aspect a été vérifié par rapport à la [documentation officielle Haptique MQTT](https://support.haptique.io/en/articles/mqtt) :

- ✅ **Niveaux QoS** : QoS 0 pour la surveillance, QoS 1 pour le contrôle
- ✅ **Messages Retained** : Uniquement sur les topics de surveillance, pas sur les déclencheurs
- ✅ **Subscribe-Once** : Pas de ré-abonnements inutiles
- ✅ **Nettoyage approprié** : Désabonnement et suppression lors de la suppression d'entité

---

## 📊 Détails techniques

### Structure des topics MQTT

**Topics de surveillance** (QoS 0, Retained) :
```
Haptique/{RemoteID}/status
Haptique/{RemoteID}/battery_level
Haptique/{RemoteID}/keys
Haptique/{RemoteID}/device/list
Haptique/{RemoteID}/macro/list
Haptique/{RemoteID}/device/{device}/commands
```

**Topics de contrôle** (QoS 1, Non Retained) :
```
Haptique/{RemoteID}/macro/{name}/trigger
Haptique/{RemoteID}/device/{device}/trigger
```

### Logs de débogage
Activez les logs MQTT complets :
```yaml
logger:
  logs:
    custom_components.haptique_rs90: debug
```

Vous verrez :
- 📡 Toutes les opérations SUBSCRIBE/UNSUBSCRIBE
- 📥 Tous les messages MQTT reçus avec payloads
- 📤 Tous les messages publiés avec QoS et flags retain

---

## 🔄 Migration depuis v1.2.0

### Ce que vous devez faire

1. **Mettre à jour l'intégration** via HACS ou manuellement
2. **Redémarrer Home Assistant**
3. **Supprimer des dashboards** :
   - Bouton Actualiser les données
   - Curseur Intervalle de scrutation
4. **Mettre à jour les automatisations** qui utilisaient les services supprimés
5. **Activer les logs DEBUG** si vous utilisiez `get_diagnostics`

### Ce qui reste identique

✅ Tous les switches de macro fonctionnent à l'identique
✅ Tous les capteurs fonctionnent sans changement
✅ La configuration ne nécessite aucun changement
✅ Vos automatisations utilisant `trigger_macro` et `trigger_device_command` fonctionnent comme avant

---

## 💡 Conseils pour une meilleure expérience

### 1. Utilisez les capteurs de commandes d'appareils
Au lieu de deviner les noms de commandes, consultez l'entité `sensor.commands_{appareil}` pour voir toutes les commandes disponibles.

### 2. Activez les logs DEBUG
Pour le dépannage ou la surveillance :
```yaml
logger:
  logs:
    custom_components.haptique_rs90: debug
```

### 3. Multi-langue
Changez la langue de Home Assistant pour voir l'intégration en français ou en anglais.

### 4. Utilisez l'icône
L'intégration a maintenant un joli logo Haptique dans l'interface !

---

## 🎯 Et ensuite ?

Améliorations futures envisagées :
- Plus de support linguistique (espagnol, allemand, néerlandais)
- Exemples d'automatisation avancés
- Bibliothèque de Blueprints
- Panneau de diagnostics amélioré

Vous avez des idées ? Ouvrez une issue ou une discussion sur [GitHub](https://github.com/daangel27/haptique_rs90) !

---

**Version** : 1.2.5
**Date de sortie** : 10 décembre 2024
**Changements incompatibles** : Oui (entités et services supprimés)
**Migration requise** : Minimale (mise à jour des dashboards et automatisations)
