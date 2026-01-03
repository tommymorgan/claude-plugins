#!/usr/bin/env bash

set -e  # Exit on first error

# Allow sourcing for testing
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    RUN_MAIN=true
else
    RUN_MAIN=false
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default paths (can be overridden for testing)
HOMELAB_DIR="${HOMELAB_DIR:-$HOME/src/homelab/tools/claude-plugins}"
PUBLISH_DIR="${PUBLISH_DIR:-$HOME/src/claude-plugins-publish}"

# Function to print colored output
log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1" >&2
}

log_step() {
    echo -e "${YELLOW}→${NC} $1"
}

# Function to bump version following semver
bump_version() {
    local version=$1
    local bump_type=$2

    IFS='.' read -r major minor patch <<< "$version"

    # Pre-1.0: both "major" and "minor" bump the minor version
    if [[ $major == "0" ]]; then
        if [[ $bump_type == "patch" ]]; then
            patch=$((patch + 1))
        else  # major or minor
            minor=$((minor + 1))
            patch=0
        fi
    else  # Post-1.0: standard semver
        case $bump_type in
            major) major=$((major + 1)); minor=0; patch=0 ;;
            minor) minor=$((minor + 1)); patch=0 ;;
            patch) patch=$((patch + 1)) ;;
        esac
    fi

    echo "$major.$minor.$patch"
}

# Main script logic (only run when executed, not sourced)
if [[ "$RUN_MAIN" == "true" ]]; then

# Cleanup trap for temporary files
TEMP_PLUGIN=""
TEMP_MARKETPLACE=""
cleanup() {
    rm -f "$TEMP_PLUGIN" "$TEMP_MARKETPLACE" 2>/dev/null || true
}
trap cleanup EXIT

