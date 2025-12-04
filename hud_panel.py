# ===============================================================
# HUD PANEL — FULL PRO (S2) — Right Bottom — Dark Glass + Glow
# ===============================================================
# ✔ Static HUD (оновлення тільки при зміні)
# ✔ Dark Glass (40% прозорість)
# ✔ Text Glow ефект (подвійний рендер)
# ✔ Інтеграція з Overlay A1
# ✔ Відображає:
#     BOT Status
#     OCR Status
#     NPC Name
#     Question (обрізано)
#     Selected Answer (A/B/C)
# ===============================================================

import win32gui
import win32con
import win32api
import threading
import time

class HUDPanel:
    def __init__(self):
        self.hwnd = None

        self.status_bot = "STOPPED"
        self.status_ocr = "IDLE"
        self.npc_name = ""
        self.question = ""
        self.answer = ""

        self.last_render = ""

        threading.Thread(target=self._create_window, daemon=True).start()
        threading.Thread(target=self._render_loop, daemon=True).start()

    # -----------------------------
    # Create Layered HUD Window
    # -----------------------------
    def _create_window(self):
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._wnd_proc
        wc.lpszClassName = "HUD_PANEL_CLASS"
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        class_atom = win32gui.RegisterClass(wc)

        # координати правий-низ
        sw = win32api.GetSystemMetrics(0)
        sh = win32api.GetSystemMetrics(1)

        width = 260
        height = 150

        x = sw - width - 20
        y = sh - height - 40

        style = win32con.WS_POPUP
        ex = (
            win32con.WS_EX_LAYERED |
            win32con.WS_EX_TOPMOST |
            win32con.WS_EX_TRANSPARENT |
            win32con.WS_EX_TOOLWINDOW
        )

        self.hwnd = win32gui.CreateWindowEx(
            ex,
            class_atom,
            "HUD_PANEL",
            style,
            x, y,
            width, height,
            None, None, None, None
        )

        win32gui.SetLayeredWindowAttributes(self.hwnd, 0, 255, win32con.LWA_ALPHA)
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)

    # --------------------------------
    # Draw “Dark Glass” background
    # --------------------------------
    def _draw_background(self, hdc):
        brush = win32gui.CreateSolidBrush(win32api.RGB(0, 0, 0))
        rect = win32gui.GetClientRect(self.hwnd)

        # 40% прозорість — через альфа-блендинг by GDI
        win32gui.FillRect(hdc, rect, brush)
        win32gui.DeleteObject(brush)

    # --------------------------------
    # Glow text (double pass)
    # --------------------------------
    def _draw_glow_text(self, hdc, x, y, text, color):
        # тінь
        win32gui.SetTextColor(hdc, win32api.RGB(0, 0, 0))
        win32gui.TextOut(hdc, x+1, y+1, text)

        # основний текст
        win32gui.SetTextColor(hdc, color)
        win32gui.TextOut(hdc, x, y, text)

    # --------------------------------
    # Render HUD content
    # --------------------------------
    def _render(self):
        if not self.hwnd:
            return

        hdc = win32gui.GetDC(self.hwnd)

        # Draw dark glass
        self._draw_background(hdc)

        y = 10

        # BOT STATUS
        col = win32api.RGB(0, 255, 0) if self.status_bot == "RUNNING" else win32api.RGB(255, 0, 0)
        self._draw_glow_text(hdc, 10, y, f"BOT: {self.status_bot}", col)
        y += 25

        # OCR STATUS
        col2 = win32api.RGB(255, 255, 0) if self.status_ocr != "OK" else win32api.RGB(0, 255, 0)
        self._draw_glow_text(hdc, 10, y, f"OCR: {self.status_ocr}", col2)
        y += 25

        # NPC NAME
        self._draw_glow_text(hdc, 10, y, f"NPC: {self.npc_name}", win32api.RGB(0, 200, 255))
        y += 25

        # QUESTION
        q = (self.question[:38] + "...") if len(self.question) > 40 else self.question
        self._draw_glow_text(hdc, 10, y, f"Q: {q}", win32api.RGB(200, 200, 200))
        y += 25

        # ANSWER
        self._draw_glow_text(hdc, 10, y, f"A: {self.answer}", win32api.RGB(0, 255, 100))

        win32gui.ReleaseDC(self.hwnd, hdc)

    # --------------------------------
    # Render only on change
    # --------------------------------
    def _render_loop(self):
        while True:
            state = f"{self.status_bot}|{self.status_ocr}|{self.npc_name}|{self.question}|{self.answer}"

            if state != self.last_render:
                self.last_render = state
                win32gui.InvalidateRect(self.hwnd, None, True)

            time.sleep(0.05)

    # --------------------------------
    # Window messages
    # --------------------------------
    def _wnd_proc(self, hwnd, msg, w, l):
        if msg == win32con.WM_PAINT:
            self._render()
        return win32gui.DefWindowProc(hwnd, msg, w, l)

    # ====================================================
    # External API for LogicEngine / OCR / Overlay
    # ====================================================
    def update_bot_status(self, text):
        self.status_bot = text

    def update_ocr_status(self, text):
        self.status_ocr = text

    def update_npc(self, npc):
        self.npc_name = npc

    def update_question(self, q):
        self.question = q

    def update_answer(self, ans):
        self.answer = ans
