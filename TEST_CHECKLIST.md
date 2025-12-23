# ✅ Checklist de Tests Manuels - Haptique RS90

## 📋 Avant chaque commit

### 🔧 Installation & Configuration
- [ ] L'intégration apparaît dans les intégrations disponibles
- [ ] La configuration MQTT fonctionne correctement
- [ ] Le RS90 est découvert automatiquement (auto-discovery)
- [ ] Toutes les entités sont créées sans erreur

### 📊 Sensors
- [ ] Les sensors `{remote_name}_commands_{device}` sont créés
- [ ] Les attributs contiennent la liste complète des commandes
- [ ] L'attribut `rs90_device_id` est présent et correct
- [ ] Les sensors `macro_{name}_info` sont créés pour chaque macro
- [ ] L'attribut `rs90_macro_id` est présent dans les sensors macros

### 🔘 Switches
- [ ] Un switch est créé pour chaque macro
- [ ] Switch ON déclenche correctement la macro
- [ ] Switch OFF déclenche correctement la macro
- [ ] L'état du switch se met à jour après déclenchement
- [ ] Les attributs du switch contiennent `rs90_macro_id`

### 🎮 Services
- [ ] Service `trigger_macro` fonctionne avec `rs90_macro_id`
- [ ] Service `trigger_macro` fonctionne avec `action` (on/off/toggle)
- [ ] Service `trigger_device_command` fonctionne avec `rs90_device_id`
- [ ] Service `trigger_device_command` envoie bien la commande
- [ ] Les erreurs sont gérées proprement (messages clairs)
- [ ] Les paramètres obsolètes affichent un warning

### 📡 MQTT
- [ ] Connexion MQTT établie au démarrage de HA
- [ ] Messages MQTT reçus du RS90 correctement parsés
- [ ] Messages MQTT envoyés au RS90 avec bon format
- [ ] Reconnexion automatique après perte de connexion
- [ ] QoS = 1 pour tous les messages
- [ ] Topics corrects (`/detail` pour requêtes, `/commands` pour réponses)

### 🔄 Renommage (Test critique)
- [ ] Renommer un device dans l'app Haptique Config
- [ ] L'entity_id reste identique dans HA
- [ ] Le friendly_name se met à jour automatiquement
- [ ] Aucune entité duplicate n'est créée
- [ ] Les services fonctionnent toujours avec la même entité

### 📝 Logs
- [ ] Aucune erreur au démarrage de HA
- [ ] Logs informatifs mais pas trop verbeux (niveau INFO)
- [ ] Warnings appropriés si problème de connexion
- [ ] Pas de stack trace en utilisation normale
- [ ] Debug logs disponibles si activés dans configuration.yaml

### 🔋 Battery & État
- [ ] Battery level sensor créé et mis à jour
- [ ] Battery level refresh toutes les 30 minutes
- [ ] État "online/offline" du RS90 détecté
- [ ] Gestion propre si RS90 hors ligne

---

## 🧪 Tests de régression (avant release)

### ✅ Compatibilité versions
- [ ] Fonctionne avec Home Assistant version actuelle (2024.12+)
- [ ] Fonctionne avec Home Assistant version N-1 (2024.11+)
- [ ] Compatible avec dernière version firmware RS90
- [ ] MQTT Broker : Mosquitto (version récente)

### ⚡ Performance
- [ ] Démarrage de l'intégration rapide (< 10 secondes)
- [ ] Pas de freeze de l'interface utilisateur
- [ ] Réponse rapide aux commandes (< 500ms)
- [ ] Pas de lag lors de multiples commandes rapides
- [ ] Utilisation mémoire raisonnable (< 50MB)

### 🔄 Migration depuis v1.2.x
- [ ] Migration automatique détecte ancienne configuration
- [ ] Pas de perte de configuration lors de la migration
- [ ] Entity IDs préservés après migration
- [ ] Messages de dépréciation affichés pour anciens paramètres
- [ ] Guide de migration disponible et clair

### 🌍 Multilingue
- [ ] Traductions FR complètes et correctes
- [ ] Traductions EN complètes et correctes
- [ ] Messages d'erreur traduits
- [ ] Interface config flow traduite

---

## 🚀 Tests d'intégration complète

### Scénario 1 : Installation fraîche
1. [ ] Supprimer l'intégration si existante
2. [ ] Redémarrer HA
3. [ ] Installer l'intégration
4. [ ] Configurer MQTT
5. [ ] Vérifier auto-discovery du RS90
6. [ ] Vérifier création de toutes les entités
7. [ ] Tester un service
8. [ ] Vérifier les logs (pas d'erreur)

### Scénario 2 : Mise à jour depuis v1.2.x
1. [ ] Installation v1.2.x fonctionnelle
2. [ ] Noter les entity IDs actuels
3. [ ] Mettre à jour vers v1.5.0
4. [ ] Redémarrer HA
5. [ ] Vérifier que les entity IDs sont préservés
6. [ ] Vérifier warnings sur paramètres obsolètes
7. [ ] Migrer vers nouveaux paramètres
8. [ ] Tester que tout fonctionne

### Scénario 3 : Utilisation intensive
1. [ ] Déclencher 10 macros en succession rapide
2. [ ] Envoyer 20 commandes devices diverses
3. [ ] Renommer 3 devices dans Haptique Config
4. [ ] Déconnecter/reconnecter MQTT
5. [ ] Redémarrer HA
6. [ ] Vérifier que tout est stable
7. [ ] Vérifier pas de memory leak

---

## 🐛 Tests de gestion d'erreurs

### Erreurs MQTT
- [ ] Broker MQTT down → Warning approprié
- [ ] Topic incorrect → Erreur loggée
- [ ] Message malformé → Erreur gérée, pas de crash
- [ ] Reconnexion après erreur → Fonctionne

### Erreurs configuration
- [ ] MQTT non configuré → Message clair
- [ ] Mauvais topic MQTT → Erreur claire
- [ ] RS90 non trouvé → Message informatif

### Erreurs services
- [ ] `rs90_macro_id` invalide → Erreur claire
- [ ] `rs90_device_id` invalide → Erreur claire
- [ ] `command_name` inexistant → Erreur claire
- [ ] Paramètre manquant → Erreur de validation

---

## 📊 Métriques qualité

### Code
- [ ] Pas de secrets hardcodés
- [ ] Pas de TODO/FIXME critiques
- [ ] Syntaxe Python correcte
- [ ] manifest.json valide
- [ ] Traductions JSON valides

### Documentation
- [ ] README à jour
- [ ] CHANGELOG à jour
- [ ] Guide de migration à jour (si breaking changes)
- [ ] Templates exemples fonctionnels

### CI/CD
- [ ] Tests GitHub Actions passent (✅)
- [ ] Hassfest validation OK
- [ ] HACS validation OK

---

## 💡 Checklist pour release

- [ ] Tous les tests manuels passent
- [ ] Tous les tests de régression OK
- [ ] Version incrémentée dans manifest.json
- [ ] CHANGELOG.md mis à jour
- [ ] README.md mis à jour si nécessaire
- [ ] Tests CI tous verts (✅)
- [ ] Tag Git créé
- [ ] Release GitHub publiée
- [ ] HACS mis à jour automatiquement

---

## 📝 Notes

**Dernière vérification** : _____________________  
**Version testée** : _____________________  
**Testeur** : _____________________  

**Problèmes trouvés** :
- 
- 
- 

**Améliorations suggérées** :
- 
- 
- 
