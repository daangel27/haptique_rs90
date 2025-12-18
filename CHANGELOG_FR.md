# Journal des modifications

Tous les changements notables de ce projet seront documentés dans ce fichier.


## [1.5.0] - 2025-12-18

### ⚠️ CHANGEMENTS INCOMPATIBLES

Cette version inclut des **changements incompatibles** dans les paramètres des services. Toutes les automations et scripts utilisant les services Haptique RS90 **doivent être mis à jour**.

#### 🔄 Paramètres de service renommés

| Ancien paramètre (v1.2.8) | Nouveau paramètre (v1.5.0) | Service |
|---------------------------|----------------------------|---------|
| `device_id` | `rs90_id` | Tous les services |
| `macro_name` | `rs90_macro_id` | `trigger_macro` |
| `device_name` | `rs90_device_id` | `trigger_device_command` |

**Migration requise** : Voir [MIGRATION_GUIDE_v1.5.0.md](MIGRATION_GUIDE_v1.5.0.md)

#### 🎯 Ce qui a changé

**1. Paramètres de service - Changements incompatibles**

Tous les paramètres de service ont été renommés pour plus de clarté et de cohérence :

```yaml
# ANCIEN (v1.2.8) - NE FONCTIONNE PLUS
service: haptique_rs90.trigger_macro
data:
  device_id: "6f99751e78b5a07de72d549143e2975c"
  macro_name: "Regarder un film"
  action: "on"

# NOUVEAU (v1.5.0) - REQUIS
service: haptique_rs90.trigger_macro
data:
  rs90_id: "6f99751e78b5a07de72d549143e2975c"
  rs90_macro_id: "692eb1561bddd5814022960c"
  action: "on"
```

**Raison** : 
- `device_id` était ambigu (télécommande RS90 ? Appareil contrôlé ?)
- `rs90_id` indique clairement qu'il s'agit de l'ID Home Assistant de la télécommande RS90
- Tous les IDs utilisent maintenant des identifiants internes stables au lieu de noms

**2. Nouveau sensor : Info macro**

Création de `sensor.macro_{nom}_info` pour chaque macro :
- **État** : `available` (le sensor sert à exposer les attributs)
- **Attributs** :
  - `rs90_macro_id` : ID stable pour les appels de service
  - `macro_name` : Nom actuel de la macro
  - `current_state` : État on/off

**Objectif** : Accès facile aux IDs de macro pour les services et automations

**3. Attributs d'entité renommés**

| Type d'entité | Ancien attribut | Nouvel attribut |
|--------------|----------------|-----------------|
| `sensor.*_commands_*` | `haptique_device_id` | `rs90_device_id` |
| `switch.macro_*` | `macro_id` | `rs90_macro_id` |

**4. IDs d'entité ultra-stables**

Les IDs uniques d'entité sont maintenant basés sur les IDs internes Haptique :
- **Macros** : `{remote_id}_macro_{macro_id}`
- **Appareils** : `{remote_id}_commands_{device_id}`

**Avantage** : Les IDs d'entité ne changent jamais, même lors d'un renommage dans Haptique Config

**5. Mise à jour automatique des noms conviviaux**

Quand vous renommez un appareil ou une macro dans Haptique Config :
- ✅ L'ID d'entité reste stable (les automations ne cassent pas)
- ✅ Le nom convivial se met à jour automatiquement dans Home Assistant
- ✅ Aucune intervention manuelle nécessaire

**Exemple** :
```yaml
# Avant renommage
Entity ID: sensor.commands_canal
Nom convivial: Commands - Canal

# Après renommage "Canal" → "Canal+" dans Haptique Config
Entity ID: sensor.commands_canal        # ← Inchangé
Nom convivial: Commands - Canal+        # ← Mis à jour automatiquement
```

**6. Journalisation professionnelle**

Tous les emojis supprimés des logs pour une sortie plus propre et professionnelle :
- `📥 MQTT` → `MQTT`
- `✓` → `SUCCESS:`
- `🔄` → `RENAME:`

#### 📋 Étapes de migration

1. **Trouvez vos IDs** :
   - `rs90_macro_id` : Vérifiez les attributs de `sensor.macro_{nom}_info` ou `switch.macro_{nom}`
   - `rs90_device_id` : Vérifiez les attributs de `sensor.commands_{nom}`
   - `rs90_id` : Vérifiez l'URL de la page de l'appareil RS90

2. **Mettez à jour les automations** :
   - Remplacez `device_id` par `rs90_id`
   - Remplacez `macro_name` par `rs90_macro_id`
   - Remplacez `device_name` par `rs90_device_id`

3. **Mettez à jour les templates Lovelace** :
   - Utilisez des lookups dynamiques : `{{ state_attr('sensor.commands_canal', 'rs90_device_id') }}`

4. **Testez tout**

**Voir le guide détaillé** : [MIGRATION_GUIDE_v1.5.0.md](MIGRATION_GUIDE_v1.5.0.md)

#### 📦 Fichiers modifiés

