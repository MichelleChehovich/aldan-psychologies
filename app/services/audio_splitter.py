import os
import math
from pydub import AudioSegment


def split_audio(
    file_path: str,
    max_size_mb: int = 20,  # чуть меньше лимита для надёжности
    temp_dir: str = "storage/temp_audio/sessions"
) -> list[str]:
    """
    Split audio file into chunks under max_size_mb each.
    Returns list of paths to chunk files.
    """
    # Load audio
    ext = os.path.splitext(file_path)[1].lower()
    fmt = ext.lstrip(".")
    if fmt == "m4a":
        fmt = "mp4"  # pydub использует mp4 для m4a
    
    audio = AudioSegment.from_file(file_path, format=fmt)
    
    # Calculate chunk duration
    total_duration_ms = len(audio)
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    # Estimate bytes per millisecond
    bytes_per_ms = os.path.getsize(file_path) / total_duration_ms if total_duration_ms > 0 else 0
    
    # Safe chunk duration in ms
    max_chunk_bytes = max_size_mb * 1024 * 1024 * 0.9  # 90% от лимита
    chunk_duration_ms = int(max_chunk_bytes / bytes_per_ms) if bytes_per_ms > 0 else total_duration_ms
    
    # Split
    chunks = []
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    
    for i, start_ms in enumerate(range(0, total_duration_ms, chunk_duration_ms)):
        end_ms = min(start_ms + chunk_duration_ms, total_duration_ms)
        chunk = audio[start_ms:end_ms]
        
        chunk_path = os.path.join(temp_dir, f"{base_name}_chunk_{i:03d}.mp3")
        chunk.export(chunk_path, format="mp3", bitrate="64k")  # низкий битрейт для экономии
        chunks.append(chunk_path)
    
    return chunks


def cleanup_chunks(chunks: list[str]) -> None:
    """Delete temporary chunk files."""
    for path in chunks:
        try:
            os.remove(path)
        except Exception:
            pass
