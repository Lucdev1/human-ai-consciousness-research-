# memory_manager.py
import json
import os
from datetime import datetime

class MemoryManager:
    """
    Gestisce il caricamento e il salvataggio della memoria dell'AI.
    """
    def __init__(self, filepath):
        self.filepath = filepath

    def load(self):
        """Carica la memoria dal file JSON."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # Se il file è corrotto o illeggibile, ritorna la struttura di default
                pass
        return self._get_default_memory()

    def save(self, memory_data):
        """Salva la memoria nel file JSON."""
        memory_data["ultimo_aggiornamento"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, indent=2, ensure_ascii=False)

    def _get_default_memory(self):
        """Restituisce la struttura di default per la memoria."""
        return {
            "profilo_utente": "",
            "progetti_attivi": [],
            "preferenze": [],
            "note_varie": [],
            "ultimo_aggiornamento": "",
            "sessioni_totali": 0
        }