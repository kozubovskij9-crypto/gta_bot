# autosave_engine.py
# FULL PRO AUTOSAVE ENGINE (Threaded / SafeWrite / JSON-per-NPC)

import os
import json
import threading
import time
from datetime import datetime


class AutoSaveEngine:
    """
    PRO Autosaver:
    ✔ зберігає answers/ІМ_Я.json окремо
    ✔ авто-збереження кожні N секунд
    ✔ SafeWrite (тимчасовий файл -> rename)
    ✔ thread-safe за допомогою локів
    ✔ log_callback(message) для HUD/GUI/Logger
    """

    def __init__(self, db_manager, interval=5, log_callback=None):
        self.db = db_manager                    # NPCDatabaseManager
        self.interval = interval                # seconds
        self.log = log_callback                 # function for logs
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

        os.makedirs("answers", exist_ok=True)

    # ----------------------------------------------------------
    # Запуск потоку автозбереження
    # ----------------------------------------------------------
    def start(self):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

        if self.log:
            self.log("[AUTOSAVE] Engine started")

    # ----------------------------------------------------------
    # Зупинка потоку автозбереження
    # ----------------------------------------------------------
    def stop(self):
        self.running = False
        if self.log:
            self.log("[AUTOSAVE] Engine stopped")

    # ----------------------------------------------------------
    # Основний цикл
    # ----------------------------------------------------------
    def _loop(self):
        while self.running:
            time.sleep(self.interval)
            self.save_all()

    # ----------------------------------------------------------
    # SafeWrite JSON (не пошкоджує файл, навіть при збоях)
    # ----------------------------------------------------------
    def _safe_write(self, path, data):
        tmp_path = path + ".tmp"

        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        os.replace(tmp_path, path)

    # ----------------------------------------------------------
    # Збереження окремого NPC
    # ----------------------------------------------------------
    def save_npc(self, npc_name):
        npc_data = self.db.get_npc(npc_name)
        if npc_data is None:
            return

        path = os.path.join("answers", f"{npc_name}.json")
        self._safe_write(path, npc_data)

        if self.log:
            self.log(f"[AUTOSAVE] Saved NPC: {npc_name}")

    # ----------------------------------------------------------
    # Збереження всієї бази NPC (кожен NPC у своєму файлі)
    # ----------------------------------------------------------
    def save_all(self):
        with self.lock:
            all_npc = self.db.get_all_npc_names()

            if not all_npc:
                return

            for npc in all_npc:
                self.save_npc(npc)

            if self.log:
                t = datetime.now().strftime("%H:%M:%S")
                self.log(f"[AUTOSAVE] All NPC saved at {t}")
