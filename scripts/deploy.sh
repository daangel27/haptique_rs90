#!/bin/bash
# Deploy script for Haptique RS90 integration to development HA instance

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
HA_CONFIG_DIR="${HA_CONFIG_DIR:-/config}"
INTEGRATION_NAME="haptique_rs90"
CUSTOM_COMPONENTS_DIR="$HA_CONFIG_DIR/custom_components"
TARGET_DIR="$CUSTOM_COMPONENTS_DIR/$INTEGRATION_NAME"

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🚀 Haptique RS90 - Deploy to Dev${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# 1. Validate source
echo -e "${YELLOW}📋 Validating source files...${NC}"
if [ ! -d "custom_components/$INTEGRATION_NAME" ]; then
    echo -e "${RED}❌ Source directory not found: custom_components/$INTEGRATION_NAME${NC}"
    exit 1
fi

if [ ! -f "custom_components/$INTEGRATION_NAME/manifest.json" ]; then
    echo -e "${RED}❌ manifest.json not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Source files validated${NC}"
echo

# 2. Create backup
if [ -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}💾 Creating backup...${NC}"
    BACKUP_DIR="$HA_CONFIG_DIR/backups"
    mkdir -p "$BACKUP_DIR"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/${INTEGRATION_NAME}_${TIMESTAMP}.tar.gz"
    
    tar -czf "$BACKUP_FILE" -C "$CUSTOM_COMPONENTS_DIR" "$INTEGRATION_NAME"
    echo -e "${GREEN}✅ Backup created: $BACKUP_FILE${NC}"
    echo
fi

# 3. Copy files
echo -e "${YELLOW}📦 Copying files to $TARGET_DIR...${NC}"
mkdir -p "$CUSTOM_COMPONENTS_DIR"
rm -rf "$TARGET_DIR"
cp -r "custom_components/$INTEGRATION_NAME" "$TARGET_DIR"

# Verify copy
if [ -f "$TARGET_DIR/manifest.json" ]; then
    VERSION=$(grep -oP '"version": "\K[^"]+' "$TARGET_DIR/manifest.json")
    echo -e "${GREEN}✅ Files copied successfully (version: $VERSION)${NC}"
else
    echo -e "${RED}❌ Copy failed${NC}"
    exit 1
fi
echo

# 4. Restart Home Assistant
echo -e "${YELLOW}🔄 Restarting Home Assistant...${NC}"

# Method 1: Try ha cli (HAOS)
if command -v ha &> /dev/null; then
    ha core restart
    echo -e "${GREEN}✅ Restart command sent via ha cli${NC}"
# Method 2: Try service call
elif command -v curl &> /dev/null && [ -n "$SUPERVISOR_TOKEN" ]; then
    curl -X POST \
         -H "Authorization: Bearer $SUPERVISOR_TOKEN" \
         -H "Content-Type: application/json" \
         http://supervisor/core/restart
    echo -e "${GREEN}✅ Restart command sent via API${NC}"
else
    echo -e "${YELLOW}⚠️  Cannot restart automatically${NC}"
    echo -e "${YELLOW}💡 Please restart Home Assistant manually:${NC}"
    echo -e "   Settings → System → Restart"
fi
echo

# 5. Watch logs (optional)
if [ "$1" == "--watch-logs" ] || [ "$1" == "-w" ]; then
    echo -e "${YELLOW}📋 Watching logs (Ctrl+C to stop)...${NC}"
    echo
    sleep 10  # Wait for HA to start
    tail -f "$HA_CONFIG_DIR/home-assistant.log" | grep -i "haptique_rs90"
fi

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
echo -e "📄 Check logs: ${YELLOW}$HA_CONFIG_DIR/home-assistant.log${NC}"
echo -e "🌐 Access HA: ${YELLOW}http://your-ha-ip:8123${NC}"
echo
echo -e "${YELLOW}💡 Options:${NC}"
echo -e "   ${YELLOW}--watch-logs, -w${NC}  : Watch logs after deploy"
echo
