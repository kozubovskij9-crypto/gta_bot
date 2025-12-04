# ===============================================
# THREAD ENGINE PRO — 6-ПОТОКОВИЙ ДВИГУН ДЛЯ БОТА
# Overlay, HUD, OCR, Logic, Logger, Autosave
# + Health Monitor інтеграція
# ===============================================

import threading
import time
import traceback
from queue import Queue

class ThreadEnginePRO:
    """
    CENTRAL THREAD ENGINE
    Керує:
        • overlay_thread
        • hud_thread
        • ocr_thread
        • logic_thread
        • logger_thread
        • autosave_thread

    + моніторинг зависань
    """

    def __init__(self, overlay, hud, ocr, logic, logger, autosaver, health_monitor):
        self.overlay = overlay
        self.hud = hud
        self.ocr = ocr
        self.logic = logic
        self.logger = logger
        self.autosaver = autosaver
        self.health = health_monitor

        self.running = False
        self.threads = {}
        self.last_cycle = {
            "overlay": 0,
            "hud": 0,
            "ocr": 0,
            "logic": 0,
            "logger": 0,
            "autosave": 0
        }

        self.log_queue = Queue()

    # ---------------------------------------------------------
    # INTERNAL SAFE WRAPPER
    # ---------------------------------------------------------
    def _safe_loop(self, name, target, delay=0.01):
        """Обертає кожен модуль у try/except для стабільності."""
        while self.running:
            try:
                t0 = time.time()
                target()                     # запускаємо цикл модуля
                self.last_cycle[name] = time.time() - t0
            except Exception as e:
                self.logger.log(f"[ERROR] {name}: {e}")
                traceback.print_exc()

            time.sleep(delay)

    # ---------------------------------------------------------
    # THREAD STARTER
    # ---------------------------------------------------------
    def _start_thread(self, name, func, delay=0.01):
        t = threading.Thread(
            target=self._safe_loop,
            args=(name, func, delay),
            daemon=True
        )
        t.start()
        self.threads[name] = t
        self.logger.log(f"[THREAD] {name} started")

    # ---------------------------------------------------------
    # START ENGINE
    # ---------------------------------------------------------
    def start(self):
        if self.running:
            return

        self.running = True
        self.logger.log("[ENGINE] Starting all PRO threads…")

        # Overlay update loop
        self._start_thread("overlay", self.overlay.update, delay=0.016)

        # HUD drawing loop
        self._start_thread("hud", self.hud.update, delay=0.03)

        # OCR reader loop
        self._start_thread("ocr", self.ocr.process_frame, delay=0.05)

        # Logic decision loop
        self._start_thread("logic", self.logic.update, delay=0.02)

        # Logger real-time flushing
        self._start_thread("logger", self.logger.flush, delay=0.1)

        # Autosave cycle
        self._start_thread("autosave", self.autosaver.cycle, delay=1.0)

        # Health monitor
        self._start_thread("health", self.health.check_health, delay=0.5)

        self.logger.log("[ENGINE] All threads running.")

    # ---------------------------------------------------------
    # STOP ENGINE
    # ---------------------------------------------------------
    def stop(self):
        if not self.running:
            return

        self.running = False
        self.logger.log("[ENGINE] Stopping threads…")

        time.sleep(0.2)

        # Force shutdown
        for name, t in self.threads.items():
            if t.is_alive():
                self.logger.log(f"[THREAD] {name} terminated")

        self.logger.log("[ENGINE] STOPPED")

    # ---------------------------------------------------------
    # THREAD STATUS DEBUG
    # ---------------------------------------------------------
    def get_status(self):
        """HUD PRO використовує це для показу FPS / LATENCY."""
        return {
            "overlay_latency": round(self.last_cycle["overlay"] * 1000, 1),
            "hud_latency": round(self.last_cycle["hud"] * 1000, 1),
            "ocr_latency": round(self.last_cycle["ocr"] * 1000, 1),
            "logic_latency": round(self.last_cycle["logic"] * 1000, 1),
            "logger_latency": round(self.last_cycle["logger"] * 1000, 1),
            "autosave_latency": round(self.last_cycle["autosave"] * 1000, 1)
        }
