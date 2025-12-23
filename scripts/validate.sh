#!/bin/sh
# Script de validation - À lancer avant chaque commit

echo "🔍 Haptique RS90 - Validation du code"
echo "======================================"
echo

# Compteur d'erreurs
ERRORS=0

# 1. Vérifier la structure
echo "📁 Vérification de la structure..."

check_file() {
    if [ ! -f "$1" ]; then
        echo "❌ Fichier manquant: $1"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
    return 0
}

check_file "custom_components/haptique_rs90/__init__.py"
check_file "custom_components/haptique_rs90/manifest.json"
check_file "custom_components/haptique_rs90/coordinator.py"
check_file "custom_components/haptique_rs90/sensor.py"
check_file "custom_components/haptique_rs90/switch.py"
check_file "custom_components/haptique_rs90/config_flow.py"
check_file "custom_components/haptique_rs90/const.py"

if [ $ERRORS -eq 0 ]; then
    echo "✅ Structure OK"
fi
echo

# 2. Vérifier manifest.json
echo "📋 Vérification manifest.json..."
MANIFEST="custom_components/haptique_rs90/manifest.json"

if [ -f "$MANIFEST" ]; then
    if ! python3 -m json.tool "$MANIFEST" > /dev/null 2>&1; then
        echo "❌ manifest.json n'est pas du JSON valide"
        ERRORS=$((ERRORS + 1))
    else
        VERSION=$(grep -o '"version": *"[^"]*"' "$MANIFEST" | cut -d'"' -f4)
        DOMAIN=$(grep -o '"domain": *"[^"]*"' "$MANIFEST" | cut -d'"' -f4)
        NAME=$(grep -o '"name": *"[^"]*"' "$MANIFEST" | cut -d'"' -f4)
        
        echo "✅ manifest.json valide"
        echo "   Nom: $NAME"
        echo "   Domaine: $DOMAIN"
        echo "   Version: $VERSION"
        
        if [ -z "$VERSION" ] || [ -z "$DOMAIN" ] || [ -z "$NAME" ]; then
            echo "❌ Champs manquants dans manifest.json"
            ERRORS=$((ERRORS + 1))
        fi
    fi
else
    echo "❌ manifest.json manquant"
    ERRORS=$((ERRORS + 1))
fi
echo

# 3. Vérifier syntaxe Python
echo "🐍 Vérification syntaxe Python..."
PYTHON_ERRORS=0

for pyfile in custom_components/haptique_rs90/*.py; do
    if [ -f "$pyfile" ]; then
        if ! python3 -m py_compile "$pyfile" 2>/dev/null; then
            echo "❌ Erreur de syntaxe: $(basename $pyfile)"
            PYTHON_ERRORS=$((PYTHON_ERRORS + 1))
            ERRORS=$((ERRORS + 1))
        fi
    fi
done

if [ $PYTHON_ERRORS -eq 0 ]; then
    echo "✅ Syntaxe Python OK"
fi
echo

# 4. Vérifier traductions
if [ -d "custom_components/haptique_rs90/translations" ]; then
    echo "🌍 Vérification traductions..."
    TRANS_ERRORS=0
    for lang_file in custom_components/haptique_rs90/translations/*.json; do
        if [ -f "$lang_file" ]; then
            if ! python3 -m json.tool "$lang_file" > /dev/null 2>&1; then
                echo "❌ JSON invalide: $(basename $lang_file)"
                TRANS_ERRORS=$((TRANS_ERRORS + 1))
                ERRORS=$((ERRORS + 1))
            fi
        fi
    done
    if [ $TRANS_ERRORS -eq 0 ]; then
        echo "✅ Traductions OK"
    fi
    echo
fi

# Résultat final
echo "======================================"
if [ $ERRORS -eq 0 ]; then
    echo "✅ Validation réussie! ($VERSION)"
    echo "💡 Prêt à commiter"
    exit 0
else
    echo "❌ $ERRORS erreur(s) détectée(s)"
    echo "💡 Corrigez les erreurs avant de commiter"
    exit 1
fi