# Validate arguments
if [[ $# -ne 2 ]]; then
    log_error "Usage: $0 <bump-type> <commit-message>"
    log_error "  bump-type: major, minor, or patch"
    log_error "  commit-message: Conventional commit message (quoted)"
    exit 1
fi

BUMP_TYPE="$1"
COMMIT_MESSAGE="$2"

# Validate bump type
if [[ ! "$BUMP_TYPE" =~ ^(major|minor|patch)$ ]]; then
    log_error "bump-type must be major, minor, or patch"
    exit 1
fi

# Check dependencies
log_step "Checking dependencies..."
for cmd in jq rsync git; do
    if ! command -v "$cmd" &> /dev/null; then
        log_error "$cmd is required but not installed"
        exit 1
    fi
done
log_info "All dependencies available"

# Change to homelab directory
cd "$HOMELAB_DIR"

# Detect changed plugins using git
log_step "Detecting changed plugins..."
# Get all changed files (staged and unstaged)
CHANGED_FILES=$(git diff --name-only HEAD)
# Strip tools/claude-plugins/ prefix if present (when run from subdirectory of git repo)
CHANGED_FILES=$(echo "$CHANGED_FILES" | sed 's|^tools/claude-plugins/||')
# Extract plugin directory names
CHANGED_PLUGINS=$(echo "$CHANGED_FILES" | cut -d/ -f1 | sort -u | grep -v -E '^(test|docs|\.claude-plugin|LICENSE|README\.md|publish\.sh)$' || true)

# Handle no changes
if [[ -z "$CHANGED_PLUGINS" ]]; then
    log_error "No plugin changes detected in git"
    log_error "Make changes to a plugin first, then run publish"
    exit 1
fi

# Handle multiple plugins
PLUGIN_COUNT=$(echo "$CHANGED_PLUGINS" | wc -l)
if [[ $PLUGIN_COUNT -gt 1 ]]; then
    log_error "Multiple plugins changed:"
    echo "$CHANGED_PLUGINS" | sed 's/^/  /' >&2
    log_error "Please publish plugins separately"
    exit 1
fi

PLUGIN_NAME="$CHANGED_PLUGINS"
log_info "Publishing plugin: $PLUGIN_NAME"

# Validate plugin structure
PLUGIN_JSON="$PLUGIN_NAME/.claude-plugin/plugin.json"
MARKETPLACE_JSON=".claude-plugin/marketplace.json"

if [[ ! -f "$PLUGIN_JSON" ]]; then
    log_error "Plugin config not found: $PLUGIN_JSON"
    log_error "Plugin directory structure is invalid"
    exit 1
fi

# Read current versions
CURRENT_PLUGIN_VERSION=$(jq -r '.version' "$PLUGIN_JSON")
CURRENT_MARKETPLACE_VERSION=$(jq -r '.metadata.version' "$MARKETPLACE_JSON")

# Calculate new versions
NEW_VERSION=$(bump_version "$CURRENT_MARKETPLACE_VERSION" "$BUMP_TYPE")

log_step "Version bump: $CURRENT_MARKETPLACE_VERSION → $NEW_VERSION ($BUMP_TYPE)"

# Update JSON files atomically using temporary files
log_step "Updating version numbers..."

# Update plugin.json
TEMP_PLUGIN=$(mktemp)
jq ".version = \"$NEW_VERSION\"" "$PLUGIN_JSON" > "$TEMP_PLUGIN"
mv "$TEMP_PLUGIN" "$PLUGIN_JSON"

# Update marketplace.json (both metadata.version and plugins array)
TEMP_MARKETPLACE=$(mktemp)
jq ".metadata.version = \"$NEW_VERSION\" |
    (.plugins[] | select(.name == \"$PLUGIN_NAME\").version) = \"$NEW_VERSION\"" \
    "$MARKETPLACE_JSON" > "$TEMP_MARKETPLACE"
mv "$TEMP_MARKETPLACE" "$MARKETPLACE_JSON"

log_info "Versions updated in JSON files"

# Verify publish directory exists
if [[ ! -d "$PUBLISH_DIR/.git" ]]; then
    log_error "Publish repo not found at $PUBLISH_DIR"
    exit 1
fi

# Sync files to publish repo
log_step "Syncing files to publish repository..."
rsync -av --delete \
    --exclude='.git' \
    --exclude='plans' \
    "$HOMELAB_DIR/" \
    "$PUBLISH_DIR/" | grep -v "/$" | tail -10

log_info "Files synced"

# Git operations in publish repo
cd "$PUBLISH_DIR"

log_step "Creating git commit and tag..."

# Stage all changes
git add -A

# Commit with provided message
git commit -m "$COMMIT_MESSAGE"

# Check if tag already exists
if git rev-parse "v$NEW_VERSION" >/dev/null 2>&1; then
    log_error "Git tag v$NEW_VERSION already exists"
    log_error "Version tag already published"
    exit 1
fi

# Create tag
git tag "v$NEW_VERSION"

log_info "Commit and tag created"

# Push to GitHub
log_step "Pushing to GitHub..."

if ! git push origin main; then
    log_error "Failed to push commit to origin/main"
    exit 1
fi

if ! git push origin "v$NEW_VERSION"; then
    log_error "Failed to push tag v$NEW_VERSION"
    exit 1
fi

log_info "Pushed to GitHub"

# Verify tag exists on remote
log_step "Verifying tag on remote..."
if git ls-remote --tags origin | grep -q "refs/tags/v$NEW_VERSION"; then
    log_info "Tag v$NEW_VERSION verified on GitHub"
else
    log_error "Tag v$NEW_VERSION not found on remote"
    exit 1
fi

# Success summary
echo ""
log_info "✨ Published $PLUGIN_NAME v$NEW_VERSION to GitHub"
echo ""
echo "  Plugin version:      $CURRENT_PLUGIN_VERSION → $NEW_VERSION"
echo "  Marketplace version: $CURRENT_MARKETPLACE_VERSION → $NEW_VERSION"
echo "  Git tag:             v$NEW_VERSION"
echo ""

fi  # End of main script logic
