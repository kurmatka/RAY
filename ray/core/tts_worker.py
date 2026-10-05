import sys
import pyttsx3


def main() -> None:
    text = " ".join(sys.argv[1:])

    engine = pyttsx3.init()

    for voice in engine.getProperty("voices"):
        if "Irina" in voice.name:
            engine.setProperty("voice", voice.id)
            break

    engine.setProperty("rate", 175)
    engine.setProperty("volume", 1.0)

    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":
    main()
