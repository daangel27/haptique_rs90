# Template de carte boutons d'appareil

Génère une magnifique carte de télécommande dans votre tableau de bord avec toutes les commandes disponibles pour n'importe quel appareil contrôlé par votre Haptique RS90.

![Exemple de carte boutons](../documentation/screenshots/device_buttons_card.png)
*Exemple : Télécommande complète pour Canal Plus*

**Mis à jour pour v1.5.0** - Utilise maintenant le paramètre stable `haptique_device_id` !

---

## 🎯 Ce que fait ce template

Ce template génère automatiquement une **carte en grille** contenant **un bouton pour chaque commande** disponible sur votre appareil. Quand vous appuyez sur un bouton :

1. 🖱️ **Bouton pressé** dans le tableau de bord Home Assistant
2. 📡 **Service appelé** : `haptique_rs90.trigger_device_command`
3. 📤 **Message MQTT envoyé** à votre télécommande Haptique RS90
4. 📻 **Commande IR transmise** du RS90 vers votre appareil réel

**Résultat** : Votre TV, ampli ou tout appareil IR répond instantanément !

---

## 📋 Prérequis

Avant d'utiliser ce template, vous avez besoin de :

1. ✅ **Intégration Haptique RS90 v1.5.0+** installée et configurée
2. ✅ **Capteur de commandes d'appareil** disponible (créé automatiquement par l'intégration)
3. ✅ **Plugin frontend card-mod** installé (pour le style 3D des boutons)

### Installer card-mod (Optionnel mais recommandé)

Le template utilise **card-mod** pour un magnifique style de boutons 3D. Sans lui, les boutons fonctionneront mais auront un aspect basique.

Installation via HACS :
1. Ouvrir HACS → Frontend
2. Rechercher "card-mod"
3. Installer et redémarrer Home Assistant

**Note** : Le template fonctionne sans card-mod, mais les boutons n'auront pas l'effet 3D.

---

## 🔍 Trouver vos informations requises

Vous avez besoin de **2 informations** pour utiliser ce template :

### 1. Nom du capteur de commandes d'appareil

**Où le trouver** :
- Allez dans **Paramètres** → **Appareils et services**
- Cliquez sur **Haptique RS90**
- Cliquez sur votre télécommande RS90
- Regardez dans la section **Diagnostic**
- Trouvez les capteurs nommés : `Commands - {Nom Appareil}`

**Exemple** : `sensor.commands_canal`

**Format** : `sensor.commands_{nom_appareil}` (espaces remplacés par underscores, minuscules)

### 2. ID d'appareil RS90 (Home Assistant)

**Où le trouver** :
- Même page d'appareil que ci-dessus
- Regardez l'URL du navigateur : `http://homeassistant.local:8123/config/devices/device/6f99751e78b5a07de72d549143e2975c`
- Copiez le long ID à la fin : `6f99751e78b5a07de72d549143e2975c`

**Méthode alternative** : Utilisez le sélecteur UI dans Services (voir [GUIDE_DEVICE_ID_FR.md](../documentation/GUIDE_DEVICE_ID_FR.md))

---

## 🚀 Démarrage rapide

### Étape 1 : Copier le template

Copiez le contenu de [`device_buttons_card.yaml`](device_buttons_card.yaml)

### Étape 2 : Remplacer les espaces réservés

Trouvez et remplacez ces espaces réservés :

```yaml
# REMPLACEZ CECI :
sensor.commands_your_device_name

# PAR LE NOM DE VOTRE CAPTEUR (exemple) :
sensor.commands_canal
```

```yaml
# REMPLACEZ CECI :
device_id: "YOUR_RS90_DEVICE_ID_HERE"

# PAR VOTRE ID D'APPAREIL RS90 (exemple) :
device_id: "6f99751e78b5a07de72d549143e2975c"
```

**Note** : Le `haptique_device_id` est **récupéré automatiquement** depuis les attributs du capteur - aucune saisie manuelle nécessaire !

### Étape 3 : Ajouter au tableau de bord

1. Ouvrez votre tableau de bord Home Assistant en **mode édition**
2. Cliquez sur **Ajouter une carte**
3. Choisissez **Manuel** en bas
4. Collez votre template modifié
5. Cliquez sur **Enregistrer**

---

## 📝 Structure du template (v1.5.0)

```yaml
type: grid
title: Votre appareil
columns: 4
square: false
cards:
  {% for cmd in state_attr('sensor.commands_votre_appareil', 'commands') %}
  - type: button
    name: "{{ cmd.replace('_', ' ') }}"
    tap_action:
      action: call-service
      service: haptique_rs90.trigger_device_command
      data:
        device_id: "VOTRE_ID_APPAREIL_RS90_ICI"
        haptique_device_id: "{{ state_attr('sensor.commands_votre_appareil', 'haptique_device_id') }}"
        command_name: "{{ cmd }}"
```

