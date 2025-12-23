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