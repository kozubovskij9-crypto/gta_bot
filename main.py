import threading
from gui_pro import run_gui
from overlay import Overlay
from hud_panel import HUDPanel
from ocr_engine_pro import OCREngine
from logic_engine import LogicEngine
from zone_selector_v1 import ZoneSelector
from logger import log


class BotCore:
    def __init__(self):
        log("Initializing PRO bot...")

        # --- Core components ---
        self.zones = ZoneSelector()
        self.ocr = OCREngine()
        self.overlay = Overlay()
        self.hud = HUDPanel(self.overlay)
        self.logic = LogicEngine(self.ocr, self.overlay, self.zones, self.hud)

        # --- Auto-start modules ---
        threading.Thread(target=self.ocr.loop, daemon=True).start()
        threading.Thread(target=self.overlay.loop, daemon=True).start()
        threading.Thread(target=self.hud.loop, daemon=True).start()

        log("Core modules initialized.")

    def start_logic(self):
        self.logic.start()

    def stop_logic(self):
        self.logic.stop()


if __name__ == "__main__":
    core = BotCore()
    run_gui(core)
