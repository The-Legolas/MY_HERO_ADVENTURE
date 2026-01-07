
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT" || exit 1

PYTHON_VERSION=$(python3 - <<EOF
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
EOF
)

REQUIRED_VERSION="3.12"

if [[ "$PYTHON_VERSION" < "$REQUIRED_VERSION" ]]; then
  echo "Warning: Python $REQUIRED_VERSION is recommended. Detected Python $PYTHON_VERSION."
fi

echo "Starting My Hero Adventure..."
python3 main.py
