# Nouveautés v1.8.0

**Date de sortie :** 7 novembre 2026
**Type :** version avec nouvelles fonctionnalités
**Changements incompatibles :** aucun ✅ (les interrupteurs de macros existants gardent leur entity ID)
**Nécessite :** firmware **Standard MQTT** de la RS90 (testé en 4.1.2 et 4.2), Home Assistant 2024.8+

---

## 🎯 Fonctionnalités principales

### 1. Macros et séquences, version Standard MQTT 🎛️

Grâce à [@ccs777](https://github.com/ccs777) (PR #38), les macros et les séquences sont maintenant découvertes séparément et déclenchées par leur **identifiant stable**.

- Un interrupteur par macro et un par séquence
- L'état affiché est celui **confirmé par la RS90** (`ON` / `OFF` / inconnu), jamais supposé
- Nouvelles actions `haptique_rs90.trigger_sequence` et `haptique_rs90.query_status` (relire un état sans rien exécuter)
- Vos interrupteurs et automatisations existants continuent de fonctionner : les entity ID sont conservés, même quand une macro devient une séquence

### 2. Lancer les applications de la RS90 📱

Également de [@ccs777](https://github.com/ccs777) (PR #39) :

- Un bouton par application installée sur la RS90, **désactivé par défaut** : activez seulement ceux qui vous intéressent dans Paramètres → Entités
- Nouvelle action `haptique_rs90.launch_app`
- Nouveau capteur **Last Reported App** : la dernière application signalée par la RS90, affichée par son nom (ex. `Kore`), même quand elle a été ouverte depuis l'écran de la RS90

### 3. Savoir ce que vos macros ont vraiment fait 📊

Nouveau capteur **Last Macro Result** :

```
CANAL · OFF · skipped (already_in_requested_state)
```

- Nom de la macro, action, statut et erreur sur une ligne, tous les détails en attributs
- **Une ligne dans le journal par résultat**, même quand le même résultat se répète, visible aussi dans le journal de la macro
- Conservé après un redémarrage de Home Assistant
- Nouvel événement `haptique_rs90_macro_result` pour les automatisations, par exemple être prévenu quand une macro est ignorée ou échoue (voir le [README](README_FR.md#résultats-des-macros))

### 4. Une vraie icône 🎨

L'intégration affiche enfin sa propre icône et son logo (thèmes clair et sombre) dans Home Assistant **2026.3+**.

---

## 🐛 Corrections

- Prête pour les prochaines versions de Home Assistant : remplacement d'appels dépréciés au registre des appareils (cassés en HA 2027.8 et 2027.10, #37)
- La page de l'appareil n'affiche plus un faux « Firmware : 1.0 »
- `• RGB Ring Light` renommé en `RGB Ring Light`
- Les descriptions des actions ne sont plus cassées en français

---

## ⚠️ Limitations connues du firmware

Signalées à Haptique, impossibles à corriger dans l'intégration :
- Une macro lancée **depuis l'écran de la RS90** n'est pas publiée sur MQTT
- En passant d'une macro à une autre, la précédente peut rester **ON**, et l'éteindre ensuite renvoie `skipped`
- La sortie d'une application n'est pas signalée : Last Reported App garde la dernière application ouverte
- Hors de son socle, la RS90 se met en veille et passe hors ligne : les commandes ne lui parviennent plus jusqu'à son réveil

---

## 🚀 Mise à jour

- **HACS** : ouvrez HACS → Haptique RS90 → **Mettre à jour**, puis redémarrez Home Assistant
- **Manuelle** : téléchargez la [v1.8.0](https://github.com/daangel27/haptique_rs90/releases/tag/v1.8.0), remplacez `custom_components/haptique_rs90/`, redémarrez

Les nouveaux boutons d'applications sont désactivés : activez ceux que vous voulez dans **Paramètres → Appareils et services → Entités**.

---

## 🙏 Remerciements

- [@ccs777](https://github.com/ccs777) pour les PR #38 et #39
- **Claude** (Anthropic), binôme IA sur cette version : code, tests, revues, documentation et icône
- Le **support Haptique** pour le firmware Standard MQTT

**Profitez bien de la v1.8.0 !** 🎉
