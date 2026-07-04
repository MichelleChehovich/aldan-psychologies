import os
import math
from pydub import AudioSegment


def split_audio(
    file_path: str,
    max_size_mb: int = 20,
    temp_dir: str = "storage/temp_audio/sessions"
) -> list[str]:
    """
    Split audio file into chunks under max_size_mb each.
    Returns list of paths to chunk files.
    """
    # Determine format
    ext = os.path.splitext(file_path)[1].lower().lstrip(".")
    
    # pydub uses "mp4" for m4a files
    fmt = "mp4" if ext == "m4a" else ext
    
    print(f"[AudioSplitter] Loading {file_path} as {fmt}, size: {os.path.getsize(file_path) / (1024*1024):.1f} MB")
    
    audio = AudioSegment.from_file(file_path, format=fmt)
    
    total_duration_ms = len(audio)
    file_size_bytes = os.path.getsize(file_path)
    bytes_per_ms = file_size_bytes / total_duration_ms if total_duration_ms > 0 else 0
    
    max_chunk_bytes = max_size_mb * 1024 * 1024 * 0.9
    chunk_duration_ms = int(max_chunk_bytes / bytes_per_ms) if bytes_per_ms > 0 else total_duration_ms
    
    # Ensure minimum chunk size
    chunk_duration_ms = max(chunk_duration_ms, 60000)  # at least 1 minute
    
    chunks = []
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    
    for i, start_ms in enumerate(range(0, total_duration_ms, chunk_duration_ms)):
        end_ms = min(start_ms + chunk_duration_ms, total_duration_ms)
        chunk = audio[start_ms:end_ms]
        
        chunk_path = os.path.join(temp_dir, f"{base_name}_chunk_{i:03d}.mp3")
        chunk.export(chunk_path, format="mp3", bitrate="64k")
        
        chunk_size = os.path.getsize(chunk_path) / (1024 * 1024)
        print(f"[AudioSplitter] Chunk {i}: {chunk_size:.1f} MB")
        chunks.append(chunk_path)
    
    print(f"[AudioSplitter] Split into {len(chunks)} chunks")
    return chunks


def cleanup_chunks(chunks: list[str]) -> None:
    """Delete temporary chunk files."""
    for path in chunks:
        try:
            os.remove(path)
        except Exception:
            pass
