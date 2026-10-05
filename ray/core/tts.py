import subprocess
import sys


class TextToSpeech:
    def speak(self, text: str) -> None:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "ray.core.tts_worker",
                text,
            ],
            check=True,
        )
