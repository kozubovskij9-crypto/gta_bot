import os
import json
import threading
from datetime import datetime


class NPCDatabase:
    """
    PRO NPC Database Manager
    — кожен NPC має свій JSON
    — структура: answers/<name>.json
    — збереження автоматичне та безпечне
    """

    def __init__(self, base_folder="answers"):
        self.base = base_folder
        self.cache = {}           # {npc_name: {question: answer}}
        self.lock = threading.Lock()

        if not os.path.exists(self.base):
            os.makedirs(self.base)

    # --------------------------
    # SAFE LOAD JSON FILE
    # --------------------------
    def _load_file(self, npc_name):
        path = os.path.join(self.base, f"{npc_name}.json")

        if not os.path.exists(path):
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            # файл пошкоджений → створюємо новий
            return {}

    # --------------------------
    # SAFE SAVE JSON FILE
    # --------------------------
    def _save_file(self, npc_name, data):
        path = os.path.join(self.base, f"{npc_name}.json")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            print(f"[NPC-DB] ERROR saving {npc_name}.json")

    # --------------------------
    # LOAD NPC DATA TO CACHE
    # --------------------------
    def load_npc(self, npc_name):
        with self.lock:
            data = self._load_file(npc_name)
            self.cache[npc_name] = data
            return data

    # --------------------------
    # GET ANSWER IF EXISTS
    # --------------------------
    def get_answer(self, npc_name, question):
        with self.lock:
            if npc_name not in self.cache:
                self.load_npc(npc_name)

            answers = self.cache.get(npc_name, {})

            # Пошук точного питання
            if question in answers:
                return answers[question]

            # Пошук часткового збігу (якщо OCR зчитав не ідеально)
            for q in answers:
                if q.lower().strip() in question.lower().strip():
                    return answers[q]

        return None  # відповіді нема

    # --------------------------
    # SAVE / UPDATE ANSWER
    # --------------------------
    def save_answer(self, npc_name, question, answer):
        with self.lock:
            if npc_name not in self.cache:
                self.cache[npc_name] = {}

            self.cache[npc_name][question] = {
                "answer": answer,
                "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Миттєво записуємо у файл
            self._save_file(npc_name, self.cache[npc_name])

    # --------------------------
    # RETURN LIST OF QUESTIONS
    # --------------------------
    def list_questions(self, npc_name):
        if npc_name not in self.cache:
            self.load_npc(npc_name)

        return list(self.cache[npc_name].keys())

    # --------------------------
    # DELETE QUESTION
    # --------------------------
    def delete_question(self, npc_name, question):
        with self.lock:
            if npc_name not in self.cache:
                return False

            if question in self.cache[npc_name]:
                del self.cache[npc_name][question]
                self._save_file(npc_name, self.cache[npc_name])
                return True

        return False

    # --------------------------
    # CLEAR NPC FILE
    # --------------------------
    def reset_npc(self, npc_name):
        with self.lock:
            self.cache[npc_name] = {}
            self._save_file(npc_name, {})

    # --------------------------
    # GET FULL NPC DATA (GUI)
    # --------------------------
    def export_npc(self, npc_name):
        if npc_name not in self.cache:
            self.load_npc(npc_name)

        return self.cache[npc_name]
