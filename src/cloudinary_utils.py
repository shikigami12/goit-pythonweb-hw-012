"""
Cloudinary integration utilities for file uploads.

This module handles file uploads to Cloudinary service for storing
user avatars and other media files.
"""
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
)


def upload_avatar(file, public_id):
    """
    Upload avatar image to Cloudinary.
    
    Args:
        file: File object to upload
        public_id: Public ID for the uploaded file
        
    Returns:
        URL of the uploaded file
    """
    r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)
    return r.get("url")
