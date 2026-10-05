from ray.core.voice import VoiceRecognizer


MODEL_PATH = "models/vosk-model-small-ru-0.22"

recognizer = VoiceRecognizer(MODEL_PATH)

print("Тест голосового управления Рея.")
print("Скажи «Рей», затем команду.")
print("Для остановки нажми Ctrl+C.")

while True:
    text = recognizer.listen_once()
    print(f"[heard] {text}")

    words = text.lower().split()

    if "рей" in words or "рэй" in words:
        print("[wake] Рей активирован!")
        print("[voice] Жду команду...")

        command = recognizer.listen_once()
        print(f"[command] {command}")