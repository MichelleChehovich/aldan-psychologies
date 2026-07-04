import os
import subprocess
import json


def split_audio(
    file_path: str,
    max_size_mb: int = 20,
    temp_dir: str = "storage/temp_audio/sessions"
) -> list[str]:
    """
    Split audio file into chunks under max_size_mb each.
    Uses ffprobe for duration and ffmpeg for precise splitting.
    """
    # Get audio duration and size
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", file_path],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr}")
    
    info = json.loads(result.stdout)
    duration = float(info["format"]["duration"])
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    print(f"[AudioSplitter] File: {file_size_mb:.1f} MB, Duration: {duration:.1f}s ({duration/60:.1f} min)")
    
    # Calculate chunk duration in seconds (90% of max size for safety)
    chunk_duration = (max_size_mb / file_size_mb) * duration * 0.9
    
    # Ensure minimum chunk is at least 60 seconds
    chunk_duration = max(chunk_duration, 60)
    
    # Calculate number of chunks
    num_chunks = max(1, int(duration / chunk_duration) + (1 if duration % chunk_duration > 0 else 0))
    
    print(f"[AudioSplitter] Will create {num_chunks} chunks of ~{chunk_duration:.0f}s each")
    
    chunks = []
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    
    for i in range(num_chunks):
        start = i * chunk_duration
        end = min(start + chunk_duration, duration)
        
        # Don't create tiny last chunk
        if end - start < 10:
            continue
        
        chunk_path = os.path.join(temp_dir, f"{base_name}_chunk_{i:03d}.mp3")
        
        cmd = [
            "ffmpeg", "-y",
            "-i", file_path,
            "-ss", str(start),
            "-t", str(end - start),  # duration, not end time
            "-b:a", "64k",
            "-ac", "1",
            chunk_path
        ]
        
        print(f"[AudioSplitter] Chunk {i}: {start:.1f}s → {end:.1f}s ({end-start:.1f}s)")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[AudioSplitter] Error on chunk {i}: {result.stderr}")
            continue
        
        chunk_size = os.path.getsize(chunk_path) / (1024 * 1024)
        print(f"[AudioSplitter] Chunk {i}: {chunk_size:.1f} MB")
        chunks.append(chunk_path)
    
    print(f"[AudioSplitter] Created {len(chunks)} chunks")
    return chunks


def cleanup_chunks(chunks: list[str]) -> None:
    """Delete temporary chunk files."""
    for path in chunks:
        try:
            os.remove(path)
        except Exception as e:
            print(f"[AudioSplitter] Failed to remove {path}: {e}")
