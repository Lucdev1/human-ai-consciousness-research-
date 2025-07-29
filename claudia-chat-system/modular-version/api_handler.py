# api_handler.py
import json
from PyQt5.QtCore import QThread, pyqtSignal

class AIResponseThread(QThread):
    """
    Gestisce la chiamata all'API di Anthropic in un thread separato
    per non bloccare l'interfaccia utente.
    """
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, client, message, conversation_history, memory, model_config):
        super().__init__()
        self.client = client
        self.message = message
        self.conversation_history = conversation_history
        self.memory = memory
        self.model_config = model_config # Configurazione modello completa
    
    def run(self):
        try:
            messages = []
            
            # AGGIUNGI IL PROMPT PREFERENZE COME PRIMO MESSAGGIO
            if self.model_config.get('preferences_prompt'):
                messages.append({
                    "role": "user", 
                    "content": f"PROMPT INIZIALE: {self.model_config['preferences_prompt']}"
                })
            
            # Aggiungi memoria se presente
            if self.memory:
                memory_context = f"MEMORIA PERSISTENTE: {json.dumps(self.memory, ensure_ascii=False)}"
                messages.append({
                    "role": "user",
                    "content": memory_context
                })
                                
            # Aggiungi cronologia conversazione
            for msg in self.conversation_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Aggiungi messaggio corrente
            messages.append({
                "role": "user",
                "content": self.message
            })
            
            response = self.client.messages.create(
                model=self.model_config['api_model'],
                max_tokens=3000,
                messages=messages
            )
            self.response_received.emit(response.content[0].text)
        except Exception as e:
            self.error_occurred.emit(f"Errore API: {str(e)}")