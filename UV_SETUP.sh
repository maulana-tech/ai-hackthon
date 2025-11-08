#!/bin/bash

# ========================================
# TrendScout - UV Quick Setup Script
# ========================================

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     TrendScout Supplier Connector - UV Setup             ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check UV installation
echo -e "${YELLOW}Step 1/7:${NC} Checking UV installation..."
if ! command -v uv &> /dev/null; then
    echo -e "${RED}✗${NC} UV not found. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    echo -e "${GREEN}✓${NC} UV installed successfully!"
else
    echo -e "${GREEN}✓${NC} UV already installed ($(uv --version))"
fi

# Step 2: Check Python version
echo ""
echo -e "${YELLOW}Step 2/7:${NC} Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.9.0"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then 
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION (meets requirement: 3.9+)"
else
    echo -e "${RED}✗${NC} Python version too old. Please upgrade to 3.9+"
    exit 1
fi

# Step 3: Create virtual environment
echo ""
echo -e "${YELLOW}Step 3/7:${NC} Creating virtual environment..."
if [ -d ".venv" ]; then
    echo -e "${YELLOW}!${NC} .venv already exists. Skipping..."
else
    uv venv
    echo -e "${GREEN}✓${NC} Virtual environment created!"
fi

# Step 4: Activate virtual environment
echo ""
echo -e "${YELLOW}Step 4/7:${NC} Activating virtual environment..."
source .venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated!"

# Step 5: Install dependencies
echo ""
echo -e "${YELLOW}Step 5/7:${NC} Installing dependencies with UV (this is fast!)..."
START_TIME=$(date +%s)
uv pip install -r requirements.txt
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo -e "${GREEN}✓${NC} Dependencies installed in ${DURATION}s!"

# Step 6: Setup environment variables
echo ""
echo -e "${YELLOW}Step 6/7:${NC} Setting up environment variables..."
if [ -f ".env" ]; then
    echo -e "${YELLOW}!${NC} .env already exists. Skipping..."
else
    if [ -f ".env.circlo" ]; then
        echo "Using .env.circlo as template with JWT token..."
        cp .env.circlo .env
        echo -e "${GREEN}✓${NC} .env created with Circlo JWT token!"
    elif [ -f ".env.example" ]; then
        echo "Using .env.example as template..."
        cp .env.example .env
        echo -e "${GREEN}✓${NC} .env created from template!"
    else
        echo -e "${RED}✗${NC} No .env template found!"
        exit 1
    fi
    
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT:${NC} Edit .env and add your API keys:"
    echo "   - FIRECRAWL_API_KEY"
    echo "   - OPENAI_API_KEY"
    echo "   - GETCIRCLO_JWT_TOKEN (already set)"
fi

# Step 7: Verify installation
echo ""
echo -e "${YELLOW}Step 7/7:${NC} Verifying installation..."
uv run python -c "
try:
    from app.main import app
    print('✓ Main app loaded successfully')
except Exception as e:
    print(f'✗ Error loading app: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Installation verified!"
else
    echo -e "${RED}✗${NC} Installation verification failed!"
    exit 1
fi

# Success message
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                 🎉 Setup Complete! 🎉                     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "1. ${YELLOW}Edit .env file${NC} with your API keys:"
echo "   ${GREEN}nano .env${NC}"
echo ""
echo "2. ${YELLOW}Start the server:${NC}"
echo "   ${GREEN}source .venv/bin/activate${NC}"
echo "   ${GREEN}uv run uvicorn app.main:app --reload${NC}"
echo ""
echo "3. ${YELLOW}Register Circlo agents:${NC}"
echo "   ${GREEN}uv run python setup_circlo_agents.py${NC}"
echo ""
echo "4. ${YELLOW}Access API docs:${NC}"
echo "   ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo "📚 Documentation:"
echo "   - Quick Start with UV: ${GREEN}QUICKSTART_UV.md${NC}"
echo "   - Circlo Integration: ${GREEN}CIRCLO_INTEGRATION.md${NC}"
echo "   - Verification Guide: ${GREEN}CIRCLO_VERIFICATION.md${NC}"
echo ""
