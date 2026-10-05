import json
import queue

import sounddevice as sd
from vosk import KaldiRecognizer, Model


class VoiceRecognizer:
    def __init__(
        self,
        model_path: str,
        sample_rate: int = 16000,
        device: int = 1,
    ):
        self.model = Model(model_path)
        self.sample_rate = sample_rate
        self.device = device
        self.audio_queue = queue.Queue()

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"[microphone] {status}")

        self.audio_queue.put(bytes(indata))

    def listen_once(
        self,
        timeout: float | None = None,
    ) -> str | None:

        recognizer = KaldiRecognizer(
            self.model,
            self.sample_rate,
        )

        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=8000,
            dtype="int16",
            channels=1,
            device=self.device,
            callback=self._callback,
        ):
            print("[voice] Слушаю...")

            while True:

                try:

                    if timeout is None:
                        data = self.audio_queue.get()

                    else:
                        data = self.audio_queue.get(
                            timeout=timeout
                        )

                except queue.Empty:
                    return None

                if recognizer.AcceptWaveform(data):

                    result = json.loads(
                        recognizer.Result()
                    )

                    text = result.get(
                        "text",
                        "",
                    ).strip()

                    if text:
                        return text