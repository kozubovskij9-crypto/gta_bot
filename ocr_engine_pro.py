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
                    self.last_result = self.read_all()
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
        if not self.zones or not self.zones.zones:
            return {}

        out = {}

        try:
            out["name"] = self.read_zone(self.zones.zones["name"])
        except:
            out["name"] = ""

        try:
            out["question"] = self.read_zone(self.zones.zones["question"])
        except:
            out["question"] = ""

        # 3 fixed answers (пояснити / запевнити / надавити)
        for i in range(1, 4):
            key = f"answer{i}"
            try:
                out[key] = self.read_zone(self.zones.zones[key])
            except:
                out[key] = ""

        return out
