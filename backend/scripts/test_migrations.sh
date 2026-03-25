#!/bin/bash
#
# Test database migrations
# This script tests forward migrations, rollback, and clean migrations
#

set -e

echo "========================================="
echo "Testing Database Migrations"
echo "========================================="

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
        exit 1
    fi
}

# Check if we're in the backend directory
if [ ! -f "alembic.ini" ]; then
    echo -e "${RED}Error: alembic.ini not found. Please run from backend directory.${NC}"
    exit 1
fi

echo ""
echo "Test 1: Get current migration"
CURRENT=$(alembic current 2>&1 | tail -1)
echo "Current migration: $CURRENT"

echo ""
echo "Test 2: Test forward migrations"
alembic upgrade head
print_status $? "Forward migrations successful"

echo ""
echo "Test 3: Test rollback (downgrade 1 step)"
alembic downgrade -1
print_status $? "Rollback successful"

echo ""
echo "Test 4: Test upgrade again"
alembic upgrade +1
print_status $? "Upgrade after rollback successful"

echo ""
echo "Test 5: Test from scratch (downgrade to base)"
echo -e "${YELLOW}Warning: This will drop all tables!${NC}"
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    alembic downgrade base
    print_status $? "Downgrade to base successful"

    echo ""
    echo "Test 6: Test upgrade from base to head"
    alembic upgrade head
    print_status $? "Upgrade from base successful"
else
    echo "Skipping base migration test"
fi

echo ""
echo "Test 7: Check migration history"
alembic history --verbose
print_status $? "Migration history retrieved"

echo ""
echo "========================================="
echo -e "${GREEN}All migration tests passed!${NC}"
echo "========================================="

