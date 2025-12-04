import cv2
import numpy as np
import pytesseract
import threading
import time
from PIL import Image

class OCREngine:
    def __init__(self, zones=None, tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
        self.enabled = True
        self.last_result = {}
        self.status = "Idle"
        self.zones = zones
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

        # Background OCR thread
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    # ======================================================
    # 🔄 MAIN LOOP
    # ======================================================
    def _loop(self):
        while True:
            if self.enabled and self.zones is not None:
                try:
                    self.status = "Reading..."
                    npc, question, answers = self.read_all()
                    self.last_result = {
                        "name": npc,
                        "question": question,
                        "answers": answers,
                    }
                    self.status = "OK"
                except Exception as e:
                    self.status = f"OCR Error: {e}"
            time.sleep(0.15)   # PRO: 6 FPS (fast enough)

    # ======================================================
    # 📸 CAPTURE MONITOR REGION
    # ======================================================
    def _capture_region(self, x1, y1, x2, y2):
        import mss
        with mss.mss() as sct:
            monitor = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}
            img = np.array(sct.grab(monitor))
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    # ======================================================
    # 🎛 IMAGE NORMALIZATION
    # ======================================================
    def normalize(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # CLAHE — PRO contrast improvement
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(4, 4))
        gray = clahe.apply(gray)

        # Gaussian blur reduces random noise
        blur = cv2.GaussianBlur(gray, (3, 3), 0)

        # Adaptive threshold for GTA text
        th = cv2.adaptiveThreshold(
            blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 31, 7)

        return th

    # ======================================================
    # 🔍 SMART OCR PASS
    # ======================================================
    def ocr_pass(self, img):
        config = "--oem 3 --psm 6"
        text = pytesseract.image_to_string(img, config=config, lang="ukr+eng")
        return text.strip()

    # ======================================================
    # 🧠 FULL READ OF ALL ZONES
    # ======================================================
    def read_zone(self, zone):
        x1, y1, x2, y2 = zone
        img = self._capture_region(x1, y1, x2, y2)
        img = self.normalize(img)
        return self.ocr_pass(img)

    def read_all(self):
        """Read NPC name, question and three answers from configured zones."""
        if not self.zones or not getattr(self.zones, "zones", None):
            return "", "", ["", "", ""]

        zones = self.zones.zones

        try:
            npc = self.read_zone(zones.get("name")) if zones.get("name") else ""
        except Exception:
            npc = ""

        try:
            question = self.read_zone(zones.get("question")) if zones.get("question") else ""
        except Exception:
            question = ""

        answers = []
        for i in range(1, 4):
            key = f"answer{i}"
            try:
                ans = self.read_zone(zones.get(key)) if zones.get(key) else ""
            except Exception:
                ans = ""
            answers.append(ans)

        return npc, question, answers

    # debug helper for GUI
    def read_raw_debug(self):
        npc, question, answers = self.read_all()
        return f"NPC: {npc}\nQ: {question}\nANS: {answers}"

    def attach_logger(self, _):
        """Compatibility stub for GUI."""
        pass
