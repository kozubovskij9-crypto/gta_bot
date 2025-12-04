# ============================================================
#  error_handler.py — FULL PRO ERROR ENGINE v1.0
# ============================================================

import traceback
import threading
import time
from datetime import datetime

class ErrorHandler:
    """
    Централізований обробник усіх помилок бота.
    Використовується у: OCR, LogicEngine, Overlay, ZoneSelector, GUI, Autosave.
    """

    def __init__(self, logger=None, hud=None):
        self.logger = logger
        self.hud = hud

        self.last_error = None
        self.last_error_time = 0
        self.error_cooldown = 1.0       # 1 секунда — захист від спаму

        self.silent_errors = False      # для OCR тихий режим (не спамити у HUD)

    # ------------------------------------------------------------
    # Центральний метод обробки помилки
    # ------------------------------------------------------------
    def handle(self, err: Exception, label: str = "UNNAMED"):
        """
        err — exception
        label — з якого модуля виклик
        """

        now = time.time()
        err_msg = f"[{label}] {type(err).__name__}: {err}"

        # ---- захист від повторів кожну мілісекунду ----
        if self.last_error == err_msg and (now - self.last_error_time) < self.error_cooldown:
            return

        self.last_error = err_msg
        self.last_error_time = now

        # ---- Лог у файл ----
        if self.logger:
            tb = traceback.format_exc()
            self.logger.error(f"❌ ERROR in {label}\n{err_msg}\n{tb}")

        # ---- HUD повідомлення ----
        if self.hud and not self.silent_errors:
            self.hud.set_error(f"{label}: {type(err).__name__}")

    # ------------------------------------------------------------
    # SafeCall — wrapper для безпечного виконання функцій
    # ------------------------------------------------------------
    def safecall(self, fn, label="SAFE"):
        """
        Повертає обгортку функції з автоматичною обробкою помилок.
        """
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                self.handle(e, label)
                return None
        return wrapper

    # ------------------------------------------------------------
    # Виконання у окремому потоці
    # ------------------------------------------------------------
    def run_threaded(self, fn, label="THREAD"):
        """
        Запускає функцію у потоці + обробка помилок.
        """
        def thread_fn():
            try:
                fn()
            except Exception as e:
                self.handle(e, label)

        t = threading.Thread(target=thread_fn, daemon=True)
        t.start()
        return t

    # ------------------------------------------------------------
    # Увімкнути "тихий режим" для OCR (не палити HUD)
    # ------------------------------------------------------------
    def enable_silent(self):
        self.silent_errors = True

    def disable_silent(self):
        self.silent_errors = False
