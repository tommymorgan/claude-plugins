#!/usr/bin/env python3
"""
Claude Code UserPromptSubmit Hook: Automatic Image Resizing

Automatically resizes images exceeding 2000px to prevent Claude API errors.
Provides clear feedback and maintains image quality.
"""

import base64
import json
import re
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError

# Configuration
MAX_DIMENSION = 2000  # Claude API limit
SUPPORTED_FORMATS = ["image/png", "image/jpeg", "image/gif"]


def read_config(project_root: str = None) -> dict:
    """
    Read configuration from .claude/tommymorgan.local.md

    Args:
        project_root: Project root directory (defaults to cwd)

    Returns:
        Dict with configuration, defaults to auto_resize_images: true
    """
    if project_root is None:
        project_root = Path.cwd()
    else:
        project_root = Path(project_root)

    config_path = project_root / ".claude" / "tommymorgan.local.md"

    # Default configuration
    config = {"auto_resize_images": True}

    if not config_path.exists():
        return config

    try:
        content = config_path.read_text(encoding="utf-8")

        # Extract YAML frontmatter
        frontmatter_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)

            # Parse auto_resize_images setting (simple boolean parsing)
            if "auto_resize_images:" in frontmatter:
                # Extract value after auto_resize_images:
                value_match = re.search(
                    r"auto_resize_images:\s*(true|false)", frontmatter, re.IGNORECASE
                )
                if value_match:
                    config["auto_resize_images"] = (
                        value_match.group(1).lower() == "true"
                    )

    except (PermissionError, UnicodeDecodeError):
        # On error, use defaults
        pass

    return config


def should_process(config: dict) -> bool:
    """
    Determine if image processing should run based on config

    Args:
        config: Configuration dict

    Returns:
        True if should process images, False to skip
    """
    return config.get("auto_resize_images", True)


def detect_plugin_conflict(enabled_plugins: list) -> bool:
    """
    Detect if auto-resize-images plugin is also installed

    Args:
        enabled_plugins: List of enabled plugin names

    Returns:
        True if auto-resize-images is present (conflict), False otherwise
    """
    return "auto-resize-images" in enabled_plugins


def warn_plugin_conflict():
    """Log warning to stderr about duplicate plugins"""
    sys.stderr.write(
        "WARNING: Both auto-resize-images and tommymorgan image resize detected.\n"
        "Duplicate processing wastes resources.\n"
        "Please uninstall auto-resize-images: claude plugin uninstall auto-resize-images\n"
    )


def block_submission(reason: str):
    """Block submission with an error message"""
    output = {
        "decision": "block",
        "reason": reason
    }
    print(json.dumps(output))
    sys.exit(0)


def read_hook_input() -> dict:
    """Read and parse JSON input from stdin"""
    try:
        return json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        print(f"Error parsing hook input: {e}", file=sys.stderr)
        sys.exit(1)


def read_transcript(transcript_path: str) -> dict:
    """Read and parse the transcript JSONL file"""
    try:
        path = Path(transcript_path)
        with open(path) as f:
            lines = f.readlines()
            return json.loads(lines[-1])
    except FileNotFoundError:
        print(f"Transcript file not found: {transcript_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing transcript JSON: {e}", file=sys.stderr)
        sys.exit(1)


def validate_format(media_type: str):
    """Validate image format is supported"""
    if media_type not in SUPPORTED_FORMATS:
        format_name = media_type.split("/")[-1].upper()
        block_submission(
            f"Image format not supported: {format_name}. "
            f"Claude Code supports: PNG, JPEG, GIF. "
            f"To convert: Open image in your default image viewer, then Save As PNG or JPEG."
        )


def decode_image(base64_data: str, media_type: str) -> Image.Image:
    """Decode base64 image data to PIL Image"""
    try:
        img_bytes = base64.b64decode(base64_data)
        return Image.open(BytesIO(img_bytes))
    except UnidentifiedImageError:
        block_submission(
            "Unable to process image: file appears corrupted. "
            "Try: Save the screenshot again, or paste from a different source."
        )
    except Exception as e:
        block_submission(
            "Unable to process image: file appears corrupted. "
            "Try: Save the screenshot again, or paste from a different source."
        )


