from ray.core.voice import VoiceRecognizer


MODEL_PATH = "models/vosk-model-small-ru-0.22"

recognizer = VoiceRecognizer(MODEL_PATH)

print("Тест активации Рея.")
print("Скажи что-нибудь. Для остановки нажми Ctrl+C.")

while True:
    text = recognizer.listen_once()
    print(f"[heard] {text}")

    normalized = text.lower()

    words = normalized.split()

if "рей" in words or "рэй" in words:
    print("[wake] Рей активирован!")