# 🧪 Système de Tests - Haptique RS90

## 📋 Vue d'ensemble

Votre système de tests à 3 niveaux :

```
┌─────────────────────────────────────────┐
│ NIVEAU 1 : Tests manuels (Checklist)   │ ← Vous testez à la main
├─────────────────────────────────────────┤
│ NIVEAU 2 : Validation automatique      │ ← Scripts locaux
│            (formatage, linting, etc.)   │
├─────────────────────────────────────────┤
│ NIVEAU 3 : Tests CI/CD GitHub Actions  │ ← Automatique sur push
│            (pytest, hassfest, HACS)     │
└─────────────────────────────────────────┘
```

---

## 🚀 NIVEAU 1 : Tests manuels

### Checklist de test (à faire avant chaque commit)

Créez : `/config/haptique_rs90_dev/TEST_CHECKLIST.md`

```markdown
# ✅ Checklist de Tests Manuels

## Avant chaque commit

### Installation & Configuration
- [ ] L'intégration apparaît dans Intégrations
- [ ] La configuration MQTT fonctionne
- [ ] Le RS90 est découvert automatiquement
- [ ] Les entités sont créées

### Sensors
- [ ] Les sensors `commands_{device}` sont créés
- [ ] Les attributs contiennent les bonnes commandes
- [ ] L'attribut `rs90_device_id` est présent
- [ ] Les sensors macros `macro_{name}_info` sont créés

### Switches
- [ ] Les switches macros sont créés
- [ ] Switch ON déclenche la macro
- [ ] Switch OFF déclenche la macro
- [ ] L'état du switch se met à jour

### Services
- [ ] `trigger_macro` fonctionne avec rs90_macro_id
- [ ] `trigger_device_command` fonctionne avec rs90_device_id
- [ ] Les erreurs sont gérées proprement

### MQTT
- [ ] Connexion MQTT établie au démarrage
- [ ] Messages reçus du RS90
- [ ] Messages envoyés au RS90
- [ ] Reconnexion automatique si déconnexion

### Renommage (Test important)
- [ ] Renommer un device dans Haptique Config
- [ ] L'entité garde son entity_id
- [ ] Le friendly_name se met à jour
- [ ] Pas de duplicate d'entité

### Logs
- [ ] Aucune erreur au démarrage
- [ ] Logs informatifs (pas trop verbeux)
- [ ] Warnings appropriés si problème

## Tests de régression (avant release)

### Compatibilité
- [ ] Fonctionne avec HA version N (actuelle)
- [ ] Fonctionne avec HA version N-1
- [ ] Compatible avec dernière version RS90 firmware

### Performance
- [ ] Démarrage rapide (< 10s)
- [ ] Pas de freeze de l'UI
- [ ] Réponse rapide aux commandes (< 500ms)

### Migration
- [ ] Migration depuis v1.2.x fonctionne
- [ ] Pas de perte de configuration
- [ ] Messages de dépréciation affichés
```

---

## 🔍 NIVEAU 2 : Validation locale (Scripts)

### Script 1 : Validation du code

Créez : `/config/haptique_rs90_dev/scripts/validate.sh`

