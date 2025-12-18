# What's New in v1.5.0

## ⚠️ Important: Breaking Changes

**Version 1.5.0 requires updating your automations and scripts.** Service parameters have been renamed for clarity and stability.

**Estimated migration time**: 15-30 minutes  
**Migration guide**: [MIGRATION_GUIDE_v1.5.0.md](MIGRATION_GUIDE_v1.5.0.md)

---

## 🎯 Top 3 Improvements

### 1. Ultra-Stable Entity IDs 🎉

**Problem solved**: When you renamed a device or macro in Haptique Config, the entity ID changed in Home Assistant, breaking your automations.

**Now**: Entity IDs are based on internal Haptique IDs and **never change**, even when you rename things.

**Example**:
```
Rename "Canal" → "Canal+" in Haptique Config

Before v1.5.0:
❌ Entity ID changed → Automations broken

After v1.5.0:
✅ Entity ID stays same → Automations keep working
✅ Friendly name updates automatically
```

### 2. New Sensor for Easy ID Access 📊

**Created**: `sensor.macro_{name}_info` for each macro

**Why**: Makes it super easy to find the IDs you need for services!

**Attributes**:
- `rs90_macro_id`: The stable ID to use in services
- `macro_name`: Current name
- `current_state`: on/off

**How to use**:
1. Find `sensor.macro_watch_movie_info`
2. Look at attributes
3. Copy `rs90_macro_id`
4. Use in your automations!

### 3. Clearer Service Parameters 🔧

**Old**: `device_id` (confusing - which device?)  
**New**: `rs90_id` (clear - it's the RS90 remote!)

**Old**: `macro_name` (breaks on rename)  
**New**: `rs90_macro_id` (never breaks!)

**Result**: More intuitive names + rename-proof automations!

---

## 🔄 What You Need to Update

### Service Parameters (Breaking Changes)

| Old | New | Why |
|-----|-----|-----|
| `device_id` | `rs90_id` | Clearer naming |
| `macro_name` | `rs90_macro_id` | Stable (never changes) |
| `device_name` | `rs90_device_id` | Stable (never changes) |

### Quick Migration Example

**Before (v1.2.8)**:
```yaml
service: haptique_rs90.trigger_macro
data:
  device_id: "abc123"
  macro_name: "Watch Movie"
```

**After (v1.5.0)**:
```yaml
service: haptique_rs90.trigger_macro
data:
  rs90_id: "abc123"
  rs90_macro_id: "692eb1561bddd5814022960c"
```

**Where to find the ID**:
- Go to `sensor.macro_watch_movie_info`
- Copy `rs90_macro_id` from attributes

---

## 📍 Finding Your IDs (Super Easy!)

### For Macros (`rs90_macro_id`)

**Method 1** - New sensor (easiest):
1. Find `sensor.macro_{name}_info`
2. Click it
3. Look in **Attributes**
4. Copy `rs90_macro_id`

**Method 2** - Existing switch:
1. Find `switch.macro_{name}`
2. Look in **Attributes**
3. Copy `rs90_macro_id`

### For Devices (`rs90_device_id`)

1. Find `sensor.{remote_name}_commands_{device_name}`
2. Click it
3. Look in **Attributes**
4. Copy `rs90_device_id`

### For RS90 Remote (`rs90_id`)

1. Go to your RS90 device page
2. Look at the URL
3. Copy the ID at the end: `.../device/ABC123`

---

## 💡 Benefits

### For You

✅ **No more broken automations** when you rename things  
✅ **Clearer parameter names** - easier to understand  
✅ **Easy ID discovery** - new sensors show IDs  
✅ **Future-proof** - IDs never change

### Technical

✅ **Stable entity IDs** - based on internal Haptique IDs  
✅ **Auto-updating friendly names** - no manual refresh  
✅ **Professional logging** - cleaner logs  
✅ **Better error messages** - easier debugging

---

## 🛠️ Migration Steps

### Step 1: Find Your IDs (5 min)

Collect all the IDs you'll need:
- Check each macro sensor for `rs90_macro_id`
- Check each device sensor for `rs90_device_id`
- Note your RS90 remote ID from device page

### Step 2: Update Automations (10-20 min)

For each automation using Haptique RS90:
1. Replace `device_id` → `rs90_id`
2. Replace `macro_name` → `rs90_macro_id`
3. Replace `device_name` → `rs90_device_id`
4. Save

### Step 3: Update Lovelace Templates (5 min)

If you have dashboard cards:
1. Update service calls
2. Use dynamic lookups for IDs
3. Test buttons work

### Step 4: Test Everything (5 min)

1. Test each automation manually
2. Check logs for errors
3. Verify services work

**Done!** 🎉

---

## ❓ FAQ

**Q: Do I have to update?**  
A: Yes, old parameters don't work anymore. But migration is quick and easy!

**Q: Will my entities disappear?**  
A: No! Entities stay, they just get more stable.

**Q: What if I mess up?**  
A: Backup your config first. If something breaks, check the logs for which ID is wrong.

**Q: Can I keep using `macro_name`?**  
A: No, it's completely removed in v1.5.0.

**Q: Why breaking changes?**  
A: To give you better names and rename-proof stability. Short-term pain for long-term gain!

---

## 🆘 Need Help?

**Migration issues?**  
→ See detailed guide: [MIGRATION_GUIDE_v1.5.0.md](MIGRATION_GUIDE_v1.5.0.md)

**Something not working?**  
→ Check logs in **Settings** → **System** → **Logs**

**Still stuck?**  
→ Open an issue: https://github.com/daangel27/haptique_rs90/issues

---

## ✅ Quick Checklist

- [ ] Read this page
- [ ] Backup your config
- [ ] Find all your IDs
- [ ] Update automations
- [ ] Update scripts
- [ ] Update Lovelace templates
- [ ] Test everything
- [ ] Celebrate! 🎉

---

**Version**: 1.5.0  
**Release Date**: December 18, 2025  
**Type**: Major Release (Breaking Changes)  
**Migration Required**: Yes  
**Time Required**: 15-30 minutes
