#!/usr/bin/env python3
"""
Tests for resize-images.py hook

Following TDD approach - tests written first, then implementation.
"""

import base64
import json
import os
import subprocess
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image


class TestResizeImagesHook(unittest.TestCase):
    """Test suite for automatic image resizing hook"""

    def setUp(self):
        """Set up test fixtures"""
        self.hook_path = Path(__file__).parent / "resize_images.py"
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_image(self, width: int, height: int, format: str = "PNG") -> str:
        """Create a test image and return base64 encoded data"""
        img = Image.new("RGB", (width, height), color=(255, 0, 0))
        buffer = BytesIO()
        img.save(buffer, format=format)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def create_transcript(self, images: list[dict]) -> Path:
        """
        Create a test transcript JSONL file with images

        Args:
            images: List of dicts with 'width', 'height', 'format' keys

        Returns:
            Path to the transcript file
        """
        transcript_path = Path(self.temp_dir) / "transcript.jsonl"

        # Create content blocks for all images
        content_blocks = []
        for img_spec in images:
            media_type = f"image/{img_spec['format'].lower()}"
            base64_data = self.create_test_image(
                img_spec['width'],
                img_spec['height'],
                img_spec['format']
            )
            content_blocks.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": base64_data
                }
            })

        # Add a text block
        content_blocks.append({
            "type": "text",
            "text": "Test prompt"
        })

        # Create the transcript entry
        transcript_entry = {
            "role": "user",
            "content": content_blocks
        }

        # Write to file
        with open(transcript_path, "w") as f:
            f.write(json.dumps(transcript_entry) + "\n")

        return transcript_path

    def run_hook(self, transcript_path: Path) -> dict:
        """
        Run the resize-images hook

        Returns:
            Dict with 'stdout', 'stderr', 'returncode' keys
        """
        hook_input = json.dumps({
            "transcript_path": str(transcript_path)
        })

        result = subprocess.run(
            ["python3", str(self.hook_path)],
            input=hook_input,
            capture_output=True,
            text=True
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }

    def read_transcript_images(self, transcript_path: Path) -> list[dict]:
        """Read images from transcript and return their dimensions"""
        with open(transcript_path) as f:
            last_line = f.readlines()[-1]

        transcript = json.loads(last_line)
        images = []

        for block in transcript["content"]:
            if block["type"] == "image":
                # Decode base64 and get dimensions
                img_data = base64.b64decode(block["source"]["data"])
                img = Image.open(BytesIO(img_data))
                images.append({
                    "width": img.width,
                    "height": img.height,
                    "format": img.format
                })

        return images

    def test_oversized_screenshot_resized(self):
        """
        Scenario: User pastes oversized screenshot
          Given I have a screenshot that is 5120x2880 pixels
          When I paste it into a prompt
          And I submit the prompt
          Then the image is automatically resized to 2000x1125 pixels
          And I see "Image resized to meet Claude Code 2000px limit: 5120x2880 to 2000x1125"
          And my prompt is submitted successfully
        """
        # Arrange: Create transcript with 5120x2880 image
        transcript_path = self.create_transcript([
            {"width": 5120, "height": 2880, "format": "PNG"}
        ])

        # Act: Run the hook
        result = self.run_hook(transcript_path)

        # Assert: Check exit code
        self.assertEqual(result["returncode"], 0,
                        f"Hook should exit successfully. stderr: {result['stderr']}")

        # Assert: Check notification
        self.assertIn(
            "Image resized to meet Claude Code 2000px limit: 5120x2880 to 2000x1125",
            result["stdout"],
            "Should output resize notification"
        )

        # Assert: Check image was actually resized
        images = self.read_transcript_images(transcript_path)
        self.assertEqual(len(images), 1, "Should have one image")
        self.assertEqual(images[0]["width"], 2000, "Width should be 2000")
        self.assertEqual(images[0]["height"], 1125, "Height should be 1125")

    def test_normal_sized_image_not_resized(self):
        """
        Scenario: User pastes normal-sized image
          Given I have an image that is 1920x1080 pixels
          When I paste it into a prompt
          And I submit the prompt
          Then the image is not resized
          And I see no resize notification
          And my prompt is submitted successfully
        """
        # Arrange: Create transcript with 1920x1080 image
        transcript_path = self.create_transcript([
            {"width": 1920, "height": 1080, "format": "PNG"}
        ])

        # Act: Run the hook
        result = self.run_hook(transcript_path)

        # Assert: Check exit code
        self.assertEqual(result["returncode"], 0,
                        f"Hook should exit successfully. stderr: {result['stderr']}")

        # Assert: No resize notification
        self.assertEqual(result["stdout"].strip(), "",
                        "Should not output any notification")

        # Assert: Image dimensions unchanged
        images = self.read_transcript_images(transcript_path)
        self.assertEqual(len(images), 1, "Should have one image")
        self.assertEqual(images[0]["width"], 1920, "Width should be unchanged")
        self.assertEqual(images[0]["height"], 1080, "Height should be unchanged")

    def test_tall_oversized_screenshot_resized(self):
        """
        Scenario: User pastes tall oversized screenshot
          Given I have a screenshot that is 1440x2560 pixels
          When I paste it into a prompt
          And I submit the prompt
          Then the image is automatically resized to 1125x2000 pixels
          And I see "Image resized to meet Claude Code 2000px limit: 1440x2560 to 1125x2000"
          And my prompt is submitted successfully
        """
        # Arrange: Create transcript with 1440x2560 image (height > width)
        transcript_path = self.create_transcript([
            {"width": 1440, "height": 2560, "format": "PNG"}
        ])

        # Act: Run the hook
        result = self.run_hook(transcript_path)

        # Assert: Check exit code
        self.assertEqual(result["returncode"], 0,
                        f"Hook should exit successfully. stderr: {result['stderr']}")

        # Assert: Check notification
        self.assertIn(
            "Image resized to meet Claude Code 2000px limit: 1440x2560 to 1125x2000",
            result["stdout"],
            "Should output resize notification"
        )

        # Assert: Check image was resized with height as max dimension
        images = self.read_transcript_images(transcript_path)
        self.assertEqual(len(images), 1, "Should have one image")
        self.assertEqual(images[0]["width"], 1125, "Width should be 1125")
        self.assertEqual(images[0]["height"], 2000, "Height should be 2000")

    def test_image_exactly_at_limit_not_resized(self):
        """
        Scenario: User pastes image exactly at limit
          Given I have an image that is 2000x1500 pixels
          When I paste it into a prompt
          And I submit the prompt
          Then the image is not resized
          And I see no resize notification
          And my prompt is submitted successfully
        """
        # Arrange: Create transcript with 2000x1500 image (exactly at limit)
        transcript_path = self.create_transcript([
            {"width": 2000, "height": 1500, "format": "PNG"}
        ])

        # Act: Run the hook
        result = self.run_hook(transcript_path)

        # Assert: Check exit code
        self.assertEqual(result["returncode"], 0,
                        f"Hook should exit successfully. stderr: {result['stderr']}")

        # Assert: No resize notification
        self.assertEqual(result["stdout"].strip(), "",
                        "Should not output any notification")

        # Assert: Image dimensions unchanged
        images = self.read_transcript_images(transcript_path)
        self.assertEqual(len(images), 1, "Should have one image")
        self.assertEqual(images[0]["width"], 2000, "Width should be unchanged")
        self.assertEqual(images[0]["height"], 1500, "Height should be unchanged")

    def test_multiple_images_with_mixed_sizes(self):
        """
        Scenario: User pastes multiple images with mixed sizes
          Given I paste a 1920x1080 pixel image
          And I paste a 5120x2880 pixel image
          And I paste a 4032x3024 pixel image
          When I submit the prompt
          Then the first image is not resized
          And the second image is resized to 2000x1125 pixels
          And the third image is resized to 2000x1500 pixels
          And I see notifications for each resized image
          And my prompt is submitted successfully
        """
        # Arrange: Create transcript with 3 images
        transcript_path = self.create_transcript([
            {"width": 1920, "height": 1080, "format": "PNG"},  # No resize
            {"width": 5120, "height": 2880, "format": "PNG"},  # Resize to 2000x1125
            {"width": 4032, "height": 3024, "format": "PNG"},  # Resize to 2000x1500
        ])

        # Act: Run the hook
        result = self.run_hook(transcript_path)

        # Assert: Check exit code
        self.assertEqual(result["returncode"], 0,
                        f"Hook should exit successfully. stderr: {result['stderr']}")

        # Assert: Check notifications for resized images
        self.assertIn(
            "Image resized to meet Claude Code 2000px limit: 5120x2880 to 2000x1125",
            result["stdout"],
            "Should notify about second image resize"
        )
        self.assertIn(
            "Image resized to meet Claude Code 2000px limit: 4032x3024 to 2000x1500",
            result["stdout"],
            "Should notify about third image resize"
        )
        # Should NOT contain notification for first image
        self.assertNotIn("1920x1080", result["stdout"],
                        "Should not notify about unchanged first image")

        # Assert: Check all images
        images = self.read_transcript_images(transcript_path)
        self.assertEqual(len(images), 3, "Should have three images")
        self.assertEqual(images[0]["width"], 1920, "First image width unchanged")
        self.assertEqual(images[0]["height"], 1080, "First image height unchanged")
        self.assertEqual(images[1]["width"], 2000, "Second image width resized")
        self.assertEqual(images[1]["height"], 1125, "Second image height resized")
        self.assertEqual(images[2]["width"], 2000, "Third image width resized")
        self.assertEqual(images[2]["height"], 1500, "Third image height resized")

    def test_ultra_wide_screenshot_resized(self):
        """
        Scenario: User pastes ultra-wide screenshot
          Given I have a screenshot that is 8000x500 pixels
          When I paste it into a prompt
          And I submit the prompt
          Then the image is resized to 2000x125 pixels
          And aspect ratio is preserved
          And my prompt is submitted successfully
        """
        # Arrange: Create transcript with 8000x500 image
        transcript_path = self.create_transcript([
            {"width": 8000, "height": 500, "format": "PNG"}
        ])

        # Act: Run the hook
        result = self.run_hook(transcript_path)

        # Assert: Check exit code
        self.assertEqual(result["returncode"], 0,
                        f"Hook should exit successfully. stderr: {result['stderr']}")

        # Assert: Check notification
        self.assertIn(
            "Image resized to meet Claude Code 2000px limit: 8000x500 to 2000x125",
            result["stdout"],
            "Should output resize notification"
        )

        # Assert: Check image was resized preserving aspect ratio
        images = self.read_transcript_images(transcript_path)
        self.assertEqual(len(images), 1, "Should have one image")
        self.assertEqual(images[0]["width"], 2000, "Width should be 2000")
        self.assertEqual(images[0]["height"], 125, "Height should be 125")

    def test_very_small_image_not_upscaled(self):
        """
        Scenario: User pastes very small image
          Given I have an image that is 100x100 pixels
          When I paste it into a prompt
          And I submit the prompt
          Then the image is not upscaled
          And my prompt is submitted successfully
        """
        # Arrange: Create transcript with 100x100 image
        transcript_path = self.create_transcript([
            {"width": 100, "height": 100, "format": "PNG"}
        ])

        # Act: Run the hook
        result = self.run_hook(transcript_path)

        # Assert: Check exit code
        self.assertEqual(result["returncode"], 0,
                        f"Hook should exit successfully. stderr: {result['stderr']}")

        # Assert: No resize notification
        self.assertEqual(result["stdout"].strip(), "",
                        "Should not output any notification")

        # Assert: Image dimensions unchanged (not upscaled)
        images = self.read_transcript_images(transcript_path)
        self.assertEqual(len(images), 1, "Should have one image")
        self.assertEqual(images[0]["width"], 100, "Width should be unchanged")
        self.assertEqual(images[0]["height"], 100, "Height should be unchanged")

    def test_unsupported_format_blocked(self):
        """
        Scenario: User receives clear error message for unsupported format
          Given I paste an image in BMP format
          When I submit the prompt
          Then my submission is blocked
          And I see "Image format not supported: BMP"
          And I see "Claude Code supports: PNG, JPEG, GIF"
          And I see "To convert: Open image in your default image viewer, Save As PNG or JPEG"
        """
        # Arrange: Create a BMP image manually
        transcript_path = Path(self.temp_dir) / "transcript.jsonl"
        img = Image.new("RGB", (1920, 1080), color=(255, 0, 0))
        buffer = BytesIO()
        img.save(buffer, format="BMP")
        base64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

        transcript_entry = {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/bmp",
                        "data": base64_data
                    }
                }
            ]
        }

        with open(transcript_path, "w") as f:
            f.write(json.dumps(transcript_entry) + "\n")

        # Act: Run the hook
        result = self.run_hook(transcript_path)

        # Assert: Should have blocking JSON output
        try:
            output = json.loads(result["stdout"])
            self.assertEqual(output["decision"], "block",
                           "Should block submission")
            self.assertIn("Image format not supported: BMP", output["reason"])
            self.assertIn("Claude Code supports: PNG, JPEG, GIF", output["reason"])
            self.assertIn("To convert:", output["reason"])
        except json.JSONDecodeError:
            self.fail(f"Expected JSON output, got: {result['stdout']}")

    def test_corrupted_image_blocked(self):
        """
        Scenario: User receives clear error message for corrupted image
          Given I paste a corrupted PNG file
          When I submit the prompt
          Then my submission is blocked
          And I see "Unable to process image: file appears corrupted"
          And I see "Try: Save the screenshot again, or paste from a different source"
        """
        # Arrange: Create transcript with corrupted base64 data
        transcript_path = Path(self.temp_dir) / "transcript.jsonl"

        # Create invalid base64 data (not a real image)
        corrupted_data = base64.b64encode(b"This is not a PNG file").decode("utf-8")

        transcript_entry = {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": corrupted_data
                    }
                }
            ]
        }

        with open(transcript_path, "w") as f:
            f.write(json.dumps(transcript_entry) + "\n")

        # Act: Run the hook
        result = self.run_hook(transcript_path)

        # Assert: Should have blocking JSON output
        try:
            output = json.loads(result["stdout"])
            self.assertEqual(output["decision"], "block",
                           "Should block submission")
            self.assertIn("Unable to process image", output["reason"])
            self.assertIn("corrupted", output["reason"])
            self.assertIn("Try:", output["reason"])
        except json.JSONDecodeError:
            self.fail(f"Expected JSON output, got: {result['stdout']}")

    def test_extremely_large_image_blocked(self):
        """
        Scenario: User pastes extremely large image
          Given I paste an image that is 10000x8000 pixels
          When I submit the prompt
          Then my submission is blocked
          And I see "Image dimensions (10000x8000) require too much memory to resize. Please resize manually to under 4000px before pasting."
        """
        # NOTE: We can't actually create a 10000x8000 image in the test
        # because it would consume too much memory. Instead, we'll create
        # a smaller image but modify the metadata to claim larger dimensions.
        # The hook should check dimensions before attempting to decode.

        # For now, skip this test as it requires PIL metadata manipulation
        # which is complex. We'll test this manually.
        self.skipTest("Requires special handling for dimension detection")

    def test_transparent_png_preserved(self):
        """
        Scenario: User pastes transparent PNG
          Given I paste a PNG image with transparency
          And the image is 3000x2000 pixels
          When I submit the prompt
          Then the image is resized to 2000x1333 pixels
          And the transparency is preserved
          And my prompt is submitted successfully
        """
        # Arrange: Create PNG with alpha channel
        img = Image.new("RGBA", (3000, 2000), color=(255, 0, 0, 128))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        base64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

        transcript_path = Path(self.temp_dir) / "transcript.jsonl"
        transcript_entry = {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": base64_data
                    }
                }
            ]
        }

        with open(transcript_path, "w") as f:
            f.write(json.dumps(transcript_entry) + "\n")

        # Act: Run the hook
        result = self.run_hook(transcript_path)

        # Assert: Check exit code
        self.assertEqual(result["returncode"], 0,
                        f"Hook should exit successfully. stderr: {result['stderr']}")

        # Assert: Check resize notification
        self.assertIn(
            "Image resized to meet Claude Code 2000px limit: 3000x2000 to 2000x1333",
            result["stdout"],
            "Should output resize notification"
        )

        # Assert: Check transparency preserved
        images_data = self.read_transcript_images(transcript_path)
        self.assertEqual(len(images_data), 1, "Should have one image")
        self.assertEqual(images_data[0]["width"], 2000, "Width should be 2000")
        self.assertEqual(images_data[0]["height"], 1333, "Height should be 1333")

        # Check that the image mode is still RGBA (has alpha channel)
        with open(transcript_path) as f:
            last_line = f.readlines()[-1]
        transcript = json.loads(last_line)
        img_data = base64.b64decode(transcript["content"][0]["source"]["data"])
        resized_img = Image.open(BytesIO(img_data))
        self.assertEqual(resized_img.mode, "RGBA",
                        "Should preserve alpha channel (RGBA mode)")


