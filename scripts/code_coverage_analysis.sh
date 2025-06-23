#!/bin/sh

# Clear the screen
clear

# ASCII art for header
echo " ____  _                         "
echo "|  _ \\(_) __ _ _ __   __ _  ___  "
echo "| | | | |/ _\` | '_ \\ / _\` |/ _ \\ "
echo "| |_| | | (_| | | | | (_| | (_) |"
echo "|____// |\\__,_|_| |_|\\__, |\\___/ "
echo "    |__/             |___/       "
echo " ____        _ _                 _       _       "
echo "| __ )  ___ (_) | ___ _ __ _ __ | | __ _| |_ ___ "
echo "|  _ \\ / _ \\| | |/ _ \\ '__| '_ \\| |/ _\` | __/ _ \\"
echo "| |_) | (_) | | |  __/ |  | |_) | | (_| | ||  __/"
echo "|____/ \\___/|_|_|\\___|_|  | .__/|_|\\__,_|\\__\\___|"
echo "                          |_|                    "


# Spacer for readability
for i in {1..5}; do echo "                                                 "; done

# Start test and coverage
echo "🚀 Starting test execution and coverage measurement..."

# Spacer for readability
for i in {1..5}; do echo "                                                 "; done

# Navigate to the app directory containing manage.py
cd app

# Run the Django tests with coverage
coverage run --source='.' manage.py test

# Spacer for readability
for i in {1..10}; do echo "                                                 "; done

echo "📊 Visualizing code coverage report..."

# Spacer for readability
for i in {1..3}; do echo "                                                 "; done

# Generate the coverage report in the terminal
coverage report -m

# Spacer for readability
for i in {1..5}; do echo "                                                 "; done

# Generate the HTML report
coverage html

echo ""
echo ""

# Notify the user
echo "✅ Test execution and coverage report generation complete."
echo ""
echo ""
echo "📝 You can view the HTML report by opening 'app/htmlcov/index.html' in a web browser."

# Navigate back to the original directory
cd ..

echo ""
echo ""

# Final message
echo "🏁 All done! Your coverage reports are ready."
