# ================================
#   GUI PRO — FULL VERSION (2025)
#   Tabs: CONTROL / OCR / OVERLAY / DB / LOGS
# ================================

import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import os


# -------------------------------------------------------
#      DARK THEME (GTA-STYLE) + GLOBAL STYLES
# -------------------------------------------------------
def apply_dark_style(root):
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(
        ".",
        background="#121212",
        foreground="#E0E0E0",
        fieldbackground="#1E1E1E"
    )

    style.configure(
        "TNotebook",
        background="#121212",
        borderwidth=0
    )

    style.configure(
        "TNotebook.Tab",
        background="#1E1E1E",
        foreground="#CCCCCC",
        padding=[10, 5],
    )

    style.map(
        "TNotebook.Tab",
        background=[("selected", "#272727")],
        foreground=[("selected", "#00FFAA")]
    )


# -------------------------------------------------------
#      GUI MAIN FUNCTION
# -------------------------------------------------------
def run_gui(logic, ocr, overlay, zones):

    root = tk.Tk()
    root.title("GTA 5 RAGE — LOGIC BOT PRO")
    root.geometry("900x600")
    root.configure(bg="#121212")

    apply_dark_style(root)

    # -------------------------
    #     Notebook TABS
    # -------------------------
    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True)

    t_control = ttk.Frame(nb)
    t_ocr = ttk.Frame(nb)
    t_overlay = ttk.Frame(nb)
    t_db = ttk.Frame(nb)
    t_logs = ttk.Frame(nb)

    nb.add(t_control, text="CONTROL")
    nb.add(t_ocr, text="OCR PRO")
    nb.add(t_overlay, text="OVERLAY")
    nb.add(t_db, text="DATABASE")
    nb.add(t_logs, text="LOGS")


    # -------------------------------------------------------
    #                TAB 1 — CONTROL
    # -------------------------------------------------------
    tk.Label(
        t_control,
        text="BOT CONTROL PANEL",
        fg="#00FFAA",
        bg="#121212",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=10)

    btn_start = tk.Button(
        t_control,
        text="▶ START BOT",
        font=("Segoe UI", 14, "bold"),
        bg="#00AA66",
        fg="white",
        command=logic.start
    )
    btn_start.pack(pady=10)

    btn_stop = tk.Button(
        t_control,
        text="■ STOP BOT",
        font=("Segoe UI", 14, "bold"),
        bg="#AA0033",
        fg="white",
        command=logic.stop
    )
    btn_stop.pack(pady=10)

    lbl_status = tk.Label(
        t_control,
        text="Status: Waiting...",
        fg="#CCCCCC",
        bg="#121212",
        font=("Segoe UI", 12)
    )
    lbl_status.pack(pady=10)


    # статус авто-оновлення
    def update_status():
        lbl_status.config(text=f"Logic Status: {logic.get_status()}")
        root.after(300, update_status)

    root.after(300, update_status)


    # -------------------------------------------------------
    #                TAB 2 — OCR SETTINGS
    # -------------------------------------------------------
    tk.Label(
        t_ocr,
        text="OCR PRO Settings",
        fg="#00CED1",
        bg="#121212",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=10)

    tk.Button(
        t_ocr,
        text="TEST OCR READ",
        bg="#333333",
        fg="white",
        command=lambda: log_text.insert("end", f"OCR: {ocr.read_raw_debug()}\n")
    ).pack(pady=5)


    # -------------------------------------------------------
    #                TAB 3 — OVERLAY
    # -------------------------------------------------------
    tk.Label(
        t_overlay,
        text="Overlay PRO Settings",
        fg="#00FF66",
        bg="#121212",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=10)

    tk.Button(
        t_overlay,
        text="TEST HIGHLIGHT",
        bg="#333333",
        fg="white",
        command=lambda: overlay.test_highlight()
    ).pack(pady=5)

    tk.Button(
        t_overlay,
        text="SHOW HUD TEST",
        bg="#333333",
        fg="white",
        command=lambda: overlay.test_hud()
    ).pack(pady=5)


    # -------------------------------------------------------
    #                TAB 4 — DATABASE VIEW
    # -------------------------------------------------------
    tk.Label(t_db, text="NPC Answer Database", fg="#87CEEB",
             bg="#121212", font=("Segoe UI", 16, "bold")).pack(pady=10)

    db_text = scrolledtext.ScrolledText(t_db, width=100, height=25, bg="#1A1A1A", fg="#00FFAA")
    db_text.pack(padx=10, pady=10)

    def reload_db():
        db_text.delete("1.0", "end")
        folder = "answers"
        if not os.path.exists(folder):
            os.makedirs(folder)
        for file in os.listdir(folder):
            if file.endswith(".json"):
                db_text.insert("end", f"\n=== {file} ===\n\n")
                try:
                    with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
                        db_text.insert("end", f.read() + "\n\n")
                except:
                    db_text.insert("end", "ERROR reading file\n\n")

    tk.Button(t_db, text="Reload DB", bg="#444444", fg="white", command=reload_db).pack()


    # -------------------------------------------------------
    #                TAB 5 — LIVE LOGS
    # -------------------------------------------------------
    tk.Label(t_logs, text="REAL-TIME LOG", fg="#FFDD55",
             bg="#121212", font=("Segoe UI", 16, "bold")).pack(pady=10)

    global log_text
    log_text = scrolledtext.ScrolledText(t_logs, width=100, height=25, bg="#1A1A1A", fg="#00FF88")
    log_text.pack(padx=10, pady=10)

    def push_log(msg):
        log_text.insert("end", msg + "\n")
        log_text.see("end")

    logic.attach_logger(push_log)
    overlay.attach_logger(push_log)
    ocr.attach_logger(push_log)


    # -------------------------------------------------------
    #                START GUI LOOP
    # -------------------------------------------------------
    root.mainloop()
