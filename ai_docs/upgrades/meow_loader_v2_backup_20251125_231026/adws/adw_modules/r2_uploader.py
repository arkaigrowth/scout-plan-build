"""Cloudflare R2 uploader for ADW screenshots."""

import os
import logging
from typing import Optional, Dict, List
from pathlib import Path
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError


class R2Uploader:
    """Handle uploads to Cloudflare R2 public bucket."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.client = None
        self.bucket_name = None
        self.public_domain = None
        self.enabled = False
        
        # Initialize if all required env vars exist
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize R2 client if all required environment variables are set."""
        account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        access_key_id = os.getenv("CLOUDFLARE_R2_ACCESS_KEY_ID")
        secret_access_key = os.getenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY")
        self.bucket_name = os.getenv("CLOUDFLARE_R2_BUCKET_NAME")
        self.public_domain = os.getenv("CLOUDFLARE_R2_PUBLIC_DOMAIN", "tac-public-imgs.iddagents.com")
        
        # Check if all required vars are present
        if not all([account_id, access_key_id, secret_access_key, self.bucket_name]):
            self.logger.info("R2 upload disabled - missing required environment variables")
            return
        
        try:
            # Create R2 client
            self.client = boto3.client(
                's3',
                endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                config=Config(signature_version='s3v4'),
                region_name='us-east-1'
            )
            self.enabled = True
            self.logger.info(f"R2 upload enabled - bucket: {self.bucket_name}, domain: {self.public_domain}")
        except Exception as e:
            self.logger.warning(f"Failed to initialize R2 client: {e}")
            self.enabled = False
    
    def upload_file(self, file_path: str, object_key: Optional[str] = None) -> Optional[str]:
        """
        Upload a file to R2 and return the public URL.
        
        Args:
            file_path: Path to the file to upload (absolute or relative)
            object_key: Optional S3 object key. If not provided, will use default pattern
            
        Returns:
            Public URL if upload successful, None if upload is disabled or fails
        """
        if not self.enabled:
            return None
        
        # Convert to absolute path if relative
        if not os.path.isabs(file_path):
            self.logger.info(f"Converting relative path to absolute: {file_path}")
            file_path = os.path.abspath(file_path)
            self.logger.info(f"Absolute path: {file_path}")
            
        if not os.path.exists(file_path):
            self.logger.warning(f"File not found at absolute path: {file_path}")
            return None
        
        # Generate object key if not provided
        if not object_key:
            # Use pattern: adw/{adw_id}/review/{filename}
            object_key = f"adw/review/{Path(file_path).name}"
        
        try:
            # Upload file
            self.client.upload_file(file_path, self.bucket_name, object_key)
            self.logger.info(f"Uploaded {file_path} to R2 as {object_key}")
            
            # Generate public URL
            public_url = f"https://{self.public_domain}/{object_key}"
            return public_url
            
        except ClientError as e:
            self.logger.error(f"Failed to upload {file_path} to R2: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error uploading to R2: {e}")
            return None
    
    def upload_screenshots(self, screenshots: List[str], adw_id: str) -> Dict[str, str]:
        """
        Upload multiple screenshots and return mapping of local paths to public URLs.
        
        Args:
            screenshots: List of local screenshot file paths
            adw_id: ADW workflow ID for organizing uploads
            
        Returns:
            Dict mapping local paths to public URLs (or original paths if upload disabled/failed)
        """
        url_mapping = {}
        
        for screenshot_path in screenshots:
            if not screenshot_path:
                continue
                
            # Generate object key with ADW ID for organization
            filename = Path(screenshot_path).name
            object_key = f"adw/{adw_id}/review/{filename}"
            
            # Upload and get public URL
            public_url = self.upload_file(screenshot_path, object_key)
            
            # Map to public URL if successful, otherwise keep original path
            url_mapping[screenshot_path] = public_url or screenshot_path
            
        return url_mapping