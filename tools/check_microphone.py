import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000
DURATION_SECONDS = 5
BAR_WIDTH = 40
LOUD_LEVEL = 1500  # уровень, при котором шкала заполняется полностью


def print_input_devices() -> None:
    print("Доступные микрофоны:\n")
    for index, device in enumerate(sd.query_devices()):
        if device["max_input_channels"] > 0:
            print(f"  [{index}] {device['name']}")
    print(f"\nМикрофон по умолчанию: [{sd.default.device[0]}]")


def on_audio(indata, frames, time, status) -> None:
    level = float(np.abs(indata).mean())
    filled = int(min(level / LOUD_LEVEL, 1.0) * BAR_WIDTH)
    print(f"\r{'█' * filled:<{BAR_WIDTH}} {level:6.0f}", end="", flush=True)


def main() -> None:
    print_input_devices()
    print(f"\nГоворите что-нибудь {DURATION_SECONDS} секунд...\n")
    with sd.InputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="int16", callback=on_audio
    ):
        sd.sleep(DURATION_SECONDS * 1000)
    print("\n\nГотово.")


if __name__ == "__main__":
    main()