# Git Commands for v1.2.5 Release

## 📋 Pre-Release Checklist

- [ ] All files updated to version 1.2.5
- [ ] CHANGELOG.md and CHANGELOG_FR.md completed
- [ ] README.md and README_FR.md updated
- [ ] Package tested locally
- [ ] All documentation reviewed

---

## 🔧 Setup (First Time Only)

```bash
# Clone your repository
git clone https://github.com/daangel27/haptique_rs90.git
cd haptique_rs90

# Configure git (if not already done)
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

---

## 📦 Adding Files to Repository

### Extract the Integration

```bash
# Extract the package to the repository
tar -xzf haptique_rs90_v1.2.5.tar.gz

# Move to correct location
mv haptique_rs90_v1.2.5/* custom_components/haptique_rs90/
rmdir haptique_rs90_v1.2.5
```

### Add Documentation Files

```bash
# Copy all documentation files to repository root
cp CHANGELOG.md .
cp CHANGELOG_FR.md .
cp README.md .
cp README_FR.md .
cp WHATS_NEW.md .
cp WHATS_NEW_FR.md .
cp RELEASE_v1.2.5.md .
cp GUIDE_DEVICE_ID.md .
cp ICON_GUIDE.md .
cp hacs.json .
cp icon.png .
cp .gitignore .
cp LICENSE .
```

---

## 🎯 Git Commands

### 1. Check Status

```bash
# See what files have changed
git status
```

### 2. Add All Files

```bash
# Add all changes
git add .

# Or add specific files
git add custom_components/haptique_rs90/
git add README.md README_FR.md
git add CHANGELOG.md CHANGELOG_FR.md
git add WHATS_NEW.md WHATS_NEW_FR.md
git add hacs.json icon.png
git add .gitignore LICENSE
```

### 3. Commit Changes

```bash
# Commit with descriptive message
git commit -m "Release v1.2.5 - Event-driven architecture

Major changes:
- 100% event-driven updates (removed polling)
- Device command sensors added
- Multi-language support (EN/FR)
- Visual improvements (colors, icons)
- MQTT protocol optimization (QoS)
- Bug fixes (random triggers, subscription leaks)
- Removed: refresh_data, get_diagnostics services
- Removed: refresh button, scan interval slider

Breaking changes documented in CHANGELOG.md"
```

### 4. Create and Push Tag

```bash
# Create annotated tag
git tag -a v1.2.5 -m "Release v1.2.5 - Event-driven architecture

🎉 Major Update: From Polling to 100% Event-Driven

Key features:
- Instant MQTT updates
- Device command sensors
- Multi-language (EN/FR)
- Visual improvements
- QoS optimization
- Critical bug fixes

See CHANGELOG.md and WHATS_NEW.md for complete details."

# Push commits
git push origin main

# Push tags
git push origin v1.2.5
```

---

## 🎨 Create GitHub Release

### Option 1: Via GitHub Web Interface

1. Go to https://github.com/daangel27/haptique_rs90/releases
2. Click "Draft a new release"
3. Choose tag: `v1.2.5`
4. Release title: `v1.2.5 - Event-Driven Architecture`
5. Description: Copy content from `WHATS_NEW.md`
6. Attach file: `haptique_rs90_v1.2.5.tar.gz`
7. Click "Publish release"

### Option 2: Via GitHub CLI (if installed)

```bash
# Install GitHub CLI if needed
# https://cli.github.com/

# Create release
gh release create v1.2.5 \
  --title "v1.2.5 - Event-Driven Architecture" \
  --notes-file WHATS_NEW.md \
  haptique_rs90_v1.2.5.tar.gz
```

---

## 🔄 Update Existing Repository

If you already have the repository cloned:

```bash
# Navigate to repository
cd ~/haptique_rs90

# Pull latest changes
git pull origin main

# Check current status
git status

# Continue with adding files...
```

---

## 🌿 Branch Strategy (Optional)

If you want to use a develop branch:

```bash
# Create and switch to develop branch
git checkout -b develop

# Make your changes
# ... add files ...

# Commit to develop
git commit -m "Prepare v1.2.5"

# Switch back to main
git checkout main

# Merge develop into main
git merge develop

# Push both branches
git push origin main
git push origin develop

# Tag and release
git tag -a v1.2.5 -m "Release v1.2.5"
git push origin v1.2.5
```

---

## ❌ Undo Commands (If Needed)

### Undo Last Commit (Keep Changes)

```bash
git reset --soft HEAD~1
```

### Undo Last Commit (Discard Changes)

```bash
git reset --hard HEAD~1
```

### Delete Local Tag

```bash
git tag -d v1.2.5
```

### Delete Remote Tag

```bash
git push origin :refs/tags/v1.2.5
```

### Discard All Local Changes

```bash
git reset --hard HEAD
git clean -fd
```

---

## 📊 Verify Everything

### Check Git Status

```bash
# Should show "nothing to commit, working tree clean"
git status
```

### Check Tags

```bash
# Should show v1.2.5
git tag
```

### Check Remote

```bash
# Should show your GitHub URL
git remote -v
```

### View Commit Log

```bash
# Should show your release commit
git log --oneline -5
```

---

## 🎯 Quick Complete Workflow

```bash
# 1. Navigate to repository
cd ~/haptique_rs90

# 2. Extract and copy files
tar -xzf ~/Downloads/haptique_rs90_v1.2.5.tar.gz
cp -r haptique_rs90_v1.2.5/* custom_components/haptique_rs90/
rm -rf haptique_rs90_v1.2.5

# Copy documentation
cp ~/Downloads/README*.md .
cp ~/Downloads/CHANGELOG*.md .
cp ~/Downloads/WHATS_NEW*.md .
cp ~/Downloads/RELEASE_v1.2.5.md .
cp ~/Downloads/GUIDE_DEVICE_ID.md .
cp ~/Downloads/ICON_GUIDE.md .
cp ~/Downloads/hacs.json .
cp ~/Downloads/icon.png .

# 3. Add, commit, and push
git add .
git status  # Review changes
git commit -m "Release v1.2.5 - Event-driven architecture"
git push origin main

# 4. Create and push tag
git tag -a v1.2.5 -m "Release v1.2.5"
git push origin v1.2.5

# 5. Create GitHub release (via web interface or gh cli)
```

---

## 🔍 Troubleshooting

### Authentication Issues

```bash
# Use SSH instead of HTTPS
git remote set-url origin git@github.com:daangel27/haptique_rs90.git

# Or use personal access token
# Generate at: https://github.com/settings/tokens
```

### Large File Warning

```bash
# If haptique_rs90_v1.2.5.tar.gz is too large for git
# Don't commit it to the repository
# Only attach it to the GitHub release
git rm --cached haptique_rs90_v1.2.5.tar.gz
echo "*.tar.gz" >> .gitignore
git add .gitignore
git commit -m "Don't track tar.gz files"
```

### Merge Conflicts

```bash
# If you have merge conflicts
git status  # See conflicted files
# Edit files to resolve conflicts
git add <resolved-files>
git commit -m "Resolved merge conflicts"
```

---

## ✅ Final Verification

After pushing everything:

1. Visit https://github.com/daangel27/haptique_rs90
2. Verify all files are present
3. Check that README.md displays correctly
4. Verify icon.png is visible
5. Check releases page for v1.2.5
6. Test HACS installation

---

**Ready to Release!** 🚀
