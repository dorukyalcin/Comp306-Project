#!/bin/bash

# Unified Seeding Script
# =====================
# This script combines all seeding operations into one unified interface.
# It can handle:
# - Basic seeding (games, admin users)
# - Analytics data seeding
# - Horse racing data
# - Comprehensive test data
# - Clean seeding (resets DB first)

# Text colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to handle errors
handle_error() {
    echo -e "${RED}❌ Error: $1${NC}"
    exit 1
}

# Function to print section header
print_header() {
    echo -e "\n${BLUE}$1${NC}"
    echo "=================================="
}

# Function to print success message
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to reset database
reset_db() {
    print_header "🗑️  Resetting Database"
    echo "DELETE ALL DATA" | python3 seeding/reset_db.py || handle_error "Database reset failed"
    print_success "Database reset complete"
}

# Function to seed games
seed_games() {
    print_header "🎮 Seeding Games"
    python3 seeding/seed_games.py || handle_error "Game seeding failed"
    print_success "Games seeded successfully"
}

# Function to seed admin users
seed_admin_users() {
    print_header "👤 Creating Admin Users"
    python3 seeding/comprehensive_seed.py || handle_error "Admin user creation failed"
    print_success "Admin users created"
}

# Function to seed user cohorts
seed_user_cohorts() {
    print_header "👥 Seeding User Cohorts"
    python3 seeding/seed_user_cohorts.py || handle_error "User cohort seeding failed"
    print_success "User cohorts seeded"
}

# Function to seed horse racing data
seed_horse_racing() {
    print_header "🐎 Seeding Horse Racing Data"
    python3 seeding/seed_horses.py || handle_error "Horse seeding failed"
    python3 seeding/seed_horse_races.py || handle_error "Horse race seeding failed"
    print_success "Horse racing data seeded"
}

# Function to enhance transactions
enhance_transactions() {
    print_header "💰 Enhancing Transaction Data"
    python3 seeding/enhance_transactions.py || handle_error "Transaction enhancement failed"
    print_success "Transactions enhanced"
}

# Show help menu
show_help() {
    echo "Usage: ./scripts/seed.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -c, --clean         Clean seed (resets DB first)"
    echo "  -b, --basic         Basic seed (games and admin users only)"
    echo "  -a, --analytics     Seed analytics data"
    echo "  -r, --horse-racing  Seed horse racing data"
    echo "  --all              Seed everything (comprehensive)"
    echo ""
    echo "Examples:"
    echo "  ./scripts/seed.sh --clean --all    # Reset DB and seed everything"
    echo "  ./scripts/seed.sh --basic          # Seed only games and admin users"
    echo "  ./scripts/seed.sh --analytics      # Seed analytics data"
    echo "  ./scripts/seed.sh -c -b            # Clean basic seed"
    exit 0
}

# Parse command line arguments
CLEAN=0
BASIC=0
ANALYTICS=0
HORSE_RACING=0
ALL=0

# If no arguments, show help
if [ $# -eq 0 ]; then
    show_help
fi

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            ;;
        -c|--clean)
            CLEAN=1
            shift
            ;;
        -b|--basic)
            BASIC=1
            shift
            ;;
        -a|--analytics)
            ANALYTICS=1
            shift
            ;;
        -r|--horse-racing)
            HORSE_RACING=1
            shift
            ;;
        --all)
            ALL=1
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            ;;
    esac
done

# Print start banner
print_header "🌱 Starting Seeding Process"

# Reset database if clean flag is set
if [ $CLEAN -eq 1 ]; then
    reset_db
fi

# Seed everything if all flag is set
if [ $ALL -eq 1 ]; then
    BASIC=1
    ANALYTICS=1
    HORSE_RACING=1
fi

# Basic seeding (games and admin users)
if [ $BASIC -eq 1 ]; then
    seed_games
    seed_admin_users
fi

# Analytics data seeding
if [ $ANALYTICS -eq 1 ]; then
    seed_user_cohorts
    enhance_transactions
fi

# Horse racing data seeding
if [ $HORSE_RACING -eq 1 ]; then
    seed_horse_racing
fi

# Print completion message
print_header "✅ Seeding Complete!"
echo "You can now:"
echo "1. Access the site at http://localhost:8000"
echo "2. Log in with:"
echo "   Username: admin_casino"
echo "   Password: password123"
if [ $ANALYTICS -eq 1 ]; then
    echo "3. View analytics data in the admin dashboard"
fi
if [ $HORSE_RACING -eq 1 ]; then
    echo "4. Check out the horse racing feature" 