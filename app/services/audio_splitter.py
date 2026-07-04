import os
import subprocess
import shutil


def split_audio(
    file_path: str,
    max_size_mb: int = 20,
    temp_dir: str = "storage/temp_audio/sessions"
) -> list[str]:
    """
    Split audio file into chunks under max_size_mb each.
    Uses ffmpeg if available, otherwise falls back to simple binary split.
    Returns list of paths to chunk files.
    """
    
    # Check if ffmpeg is available
    ffmpeg_available = shutil.which("ffmpeg") is not None
    
    if not ffmpeg_available:
        print("[AudioSplitter] ffmpeg not found, using binary split")
        return _split_binary(file_path, max_size_mb, temp_dir)
    
    return _split_with_ffmpeg(file_path, max_size_mb, temp_dir)


def _split_with_ffmpeg(
    file_path: str,
    max_size_mb: int,
    temp_dir: str
) -> list[str]:
    """Split using ffmpeg (proper audio chunks)."""
    import json
    
    # Get audio duration
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", file_path],
        capture_output=True, text=True
    )
    info = json.loads(result.stdout)
    duration = float(info["format"]["duration"])
    
    # Calculate chunk duration
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    chunk_duration = (max_size_mb / file_size_mb) * duration * 0.9  # 90% safety margin
    
    chunks = []
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    
    start = 0
    i = 0
    while start < duration:
        end = min(start + chunk_duration, duration)
        chunk_path = os.path.join(temp_dir, f"{base_name}_chunk_{i:03d}.mp3")
        
        subprocess.run([
            "ffmpeg", "-y", "-i", file_path,
            "-ss", str(start), "-to", str(end),
            "-b:a", "64k", chunk_path
        ], capture_output=True)
        
        chunks.append(chunk_path)
        start = end
        i += 1
    
    return chunks


def _split_binary(
    file_path: str,
    max_size_mb: int,
    temp_dir: str
) -> list[str]:
    """
    Simple binary split — just cuts file into pieces.
    Each piece is a valid audio file (MP3 frames are independent).
    """
    max_size_bytes = int(max_size_mb * 1024 * 1024 * 0.9)
    
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    ext = os.path.splitext(file_path)[1]
    
    chunks = []
    
    with open(file_path, "rb") as f:
        i = 0
        while True:
            data = f.read(max_size_bytes)
            if not data:
                break
            
            chunk_path = os.path.join(temp_dir, f"{base_name}_chunk_{i:03d}{ext}")
            with open(chunk_path, "wb") as chunk_file:
                chunk_file.write(data)
            
            chunks.append(chunk_path)
            i += 1
    
    print(f"[AudioSplitter] Binary split into {len(chunks)} chunks")
    return chunks


def cleanup_chunks(chunks: list[str]) -> None:
    """Delete temporary chunk files."""
    for path in chunks:
        try:
            os.remove(path)
        except Exception:
            pass
