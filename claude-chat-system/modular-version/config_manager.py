import json
import sys
from PyQt5.QtWidgets import QMessageBox

class ModelConfigManager:
    def __init__(self, models_file="models.json"):
        self.models_file = models_file
        self.models_config = self._load_models_config()
        self.current_model_name = self._get_selected_model_name()

    def _load_models_config(self):
        """Carica la configurazione dei modelli dal file JSON."""
        try:
            with open(self.models_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.critical(None, "Errore Caricamento Configurazione", 
                                 f"Impossibile caricare {self.models_file}: {str(e)}")
            sys.exit(1)
            
    def _get_selected_model_name(self):
        """Ottiene il nome del modello attualmente selezionato o il primo disponibile."""
        for model_name, config in self.models_config.items():
            if config.get('selected', False):
                return model_name
        # Se nessuno è selezionato, prendi il primo
        if self.models_config:
            return list(self.models_config.keys())[0]
        return None # Nessun modello configurato

    def get_model_config(self, model_name=None):
        """Restituisce la configurazione completa per un dato nome modello o per quello corrente."""
        name = model_name if model_name else self.current_model_name
        return self.models_config.get(name)

    def save_models_config(self):
        """Salva la configurazione dei modelli nel file JSON."""
        with open(self.models_file, 'w', encoding='utf-8') as f:
            json.dump(self.models_config, f, indent=2, ensure_ascii=False)

    def set_current_model(self, new_model_name):
        """Imposta il modello corrente e salva la configurazione."""
        if new_model_name in self.models_config:
            # Deseleziona tutti
            for config in self.models_config.values():
                config['selected'] = False
            
            # Seleziona il nuovo
            self.models_config[new_model_name]['selected'] = True
            self.current_model_name = new_model_name
            self.save_models_config()
            return True
        return False
        
    def get_all_model_names(self):
        """Restituisce una lista di tutti i nomi dei modelli configurati."""
        return list(self.models_config.keys())
