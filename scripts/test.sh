#!/bin/bash
# Test script for Haptique RS90 integration

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🧪 Haptique RS90 - Test Suite${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest not found. Installing test dependencies...${NC}"
    pip install -r requirements_test.txt
fi

# 1. Code formatting check
echo -e "${YELLOW}📝 Checking code formatting...${NC}"
if black --check custom_components/haptique_rs90/ tests/; then
    echo -e "${GREEN}✅ Code formatting: PASS${NC}"
else
    echo -e "${RED}❌ Code formatting: FAIL${NC}"
    echo -e "${YELLOW}💡 Run: black custom_components/haptique_rs90/ tests/${NC}"
    exit 1
fi
echo

# 2. Linting
echo -e "${YELLOW}🔍 Running linter...${NC}"
if flake8 custom_components/haptique_rs90/ --max-line-length=100 --ignore=E501,W503; then
    echo -e "${GREEN}✅ Linting: PASS${NC}"
else
    echo -e "${RED}❌ Linting: FAIL${NC}"
    exit 1
fi
echo

# 3. Type checking
echo -e "${YELLOW}🔎 Type checking...${NC}"
if mypy custom_components/haptique_rs90/ --ignore-missing-imports; then
    echo -e "${GREEN}✅ Type checking: PASS${NC}"
else
    echo -e "${YELLOW}⚠️  Type checking: WARNINGS (non-blocking)${NC}"
fi
echo

# 4. Unit tests
echo -e "${YELLOW}🧪 Running unit tests...${NC}"
if pytest tests/unit/ -v --cov=custom_components.haptique_rs90 --cov-report=term-missing; then
    echo -e "${GREEN}✅ Unit tests: PASS${NC}"
else
    echo -e "${RED}❌ Unit tests: FAIL${NC}"
    exit 1
fi
echo

# 5. Integration tests (if they exist)
if [ -d "tests/integration" ] && [ "$(ls -A tests/integration)" ]; then
    echo -e "${YELLOW}🔗 Running integration tests...${NC}"
    if pytest tests/integration/ -v; then
        echo -e "${GREEN}✅ Integration tests: PASS${NC}"
    else
        echo -e "${RED}❌ Integration tests: FAIL${NC}"
        exit 1
    fi
    echo
fi

# 6. Coverage report
echo -e "${YELLOW}📊 Coverage summary:${NC}"
pytest tests/ --cov=custom_components.haptique_rs90 --cov-report=term --cov-report=html --quiet

# Check coverage threshold
COVERAGE=$(pytest tests/ --cov=custom_components.haptique_rs90 --cov-report=term | grep "TOTAL" | awk '{print $4}' | sed 's/%//')
THRESHOLD=80

if [ -n "$COVERAGE" ]; then
    if (( $(echo "$COVERAGE >= $THRESHOLD" | bc -l) )); then
        echo -e "${GREEN}✅ Coverage: ${COVERAGE}% (threshold: ${THRESHOLD}%)${NC}"
    else
        echo -e "${YELLOW}⚠️  Coverage: ${COVERAGE}% (threshold: ${THRESHOLD}%)${NC}"
        echo -e "${YELLOW}💡 Consider adding more tests${NC}"
    fi
fi

echo
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ All tests passed!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
echo -e "📄 HTML coverage report: ${YELLOW}htmlcov/index.html${NC}"
echo
