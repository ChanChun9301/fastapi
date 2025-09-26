import subprocess
import magic

def get_video_duration(file_path: str) -> int:
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        duration = float(result.stdout)
        return int(duration)
    except Exception as e:
        print(f"Ошибка при получении длительности: {e}")
        return 0


def get_mime_type(file_path: str) -> str:
    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(file_path)
    return mime_type
