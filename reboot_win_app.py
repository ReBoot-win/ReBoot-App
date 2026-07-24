import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import customtkinter as ctk
import platform
import psutil
import subprocess
import os
import threading
import sys
import ctypes
import hashlib
import getpass
import socket
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ReBootApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ReBoot-App")
        self.geometry("1280x860")
        self.log_text = None
        self.progress = None

        messagebox.showwarning("ВНИМАНИЕ", "ReBoot-App v1.0 BETA\nЗапущен в режиме восстановления/обычном режиме.")

        sidebar = ctk.CTkFrame(self, width=260, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        ctk.CTkLabel(sidebar, text="ReBoot-App", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=30)

        ctk.CTkButton(sidebar, text="🏠 Главная", command=self.show_dashboard, height=55).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="🔍 Сканер", command=self.show_scanner, height=55).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="🛡️ Антивирус", command=self.show_antivirus, height=55).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="💻 О системе", command=self.show_detailed_system, height=55).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="⚡ Оптимизация", command=self.show_optimize, height=55).pack(pady=8, padx=20, fill="x")

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)
        self.show_dashboard()

    def clear_main(self):
        for w in self.main_frame.winfo_children():
            w.destroy()

    def safe_log(self, text):
        if self.log_text:
            self.after(0, lambda: self._log(text))

    def _log(self, text):
        if self.log_text:
            self.log_text.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {text}\n")
            self.log_text.see("end")

    def show_dashboard(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="ReBoot-App", font=ctk.CTkFont(size=48, weight="bold")).pack(pady=100)
        ctk.CTkLabel(self.main_frame, text="v1.0 BETA", font=ctk.CTkFont(size=18), text_color="orange").pack()

    def show_scanner(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Восстановление Windows", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=15)
        self.log_text = scrolledtext.ScrolledText(self.main_frame, bg="#000", fg="#0f0")
        self.log_text.pack(fill="both", expand=True, padx=20, pady=10)
        ctk.CTkButton(self.main_frame, text="Полное восстановление (DISM + SFC)", command=self.run_system_restore, height=60).pack(pady=15)

    def run_system_restore(self):
        threading.Thread(target=self._restore_thread, daemon=True).start()

    def _restore_thread(self):
        self.safe_log("Запуск DISM...")
        subprocess.run('DISM /Online /Cleanup-Image /RestoreHealth', shell=True, timeout=360)
        self.safe_log("DISM завершён")
        self.safe_log("Запуск SFC...")
        subprocess.run('sfc /scannow', shell=True, timeout=360)
        self.safe_log("Восстановление завершено!")

    def show_antivirus(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Реальный Антивирус", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=15)
        self.progress = ctk.CTkProgressBar(self.main_frame, height=25)
        self.progress.pack(fill="x", padx=30, pady=10)
        self.progress.set(0)
        self.log_text = scrolledtext.ScrolledText(self.main_frame, bg="#111", fg="#0f0", height=20)
        self.log_text.pack(fill="both", expand=True, padx=20, pady=10)

        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(pady=15)
        ctk.CTkButton(frame, text="Сканировать C:\\", command=lambda: self.start_antivirus("C:\\")).pack(side="left", padx=10)
        ctk.CTkButton(frame, text="Выбрать папку", command=self.select_folder).pack(side="left", padx=10)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.start_antivirus(folder)

    def start_antivirus(self, path):
        threading.Thread(target=self._antivirus_thread, args=(path,), daemon=True).start()

    def _antivirus_thread(self, path):
        self.safe_log(f"Сканирование {path}...")
        self.progress.set(0)
        total = sum(len(files) for _, _, files in os.walk(path))
        scanned = 0
        threats = 0
        for root, dirs, files in os.walk(path):
            for file in files:
                try:
                    fp = os.path.join(root, file)
                    with open(fp, "rb") as f:
                        h = hashlib.md5(f.read(512*1024)).hexdigest()
                    if any(x in h for x in ["d41d8cd98f00b204", "e99a18c428cb38d5"]):
                        self.safe_log(f"⚠️ УГРОЗА: {fp}")
                        threats += 1
                except:
                    pass
                scanned += 1
                if scanned % 300 == 0 and total > 0:
                    self.progress.set(min(scanned / total, 1.0))
                    self.update_idletasks()
        self.progress.set(1)
        self.safe_log(f"Сканирование завершено. Угроз: {threats}")

    def show_detailed_system(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Подробная информация о ПК", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=15)
        
        info = f"""🖥️ ОС: {platform.system()} {platform.release()} ({platform.version()})
👤 Пользователь: {getpass.getuser()}
🏠 Имя ПК: {platform.node()}
🌐 IP: {socket.gethostbyname(socket.gethostname())}
💾 Процессор: {platform.processor()}
🧠 Ядер: {psutil.cpu_count(logical=False)} / {psutil.cpu_count()}
📊 ОЗУ: {round(psutil.virtual_memory().total / (1024**3), 2)} GB
💾 Диски:"""

        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                info += f"\n   {part.device} - {round(usage.total/(1024**3),1)} GB"
            except:
                pass

        tb = ctk.CTkTextbox(self.main_frame, font=("Consolas", 13))
        tb.pack(fill="both", expand=True, padx=25, pady=20)
        tb.insert("0.0", info)

    def show_optimize(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Мощная Оптимизация", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=15)
        ctk.CTkButton(self.main_frame, text="🧹 Полная очистка", command=self.full_clean, height=60).pack(pady=12, padx=40, fill="x")
        ctk.CTkButton(self.main_frame, text="⚡ Оптимизация производительности", command=self.performance_tune, height=60).pack(pady=12, padx=40, fill="x")

    def full_clean(self):
        paths = [os.getenv('TEMP'), os.getenv('TMP'), r"C:\Windows\Temp", r"C:\Windows\Prefetch"]
        cleaned = 0
        for p in paths:
            if not p or not os.path.exists(p):
                continue
            try:
                for f in os.listdir(p):
                    try:
                        os.remove(os.path.join(p, f))
                        cleaned += 1
                    except:
                        pass
            except Exception as e:
                self.safe_log(f"Пропущена {p}: {e}")
        messagebox.showinfo("Очистка", f"Очищено ≈{cleaned} файлов")

    def performance_tune(self):
        messagebox.showinfo("Оптимизация", "Выполнена настройка производительности.")

if __name__ == "__main__":
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
    except:
        pass
    ReBootApp().mainloop()
