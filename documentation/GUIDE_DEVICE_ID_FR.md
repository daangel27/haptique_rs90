# Trouver l'identifiant de votre RS90 (`rs90_id`)

Toutes les actions de l'intégration (`trigger_macro`, `trigger_sequence`, `trigger_device_command`, `launch_app`, `query_status`…) demandent **`rs90_id`** : l'**identifiant d'appareil Home Assistant** de votre télécommande, ex. `6f99751e78b5a07de72d549143e2975c`.

Ce n'est **pas** :
- ❌ l'identifiant MQTT de la RS90 (ex. `3d5d95aa3a7f7b20`, utilisé dans les topics comme `Haptique/3d5d95aa3a7f7b20/status`)
- ❌ le nom de la RS90 (ex. « RS90 Salon »)

> 💡 Vous voulez juste appuyer sur des boutons ? Le **tableau de bord Haptique RS90** n'a besoin d'aucun identifiant (voir le README). Ce guide sert pour les automatisations et les scripts.

---

## 1. Le capteur Info Summary (le plus rapide)

Page de l'appareil RS90 → **Capteurs** → **Info Summary** → **Attributs** :
- **Rs90 ID** : le `rs90_id` à utiliser dans les actions
- **Rs90 remote ID** : l'identifiant MQTT
- **Macros / Sequences / Devices / Apps by ID** : les identifiants à utiliser pour `rs90_macro_id`, `rs90_sequence_id`, `rs90_device_id` et `app_package_id`

Voir [Retrouver les identifiants](../README_FR.md#-retrouver-les-identifiants--le-capteur-info-summary) dans le README.

## 2. Le laisser remplir par Home Assistant

Dans une automatisation, un script ou **Outils de développement → Actions**, choisissez une action comme **Haptique RS90 : Trigger macro**, puis sélectionnez votre télécommande dans le champ **RS90 Remote**. En mode YAML, Home Assistant affiche le `rs90_id` qu'il a rempli.

## 3. Avec un template (sans copier-coller)

```yaml
rs90_id: "{{ device_id('sensor.rs90_battery') }}"
```

Remplacez `sensor.rs90_battery` par n'importe quelle entité de votre RS90. L'identifiant suit alors la télécommande, même si l'intégration est supprimée puis ajoutée à nouveau.

## 4. Dans l'adresse de la page de l'appareil

**Paramètres → Appareils et services → Haptique RS90 → votre RS90**. La fin de l'adresse est l'identifiant :
```
http://homeassistant.local:8123/config/devices/device/6f99751e78b5a07de72d549143e2975c
```

---

## Exemples

Allumer une macro :
```yaml
action: haptique_rs90.trigger_macro
data:
  rs90_id: "{{ device_id('sensor.rs90_battery') }}"
  rs90_macro_id: "692eb1561bddd5814022960c"   # Info Summary → Macros by ID
  action: "on"
```

Envoyer une commande à un appareil :
```yaml
action: haptique_rs90.trigger_device_command
data:
  rs90_id: 6f99751e78b5a07de72d549143e2975c
  rs90_device_id: "6adf6831cd975fa9bbfbb363"   # Info Summary → Devices by ID
  command_name: "VOLUME_UP"                    # capteur Commands de l'appareil
```

> ⚠️ `rs90_id` se met dans `data:`. Utiliser `target: device_id:` à la place ne fonctionne pas avec ces actions.

---

## FAQ

**Le `rs90_id` peut-il changer ?**
Non, tant que vous ne supprimez pas la RS90 de Home Assistant. Si vous le faites, le template de la méthode 3 garde vos automatisations fonctionnelles.

**J'ai plusieurs RS90, comment les distinguer ?**
Donnez à chacune un nom clair lors de l'ajout (« RS90 Salon », « RS90 Chambre ») : le sélecteur **RS90 Remote** affiche ces noms.
