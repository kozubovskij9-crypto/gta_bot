import tkinter as tk
from tkinter import ttk


def run_gui(core):
    """Minimal control panel for starting/stopping the bot."""

    root = tk.Tk()
    root.title("GTA 5 RAGE — LOGIC BOT PRO")
    root.geometry("420x220")

    frm = ttk.Frame(root, padding=20)
    frm.pack(fill="both", expand=True)

    status_var = tk.StringVar(value="Bot stopped")

    def update_status():
        state = "running" if core.logic.running else "stopped"
        status_var.set(f"Bot is {state}")
        root.after(300, update_status)

    ttk.Label(frm, text="Bot control", font=("Segoe UI", 14, "bold")).pack(pady=5)
    ttk.Button(frm, text="▶ START", command=core.start_logic).pack(pady=5, fill="x")
    ttk.Button(frm, text="■ STOP", command=core.stop_logic).pack(pady=5, fill="x")
    ttk.Label(frm, textvariable=status_var, font=("Segoe UI", 11)).pack(pady=10)

    # Zones info hint
    ttk.Label(
        frm,
        text="Використовуйте F6 для вибору зон (name/question/answer1-3)",
        wraplength=360,
    ).pack(pady=10)

    update_status()
    root.mainloop()

