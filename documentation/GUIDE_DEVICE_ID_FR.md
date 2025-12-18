# Comment trouver le Device ID (Home Assistant) de votre RS90

## Qu'est-ce que le device_id ?

Le `device_id` est l'**identifiant unique Home Assistant** de votre télécommande RS90.

**Ce n'est PAS** :
- ❌ L'ID MQTT du RS90 (ex: `3d5d95aa3a7f7b20`)
- ❌ Le nom du RS90 (ex: "RS90 Salon")

**C'est** :
- ✅ L'identifiant interne Home Assistant (ex: `6f99751e78b5a07de72d549143e2975c`)

---

## Méthode 1 : Interface graphique (Recommandé)

### Dans l'UI des Services

1. Allez dans **Outils de développement** > **Services**
2. Sélectionnez le service `haptique_rs90.trigger_macro`
3. Cliquez sur le champ **"RS90 Remote"**
4. **Sélectionnez votre RS90 dans la liste** → Home Assistant remplit automatiquement le `device_id` !

✅ **Pas besoin de chercher l'ID manuellement !**

---

## Méthode 2 : Via les Paramètres

Si vous voulez voir l'ID explicitement :

1. Allez dans **Paramètres** > **Appareils et services**
2. Cliquez sur **Haptique RS90**
3. Cliquez sur votre télécommande (ex: "RS90 Salon")
4. L'URL dans votre navigateur contient le device_id :
   ```
   http://homeassistant.local:8123/config/devices/device/6f99751e78b5a07de72d549143e2975c
                                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                                          C'est le device_id !
   ```

---

## Méthode 3 : Via un template

Dans **Outils de développement** > **Template**, testez :

```yaml
{% for device in integration_entities('haptique_rs90') | map('device_id') | unique | list %}
  {{ device }}
{% endfor %}
```

---

## Utilisation dans les services

### ✅ Méthode recommandée (Interface graphique)

```yaml
service: haptique_rs90.trigger_macro
data:
  rs90_id: 6f99751e78b5a07de72d549143e2975c  # ← ID de l'appareil RS90
  rs90_macro_id: "692eb1561bddd5814022960c"  # ← Depuis attributs de sensor.macro_{nom}_info
  action: "on"
```

### ✅ Alternative (Sélecteur device)

```yaml
service: haptique_rs90.trigger_macro
target:
  device_id: 6f99751e78b5a07de72d549143e2975c
data:
  rs90_macro_id: "692eb1561bddd5814022960c"  # ← Depuis attributs de sensor.macro_{nom}_info
  action: "on"
```

---

## Correspondance ID MQTT ↔ ID Home Assistant

| Type | Exemple | Utilisation |
|------|---------|-------------|
| **ID MQTT** | `3d5d95aa3a7f7b20` | Topics MQTT (ex: `Haptique/3d5d95aa3a7f7b20/status`) |
| **ID Home Assistant** | `6f99751e78b5a07de72d549143e2975c` | Services HA (ex: `device_id` dans les services) |

**Important** : 
- L'ID MQTT est visible dans les logs de l'intégration
- L'ID Home Assistant est généré par Home Assistant lors de l'ajout de l'appareil
- Les deux sont différents et ne sont **pas interchangeables**

---

## FAQ

### Q: Pourquoi ne pas utiliser l'ID MQTT directement ?

R: Home Assistant génère son propre ID pour chaque appareil. Cela permet de gérer plusieurs RS90 avec le même firmware, des remplacements d'appareils, etc.

### Q: Comment savoir quel RS90 est lequel si j'en ai plusieurs ?

R: Donnez des noms clairs lors de l'installation :
- ✅ "RS90 Salon"
- ✅ "RS90 Chambre"
- ❌ "Haptique RS90 3d5d95aa"

### Q: Le device_id change-t-il ?

R: Non, il reste fixe tant que vous ne supprimez pas et ne recréez pas l'intégration.

---

## Résumé

**Pour utiliser les services Haptique RS90** :
1. Ouvrez l'interface des services
2. Sélectionnez votre RS90 dans le menu déroulant
3. Le device_id est automatiquement rempli ✅

**Pas besoin de chercher l'ID manuellement !**