**Intégration principale** :
- `services.yaml` / `services.fr.yaml` - Paramètres renommés
- `__init__.py` - Gestionnaires de services mis à jour
- `sensor.py` - Nouveau sensor info macro + attribut renommé
- `switch.py` - Attribut renommé
- `translations/en.json` / `fr.json` - Descriptions de services

**Templates** :
- `templates/device_buttons_card.yaml` - Mis à jour pour nouveaux paramètres
- `templates/example_canal_plus.yaml` - Mis à jour pour nouveaux paramètres
- `templates/README.md` - Guide de migration
- `templates/README_FR.md` - Guide de migration

**Documentation** :
- `MIGRATION_GUIDE_v1.5.0.md` - Guide de migration complet (NOUVEAU)
- `CHANGELOG.md` - Ce fichier
- `README.md` - Exemples mis à jour

#### ⚡ Performance et stabilité

- Détection de renommage thread-safe
- Intégration Entity Registry pour mises à jour UI instantanées
- Meilleure gestion des erreurs
- Meilleure exposition des attributs

#### 🌍 Traductions

- Traductions EN/FR complètes pour tous les services
- Descriptions de service mises à jour dans les deux langues

---

---

### 🔄 Guide de migration : 1.2.8 → 1.5.0

#### Ce qui a changé

**Services** :
- ✅ Nouveaux paramètres : `macro_id`, `haptique_device_id` (recommandés)
- ⚠️ Obsolètes : `macro_name`, `device_name` (fonctionnent encore, mais déconseillés)

**Stabilité des entités** :
- ✅ IDs uniques maintenant basés sur les IDs internes (ultra-stables)
- ✅ Les noms conviviaux se mettent à jour automatiquement au renommage
- ⚠️ Les IDs d'entité peuvent changer lors de la première mise à niveau (une seule fois)

#### Étapes de migration

**Option A : Continuer à utiliser les noms (aucun changement requis)**
```yaml
# Vos automations existantes continuent de fonctionner
service: haptique_rs90.trigger_macro
data:
  device_id: 1234567890abcdef
  macro_name: "Watch Movie"  # ← Fonctionne toujours avec avertissement
```

**Option B : Migrer vers les IDs (recommandé)**

1. **Trouver l'ID** dans les attributs d'entité :
   - Allez dans Paramètres > Appareils et services > Haptique RS90
   - Cliquez sur un switch de macro ou un capteur d'appareil
   - Cherchez `haptique_macro_id` ou `haptique_device_id` dans les attributs

2. **Mettez à jour vos automations** :
```yaml
# Ancienne méthode
service: haptique_rs90.trigger_macro
data:
  device_id: 1234567890abcdef
  macro_name: "Watch Movie"

# Nouvelle méthode (recommandée)
service: haptique_rs90.trigger_macro
data:
  device_id: 1234567890abcdef
  macro_id: "692eb1561bddd5814022960c"  # ← Copiez depuis les attributs
```

3. **Testez** vos automations

#### Avantages de la migration

- 🎯 **Résistant aux renommages** : Les IDs ne changent jamais, même si vous renommez dans Haptique Config
- 🚀 **Plus fiable** : Pas de confusion entre appareils/macros avec des noms similaires
- 📝 **À l'épreuve du temps** : Préparé pour la suppression éventuelle des paramètres basés sur les noms

---

## [1.2.8] - 2025-12-12

### ✨ Améliorations majeures

Cette version apporte la découverte automatique des commandes d'appareils et des améliorations de la surveillance de la batterie.

#### 🎯 Nouvelles fonctionnalités
- **Découverte automatique des commandes d'appareils** : Les nouveaux appareils ajoutés dans Haptique Config apparaissent maintenant automatiquement avec leurs commandes
- **Rafraîchissement automatique de la batterie** : Le niveau de batterie se met à jour automatiquement toutes les heures

#### 🔧 Améliorations
- **Service refresh_lists amélioré** : Amélioration pour re-scanner et s'abonner activement aux nouveaux appareils/macros
- **Meilleure conformité MQTT** : Correction du dernier problème de QoS avec les abonnements aux déclencheurs de macros

#### 🐛 Corrections de bugs
- **Correction de l'erreur de rechargement de l'intégration** : Résolution de l'erreur "Cannot unsubscribe topic twice"

---

## Tableau de comparaison des versions

| Fonctionnalité | 1.2.8 | 1.5.0 |
|----------------|-------|-------|
| **IDs uniques d'entité** | Basé sur le nom | Basé sur l'ID (stable) |
| **Mise à jour des noms conviviaux** | Manuelle | Automatique |
| **Paramètres de service** | `macro_name`, `device_name` | `macro_id`, `haptique_device_id` (recommandés) |
| **Style de logs** | Emojis | Texte professionnel uniquement |
| **Détection de renommage** | Non | Oui (mise à jour instantanée de l'interface) |
| **Stabilité des entités** | Bonne | Excellente |
| **Migration requise** | Non | Optionnelle (recommandée) |

---

## Support

- **Problèmes** : https://github.com/daangel27/haptique_rs90/issues
- **Discussions** : https://github.com/daangel27/haptique_rs90/discussions
- **Documentation** : https://github.com/daangel27/haptique_rs90
