# login.py - Giriş Ekranı
import tkinter as tk
from tkinter import messagebox
import hashlib
import json
import os

class LoginScreen:
    def __init__(self, master):
        self.master = master
        master.title("DEM Analiz Sistemi - Giriş")
        master.geometry("400x500")
        master.configure(bg='#2c3e50')
        
        # Renkler
        self.bg_color = "#2c3e50"
        self.fg_color = "#ecf0f1"
        self.btn_color = "#3498db"
        self.btn_hover = "#2980b9"
        
        # Başlık
        title = tk.Label(master, text="🔍 DEM ANALİZ SİSTEMİ", 
                        font=("Arial", 20, "bold"),
                        bg=self.bg_color, fg=self.fg_color)
        title.pack(pady=50)
        
        # Alt başlık
        subtitle = tk.Label(master, text="Yeraltı Boşluk Tespit Sistemi",
                           font=("Arial", 10),
                           bg=self.bg_color, fg="#bdc3c7")
        subtitle.pack(pady=5)
        
        # Kullanıcı adı
        tk.Label(master, text="Kullanıcı Adı", font=("Arial", 12),
                bg=self.bg_color, fg=self.fg_color).pack(pady=(40,5))
        self.username_entry = tk.Entry(master, font=("Arial", 12), width=30)
        self.username_entry.pack(pady=5)
        self.username_entry.insert(0, "admin")
        
        # Şifre
        tk.Label(master, text="Şifre", font=("Arial", 12),
                bg=self.bg_color, fg=self.fg_color).pack(pady=(20,5))
        self.password_entry = tk.Entry(master, show="*", font=("Arial", 12), width=30)
        self.password_entry.pack(pady=5)
        self.password_entry.insert(0, "admin")
        
        # Giriş butonu
        self.login_btn = tk.Button(master, text="GİRİŞ YAP", 
                                   font=("Arial", 12, "bold"),
                                   bg=self.btn_color, fg="white",
                                   width=20, height=2,
                                   command=self.login)
        self.login_btn.pack(pady=40)
        
        # Hover efekti
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.config(bg=self.btn_hover))
        self.login_btn.bind("<Leave>", lambda e: self.login_btn.config(bg=self.btn_color))
        
        # Durum çubuğu
        self.status_label = tk.Label(master, text="DEM Analiz Sistemi v1.0",
                                     font=("Arial", 9),
                                     bg=self.bg_color, fg="#7f8c8d")
        self.status_label.pack(side=tk.BOTTOM, pady=10)
        
        # Enter tuşu
        master.bind('<Return>', lambda e: self.login())
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # Basit doğrulama (şifre: admin / admin)
        # Gerçek uygulamada hash'li saklama kullanın
        if username == "admin" and password == "admin":
            self.status_label.config(text="✓ Giriş başarılı! Ana ekran açılıyor...", fg="#2ecc71")
            self.master.after(1000, self.open_main_app)
        else:
            messagebox.showerror("Hata", "Kullanıcı adı veya şifre hatalı!")
            self.status_label.config(text="✗ Giriş başarısız!", fg="#e74c3c")
    
    def open_main_app(self):
        self.master.destroy()
        import gui_app
        gui_app.main()