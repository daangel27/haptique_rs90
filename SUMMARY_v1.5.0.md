# Haptique RS90 v1.5.0 - Release Summary

**Release Date**: December 17, 2025  
**Type**: Major Feature Release  
**Status**: ✅ Production Ready

---

## 📦 Quick Info

- **Version**: 1.5.0
- **Previous Version**: 1.2.8
- **Breaking Changes**: None (100% backwards compatible)
- **Migration Required**: No (optional but recommended)
- **Package Size**: 941 KB

---

## 🎯 TL;DR

This release makes your entities **ultra-stable** and introduces **rename-proof** service parameters.

**Key benefit**: Rename devices/macros in Haptique Config → Everything still works in Home Assistant. No broken automations, no manual fixes.

---

## ✨ What's New (3 Main Features)

### 1. Stable Entities 🎯

**Before**: Entity IDs changed when you renamed devices  
**Now**: Entity IDs stay stable, friendly names update automatically

### 2. New Service Parameters 🔧

**Before**: `macro_name: "Watch Movie"` (can change)  
**Now**: `macro_id: "692eb..."` (never changes)

### 3. Professional Logs 📝

**Before**: Emojis in logs (📥, ✓, 🔄)  
**Now**: Clean text (MQTT, SUCCESS, RENAME)

---

## 🔄 Do I Need to Update My Code?

### Short Answer

**No!** Everything works as-is.

### Long Answer

**Should you migrate?** Yes, when convenient.

**Why?** Better stability, rename-proof automations.

**How?** Replace `macro_name` with `macro_id` in automations.

---

## 📊 Comparison

| What | v1.2.8 | v1.5.0 |
|------|--------|--------|
| **Unique IDs** | Name-based | ID-based ✅ |
| **Rename handling** | Manual | Automatic ✅ |
| **Service params** | Names only | IDs + names ✅ |
| **Logs** | Emojis | Text ✅ |
| **Breaking changes** | N/A | None ✅ |

---

## 📋 Files Updated

### Core (8 files)
- `coordinator.py` - Professional logging
- `sensor.py` - Stable IDs + rename detection
- `switch.py` - Stable IDs + rename detection
- `services.yaml` - New parameters
- `services.fr.yaml` - French translations
- `manifest.json` - Version 1.5.0
- `translations/en.json` - Service descriptions
- `translations/fr.json` - Service descriptions

### Documentation (8 files)
- `CHANGELOG.md` - New v1.5.0 section
- `CHANGELOG_FR.md` - French version
- `WHATS_NEW.md` - User guide
- `WHATS_NEW_FR.md` - French guide
- `README.md` - Updated badges
- `README_FR.md` - Updated badges
- `INDEX.md` - Updated index
- `RELEASE_v1.5.0.md` - This release doc

### Templates (4 files)
- `templates/device_buttons_card.yaml` - Uses `haptique_device_id`
- `templates/example_canal_plus.yaml` - Updated example
- `templates/README.md` - Migration guide
- `templates/README_FR.md` - French guide

### New Files (4 files)
- `RELEASE_v1.5.0.md` - Release documentation
- `SUMMARY_v1.5.0.md` - This file
- `WHATS_NEW.md` - User what's new
- `WHATS_NEW_FR.md` - French what's new

**Total**: 24 files updated/created

---

## 🚀 Installation

### Via HACS (Recommended)
```bash
1. HACS > Integrations
2. Search "Haptique RS90"
3. Update to v1.5.0
4. Restart Home Assistant
```

### Manual
```bash
1. Download haptique_rs90_v1.5.0_FINAL.tar.gz
2. Extract to custom_components/
3. Restart Home Assistant
```

---

## ✅ Testing Checklist

- [ ] Install v1.5.0
- [ ] Verify existing automations work
- [ ] Rename a device in Haptique Config
- [ ] Check friendly name updates in HA
- [ ] Test service with new `macro_id` parameter
- [ ] Check logs for clean text (no emojis)

---

## 📖 Documentation

### User Guides
- **[WHATS_NEW.md](WHATS_NEW.md)** - What's new and how to migrate
- **[CHANGELOG.md](CHANGELOG.md)** - Detailed changelog
- **[README.md](README.md)** - Complete documentation

### Technical
- **[RELEASE_v1.5.0.md](RELEASE_v1.5.0.md)** - Full release notes
- **[templates/README.md](templates/README.md)** - Template guide
- **[INDEX.md](INDEX.md)** - Documentation index

---

## 🎯 Migration Example

### Old Automation (v1.2.8)
```yaml
automation:
  - trigger:
      platform: time
      at: "20:00:00"
    action:
      service: haptique_rs90.trigger_macro
      data:
        device_id: abc123
        macro_name: "Watch Movie"  # ← Can break if renamed
```

### New Automation (v1.5.0)
```yaml
automation:
  - trigger:
      platform: time
      at: "20:00:00"
    action:
      service: haptique_rs90.trigger_macro
      data:
        device_id: abc123
        macro_id: "692eb1561bddd5814022960c"  # ← Never breaks
```

**Where to find the ID?**
1. Go to your macro switch entity
2. Look in attributes
3. Copy `haptique_macro_id`

---

## 🐛 Known Issues

**None at this time.**

If you find any, please report at: https://github.com/daangel27/haptique_rs90/issues

---

## 🔮 What's Next?

Possible future improvements:
- Blueprint examples using new parameters
- UI for easier ID discovery
- Advanced macro scheduling

**Have ideas?** Open a discussion: https://github.com/daangel27/haptique_rs90/discussions

---

## 💡 Tips

### Find IDs Quickly
```yaml
# In Developer Tools > States
# Search for your entity
# Look for haptique_macro_id or haptique_device_id
```

### Test Before Migrating
```yaml
# Keep old parameter as comment
# macro_name: "Watch Movie"  # Old way
macro_id: "692eb..."  # New way
```

### Update Templates First
Templates are most affected by renames. Update those first for best results.

---

## 📞 Support

**Need help?**
- Check [WHATS_NEW.md](WHATS_NEW.md) for migration guide
- Search [Issues](https://github.com/daangel27/haptique_rs90/issues)
- Ask in [Discussions](https://github.com/daangel27/haptique_rs90/discussions)

**Found a bug?**
- Open an [Issue](https://github.com/daangel27/haptique_rs90/issues/new)
- Include Home Assistant version
- Include integration version
- Include logs if possible

---

## 🙏 Credits

- **Maintainer**: [@daangel27](https://github.com/daangel27)
- **Hardware**: Cantata Communication Solutions
- **Software**: Haptique
- **Community**: Home Assistant users

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file

---

**Happy Automating!** 🎉

---

**Document Version**: 1.0  
**Last Updated**: December 17, 2025  
**For**: Haptique RS90 v1.5.0
