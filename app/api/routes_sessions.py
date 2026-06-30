from fastapi import (
    BackgroundTasks,
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)

from app.deps import get_current_user
from app.supabase import get_supabase
from app.services.tasks.session_processing import process_session_audio, 
                                                  process_session_transcript

from app.services.agent_task_service import get_agent_statuses

from app.schemas import (
    SessionCreate,
    SessionMetaUpdate,
    SessionAudioUpdate,
    SessionSelfAnalysisUpdate
)

from app.services.session_service import (
    create_session,
    get_sessions,
    get_session_by_id,
    get_client_sessions,
    update_session_meta,
    update_session_audio,
    update_self_analysis,
    upload_audio_file,
    upload_self_analysis_audio
)

router = APIRouter(prefix="/sessions", tags=["sessions"])

# =====================================================
# READ PROCESSING LOG
# =====================================================

@router.get("/processing-log")
async def get_processing_log(user=Depends(get_current_user)):
    """Read processing log"""
    try:
        with open("/app/storage/processing.log", "r") as f:
            return {"log": f.read()}
    except FileNotFoundError:
        return {"log": "No log file yet"}

# =====================================================
# CREATE SESSION
# =====================================================

@router.post("/")
def create_new_session(
    data: SessionCreate,
    user=Depends(get_current_user)
):
    try:
        res = create_session(
            psychologist_id=user.id,
            client_id=data.client_id,
            session_date=data.session_date,
            title=data.title,
            duration_minutes=data.duration_minutes,
            status=data.status
        )

        return res.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# GET ALL SESSIONS
# =====================================================

@router.get("/")
def get_all_sessions(
    user=Depends(get_current_user)
):
    try:
        res = get_sessions(
            psychologist_id=user.id
        )

        return res.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# GET SESSION BY ID
# =====================================================

@router.get("/{session_id}")
def get_session(
    session_id: str,
    user=Depends(get_current_user)
):
    try:
        res = get_session_by_id(
            psychologist_id=user.id,
            session_id=session_id
        )

        return res.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# GET ALL CLIENT SESSIONS
# =====================================================

@router.get("/client/{client_id}")
def get_sessions_by_client(
    client_id: str,
    user=Depends(get_current_user)
):
    try:
        res = get_client_sessions(
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
# UPDATE SESSION META
# =====================================================

@router.patch("/{session_id}/meta")
def patch_session_meta(
    session_id: str,
    data: SessionMetaUpdate,
    user=Depends(get_current_user)
):
    try:
        update_data = data.model_dump(
            exclude_unset=True
        )

        if "session_date" in update_data:
            update_data["session_date"] = (
                update_data["session_date"].isoformat()
            )

        res = update_session_meta(
            psychologist_id=user.id,
            session_id=session_id,
            data=update_data
        )

        return res.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# UPDATE AUDIO URL
# =====================================================

@router.patch("/{session_id}/audio")
def patch_audio(
    session_id: str,
    data: SessionAudioUpdate,
    user=Depends(get_current_user)
):
    try:
        res = update_session_audio(
            psychologist_id=user.id,
            session_id=session_id,
            audio_url=data.audio_url
        )

        return res.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# UPDATE SELF ANALYSIS
# =====================================================

@router.patch("/{session_id}/self-analysis")
def patch_self_analysis(
    session_id: str,
    data: SessionSelfAnalysisUpdate,
    user=Depends(get_current_user)
):
    try:
        res = update_self_analysis(
            psychologist_id=user.id,
            session_id=session_id,
            analysis_self=data.analysis_self
        )

        return res.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# UPLOAD SESSION AUDIO FILE
# =====================================================

@router.post("/{session_id}/upload-audio")
async def upload_audio(
    session_id: str,
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    try:

        result = await upload_audio_file(
            psychologist_id=user.id,
            session_id=session_id,
            file=file
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# UPLOAD SELF ANALYSIS AUDIO
# =====================================================

@router.post(
    "/{session_id}/upload-self-analysis-audio"
)
async def upload_self_analysis_audio_endpoint(
    session_id: str,
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    try:

        result = await upload_self_analysis_audio(
            psychologist_id=user.id,
            session_id=session_id,
            file=file
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =====================================================
# Запустите конвейер фоновой обработки звука для сеанса.
# =====================================================

@router.post("/{session_id}/process")
async def start_processing(
    session_id: str,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user),
):
    """
    Start background audio processing pipeline for a session.
    """
    background_tasks.add_task(
        process_session_audio,
        session_id,
        user.id,  # ← передаём user.id, а не объект user
    )
    return {"status": "processing_started", "session_id": session_id}


# =====================================================
# Получите текущее состояние всех агентов обработки
# =====================================================

@router.get("/{session_id}/agents")
async def get_agents_status(
    session_id: str,
    user=Depends(get_current_user),
):
    """
    Get current status of all processing agents for a session.
    """
    result = get_agent_statuses(session_id)
    return result.data

# =====================================================
# Быстрый тест в обход всего пайплайна  для проверки только транскрибации
# =====================================================

@router.post("/test-transcription")
async def test_transcription(
    provider: str = "proxyapi",
    user=Depends(get_current_user),
):
    """Test transcription with a small audio file"""
    from app.stt import transcribe_audio
    import os
    
    # Use the last uploaded audio file, or specify path
    audio_dir = "storage/temp_audio/sessions"
    files = os.listdir(audio_dir)
    if not files:
        return {"error": "No audio files found"}
    
    audio_path = os.path.join(audio_dir, files[-1])
    
    try:
        transcript = await transcribe_audio(audio_path, provider)
        return {"status": "ok", "transcript": transcript[:500] + "..."}
    except Exception as e:
        return {"error": str(e)}

# =====================================================
# Эндпоинт для проверки LLM
# =====================================================

@router.post("/test-llm")
async def test_llm(provider: str = "proxyapi", user=Depends(get_current_user)):
    """Test LLM chat completion"""
    from app.llm import chat_completion
    
    test_prompt = "Привет! Скажи 'тест пройден' и больше ничего."
    
    try:
        result = await chat_completion(
            messages=[{"role": "user", "content": test_prompt}],
            provider=provider,
            max_tokens=50,
        )
        return {
            "status": "ok",
            "provider": provider,
            "response": result,
            "length": len(result) if result else 0,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

# =====================================================
# Эндпоинт для загрузки текстового транскрипта
# =====================================================

@router.post("/{session_id}/upload-transcript")
async def upload_transcript(
    session_id: str,
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    """Upload transcript text file to session"""
    from app.supabase import get_supabase
    
    try:
        # Read file content
        content = await file.read()
        transcript_text = content.decode("utf-8")
        
        # Update session
        supabase = get_supabase()
        supabase.table("sessions").update({
            "transcript": transcript_text
        }).eq("id", session_id).eq("psychologist_id", user.id).execute()
        
        return {
            "status": "uploaded",
            "transcript_length": len(transcript_text)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================
# Эндпоинт начала работы пайплайна с текстового транскрипта
# =====================================================

@router.post("/{session_id}/process-transcript")
async def start_transcript_processing(
    session_id: str,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user),
):
    """
    Start background processing for a session that already has transcript text.
    Skips transcription, goes straight to editing and summarization.
    """
    background_tasks.add_task(
        process_session_transcript,
        session_id,
        user.id,
    )
    return {"status": "processing_started", "session_id": session_id}

