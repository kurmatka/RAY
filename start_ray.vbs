Set shell = CreateObject("WScript.Shell")

shell.CurrentDirectory = "C:\Users\frfrf\ray"

shell.Run """C:\Users\frfrf\ray\.venv\Scripts\pythonw.exe"" -m ray.ui", 0, False