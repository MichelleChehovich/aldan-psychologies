from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.deps import get_current_user

from app.schemas import (
    ClientCreate,
    ClientUpdate
)

from app.services.client_service import (
    create_client,
    get_clients,
    get_archived_clients,
    get_client_by_id,
    update_client,
    archive_client,
    restore_client
)

router = APIRouter(
    prefix="/clients",
    tags=["clients"]
)


# =====================================================
# CREATE
# =====================================================

@router.post("/")
def create_new_client(
    data: ClientCreate,
    user=Depends(get_current_user)
):
    try:

        res = create_client(
            psychologist_id=user.id,
            data=data.model_dump()
        )

        return res.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# ACTIVE CLIENTS
# =====================================================

@router.get("/")
def get_all_clients(
    user=Depends(get_current_user)
):
    try:

        res = get_clients(
            psychologist_id=user.id
        )

        return res.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# ARCHIVE
# =====================================================

@router.get("/archive")
def get_archive(
    user=Depends(get_current_user)
):
    try:

        res = get_archived_clients(
            psychologist_id=user.id
        )

        return res.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# GET CLIENT
# =====================================================

@router.get("/{client_id}")
def get_client(
    client_id: str,
    user=Depends(get_current_user)
):
    try:

        res = get_client_by_id(
            psychologist_id=user.id,
            client_id=client_id
        )

        return res.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# UPDATE
# =====================================================

@router.patch("/{client_id}")
def patch_client(
    client_id: str,
    data: ClientUpdate,
    user=Depends(get_current_user)
):
    try:

        res = update_client(
            psychologist_id=user.id,
            client_id=client_id,
            data=data.model_dump(
                exclude_unset=True
            )
        )

        return res.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# ARCHIVE CLIENT
# =====================================================

@router.patch("/{client_id}/archive")
def archive(
    client_id: str,
    user=Depends(get_current_user)
):
    try:

        archive_client(
            psychologist_id=user.id,
            client_id=client_id
        )

        return {
            "status": "archived",
            "client_id": client_id
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# RESTORE CLIENT
# =====================================================

@router.patch("/{client_id}/restore")
def restore(
    client_id: str,
    user=Depends(get_current_user)
):
    try:

        restore_client(
            psychologist_id=user.id,
            client_id=client_id
        )

        return {
            "status": "restored",
            "client_id": client_id
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
