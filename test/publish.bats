#!/usr/bin/env bats

setup() {
    # Create temporary test directories
    export TEST_DIR="$(mktemp -d)"
    export HOMELAB_DIR="$TEST_DIR/homelab/tools/claude-plugins"
    export PUBLISH_DIR="$TEST_DIR/publish"

    # Create mock homelab repo structure
    mkdir -p "$HOMELAB_DIR/tommymorgan/.claude-plugin"
    mkdir -p "$HOMELAB_DIR/.claude-plugin"

    # Create mock plugin.json
    cat > "$HOMELAB_DIR/tommymorgan/.claude-plugin/plugin.json" <<EOF
{
  "name": "tommymorgan",
  "version": "0.3.0"
}
EOF

    # Create initial README
    echo "# Plugin" > "$HOMELAB_DIR/tommymorgan/README.md"

    # Create mock marketplace.json
    cat > "$HOMELAB_DIR/.claude-plugin/marketplace.json" <<EOF
{
  "name": "tommymorgan",
  "metadata": {
    "version": "0.3.0"
  },
  "plugins": [
    {
      "name": "tommymorgan",
      "version": "0.3.0"
    }
  ]
}
EOF

    # Initialize git repo in homelab
    cd "$HOMELAB_DIR"
    git init -q
    git config user.email "test@example.com"
    git config user.name "Test User"
    git add .
    git commit -q -m "Initial commit"

    # Modify existing file in plugin
    echo "# Changed" > tommymorgan/README.md

    # Initialize publish repo with main branch
    mkdir -p "$PUBLISH_DIR"
    cd "$PUBLISH_DIR"
    git init -q --initial-branch=main
    git config user.email "test@example.com"
    git config user.name "Test User"

    # Create initial commit on main
    echo "# Initial" > README.md
    git add README.md
    git commit -q -m "Initial commit"

    # Set up mock remote (bare repo)
    REMOTE_DIR="$TEST_DIR/remote"
    mkdir -p "$REMOTE_DIR"
    cd "$REMOTE_DIR"
    git init -q --bare

    cd "$PUBLISH_DIR"
    git remote add origin "$REMOTE_DIR"
    git push -q origin main

    # Copy publish.sh to test location
    cp "$(dirname "$BATS_TEST_FILENAME")/../publish.sh" "$TEST_DIR/publish.sh"
    chmod +x "$TEST_DIR/publish.sh"
    export SCRIPT_PATH="$TEST_DIR/publish.sh"
}

teardown() {
    rm -rf "$TEST_DIR"
}

@test "Publish plugin with version bump" {
    cd "$HOMELAB_DIR"

    # Run publish script with modified paths
    HOMELAB_DIR="$HOMELAB_DIR" PUBLISH_DIR="$PUBLISH_DIR" \
        run "$SCRIPT_PATH" minor "feat(plan): add new feature"

    # Should succeed
    [ "$status" -eq 0 ]

    # Verify plugin version bumped
    plugin_version=$(jq -r '.version' tommymorgan/.claude-plugin/plugin.json)
    [ "$plugin_version" = "0.4.0" ]

    # Verify marketplace version bumped
    marketplace_version=$(jq -r '.metadata.version' .claude-plugin/marketplace.json)
    [ "$marketplace_version" = "0.4.0" ]

    # Verify marketplace plugins entry version bumped
    plugin_entry_version=$(jq -r '.plugins[0].version' .claude-plugin/marketplace.json)
    [ "$plugin_entry_version" = "0.4.0" ]

    # Verify files synced to publish repo
    [ -f "$PUBLISH_DIR/tommymorgan/.claude-plugin/plugin.json" ]

    # Verify git commit created in publish repo
    cd "$PUBLISH_DIR"
    commit_msg=$(git log -1 --pretty=%B)
    [[ "$commit_msg" == *"feat(plan): add new feature"* ]]

    # Verify git tag created
    tag=$(git tag -l "v0.4.0")
    [ "$tag" = "v0.4.0" ]
}

