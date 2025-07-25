import tomllib
import re
import sys

# Read version from pyproject.toml
with open("pyproject.toml", "rb") as f:
    version = tomllib.load(f)["project"]["version"]

# Read changelog
with open("CHANGELOG.md", "r") as f:
    changelog_content = f.read()

# Check if version is in changelog
version_pattern = rf"\[v{re.escape(version)}\]"
if not re.search(version_pattern, changelog_content):
    print(f"ERROR: Version {version} not found in CHANGELOG.md")
    print(
        f"Please add an entry for version {version} in the changelog before committing."
    )
    sys.exit(1)

print(f"✓ Version {version} found in CHANGELOG.md")
