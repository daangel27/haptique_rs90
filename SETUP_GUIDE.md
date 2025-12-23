# 🛠️ Guide d'installation - Environnement de développement Haptique RS90

## 📋 Prérequis

✅ Home Assistant OS installé (votre instance de dev)  
✅ Add-on "Studio Code Server" installé  
✅ Add-on "Mosquitto broker" installé (pour MQTT)  
✅ Git installé dans VSCode Server  

---

## 🚀 Installation rapide (10 minutes)

### 1. Cloner le repo dans VSCode Server

Ouvrez le terminal dans VSCode Server :

```bash
cd /config
git clone https://github.com/daangel27/haptique_rs90.git haptique_rs90_dev
cd haptique_rs90_dev
```

### 2. Installer les dépendances de test

```bash
pip install -r requirements_test.txt
```

### 3. Copier la structure de dev

```bash
# Copier les fichiers de configuration
cp -r .vscode /config/
cp -r scripts /config/
cp -r tests /config/
cp pytest.ini /config/
cp requirements_test.txt /config/

# Rendre les scripts exécutables
chmod +x scripts/*.sh
```

### 4. Configurer l'intégration dans HA

```bash
# Déployer vers votre HA de dev
./scripts/deploy.sh
```

### 5. Configurer l'intégration

1. Allez sur votre HA : `http://votre-ha:8123`
2. **Settings** → **Devices & Services** → **Add Integration**
3. Cherchez "Haptique RS90"
4. Suivez la configuration

---

## 🔧 Workflow de développement

### Modifier le code

```bash
# 1. Créer une branche
git checkout -b feature/ma-nouvelle-feature

# 2. Modifier le code dans VSCode Server
# Éditer : custom_components/haptique_rs90/...

# 3. Lancer les tests
./scripts/test.sh

# 4. Déployer vers HA de dev
./scripts/deploy.sh

# 5. Tester manuellement dans HA

# 6. Commit
git add .
git commit -m "feat: Description de la feature"

# 7. Push
git push origin feature/ma-nouvelle-feature
```

### Tests automatisés

```bash
# Tous les tests
./scripts/test.sh

# Tests unitaires seulement
pytest tests/unit/ -v

# Tests avec couverture
pytest tests/ --cov=custom_components.haptique_rs90 --cov-report=html

# Test spécifique
pytest tests/unit/test_coordinator.py::test_coordinator_initialization -v

# Test en mode debug
pytest tests/unit/test_coordinator.py -v -s --pdb
```

### Déploiement

```bash
# Déploiement simple
./scripts/deploy.sh

# Déploiement + watch logs
./scripts/deploy.sh --watch-logs

# Déploiement manuel
cp -r custom_components/haptique_rs90 /config/custom_components/
ha core restart
```

---

## 🐛 Debug dans VSCode

### Setup (une seule fois)

Ajoutez dans `configuration.yaml` de votre HA de dev :

```yaml
# Enable debugpy for VSCode
debugpy:
  start: true
  wait: false
  port: 5678
```

Redémarrez HA.

### Utilisation

1. Dans VSCode Server, ouvrez le fichier à débugger
2. Mettez des breakpoints (cliquez à gauche du numéro de ligne)
3. Appuyez sur **F5** ou menu **Run** → **Start Debugging**
4. Choisissez **"Python: Home Assistant"**
5. Déclenchez l'action dans HA (ex: appeler un service)
6. Le code s'arrête sur vos breakpoints !

**Vous pouvez** :
- ✅ Inspecter les variables
- ✅ Voir la call stack
- ✅ Exécuter du code dans la console
- ✅ Avancer pas à pas (F10, F11)

---

## 📊 Structure des tests

### Tests unitaires (`tests/unit/`)

Testent des fonctions isolées :

```python
# tests/unit/test_coordinator.py
@pytest.mark.unit
async def test_async_trigger_macro(hass, coordinator):
    """Test triggering a macro."""
    await coordinator.async_trigger_macro("Movie", "on")
    assert coordinator.data["last_macro"] == "Movie"
```

### Tests d'intégration (`tests/integration/`)

Testent plusieurs composants ensemble :

```python
# tests/integration/test_mqtt_flow.py
@pytest.mark.integration
async def test_full_mqtt_flow(hass, mqtt_mock):
    """Test complete MQTT communication flow."""
    # Setup integration
    # Send MQTT message
    # Verify entities created
    # Trigger service
    # Verify MQTT publish
```

### Fixtures (`tests/fixtures/`)

Données de test réutilisables :

```python
# tests/fixtures/mqtt_messages.py
MOCK_DEVICES_LIST = {
    "devices": [
        {"name": "TV", "id": "dev1", "type": "IR"},
        {"name": "Soundbar", "id": "dev2", "type": "IR"}
    ]
}
```

