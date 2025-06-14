#!/bin/bash

# Setup Script - Makes all development scripts executable
# Run this after cloning the repository from GitHub

echo "🛠️  REPOSITORY SETUP"
echo "==================="
echo "Making all development scripts executable..."

# Make all scripts in the scripts directory executable
chmod +x scripts/*.sh

# Make this setup script executable too (for future use)
chmod +x setup.sh

echo ""
echo "✅ Setup complete! All scripts are now executable."
echo ""
echo "🎯 Quick Start Options:"
echo "   ./scripts/dev_menu.sh     - Interactive menu (recommended)"
echo "   ./scripts/fresh_start.sh  - Complete fresh site with test data"
echo "   ./scripts/quick_view.sh   - Check current status"
echo ""
echo "🐎 Horse Racing Features:"
echo "   • 24 unique horses with realistic characteristics"
echo "   • Dynamic odds based on horse stats"
echo "   • Physics-based race simulation"
echo "   • Win/Place/Show betting options"
echo ""
echo "📖 Documentation:"
echo "   scripts/README.md         - Complete scripts guide"
echo "   seeding/README.md         - Database seeding guide"
echo "   DEVELOPMENT_SCRIPTS.md    - Development workflow guide"
echo ""
echo "🌐 After setup, visit:"
echo "   Website: http://localhost:8000"
echo "   Horse Racing: http://localhost:8000/horse-racing"
echo "===================" 