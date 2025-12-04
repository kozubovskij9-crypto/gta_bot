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
        self.ocr = OCREngine(self.zones)
        self.overlay = Overlay(self.zones)
        self.hud = HUDPanel()
        self.logic = LogicEngine(self.ocr, self.overlay, self.hud, self.zones)

        log("Core modules initialized.")

    def start_logic(self):
        self.logic.start()

    def stop_logic(self):
        self.logic.stop()


if __name__ == "__main__":
    core = BotCore()
    run_gui(core)
