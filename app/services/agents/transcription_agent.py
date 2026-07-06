from app.stt import transcribe_audio
from app.services.agent_task_service import update_agent_status, AGENT_STATUS
from app.services.audio_splitter import split_audio, cleanup_chunks
import os


class TranscriptionAgent:
    def __init__(self, session_id: str, provider: str = "proxyapi"):
        self.session_id = session_id
        self.provider = provider
        self.agent_name = "transcription_agent"

    async def process(self, audio_file_path: str) -> str:
        try:
            # DEBUG
            print(f"[TranscriptionAgent] File path: {audio_file_path}")
            print(f"[TranscriptionAgent] Exists: {os.path.exists(audio_file_path)}")
            if os.path.exists(audio_file_path):
                print(f"[TranscriptionAgent] Size: {os.path.getsize(audio_file_path) / (1024*1024):.1f} MB")
            
            update_agent_status(self.session_id, self.agent_name, AGENT_STATUS["in_progress"])

            file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
            
            if file_size_mb > 20:
                print(f"[TranscriptionAgent] File too large ({file_size_mb:.1f} MB), splitting...")
                chunks = split_audio(audio_file_path, max_size_mb=20)
                print(f"[TranscriptionAgent] Split into {len(chunks)} chunks")
                
                transcripts = []
                for i, chunk_path in enumerate(chunks):
                    print(f"[TranscriptionAgent] Transcribing chunk {i+1}/{len(chunks)}...")
                    update_agent_status(self.session_id, self.agent_name, AGENT_STATUS["waiting_external"])
                    chunk_text = await transcribe_audio(chunk_path, self.provider)
                    transcripts.append(chunk_text)
                    print(f"[TranscriptionAgent] Chunk {i+1} done, length: {len(chunk_text)}")
                
                cleanup_chunks(chunks)
                transcript = " ".join(transcripts)
            else:
                update_agent_status(self.session_id, self.agent_name, AGENT_STATUS["waiting_external"])
                transcript = await transcribe_audio(audio_file_path, self.provider)

            update_agent_status(self.session_id, self.agent_name, AGENT_STATUS["completed"])
            return transcript

        except Exception as e:
            update_agent_status(self.session_id, self.agent_name, AGENT_STATUS["error"], str(e))
            raise