---

## 🔍 Commandes utiles

### Tests

```bash
# Tests rapides (sans coverage)
pytest tests/ -v

# Tests avec markers
pytest -m unit          # Seulement tests unitaires
pytest -m integration   # Seulement tests intégration
pytest -m "not slow"    # Exclure tests lents

# Tests en parallèle (plus rapide)
pytest tests/ -n auto

# Watch mode (re-run sur changement)
pytest-watch tests/
```

### Code quality

```bash
# Formatage automatique
black custom_components/haptique_rs90/ tests/

# Check formatting
black --check custom_components/haptique_rs90/

# Linting
flake8 custom_components/haptique_rs90/

# Type checking
mypy custom_components/haptique_rs90/

# Tout en un
./scripts/test.sh
```

### Git

```bash
# Status
git status

# Créer branche
git checkout -b feature/nom

# Voir les changements
git diff

# Commit
git add .
git commit -m "type: description"

# Push
git push origin feature/nom

# Revenir à main
git checkout main
git pull
```

---

## 📁 Structure des fichiers

```
/config/
├── custom_components/
│   └── haptique_rs90/          # ← Code de l'intégration
│       ├── __init__.py
│       ├── coordinator.py
│       ├── sensor.py
│       ├── switch.py
│       └── ...
├── tests/                       # ← Tests
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── scripts/                     # ← Scripts utilitaires
│   ├── test.sh
│   ├── deploy.sh
│   └── validate.sh
├── .vscode/                     # ← Config VSCode
│   ├── settings.json
│   └── launch.json
├── pytest.ini                   # ← Config pytest
├── requirements_test.txt        # ← Dépendances tests
└── configuration.yaml           # ← Config HA
```

---

## 🎯 Bonnes pratiques

### Commits

Utilisez les préfixes conventionnels :

```
feat: Nouvelle fonctionnalité
fix: Correction de bug
docs: Documentation
test: Ajout/modification tests
refactor: Refactoring (sans changement fonctionnel)
chore: Maintenance (deps, config, etc.)
```

### Tests

- ✅ Écrivez un test **avant** le code (TDD)
- ✅ Un test = une chose testée
- ✅ Noms de tests descriptifs
- ✅ Utilisez des fixtures pour les données communes
- ✅ Mockez les dépendances externes (MQTT, HA, etc.)

### Code

- ✅ Formatez avec `black` avant commit
- ✅ Utilisez les type hints
- ✅ Commentez le "pourquoi", pas le "quoi"
- ✅ Fonctions courtes et focused
- ✅ Noms explicites

---

## 🚀 CI/CD avec GitHub Actions

Les tests se lancent automatiquement sur chaque push/PR :

1. **Tests** - Python 3.11 et 3.12
2. **Formatage** - Black check
3. **Linting** - Flake8
4. **Type checking** - Mypy
5. **Hassfest** - Validation HA officielle
6. **HACS** - Validation HACS

Voir les résultats : https://github.com/daangel27/haptique_rs90/actions

---

## 📊 Coverage

Après `./scripts/test.sh`, ouvrez :

```
htmlcov/index.html
```

Objectif : **> 80% coverage**

- 🟢 > 80% : Excellent
- 🟡 60-80% : Bon
- 🔴 < 60% : À améliorer

---

## 🆘 Problèmes courants

### Tests échouent avec "ModuleNotFoundError"

```bash
# Réinstaller les dépendances
pip install -r requirements_test.txt
```

### HA ne redémarre pas

```bash
# Vérifier les logs
tail -f /config/home-assistant.log

# Redémarrer manuellement
ha core restart
```

### VSCode debugger ne se connecte pas

Vérifiez dans `configuration.yaml` :

```yaml
debugpy:
  start: true
  port: 5678
```

Redémarrez HA et réessayez.

### Import errors dans les tests

Ajoutez à `conftest.py` :

```python
import sys
sys.path.insert(0, "/config/custom_components")
```

---

## 📚 Ressources

- **Home Assistant Dev Docs** : https://developers.home-assistant.io/
- **Pytest Documentation** : https://docs.pytest.org/
- **Black Documentation** : https://black.readthedocs.io/
- **Type Hints (Python)** : https://docs.python.org/3/library/typing.html

---

## 🎉 Vous êtes prêt !

Votre environnement de dev est configuré. Vous pouvez maintenant :

✅ Modifier le code dans VSCode Server  
✅ Tester automatiquement  
✅ Débugger en live  
✅ Déployer instantanément  
✅ Pusher vers GitHub avec CI/CD  

**Happy coding!** 🚀