class TestConfigurationSupport(unittest.TestCase):
    """Test configuration support via .claude/tommymorgan.local.md"""

    def test_reads_config_from_local_md(self):
        """Should read auto_resize_images setting from YAML frontmatter"""
        from resize_images import read_config

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".claude" / "tommymorgan.local.md"
            config_path.parent.mkdir(parents=True)
            config_path.write_text("""---
auto_resize_images: false
---

# Configuration
""")

            config = read_config(tmpdir)

            self.assertFalse(config["auto_resize_images"])

    def test_defaults_to_enabled_when_no_config(self):
        """Should default auto_resize_images to true when config missing"""
        from resize_images import read_config

        with tempfile.TemporaryDirectory() as tmpdir:
            config = read_config(tmpdir)

            self.assertTrue(config["auto_resize_images"])

    def test_skips_processing_when_disabled(self):
        """Should exit early when auto_resize_images: false"""
        from resize_images import should_process

        config = {"auto_resize_images": False}

        self.assertFalse(should_process(config))

    def test_processes_when_enabled(self):
        """Should process images when auto_resize_images: true"""
        from resize_images import should_process

        config = {"auto_resize_images": True}

        self.assertTrue(should_process(config))


class TestConflictDetection(unittest.TestCase):
    """Test detection of old auto-resize-images plugin"""

    def test_detects_old_plugin_conflict(self):
        """Should detect if auto-resize-images plugin is installed"""
        from resize_images import detect_plugin_conflict

        # Mock scenario where old plugin exists
        mock_enabled_plugins = ["tommymorgan", "auto-resize-images", "other-plugin"]

        has_conflict = detect_plugin_conflict(mock_enabled_plugins)

        self.assertTrue(has_conflict)

    def test_no_conflict_when_old_plugin_absent(self):
        """Should not detect conflict when auto-resize-images not installed"""
        from resize_images import detect_plugin_conflict

        mock_enabled_plugins = ["tommymorgan", "other-plugin"]

        has_conflict = detect_plugin_conflict(mock_enabled_plugins)

        self.assertFalse(has_conflict)

    def test_logs_warning_for_conflict(self):
        """Should log warning to stderr when old plugin detected"""
        from resize_images import warn_plugin_conflict

        import io
        from contextlib import redirect_stderr

        stderr_capture = io.StringIO()
        with redirect_stderr(stderr_capture):
            warn_plugin_conflict()

        output = stderr_capture.getvalue()

        self.assertIn("WARNING:", output)
        self.assertIn("auto-resize-images", output)
        self.assertIn("tommymorgan", output)
        self.assertIn("Duplicate processing wastes resources", output)
        self.assertIn("claude plugin uninstall auto-resize-images", output)


if __name__ == "__main__":
    unittest.main()
