# Nouveautés v1.9.2

**Date de sortie :** 25 novembre 2026 · **Type :** correctif · **Pour :** firmware RS90 4.4

Le firmware RS90 4.4 corrige les commandes en double : chaque code a maintenant son propre ID, et la bascule **Power** de l'AMPLI fonctionne enfin depuis Home Assistant. Mais certains de ces ID sont techniques (`6adf6831cd975fa9bbfbb366`), et le tableau de bord les affichait sur les boutons. La 1.9.2 adapte l'intégration :

- **Les boutons affichent le nom de la commande** (`Power`, `Mute/Unmute`, `Volume + 2`…) et la section **Alimentation** revient avec `On`, `Off` et `Power`.
- Votre **sélection de commandes** faite avec le firmware 4.3 reste valable.
- L'**Activité** affiche `RS90 AMPLI → Power sent` au lieu de l'ID.
- ⚠️ Après le passage de la RS90 en 4.4, les automatisations qui envoient `POWER`, `MUTE_UNMUTE` ou `PLAY_PAUSE` peuvent devoir utiliser les nouveaux ID (`ON`/`OFF`, `MUTE`/`UNMUTE`, `PLAY`/`PAUSE`) : voir le capteur **Commands** de l'appareil.

Toujours en firmware 4.3 ? Rien ne change pour vous.

---

# Nouveautés v1.9.1

**Date de sortie :** 18 novembre 2026 · **Type :** correctif

- **Les appuis de touche ne sont plus rejoués au démarrage.** La RS90 garde son dernier appui sur le broker MQTT (retained), et l'intégration le prenait pour un nouvel appui à chaque redémarrage de Home Assistant ou rechargement de l'intégration : une automatisation sur cette touche se relançait (ex. une touche Power qui éteignait tout). Il ne met plus à jour que **Last Key Pressed**. Merci à @Nick de l'avoir repéré !
- Modèles de cartes supprimés : utilisez le **tableau de bord Haptique RS90** (Paramètres → Tableaux de bord → Ajouter un tableau de bord → Haptique RS90).

---

# Nouveautés v1.9.0

**Date de sortie :** 8 novembre 2026
**Type :** version avec nouvelles fonctionnalités
**Changements incompatibles :** aucun ✅
**Nécessite :** firmware **Standard MQTT** de la RS90 (testé en 4.2), Home Assistant 2024.8+ (2026.5+ pour le tableau de bord)

---

## 🎯 Fonctionnalités principales

### 1. Un tableau de bord télécommande prêt à l'emploi 📺

Plus besoin de YAML ni de cartes faites à la main : l'intégration fournit son propre **tableau de bord Haptique RS90**.
**Paramètres → Tableaux de bord → Ajouter un tableau de bord → Haptique RS90**, et c'est tout.

- **Un onglet par appareil** (TV, ampli, Kodi…), organisé comme une vraie télécommande : marche/arrêt, pavé de navigation, volume et chaînes, lecture, pavé numérique, entrées
- **Un onglet RS90** pour lancer les macros (en vert quand elles sont ON), les séquences et les applications d'une touche, avec l'état de la télécommande
- **Toujours à jour** : ajoutez, renommez ou supprimez un appareil, une macro ou une application sur la RS90, le tableau de bord suit tout seul
- **Seulement les boutons utiles** : dans les options de l'intégration, choisissez pour chaque appareil toutes les commandes, seulement celles que vous cochez (avec les raccourcis **Tout cocher / Tout décocher**), ou aucune pour masquer l'appareil

### 2. La RS90 dort ? Home Assistant la réveille 😴

Hors de son socle, la RS90 se met en veille et n'écoute plus MQTT. Indiquez son adresse IP dans les options de l'intégration :

- un bouton **Réveiller** la réveille à la demande
- avec le **réveil automatique**, elle est réveillée avant les macros, applications, commandes d'appareils, anneau RGB et Synchroniser, sans toucher à la télécommande
- seule l'IP est nécessaire : ça fonctionne avec l'adresse MAC Wi-Fi aléatoire de la RS90 (donnez-lui une IP fixe dans votre box)
- les boutons appuyés pendant le réveil sont gardés et envoyés un par un dès qu'elle est prête

### 3. Voir ce qui se passe 🔎

Chaque commande envoyée, chaque réveil et chaque résultat de macro apparaît maintenant dans l'**Activité** de Home Assistant, avec une icône :
- `Commands - KODI → DOWN sent`
- `Wake up → woke up in 8 s`, `did not wake up`, `already awake`
- `KODI → ON: executed`

Filtrez le panneau **Activité** sur la RS90, ou sur une seule entité (ex. **Commands - AMPLI**), pour vérifier qu'une commande est bien partie de Home Assistant.

### 4. Et aussi ✨

- Bouton **Synchroniser** : demande à la RS90 de republier ses appareils, commandes, macros, séquences et applications. Les listes sont aussi rafraîchies quand la RS90 se réveille (au plus toutes les 5 minutes)
- **Last Reported App** garde sa valeur pendant que la RS90 dort
- Les séquences ont leurs propres icônes, distinctes des macros

---

## 🐛 Corrections

- Renommer la télécommande n'efface plus les autres options
- Après une mise à jour, le navigateur charge le nouveau tableau de bord au lieu d'une version en cache

---

## ⚠️ Limitations connues du firmware

Signalées à Haptique, impossibles à corriger dans l'intégration (certaines corrections sont prévues dans le firmware 4.3) :
- Juste après un réveil, une commande vers un appareil réseau (ex. Kodi) peut être perdue quand plusieurs sont appuyées d'affilée. Les appareils infrarouges ne sont pas concernés
- Si un appareil a deux commandes du même nom (ex. deux `POWER`), une seule peut être envoyée : renommez-en une dans l'application Haptique
- Une séquence lancée par une macro n'a pas d'état ON/OFF tant qu'elle n'a pas été lancée seule une fois
- Une macro lancée **depuis l'écran de la RS90** n'est pas publiée sur MQTT, et en passant d'une macro à une autre la précédente peut rester **ON**

---

## 🚀 Mise à jour

- **Marketplace** (Home Assistant 2026.11+) : Paramètres → Marketplace → Haptique RS90 → **Mettre à jour**
- **HACS** (versions plus anciennes) : ouvrez HACS → Haptique RS90 → **Mettre à jour**
- **Manuelle** : téléchargez la [v1.9.0](https://github.com/daangel27/haptique_rs90/releases/tag/v1.9.0), remplacez `custom_components/haptique_rs90/`

Redémarrez ensuite Home Assistant et rafraîchissez le navigateur (Ctrl+F5). Pour profiter des nouveautés :
1. **Tableau de bord** : Paramètres → Tableaux de bord → Ajouter un tableau de bord → **Haptique RS90**
2. **Réveil** : Paramètres → Appareils et services → Haptique RS90 → **Configurer** → Réveiller la RS90

---

## 🙏 Remerciements

- **Claude** (Anthropic), binôme IA sur cette version : code, tests, revues et documentation
- [@ccs777](https://github.com/ccs777) / WillisD et **Haptique** pour le firmware Standard MQTT et leurs retours rapides

**Profitez bien de la v1.9.0 !** 🎉
