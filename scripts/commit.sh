#!/bin/sh
# Script de commit avec validation automatique

if [ -z "$1" ]; then
    echo "Usage: ./scripts/commit.sh \"message du commit\""
    echo ""
    echo "Exemples:"
    echo "  ./scripts/commit.sh \"fix: correction bug timeout\""
    echo "  ./scripts/commit.sh \"feat: ajout nouveau sensor\""
    echo "  ./scripts/commit.sh \"docs: mise à jour README\""
    exit 1
fi

echo "🔍 Validation avant commit..."
echo

# Vérifier qu'on n'est pas sur main
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
if [ "$BRANCH" = "main" ]; then
    echo "❌ Vous êtes sur la branche main!"
    echo "💡 Utilisez: git checkout dev"
    exit 1
fi

echo "📍 Branche: $BRANCH"
echo

# Lancer la validation
if [ -f "./scripts/validate.sh" ]; then
    if ! ./scripts/validate.sh; then
        echo
        echo "❌ Validation échouée"
        echo "💡 Corrigez les erreurs et réessayez"
        exit 1
    fi
else
    echo "⚠️  Script de validation non trouvé"
    echo "💡 Vérification basique..."
    
    if ! python3 -m json.tool custom_components/haptique_rs90/manifest.json > /dev/null 2>&1; then
        echo "❌ manifest.json invalide"
        exit 1
    fi
    
    echo "✅ Vérification basique OK"
fi

echo
echo "✅ Validation OK"
echo

# Afficher les fichiers modifiés
echo "📝 Fichiers à commiter:"
git status --short
echo

# Commit
echo "💾 Commit en cours..."
git add .
git commit -m "$1"

if [ $? -eq 0 ]; then
    echo
    echo "✅ Commit réussi!"
    echo "📍 Branche: $BRANCH"
    echo
    echo "💡 N'oubliez pas: git push"
else
    echo
    echo "❌ Erreur lors du commit"
    exit 1
fi