@test "Reject multiple changed plugins" {
    cd "$HOMELAB_DIR"

    # Create second plugin
    mkdir -p other-plugin/.claude-plugin
    echo '{"name": "other-plugin", "version": "1.0.0"}' > other-plugin/.claude-plugin/plugin.json
    echo "# Other" > other-plugin/README.md
    git add other-plugin
    git commit -q -m "Add second plugin"

    # Modify both plugins
    echo "# Changed 1" > tommymorgan/README.md
    echo "# Changed 2" > other-plugin/README.md

    # Run publish script
    HOMELAB_DIR="$HOMELAB_DIR" PUBLISH_DIR="$PUBLISH_DIR" \
        run "$SCRIPT_PATH" minor "feat: updates"

    # Should fail
    [ "$status" -eq 1 ]

    # Should show error about multiple plugins
    [[ "$output" == *"Multiple plugins changed"* ]]
    [[ "$output" == *"tommymorgan"* ]]
    [[ "$output" == *"other-plugin"* ]]
    [[ "$output" == *"Please publish plugins separately"* ]]
}

@test "Reject when no changes detected" {
    cd "$HOMELAB_DIR"

    # Ensure working tree is clean (all changes committed)
    git add -A
    git commit -q -m "Clean state" || true

    # Run publish script with no changes
    HOMELAB_DIR="$HOMELAB_DIR" PUBLISH_DIR="$PUBLISH_DIR" \
        run "$SCRIPT_PATH" patch "fix: something"

    # Should fail
    [ "$status" -eq 1 ]

    # Should show error about no changes
    [[ "$output" == *"No plugin changes detected"* ]]
    [[ "$output" == *"Make changes to a plugin first"* ]]
}

@test "Script validates required dependencies" {
    # Verify script checks for dependencies
    grep -q 'for cmd in jq rsync git' "$SCRIPT_PATH"
    grep -q 'command -v.*cmd' "$SCRIPT_PATH"
    grep -q "required but not installed" "$SCRIPT_PATH"
}

@test "Script validates arguments - no arguments" {
    run "$SCRIPT_PATH"

    # Should fail
    [ "$status" -eq 1 ]

    # Should show usage
    [[ "$output" == *"Usage:"* ]]
    [[ "$output" == *"bump-type"* ]]
    [[ "$output" == *"commit-message"* ]]
}

@test "Script validates arguments - invalid bump type" {
    cd "$HOMELAB_DIR"
    echo "# Test" > tommymorgan/README.md

    HOMELAB_DIR="$HOMELAB_DIR" PUBLISH_DIR="$PUBLISH_DIR" \
        run "$SCRIPT_PATH" invalid "fix: test"

    # Should fail
    [ "$status" -eq 1 ]

    # Should show error about bump type
    [[ "$output" == *"bump-type must be major, minor, or patch"* ]]
}

@test "Version bump follows semver pre-1.0 rules" {
    # Test the bump_version function with pre-1.0 versions
    source "$SCRIPT_PATH"

    # Major bump in pre-1.0 → minor bump
    result=$(bump_version "0.3.0" "major")
    [ "$result" = "0.4.0" ]

    # Minor bump in pre-1.0 → minor bump
    result=$(bump_version "0.3.0" "minor")
    [ "$result" = "0.4.0" ]

    # Patch bump in pre-1.0 → patch bump
    result=$(bump_version "0.3.0" "patch")
    [ "$result" = "0.3.1" ]
}

@test "Version bump follows semver post-1.0 rules" {
    source "$SCRIPT_PATH"

    # Major bump
    result=$(bump_version "1.2.3" "major")
    [ "$result" = "2.0.0" ]

    # Minor bump
    result=$(bump_version "1.2.3" "minor")
    [ "$result" = "1.3.0" ]

    # Patch bump
    result=$(bump_version "1.2.3" "patch")
    [ "$result" = "1.2.4" ]
}

@test "Show progress during publish" {
    cd "$HOMELAB_DIR"

    # Modify plugin file
    echo "# Progress test" > tommymorgan/README.md

    # Run publish script
    HOMELAB_DIR="$HOMELAB_DIR" PUBLISH_DIR="$PUBLISH_DIR" \
        run "$SCRIPT_PATH" patch "fix: progress test"

    # Should succeed
    [ "$status" -eq 0 ]

    # Verify progress messages shown
    [[ "$output" == *"Publishing plugin: tommymorgan"* ]]
    [[ "$output" == *"Version bump: 0.3.0 → 0.3.1"* ]]
    [[ "$output" == *"Syncing files"* ]]
    [[ "$output" == *"Creating git commit and tag"* ]]
    [[ "$output" == *"Pushing to GitHub"* ]]
    [[ "$output" == *"Published tommymorgan v0.3.1"* ]]
}

