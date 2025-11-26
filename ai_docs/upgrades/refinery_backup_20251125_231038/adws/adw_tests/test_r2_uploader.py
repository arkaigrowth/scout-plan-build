#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "boto3>=1.26.0", "requests"]
# ///

"""
Test R2 Uploader - Real upload test to verify Cloudflare R2 setup

Usage:
    uv run adws/adw_tests/test_r2_uploader.py

This will:
1. Upload app/client/public/bg.png to R2
2. Verify the upload succeeded
3. Check if the public URL is accessible
4. Clean up the test file (optional)
"""

import os
import sys
import logging
from pathlib import Path
import requests
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from adw_modules.r2_uploader import R2Uploader

# Load environment variables
load_dotenv()


def setup_logger() -> logging.Logger:
    """Set up a simple logger for the test."""
    logger = logging.getLogger("test_r2_uploader")
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


def test_r2_upload():
    """Test uploading an image to R2."""
    logger = setup_logger()

    print("🧪 R2 Uploader Test")
    print("=" * 50)

    # Check environment variables
    required_vars = [
        "CLOUDFLARE_ACCOUNT_ID",
        "CLOUDFLARE_R2_ACCESS_KEY_ID",
        "CLOUDFLARE_R2_SECRET_ACCESS_KEY",
        "CLOUDFLARE_R2_BUCKET_NAME",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("\n❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables and try again.")
        return False

    # Initialize R2 uploader
    print("\n1️⃣ Initializing R2 Uploader...")
    uploader = R2Uploader(logger)

    if not uploader.enabled:
        print("❌ R2 Uploader failed to initialize. Check your credentials.")
        return False

    print("✅ R2 Uploader initialized successfully")
    print(f"   Bucket: {uploader.bucket_name}")
    print(f"   Domain: {uploader.public_domain}")

    # Find test file
    test_file = "app/client/public/bg.png"
    print(f"\n2️⃣ Looking for test file: {test_file}")

    # The uploader will handle path resolution, but let's check manually too
    project_root = Path(__file__).parent.parent.parent
    full_path = project_root / test_file

    if not full_path.exists():
        print(f"❌ Test file not found at: {full_path}")
        return False

    print(f"✅ Found test file: {full_path}")
    print(f"   Size: {full_path.stat().st_size:,} bytes")

    # Upload the file
    print(f"\n3️⃣ Uploading to R2...")

    # Generate a unique object key for testing
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    object_key = f"adw/test/r2_upload_test_{timestamp}_bg.png"

    public_url = uploader.upload_file(str(test_file), object_key)

    if not public_url:
        print("❌ Upload failed! Check the logs above for details.")
        return False

    print(f"✅ Upload successful!")
    print(f"   URL: {public_url}")

    # Test if the URL is accessible
    print(f"\n4️⃣ Testing public URL accessibility...")

    try:
        response = requests.head(public_url, timeout=10)
        if response.status_code == 200:
            print(f"✅ URL is publicly accessible!")
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(
                f"   Content-Length: {response.headers.get('Content-Length', 'N/A')} bytes"
            )
        else:
            print(f"⚠️  URL returned status code: {response.status_code}")
            print("   The file might be uploaded but not publicly accessible.")
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Could not verify URL accessibility: {e}")
        print("   This might be normal if the bucket isn't fully public yet.")

    # Test batch upload
    print(f"\n5️⃣ Testing batch upload with multiple paths...")

    test_screenshots = [
        test_file,  # This should work
        "nonexistent/file.png",  # This should fail gracefully
        full_path.as_posix(),  # Absolute path should work
    ]

    url_mapping = uploader.upload_screenshots(test_screenshots, "test_adw_id")

    print(f"✅ Batch upload completed")
    print(f"   Total files: {len(test_screenshots)}")
    print(
        f"   Successful uploads: {sum(1 for v in url_mapping.values() if v.startswith('http'))}"
    )

    for original, result in url_mapping.items():
        if result.startswith("http"):
            print(f"   ✅ {Path(original).name} → {result}")
        else:
            print(f"   ❌ {Path(original).name} → (failed, kept original path)")

    # Summary
    print("\n" + "=" * 50)
    print("✅ R2 Upload Test Complete!")
    print("\nYour R2 setup is working correctly. You can now:")
    print("1. View your uploaded test image at:")
    print(f"   {public_url}")
    print("2. Check your R2 bucket in the Cloudflare dashboard")
    print("3. Run ADW reviews - screenshots will be automatically uploaded")

    return True


def main():
    """Main entry point."""
    success = test_r2_upload()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
