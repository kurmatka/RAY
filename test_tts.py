import pyttsx3


engine = pyttsx3.init()

voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)

engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

print("Тест голоса Рея.")

engine.say("Привет. Я Рей. Готов к работе.")
engine.runAndWait()

print("Готово.")