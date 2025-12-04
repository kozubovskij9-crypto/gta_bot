import tkinter as tk
import json
import os
import keyboard

ZONES_FILE = "zones.json"

class ZoneSelector:
    def __init__(self):
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.active = False
        self.current_zone_name = None

        # F6 = запускаємо вибір зони
        keyboard.add_hotkey("f6", self.open_selector)

    def open_selector(self, zone_name=None):
        """Запуск напівпрозорого вікна для виділення зони"""
        if self.active:
            return

        self.current_zone_name = zone_name
        self.active = True

        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-alpha", 0.25)
        self.root.configure(bg="black")
        self.root.attributes("-topmost", True)
        self.root.bind("<Button-1>", self.on_mouse_down)
        self.root.bind("<B1-Motion>", self.on_mouse_drag)
        self.root.bind("<ButtonRelease-1>", self.on_mouse_up)

        canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        self.canvas = canvas

        self.root.mainloop()

    def on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline="red", width=3
        )

    def on_mouse_drag(self, event):
        if self.rect:
            self.canvas.coords(self.rect,
                self.start_x, self.start_y, event.x, event.y
            )

    def on_mouse_up(self, event):
        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x, event.y

        zone = {
            "x1": int(min(x1, x2)),
            "y1": int(min(y1, y2)),
            "x2": int(max(x1, x2)),
            "y2": int(max(y1, y2))
        }

        self.save_zone(zone)
        self.root.destroy()
        self.active = False

    def save_zone(self, zone):
        """Автозбереження зони у zones.json"""
        if not os.path.exists(ZONES_FILE):
            data = {}
        else:
            with open(ZONES_FILE, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except:
                    data = {}

        # якщо не подав назву — питаємо
        if not self.current_zone_name:
            # зона по порядку: name_zone_1, name_zone_2...
            idx = len(data.keys()) + 1
            name = f"zone_{idx}"
        else:
            name = self.current_zone_name

        data[name] = zone

        with open(ZONES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"[ZONE SAVED] {name} → {zone}")


# Головний об’єкт модулю
selector = ZoneSelector()

def select_zone(name):
    """Виклик вибору зони з іншого модуля"""
    selector.open_selector(zone_name=name)