**Nouveau dans v1.5.0** :
- ✅ Utilise `haptique_device_id` (ID stable) au lieu de `device_name`
- ✅ Récupère automatiquement l'ID d'appareil depuis les attributs du capteur
- ✅ Résistant aux renommages : Fonctionne même si vous renommez l'appareil dans Haptique Config

---

## 🎨 Personnalisation

### Changer la disposition en grille

```yaml
columns: 3  # Changer le nombre de colonnes (défaut : 4)
square: true  # Rendre les boutons carrés (défaut : false)
```

### Changer les couleurs des boutons

Trouvez ces lignes dans le template et modifiez les couleurs hexadécimales :

```yaml
--mdc-theme-primary: #1e3a8a;    # Couleur du bouton (défaut : bleu foncé)
--mdc-theme-secondary: #0f172a;  # Dégradé du bouton (défaut : bleu plus foncé)
```

**Exemples de couleurs** :
- Rouge : `#dc2626` / `#7f1d1d`
- Vert : `#16a34a` / `#14532d`
- Orange : `#ea580c` / `#7c2d12`
- Violet : `#9333ea` / `#581c87`

### Changer la taille des boutons

```yaml
height: 50px !important;      # Hauteur du bouton (défaut : 50px)
min-height: 50px !important;  # Hauteur minimale
font-size: 11px !important;   # Taille du texte (défaut : 11px)
```

---

## 📱 Exemple : Canal Plus

Voir [`example_canal_plus.yaml`](example_canal_plus.yaml) pour un exemple complet fonctionnel.

**Fonctionnalités** :
- Grille à 4 colonnes
- Style de boutons 3D avec ombres
- Récupération automatique des commandes
- Utilise `haptique_device_id` stable

---

## ❓ Dépannage

### Les boutons ne fonctionnent pas

**Vérifiez** :
1. Le nom du service est-il correct ? `haptique_rs90.trigger_device_command`
2. Votre télécommande RS90 est-elle en ligne ? (Vérifiez le capteur binaire : `binary_sensor.{nom}_connection`)
3. Utilisez-vous le bon device_id ? (Vérifiez l'URL ou utilisez le sélecteur UI)

### Erreur "Command not found"

**Vérifiez** :
1. Le nom de la commande est-il correct ? (Vérifiez les attributs du capteur pour les IDs de commandes exacts)
2. L'appareil a-t-il cette commande ? (Liste des commandes dans les attributs du capteur)

### Les boutons ont un aspect basique

**Solution** : Installez **card-mod** depuis HACS (voir section Prérequis ci-dessus)

### Appareil renommé - Les boutons ont cessé de fonctionner

**Solution** : Avec v1.5.0, cela NE DEVRAIT PAS arriver ! Le template utilise `haptique_device_id` qui est stable.

Si vous utilisez un ancien template (pré-v1.5.0 avec `device_name`), mettez à jour vers la nouvelle version.

---

## 🔄 Migration depuis l'ancien template (pré-v1.5.0)

**L'ancien template utilisait** :
```yaml
device_name: "Nom de votre appareil"  # ← Casse au renommage
```

**Le nouveau template utilise** :
```yaml
haptique_device_id: "{{ state_attr('sensor.commands_votre_appareil', 'haptique_device_id') }}"  # ← Stable !
```

**Étapes de migration** :
1. Remplacez votre ancien template par le nouveau
2. Mettez à jour le nom du capteur
3. Mettez à jour device_id
4. Terminé ! Le `haptique_device_id` est automatique

---

## 💡 Conseils

### Organiser par pièce

Créez des vues de tableau de bord séparées pour chaque pièce :
- **Salon** : TV, Barre de son, Décodeur
- **Chambre** : TV, Ventilateur
- **Bureau** : Projecteur, Système audio

### Utiliser des titres de carte

Ajoutez un titre pour identifier chaque télécommande :

```yaml
title: Télécommande Canal Plus  # ← Titre personnalisé
type: grid
```

### Combiner avec d'autres cartes

Ajoutez des switchs de macros au-dessus des boutons d'appareil :

```yaml
type: vertical-stack
cards:
  - type: entities
    entities:
      - switch.macro_watch_movie
      - switch.macro_tv
  - type: grid  # ← Votre template de boutons d'appareil
    ...
```

---

## 📚 Voir aussi

- [GUIDE_DEVICE_ID_FR.md](../documentation/GUIDE_DEVICE_ID_FR.md) - Comment trouver les IDs d'appareil Home Assistant
- [GUIDE_DEVICE_ID.md](../documentation/GUIDE_DEVICE_ID.md) - Version anglaise
- [README_FR.md](../README_FR.md) - Documentation principale de l'intégration
- [CHANGELOG_FR.md](../CHANGELOG_FR.md) - Changements v1.5.0

---

## 🙏 Crédits

Template créé pour l'intégration Home Assistant **Haptique RS90**.

- **Matériel** : Cantata Communication Solutions
- **Logiciel** : Haptique
- **Intégration** : [@daangel27](https://github.com/daangel27)

---

**Questions ?** Ouvrez un ticket sur [GitHub](https://github.com/daangel27/haptique_rs90/issues) !
