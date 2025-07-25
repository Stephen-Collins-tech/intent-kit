import os
import subprocess
import sys

# Run pytest with coverage
result = subprocess.run(
    [
        sys.executable,
        "-m",
        "pytest",
        "--cov=intent_kit",
        "--cov-report=term-missing",
        "--cov-report=html",
        *sys.argv[1:],
    ]
)

print(f"Open {os.path.abspath('htmlcov/index.html')} for a detailed report.")

# Exit with the same code as pytest
sys.exit(result.returncode)
