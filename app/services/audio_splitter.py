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
    Uses ffmpeg directly to avoid loading entire file into memory.
    """
    import subprocess
    import json
    
    # Get audio duration using ffprobe (fast, no memory usage)
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", file_path],
        capture_output=True, text=True
    )
    info = json.loads(result.stdout)
    duration = float(info["format"]["duration"])
    
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f"[AudioSplitter] File: {file_size_mb:.1f} MB, Duration: {duration:.1f}s")
    
    # Calculate chunk duration (seconds)
    chunk_duration = (max_size_mb / file_size_mb) * duration * 0.9  # 90% safety
    
    chunks = []
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    
    start = 0
    i = 0
    while start < duration:
        end = min(start + chunk_duration, duration)
        chunk_path = os.path.join(temp_dir, f"{base_name}_chunk_{i:03d}.mp3")
        
        # Use ffmpeg to extract chunk directly (no memory load)
        cmd = [
            "ffmpeg", "-y",
            "-i", file_path,
            "-ss", str(start),
            "-to", str(end),
            "-b:a", "64k",
            "-ac", "1",  # mono to save space
            chunk_path
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        
        chunk_size = os.path.getsize(chunk_path) / (1024 * 1024)
        print(f"[AudioSplitter] Chunk {i}: {chunk_size:.1f} MB")
        chunks.append(chunk_path)
        
        start = end
        i += 1
    
    print(f"[AudioSplitter] Split into {len(chunks)} chunks")
    return chunks


def cleanup_chunks(chunks: list[str]) -> None:
    """Delete temporary chunk files."""
    for path in chunks:
        try:
            os.remove(path)
        except Exception:
            pass
