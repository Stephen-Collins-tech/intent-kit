import tomllib
import re

# Read version from pyproject.toml
with open("pyproject.toml", "rb") as f:
    version = tomllib.load(f)["project"]["version"]

# Update __init__.py
with open("intent_kit/__init__.py", "r") as f:
    content = f.read()

content = re.sub(r'__version__ = "[^"]*"', f'__version__ = "{version}"', content)

with open("intent_kit/__init__.py", "w") as f:
    f.write(content)

print(f"Updated version to {version}")
