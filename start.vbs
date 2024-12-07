Set Sh = WScript.CreateObject("WScript.Shell")

Sh.Run "python app.py", 3

Sh.Run "http://localhost:5000", 3