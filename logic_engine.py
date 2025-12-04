import threading
import time
import json
import os
import difflib


class LogicEngine:
    """
    FULL PRO LOGIC ENGINE
    ---------------------
    ✔ Auto-learn per NPC
    ✔ answers/<NPC>.json
    ✔ Smart Update (update only when needed)
    ✔ Strong fuzzy logic matching
    ✔ Overlay highlight control
    ✔ HUD status updates
    """

    def __init__(self, ocr, overlay, hud, zones, zones_folder="answers"):
        self.ocr = ocr
        self.overlay = overlay
        self.hud = hud
        self.zones = zones

        self.zones_folder = zones_folder
        os.makedirs(self.zones_folder, exist_ok=True)

        self.running = False

        self.current_npc = ""
        self.current_question = ""
        self.current_answer = ""

        # Каждую NPC → отдельный файл answers/NPC.json
        self.local_db = {}

        # Thread
        self.thread = threading.Thread(target=self._loop, daemon=True)

    # ======================================================================
    # PUBLIC API
    # ======================================================================

    def start(self):
        """Запуск логіки"""
        if not self.thread.is_alive():
            self.thread = threading.Thread(target=self._loop, daemon=True)
        self.running = True
        self.hud.set_bot_status("RUNNING")
        self.overlay.set_status("BOT ACTIVE")
        self.thread.start()

    def stop(self):
        """Зупинка логіки"""
        self.running = False
        self.hud.set_bot_status("STOPPED")
        self.overlay.set_status("BOT STOPPED")

    # ======================================================================
    # INTERNAL LOOP
    # ======================================================================

    def _loop(self):
        while self.running:
            try:
                time.sleep(0.05)

                # 1 — OCR Зчитування
                npc, question, answers = self.ocr.read_all()

                if not npc or not question:
                    continue

                # Оновлення HUD
                self.hud.set_current_name(npc)
                self.hud.set_question_text(question)

                # Якщо змінилось питання — запускаємо логіку
                if question != self.current_question or npc != self.current_npc:
                    self.current_question = question
                    self.current_npc = npc

                    answer = self._determine_answer(npc, question, answers)

                    if answer:
                        idx = ["пояснити", "запевнити", "надавити"].index(answer)
                        self.overlay.highlight(idx)
                        self.hud.set_selected_answer(answer)
                    else:
                        self.overlay.clear_highlight()
                        self.hud.set_selected_answer("Немає")

            except Exception as e:
                self.hud.set_error(str(e))
                print("Logic error:", e)

    # ======================================================================
    # DATABASE FUNCTIONS
    # ======================================================================

    def _npc_file(self, npc):
        """Файл answers/NPC.json"""
        safe = npc.replace(" ", "_")
        return os.path.join(self.zones_folder, safe + ".json")

    def _load_db(self, npc):
        """Load NPC DB into memory"""
        path = self._npc_file(npc)
        if not os.path.exists(path):
            self.local_db[npc] = {}
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                self.local_db[npc] = json.load(f)
        except:
            self.local_db[npc] = {}

    def _save_db(self, npc):
        """Save NPC DB"""
        path = self._npc_file(npc)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.local_db[npc], f, ensure_ascii=False, indent=2)

    # ======================================================================
    # SMART ANSWER LOGIC
    # ======================================================================

    def _determine_answer(self, npc, question, answers):
        """
        FULL PRO LOGIC:
        1) Точний пошук питання
        2) Fuzzy-матчинг
        3) Auto-learn (записує нову відповідь)
        """

        # Загрузити DB NPC
        if npc not in self.local_db:
            self._load_db(npc)

        db = self.local_db.get(npc, {})

        # 1 — Точний матч
        if question in db:
            return db[question]

        # 2 — Fuzzy матчинг (пошук схожих)
        if db:
            all_q = list(db.keys())
            match = difflib.get_close_matches(question, all_q, n=1, cutoff=0.65)
            if match:
                return db[match[0]]

        # 3 — Якщо не знайдено — логіка за замовчуванням (AI)
        best = self._logic_ai(question, answers)

        # Зберегти auto-learn
        db[question] = best
        self._save_db(npc)

        return best

    # ======================================================================
    # AI LOGIC — базова, але працює
    # ======================================================================

    def _logic_ai(self, question, answers):
        """
        PRO AI Logic:
        - keyword detection
        - emotional weight
        - answer-mapping
        """

        q = question.lower()

        # Пояснити
        if any(w in q for w in ["чому", "що", "поясни", "розкажи"]):
            return "пояснити"

        # Запевнити
        if any(w in q for w in ["спокій", "заспокій", "тихіше", "не переживай", "запевни"]):
            return "запевнити"

        # Надовити
        if any(w in q for w in ["швидше", "давай", "ти мусиш", "вимога", "зроби"]):
            return "надавити"

        # fallback
        return "пояснити"
