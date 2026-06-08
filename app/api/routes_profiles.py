from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)

from app.deps import get_current_user
from app.schemas import (ProfileUpdate)
from app.services.profile_service import (
    get_profile,
    update_profile,
    #upload_profile_photo
)

router = APIRouter(
    prefix="/profile",
    tags=["profile"]
)

# =====================================================
# GET PROFILE
# =====================================================

@router.get("/")
def get_my_profile(
    user=Depends(get_current_user)
):
    try:

        res = get_profile(
            psychologist_id=user.id
        )

        return res.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =====================================================
# UPDATE PROFILE
# =====================================================

@router.patch("/")
def patch_profile(
    data: ProfileUpdate,
    user=Depends(get_current_user)
):
    try:

        update_data = data.model_dump(
            exclude_unset=True
        )

        res = update_profile(
            psychologist_id=user.id,
            data=update_data
        )

        return res.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =====================================================
# UPLOAD PHOTO
# =====================================================

#@router.post("/upload-photo")
#async def upload_photo(
#    file: UploadFile = File(...),
#    user=Depends(get_current_user)
#):
#    try:

#        result = await upload_profile_photo(
#            psychologist_id=user.id,
#            file=file
#        )

#       return result

#    except Exception as e:
#        raise HTTPException(
#            status_code=500,
#            detail=str(e)
#        )
