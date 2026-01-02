
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT" || exit 1


echo "Running unit tests..."
python3 -m unittest discover -s game/tests