@test "Script updates all version locations" {
    cd "$HOMELAB_DIR"
    echo "# Update test" > tommymorgan/README.md

    # Run publish
    HOMELAB_DIR="$HOMELAB_DIR" PUBLISH_DIR="$PUBLISH_DIR" \
        run "$SCRIPT_PATH" minor "feat: version update test"

    [ "$status" -eq 0 ]

    # Check all three version locations in homelab dir
    plugin_ver=$(jq -r '.version' tommymorgan/.claude-plugin/plugin.json)
    marketplace_ver=$(jq -r '.metadata.version' .claude-plugin/marketplace.json)
    plugin_entry_ver=$(jq -r '.plugins[] | select(.name=="tommymorgan") | .version' .claude-plugin/marketplace.json)

    [ "$plugin_ver" = "0.4.0" ]
    [ "$marketplace_ver" = "0.4.0" ]
    [ "$plugin_entry_ver" = "0.4.0" ]
}

@test "Script syncs files excluding git and plans" {
    cd "$HOMELAB_DIR"

    # Create files that should be synced
    echo "# Sync me" > tommymorgan/SYNC.md
    mkdir -p plans
    echo "# Don't sync" > plans/test-plan.md

    # Ensure git directory exists but shouldn't be synced
    echo "# Git file" > .git/test-file

    git add tommymorgan/SYNC.md
    git commit -q -m "Add sync test"
    echo "# Changed" > tommymorgan/SYNC.md

    # Run publish
    HOMELAB_DIR="$HOMELAB_DIR" PUBLISH_DIR="$PUBLISH_DIR" \
        run "$SCRIPT_PATH" patch "fix: sync test"

    [ "$status" -eq 0 ]

    # Verify synced file exists
    [ -f "$PUBLISH_DIR/tommymorgan/SYNC.md" ]

    # Verify plans not synced
    [ ! -d "$PUBLISH_DIR/plans" ]

    # Verify .git not synced (publish repo has its own .git)
    [ ! -f "$PUBLISH_DIR/.git/test-file" ]
}

@test "Script creates git commit and tag" {
    # Already covered by test 1, but verify explicitly
    cd "$HOMELAB_DIR"
    echo "# Commit test" > tommymorgan/README.md

    HOMELAB_DIR="$HOMELAB_DIR" PUBLISH_DIR="$PUBLISH_DIR" \
        run "$SCRIPT_PATH" patch "fix: commit test"

    [ "$status" -eq 0 ]

    # Verify commit message in publish repo
    cd "$PUBLISH_DIR"
    commit_msg=$(git log -1 --pretty=%B)
    [ "$commit_msg" = "fix: commit test" ]

    # Verify tag created
    tags=$(git tag -l)
    [[ "$tags" == *"v0.3.1"* ]]
}

@test "Script detects changed plugin from git" {
    # Already covered by test 1
    cd "$HOMELAB_DIR"
    echo "# Detection test" > tommymorgan/README.md

    HOMELAB_DIR="$HOMELAB_DIR" PUBLISH_DIR="$PUBLISH_DIR" \
        run "$SCRIPT_PATH" patch "fix: detection test"

    [ "$status" -eq 0 ]
    [[ "$output" == *"Publishing plugin: tommymorgan"* ]]
}

@test "Script updates JSON files atomically" {
    # Verify script uses temp files and mv for atomic updates
    grep -q 'mktemp' "$SCRIPT_PATH"
    grep -q 'TEMP_PLUGIN' "$SCRIPT_PATH"
    grep -q 'TEMP_MARKETPLACE' "$SCRIPT_PATH"
    grep -q 'mv.*TEMP_PLUGIN.*PLUGIN_JSON' "$SCRIPT_PATH"
    grep -q 'mv.*TEMP_MARKETPLACE.*MARKETPLACE_JSON' "$SCRIPT_PATH"
}

@test "Script detects git push failures" {
    # Verify script checks git push exit codes
    grep -q 'if ! git push origin main' "$SCRIPT_PATH"
    grep -q 'Failed to push commit' "$SCRIPT_PATH"
    grep -q 'if ! git push origin.*NEW_VERSION' "$SCRIPT_PATH"
    grep -q 'Failed to push tag' "$SCRIPT_PATH"
}

@test "Script prevents duplicate version tags" {
    # Verify script checks for existing tags
    grep -q 'git rev-parse.*NEW_VERSION' "$SCRIPT_PATH"
    grep -q 'already exists' "$SCRIPT_PATH"
}

@test "Script verifies tag pushed to GitHub" {
    # Verify script checks remote for tag
    grep -q 'git ls-remote.*tags.*origin' "$SCRIPT_PATH"
    grep -q 'verified on GitHub' "$SCRIPT_PATH"
}