```bash
#!/bin/sh
# Script de validation - À lancer avant chaque commit

echo "🔍 Haptique RS90 - Validation du code"
echo "======================================"
echo

# Compteur d'erreurs
ERRORS=0

# 1. Vérifier la structure
echo "📁 Vérification de la structure..."
REQUIRED_FILES=(
    "custom_components/haptique_rs90/__init__.py"
    "custom_components/haptique_rs90/manifest.json"
    "custom_components/haptique_rs90/coordinator.py"
    "custom_components/haptique_rs90/sensor.py"
    "custom_components/haptique_rs90/switch.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Fichier manquant: $file"
        ERRORS=$((ERRORS + 1))
    fi
done

if [ $ERRORS -eq 0 ]; then
    echo "✅ Structure OK"
fi
echo

# 2. Vérifier manifest.json
echo "📋 Vérification manifest.json..."
MANIFEST="custom_components/haptique_rs90/manifest.json"

if [ -f "$MANIFEST" ]; then
    # Vérifier que c'est du JSON valide
    if ! python3 -m json.tool "$MANIFEST" > /dev/null 2>&1; then
        echo "❌ manifest.json n'est pas du JSON valide"
        ERRORS=$((ERRORS + 1))
    else
        echo "✅ manifest.json valide"
        
        # Afficher la version
        VERSION=$(grep -o '"version": *"[^"]*"' "$MANIFEST" | cut -d'"' -f4)
        echo "   Version: $VERSION"
    fi
else
    echo "❌ manifest.json manquant"
    ERRORS=$((ERRORS + 1))
fi
echo

# 3. Vérifier les imports Python (basique)
echo "🐍 Vérification imports Python..."
for pyfile in custom_components/haptique_rs90/*.py; do
    if [ -f "$pyfile" ]; then
        # Vérifier syntaxe Python
        if ! python3 -m py_compile "$pyfile" 2>/dev/null; then
            echo "❌ Erreur de syntaxe: $pyfile"
            ERRORS=$((ERRORS + 1))
        fi
    fi
done

if [ $ERRORS -eq 0 ]; then
    echo "✅ Syntaxe Python OK"
fi
echo

# 4. Vérifier qu'il n'y a pas de secrets hardcodés
echo "🔒 Vérification sécurité..."
SECURITY_PATTERNS=(
    "password.*=.*['\"]"
    "token.*=.*['\"]"
    "api_key.*=.*['\"]"
    "secret.*=.*['\"]"
)

for pattern in "${SECURITY_PATTERNS[@]}"; do
    if grep -r -i -E "$pattern" custom_components/haptique_rs90/*.py 2>/dev/null | grep -v "# "; then
        echo "⚠️  Possible secret hardcodé trouvé"
        ERRORS=$((ERRORS + 1))
    fi
done

if [ $ERRORS -eq 0 ]; then
    echo "✅ Pas de secret détecté"
fi
echo

# 5. Vérifier les TODOs
echo "📝 Vérification TODOs..."
TODO_COUNT=$(grep -r "TODO\|FIXME\|XXX" custom_components/haptique_rs90/*.py 2>/dev/null | wc -l)
if [ $TODO_COUNT -gt 0 ]; then
    echo "ℹ️  $TODO_COUNT TODO(s) trouvé(s)"
    grep -r -n "TODO\|FIXME\|XXX" custom_components/haptique_rs90/*.py 2>/dev/null | head -5
else
    echo "✅ Pas de TODO"
fi
echo

# Résultat final
echo "======================================"
if [ $ERRORS -eq 0 ]; then
    echo "✅ Validation réussie!"
    echo "💡 Prêt à commiter"
    exit 0
else
    echo "❌ $ERRORS erreur(s) détectée(s)"
    echo "💡 Corrigez les erreurs avant de commiter"
    exit 1
fi
```

**Rendre exécutable** :
```bash
chmod +x /config/haptique_rs90_dev/scripts/validate.sh
```

---

### Script 2 : Vérification pre-commit

Créez : `/config/haptique_rs90_dev/scripts/pre-commit-check.sh`

```bash
#!/bin/sh
# Vérifications rapides avant commit

echo "🚦 Pre-commit checks..."

# 1. Vérifier qu'on n'est pas sur main
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" = "main" ]; then
    echo "❌ Vous êtes sur main!"
    echo "💡 Utilisez: git checkout dev"
    exit 1
fi

# 2. Vérifier manifest.json
if ! python3 -m json.tool custom_components/haptique_rs90/manifest.json > /dev/null 2>&1; then
    echo "❌ manifest.json invalide"
    exit 1
fi

# 3. Vérifier syntaxe Python
for pyfile in custom_components/haptique_rs90/*.py; do
    if [ -f "$pyfile" ]; then
        if ! python3 -m py_compile "$pyfile" 2>/dev/null; then
            echo "❌ Erreur syntaxe: $pyfile"
            exit 1
        fi
    fi
done

echo "✅ Pre-commit OK"
exit 0
```

**Rendre exécutable** :
```bash
chmod +x /config/haptique_rs90_dev/scripts/pre-commit-check.sh
```

---

### Script 3 : Script de commit avec validation

Créez : `/config/haptique_rs90_dev/scripts/commit.sh`

```bash
#!/bin/sh
# Script de commit avec validation automatique

if [ -z "$1" ]; then
    echo "Usage: ./scripts/commit.sh \"message du commit\""
    exit 1
fi

echo "🔍 Validation avant commit..."
echo

# Lancer la validation
if ! ./scripts/pre-commit-check.sh; then
    echo
    echo "❌ Validation échouée"
    echo "💡 Corrigez les erreurs et réessayez"
    exit 1
fi

echo
echo "✅ Validation OK"
echo

# Afficher les fichiers modifiés
echo "📝 Fichiers à commiter:"
git status --short
echo

# Demander confirmation
echo "Continuer avec le commit? (y/n)"
read -r CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "❌ Commit annulé"
    exit 0
fi

# Commit
git add .
git commit -m "$1"

if [ $? -eq 0 ]; then
    echo
    echo "✅ Commit réussi!"
    echo "💡 N'oubliez pas: git push"
else
    echo
    echo "❌ Erreur lors du commit"
    exit 1
fi
```

**Rendre exécutable** :
```bash
chmod +x /config/haptique_rs90_dev/scripts/commit.sh
```

