import os
import uuid
import aiofiles

from fastapi import (
    UploadFile,
    HTTPException)

from app.supabase import get_supabase

PROFILE_PHOTOS_DIR = "storage/profile_photos"

ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp"
]

MAX_PHOTO_SIZE = 10 * 1024 * 1024

def get_profile(
    psychologist_id: str
):
    supabase = get_supabase()

    return (
        supabase
        .table("profiles")
        .select("*")
        .eq("id", psychologist_id)
        .single()
        .execute()
    )


def update_profile(
    psychologist_id: str,
    data: dict
):
    supabase = get_supabase()

    return (
        supabase
        .table("profiles")
        .update(data)
        .eq("id", psychologist_id)
        .execute()
    )

async def upload_profile_photo(
    psychologist_id: str,
    file: UploadFile
):

    supabase = get_supabase()

    # -----------------------------------------
    # VALIDATE FILE TYPE
    # -----------------------------------------

    if file.content_type not in ALLOWED_IMAGE_TYPES:

        raise HTTPException(
            status_code=400,
            detail="Unsupported image format"
        )

    # -----------------------------------------
    # CREATE DIRECTORY
    # -----------------------------------------

    os.makedirs(
        PROFILE_PHOTOS_DIR,
        exist_ok=True
    )

    # -----------------------------------------
    # GENERATE SAFE FILENAME
    # -----------------------------------------

    extension = os.path.splitext(
        file.filename
    )[1]

    filename = (
        f"{psychologist_id}_{uuid.uuid4()}"
        f"{extension}"
    )

    file_path = os.path.join(
        PROFILE_PHOTOS_DIR,
        filename
    )

    # -----------------------------------------
    # SAVE FILE
    # -----------------------------------------

    size = 0

    async with aiofiles.open(
        file_path,
        "wb"
    ) as out_file:

        while chunk := await file.read(1024 * 1024):

            size += len(chunk)

            if size > MAX_PHOTO_SIZE:

                raise HTTPException(
                    status_code=400,
                    detail="Image too large"
                )

            await out_file.write(chunk)

    # -----------------------------------------
    # -----------------------------------------
    # PUBLIC URL
    # -----------------------------------------

    photo_url = (
        f"/storage/profile_photos/{filename}"
    )

    # -----------------------------------------
    # UPDATE PROFILE
    # -----------------------------------------

    (
        supabase
        .table("profiles")
        .update({
            "photo_url": photo_url
        })
        .eq("id", psychologist_id)
        .execute()
    )

    # -----------------------------------------
    # RESPONSE
    # -----------------------------------------

    return {
        "status": "uploaded",
        "photo_url": photo_url,
        "filename": filename,
        "size_bytes": size
    }
