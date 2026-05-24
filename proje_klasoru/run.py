# run.py - Uygulamayı başlat
import tkinter as tk
from login import LoginScreen

if __name__ == "__main__":
    root = tk.Tk()
    login = LoginScreen(root)
    root.mainloop()