**Utilisation** :
```bash
./scripts/commit.sh "fix: correction bug timeout"
```

---

## 🤖 NIVEAU 3 : Tests CI/CD GitHub Actions

### Workflow 1 : Tests complets

Créez : `/config/haptique_rs90_dev/.github/workflows/tests.yml`

```yaml
name: Tests

on:
  push:
    branches: [dev, main]
  pull_request:
    branches: [dev, main]

jobs:
  validate:
    name: Validation
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Validate manifest.json
        run: |
          python3 -m json.tool custom_components/haptique_rs90/manifest.json

      - name: Check Python syntax
        run: |
          for file in custom_components/haptique_rs90/*.py; do
            python3 -m py_compile "$file"
          done

  hassfest:
    name: Hassfest
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Hassfest validation
        uses: home-assistant/actions/hassfest@master

  hacs:
    name: HACS Validation
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: HACS validation
        uses: hacs/action@main
        with:
          category: integration
```

---

### Workflow 2 : Validation rapide sur dev

Créez : `/config/haptique_rs90_dev/.github/workflows/quick-check.yml`

```yaml
name: Quick Check

on:
  push:
    branches: [dev]

jobs:
  quick-check:
    name: Quick validation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check structure
        run: |
          test -f custom_components/haptique_rs90/__init__.py
          test -f custom_components/haptique_rs90/manifest.json
          test -f custom_components/haptique_rs90/coordinator.py
          echo "✅ Structure OK"

      - name: Validate JSON
        run: |
          python3 -m json.tool custom_components/haptique_rs90/manifest.json > /dev/null
          echo "✅ manifest.json valid"

      - name: Extract version
        run: |
          VERSION=$(grep -o '"version": *"[^"]*"' custom_components/haptique_rs90/manifest.json | cut -d'"' -f4)
          echo "Version: $VERSION"
```

---

### Workflow 3 : Protection main (empêche push direct)

Créez : `/config/haptique_rs90_dev/.github/workflows/protect-main.yml`

```yaml
name: Protect Main

on:
  push:
    branches: [main]

jobs:
  check-direct-push:
    name: Block direct push to main
    runs-on: ubuntu-latest
    steps:
      - name: Check if from PR
        run: |
          if [ "${{ github.event.head_commit.author.name }}" != "GitHub" ]; then
            echo "❌ Direct push to main is not allowed!"
            echo "💡 Create a PR from dev instead"
            exit 1
          fi
```

---

## 📊 Dashboard de qualité (Badges GitHub)

Ajoutez dans votre `README.md` :

```markdown
# Haptique RS90

[![Tests](https://github.com/daangel27/haptique_rs90/workflows/Tests/badge.svg)](https://github.com/daangel27/haptique_rs90/actions)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Version](https://img.shields.io/github/v/release/daangel27/haptique_rs90)](https://github.com/daangel27/haptique_rs90/releases)

...
```

---

## 🎯 Workflow complet de développement avec tests

```bash
# 1. Créer une feature
git checkout -b feature/nouvelle-feature

# 2. Développer
# WinSCP: Éditer les fichiers

# 3. Déployer et tester manuellement
./scripts/deploy.sh
# Tester dans HA

# 4. Validation locale
./scripts/validate.sh

# 5. Commit avec validation
./scripts/commit.sh "feat: nouvelle feature"

# 6. Push
git push -u origin feature/nouvelle-feature

# 7. Sur GitHub
# - Tests CI se lancent automatiquement
# - Vérifier que tout est vert ✅
# - Créer Pull Request vers dev

# 8. Après merge
git checkout dev
git pull
```

---

## 📋 Installation des scripts

### Tout en une fois

```bash
cd /config/haptique_rs90_dev

# Créer les scripts
mkdir -p scripts .github/workflows

# Rendre exécutables
chmod +x scripts/*.sh

# Tester la validation
./scripts/validate.sh
```

---

## ✅ Checklist setup tests

- [ ] Script `validate.sh` créé et testé
- [ ] Script `pre-commit-check.sh` créé
- [ ] Script `commit.sh` créé
- [ ] Workflows GitHub Actions créés
- [ ] Protection de la branche main activée sur GitHub
- [ ] Badges ajoutés au README (optionnel)
- [ ] Première validation passée

---

## 🎓 Utilisation quotidienne

### Avant chaque commit

```bash
# Validation complète
./scripts/validate.sh

# OU commit avec validation automatique
./scripts/commit.sh "fix: correction bug"
```

### Vérifier les tests CI

Après un push, allez sur :
```
https://github.com/daangel27/haptique_rs90/actions
```

Vous verrez les workflows en cours d'exécution avec ✅ ou ❌

---

**Prêt à créer les scripts ?** Je vous guide étape par étape ! 🚀
