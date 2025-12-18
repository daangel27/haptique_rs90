# Nouveautés v1.5.0

## ⚠️ Important : Changements incompatibles

**La version 1.5.0 nécessite de mettre à jour vos automations et scripts.** Les paramètres de service ont été renommés pour plus de clarté et de stabilité.

**Temps de migration estimé** : 15-30 minutes  
**Guide de migration** : [MIGRATION_GUIDE_v1.5.0.md](MIGRATION_GUIDE_v1.5.0.md)

---

## 🎯 Top 3 améliorations

### 1. IDs d'entité ultra-stables 🎉

**Problème résolu** : Renommer un appareil/macro dans Haptique Config changeait l'entity ID dans Home Assistant, cassant les automations.

**Maintenant** : Les entity IDs sont basés sur les IDs internes Haptique et **ne changent jamais**.

### 2. Nouveau sensor pour accès facile aux IDs 📊

**Créé** : `sensor.macro_{nom}_info` pour chaque macro

**Attributs** :
- `rs90_macro_id` : L'ID stable à utiliser dans les services
- `macro_name` : Nom actuel
- `current_state` : État on/off

### 3. Paramètres de service plus clairs 🔧

**Ancien** : `device_id` (ambigu)  
**Nouveau** : `rs90_id` (clair!)

---

## 🔄 Ce que vous devez mettre à jour

| Ancien | Nouveau |
|--------|---------|
| `device_id` | `rs90_id` |
| `macro_name` | `rs90_macro_id` |
| `device_name` | `rs90_device_id` |

**Exemple rapide** :
```yaml
# Avant (v1.2.8)
service: haptique_rs90.trigger_macro
data:
  device_id: "abc123"
  macro_name: "Film"

# Après (v1.5.0)
service: haptique_rs90.trigger_macro
data:
  rs90_id: "abc123"
  rs90_macro_id: "692eb1561bddd5814022960c"
```

---

## 📍 Trouver vos IDs

### rs90_macro_id
1. Trouvez `sensor.macro_{nom}_info`
2. Regardez les attributs
3. Copiez `rs90_macro_id`

### rs90_device_id
1. Trouvez `sensor.{nom_telecommande}_commands_{nom}`
2. Regardez les attributs
3. Copiez `rs90_device_id`

### rs90_id
- URL de la page de l'appareil RS90

---

## 🛠️ Étapes de migration

1. **Trouvez vos IDs** (5 min)
2. **Mettez à jour les automations** (10-20 min)
3. **Mettez à jour les templates Lovelace** (5 min)
4. **Testez tout** (5 min)

**Guide détaillé** : [MIGRATION_GUIDE_v1.5.0.md](MIGRATION_GUIDE_v1.5.0.md)

---

**Version** : 1.5.0  
**Date de sortie** : 18 décembre 2025  
**Type** : Version majeure (Changements incompatibles)  
**Migration requise** : Oui