def calculate_resize_dimensions(width: int, height: int) -> tuple[int, int]:
    """
    Calculate new dimensions preserving aspect ratio

    Args:
        width: Original width
        height: Original height

    Returns:
        Tuple of (new_width, new_height)
    """
    if width >= height:
        # Width is longer dimension
        new_width = MAX_DIMENSION
        new_height = int(height * (MAX_DIMENSION / width))
    else:
        # Height is longer dimension
        new_height = MAX_DIMENSION
        new_width = int(width * (MAX_DIMENSION / height))

    return new_width, new_height


def resize_image(img: Image.Image, new_width: int, new_height: int) -> Image.Image:
    """Resize image using high-quality LANCZOS resampling"""
    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)


def encode_image(img: Image.Image, format: str) -> str:
    """Encode PIL Image to base64 string"""
    buffer = BytesIO()

    if format == "JPEG":
        # Convert RGBA to RGB for JPEG (no alpha channel support)
        if img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])  # Use alpha as mask
            img = background
        img.save(buffer, format=format, quality=95)
    else:
        # PNG and GIF - preserve alpha channel
        img.save(buffer, format=format)

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def process_transcript(transcript: dict) -> tuple[dict, list[str]]:
    """
    Process transcript and resize images as needed

    Args:
        transcript: The transcript dict

    Returns:
        Tuple of (modified_transcript, notifications)
    """
    notifications = []
    modified = False

    for block in transcript.get("content", []):
        if block.get("type") != "image":
            continue

        source = block.get("source", {})
        if source.get("type") != "base64":
            continue

        base64_data = source.get("data", "")
        media_type = source.get("media_type", "")

        # Validate format
        validate_format(media_type)

        # Decode image
        img = decode_image(base64_data, media_type)
        orig_width, orig_height = img.size

        # Check if resize needed
        max_dim = max(orig_width, orig_height)
        if max_dim <= MAX_DIMENSION:
            continue  # No resize needed

        # Calculate new dimensions
        new_width, new_height = calculate_resize_dimensions(orig_width, orig_height)

        # Resize image
        resized_img = resize_image(img, new_width, new_height)

        # Re-encode
        format = img.format or "PNG"
        new_base64_data = encode_image(resized_img, format)

        # Update transcript
        source["data"] = new_base64_data
        modified = True

        # Create notification
        notification = (
            f"Image resized to meet Claude Code 2000px limit: "
            f"{orig_width}x{orig_height} to {new_width}x{new_height}"
        )
        notifications.append(notification)

    return transcript, notifications


def write_transcript(transcript_path: str, transcript: dict):
    """Write transcript back to file"""
    path = Path(transcript_path)
    with open(path, "w") as f:
        f.write(json.dumps(transcript) + "\n")


def main():
    """Main hook execution"""
    # Read input
    hook_input = read_hook_input()

    # Check for plugin conflicts
    enabled_plugins = hook_input.get("enabled_plugins", [])
    if detect_plugin_conflict(enabled_plugins):
        warn_plugin_conflict()

    # Read configuration
    config = read_config()

    # Check if processing is enabled
    if not should_process(config):
        sys.exit(0)  # Silent skip when disabled

    transcript_path = hook_input.get("transcript_path")

    if not transcript_path:
        print("Missing transcript_path in hook input", file=sys.stderr)
        sys.exit(1)

    # Read transcript
    transcript = read_transcript(transcript_path)

    # Process images
    modified_transcript, notifications = process_transcript(transcript)

    # Write back if modified
    if notifications:
        write_transcript(transcript_path, modified_transcript)

    # Output notifications
    for notification in notifications:
        print(notification)

    sys.exit(0)


if __name__ == "__main__":
    main()
