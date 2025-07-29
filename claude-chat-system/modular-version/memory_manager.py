import json
import os
from datetime import datetime

class MemoryManager:
    def __init__(self, memory_file="claudia_memory.json"):
        self.memory_file = memory_file
        self.memory = self._load_memory()

    def _load_memory(self):
        """Carica la memoria dal file JSON."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                # In caso di errore o file corrotto, reinizializza la memoria
                pass
        
        # Struttura di memoria predefinita
        return {
            "profilo_utente": "",
            "progetti_attivi": [],
            "preferenze": [],
            "note_varie": [],
            "ultimo_aggiornamento": "",
            "sessioni_totali": 0
        }
    
    def save_memory(self):
        """Salva la memoria corrente nel file JSON."""
        self.memory["ultimo_aggiornamento"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)

    def get_memory_content(self):
        """Restituisce il contenuto completo della memoria."""
        return self.memory

    def update_memory_data(self, updated_data):
        """Aggiorna la memoria con i nuovi dati e incrementa il contatore sessioni."""
        self.memory.update(updated_data)
        self.memory["sessioni_totali"] += 1
        self.save_memory()

    def format_memory_for_display(self):
        """Formatta la memoria per una visualizzazione leggibile."""
        formatted = ""
        if self.memory["profilo_utente"]:
            formatted += f"• Profilo: {self.memory['profilo_utente']}\n"
        if self.memory["progetti_attivi"]:
            formatted += f"• Progetti: {', '.join(self.memory['progetti_attivi'])}\n"
        if self.memory["preferenze"]:
            formatted += f"• Preferenze: {', '.join(self.memory['preferenze'])}\n"
        if self.memory["note_varie"]:
            formatted += f"• Note: {', '.join(self.memory['note_varie'])}\n"
        return formatted.strip() or "Niente di specifico ancora salvato."
        
    def reset_memory(self):
        """Reinizializza la memoria allo stato predefinito."""
        self.memory = {
            "profilo_utente": "",
            "progetti_attivi": [],
            "preferenze": [],
            "note_varie": [],
            "ultimo_aggiornamento": "",
            "sessioni_totali": 0
        }
        self.save_memory() # Salva lo stato resettato
