import win32gui
import win32con
import win32api
import threading
import time

class Overlay:
    """
    FULL PRO OVERLAY:
    - WinAPI transparent window
    - GDI rendering
    - FULL pass-through (mouse ignores overlay)
    - Green glowing frame (#00FF66) for answer highlight
    - Smart update: redraw only when answer changes
    """

    def __init__(self):
        self.hwnd = None
        self.frame_rect = None
        self.needs_redraw = False
        self.running = True

        threading.Thread(target=self._create_window, daemon=True).start()
        threading.Thread(target=self._render_loop, daemon=True).start()

    # ------------------------------------------------------
    # CREATE TRANSPARENT WINDOW
    # ------------------------------------------------------
    def _create_window(self):
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._wnd_proc
        wc.lpszClassName = "GTA5_OVERLAY_PRO"
        class_atom = win32gui.RegisterClass(wc)

        # extended styles: topmost + layered + transparent
        ex_style = (
            win32con.WS_EX_TOPMOST |
            win32con.WS_EX_LAYERED |
            win32con.WS_EX_TRANSPARENT |
            win32con.WS_EX_TOOLWINDOW
        )

        # normal style: no border, no caption
        style = win32con.WS_POPUP

        self.hwnd = win32gui.CreateWindowEx(
            ex_style,
            class_atom,
            None,
            style,
            0, 0,
            win32api.GetSystemMetrics(0),
            win32api.GetSystemMetrics(1),
            None,
            None,
            None,
            None
        )

        # make click-through + visible
        win32gui.SetLayeredWindowAttributes(self.hwnd, 0x000000, 255, win32con.LWA_COLORKEY)
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)

    # ------------------------------------------------------
    # WINDOW MESSAGE HANDLER
    # ------------------------------------------------------
    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_PAINT:
            self._draw()
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    # ------------------------------------------------------
    # DRAW GREEN FRAME
    # ------------------------------------------------------
    def _draw(self):
        if not self.frame_rect:
            return

        left, top, right, bottom = self.frame_rect

        hdc, paint = win32gui.BeginPaint(self.hwnd)

        # GREEN frame color
        pen = win32gui.CreatePen(win32con.PS_SOLID, 3, win32api.RGB(0, 255, 102))
        win32gui.SelectObject(hdc, pen)

        # Draw rectangle
        win32gui.Rectangle(hdc, left, top, right, bottom)

        # Glow effect (second pass, slightly larger)
        pen_glow = win32gui.CreatePen(win32con.PS_SOLID, 6, win32api.RGB(0, 180, 60))
        win32gui.SelectObject(hdc, pen_glow)
        win32gui.Rectangle(hdc, left - 1, top - 1, right + 1, bottom + 1)

        win32gui.EndPaint(self.hwnd, paint)

    # ------------------------------------------------------
    # SMART UPDATE LOOP
    # ------------------------------------------------------
    def _render_loop(self):
        while self.running:
            if self.needs_redraw and self.hwnd:
                win32gui.InvalidateRect(self.hwnd, None, True)
                self.needs_redraw = False
            time.sleep(0.02)  # 50 FPS refresh

    # ------------------------------------------------------
    # PUBLIC API CALLS
    # ------------------------------------------------------
    def highlight_zone(self, rect):
        """ rect = (x1, y1, x2, y2) """
        self.frame_rect = rect
        self.needs_redraw = True

    def clear_highlight(self):
        self.frame_rect = None
        self.needs_redraw = True

    def stop(self):
        self.running = False
