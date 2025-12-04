# ============================================
#  PRO LOGGER ENGINE (B — Threaded Queue)
#  Потокобезпечний, з callback у GUI + HUD
# ============================================

import threading
import time
import queue
import os
from datetime import datetime

class ProLogger:
    def __init__(self):
        self.log_queue = queue.Queue(maxsize=5000)
        self.gui_callback = None       # Функція що оновлює LOG-вкладку
        self.hud_callback = None       # Короткі повідомлення в HUD
        self.log_file = "logs/latest.log"

        # Створення каталогу logs/
        os.makedirs("logs", exist_ok=True)

        # Очищуємо останній лог
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write("=== GTA LOGIC BOT PRO LOG START ===\n")

        # Фоновий потік
        self.worker = threading.Thread(target=self._process, daemon=True)
        self.worker.start()

    # ---------------------------------------------------
    # Публічний метод — викликається усіма модулями бота
    # ---------------------------------------------------
    def log(self, msg: str):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        entry = f"{timestamp} {msg}"

        try:
            self.log_queue.put(entry, block=False)
        except queue.Full:
            # Якщо черга переповнилась — видаляємо половину
            self._reduce_queue()
            self.log_queue.put(entry)

    # ---------------------------------------------------
    # Фоновий обробник логів
    # ---------------------------------------------------
    def _process(self):
        while True:
            try:
                entry = self.log_queue.get()
            except:
                time.sleep(0.01)
                continue

            # Пишемо у файл
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(entry + "\n")
            except:
                pass

            # Оновити GUI LOG WINDOW
            if self.gui_callback:
                try:
                    self.gui_callback(entry)
                except:
                    pass

            # Оновити HUD (тільки короткий текст)
            if self.hud_callback:
                try:
                    short = entry[11:]  # без часу
                    self.hud_callback(short)
                except:
                    pass

            time.sleep(0.001)

    # ---------------------------------------------------
    # Допоміжний метод для очищення черги
    # ---------------------------------------------------
    def _reduce_queue(self):
        # Викидаємо половину старих логів
        temp = []
        while not self.log_queue.empty():
            temp.append(self.log_queue.get())

        # Обрізаємо
        keep = temp[len(temp)//2:]

        # Повертаємо назад
        for item in keep:
            self.log_queue.put(item)

    # ---------------------------------------------------
    # Прив’язка callback з GUI
    # ---------------------------------------------------
    def bind_gui(self, func):
        self.gui_callback = func

    # ---------------------------------------------------
    # Прив’язка callback з HUD
    # ---------------------------------------------------
    def bind_hud(self, func):
        self.hud_callback = func

