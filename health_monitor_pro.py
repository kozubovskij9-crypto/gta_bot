# ============================================================
# health_monitor_pro.py — FULL PRO VERSION
# ============================================================
# Функції:
# ✔ Вимірює FPS overlay
# ✔ Вимірює затримку OCR (mean latency)
# ✔ Вимірює час роботи LogicEngine
# ✔ Виявляє зависання потоків
# ✔ Робить авто-перезапуск потоків
# ✔ Передає статуси у HUD (зелений/жовтий/червоний)
# ✔ Веде записи у logger
# ============================================================

import time
import threading

class HealthMonitorPRO:
    def __init__(self, hud, overlay, ocr, logic, logger, thread_engine):
        self.hud = hud
        self.overlay = overlay
        self.ocr = ocr
        self.logic = logic
        self.logger = logger
        self.thread_engine = thread_engine

        self.running = False

        # метрики
        self.overlay_fps = 0
        self.ocr_latency = 0
        self.logic_latency = 0

        # внутрішні змінні
        self._last_overlay_frame = time.time()
        self._last_logic_tick = time.time()
        self._last_ocr_tick = time.time()

        # останні записи
        self._frame_counter = 0

    # ===================================================================
    # 📌 Викликається overlay при кожному кадрі
    # ===================================================================
    def mark_overlay_frame(self):
        self._frame_counter += 1

    # ===================================================================
    # 📌 Викликається OCR Engine при кожному зчитуванні
    # ===================================================================
    def mark_ocr_tick(self, latency):
        self.ocr_latency = latency
        self._last_ocr_tick = time.time()

    # ===================================================================
    # 📌 Викликається LogicEngine при кожному циклі
    # ===================================================================
    def mark_logic_tick(self, latency):
        self.logic_latency = latency
        self._last_logic_tick = time.time()

    # ===================================================================
    # ▶ СТАРТ МОНІТОРА
    # ===================================================================
    def start(self):
        if self.running:
            return
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()
        self.logger.log("HealthMonitor: STARTED")

    # ===================================================================
    # ⏹ СТОП МОНІТОРА
    # ===================================================================
    def stop(self):
        self.running = False
        self.logger.log("HealthMonitor: STOPPED")

    # ===================================================================
    # 🔄 Основний цикл моніторингу
    # ===================================================================
    def _loop(self):
        prev_time = time.time()

        while self.running:
            time.sleep(1.0)

            now = time.time()
            dt = now - prev_time
            prev_time = now

            # --------------------------
            # FPS OVERLAY
            # --------------------------
            self.overlay_fps = round(self._frame_counter / dt, 1)
            self._frame_counter = 0

            # --------------------------
            # Виявлення зависань
            # --------------------------
            overlay_ok = self.overlay_fps > 5
            ocr_ok = (now - self._last_ocr_tick) < 2.5
            logic_ok = (now - self._last_logic_tick) < 2.0

            # --------------------------
            # Авто-перезапуск логіки
            # --------------------------
            if not logic_ok:
                self.logger.log("⚠ LogicEngine HANG detected — restarting thread")
                self.thread_engine.restart_logic()

            if not ocr_ok:
                self.logger.log("⚠ OCREngine HANG detected — restarting thread")
                self.thread_engine.restart_ocr()

            # --------------------------
            # Оновлення HUD
            # --------------------------
            self._update_hud(overlay_ok, ocr_ok, logic_ok)

            # --------------------------
            # Логи
            # --------------------------
            self.logger.log(
                f"HEALTH | FPS:{self.overlay_fps} | OCR:{self.ocr_latency:.2f}s | "
                f"LOGIC:{self.logic_latency:.2f}s | OK:[O:{ocr_ok} L:{logic_ok}]"
            )

    # ===================================================================
    # 🟩🟨🟥 Вивід статусів у HUD
    # ===================================================================
    def _update_hud(self, overlay_ok, ocr_ok, logic_ok):
        # FPS
        fps_color = "green" if overlay_ok else "red"
        self.hud.set_metric("FPS Overlay", f"{self.overlay_fps} FPS", fps_color)

        # OCR latency
        if ocr_ok:
            color = "green" if self.ocr_latency < 0.25 else "yellow"
        else:
            color = "red"

        self.hud.set_metric("OCR", f"{self.ocr_latency:.2f}s", color)

        # Logic cycle latency
        if logic_ok:
            color = "green" if self.logic_latency < 0.15 else "yellow"
        else:
            color = "red"

        self.hud.set_metric("Logic", f"{self.logic_latency:.2f}s", color)

        # Загальний статус
        if overlay_ok and ocr_ok and logic_ok:
            g = "green"
            status = "SYSTEM OK"
        else:
            g = "red"
            status = "ISSUES DETECTED"

        self.hud.set_metric("SYSTEM", status, g)
