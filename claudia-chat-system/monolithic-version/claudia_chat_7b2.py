import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QTextEdit, QLineEdit, QPushButton, QLabel,
                             QMessageBox, QSplitter, QGroupBox, QScrollArea, QComboBox, QToolBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCursor, QPalette, QColor

class AIResponseThread(QThread):
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
            print(f"\n=== THREAD RUN AVVIATO ===")
            print(f"Modello selezionato: {self.model_config['api_model']}")
            print(f"Messaggio: '{self.message}'")
            
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
            
            print(f"DEBUG: Chiamando modello: {self.model_config['api_model']}")
            
            response = self.client.messages.create(
                model=self.model_config['api_model'],
                max_tokens=3000,
                messages=messages
            )
            self.response_received.emit(response.content[0].text)
        except Exception as e:
            self.error_occurred.emit(f"Errore API: {str(e)}")

class MemoryChatGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Carica variabili d'ambiente
        load_dotenv()
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            QMessageBox.critical(self, "Errore", "ANTHROPIC_API_KEY non trovata nel file .env")
            sys.exit(1)
        
        self.client = Anthropic(api_key=self.api_key)
        self.memory_file = "claudia_memory.json"
        self.models_file = "model.json" # Manteniamo il nome file per consistenza, anche se contiene un solo modello
        self.session_history = []
        
        # Carica configurazioni modelli e imposta il modello unico
        self.models_config = self.load_models_config()
        self.current_model_name = self.get_single_model_name() # Cambiato il nome della variabile per chiarezza
        self.current_model_config = self.models_config[self.current_model_name] # La configurazione completa del modello
        
        # Carica memoria esistente
        self.memory = self.load_memory()
        
        self.init_ui()
        self.show_initial_message()
        
    def load_models_config(self):
        """Carica la configurazione dei modelli (ora attende un solo modello)"""
        try:
            with open(self.models_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if not isinstance(config, dict) or not config:
                    raise ValueError(f"Il file {self.models_file} deve contenere un oggetto JSON con almeno un modello.")
                return config
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile caricare {self.models_file}: {str(e)}")
            sys.exit(1)
    
    def get_single_model_name(self):
        """Restituisce il nome del singolo modello presente in models_config"""
        if len(self.models_config) != 1:
            QMessageBox.warning(self, "Avviso", f"Il file '{self.models_file}' dovrebbe contenere un solo modello, ma ne contiene {len(self.models_config)}. Verrà usato il primo trovato.")
        return list(self.models_config.keys())[0]

    def update_window_title(self):
        """Aggiorna il titolo della finestra"""
        model_display = self.current_model_name
        if "Sonnet 4" in self.current_model_name:
            title = f"💙 Chat con Claudia - {model_display}"
        else:
            title = f"🤖 Chat con AI - {model_display}"
        self.setWindowTitle(title)
        
    def keyPressEvent(self, event):
        """Gestisce i tasti premuti globalmente"""
        if (self.message_input.hasFocus() and 
             event.key() == Qt.Key_Return and 
             event.modifiers() == Qt.ControlModifier):
             self.send_message()
             event.accept()
             return
        elif (self.message_input.hasFocus() and 
              event.key() == Qt.Key_Return and 
              event.modifiers() == Qt.NoModifier):
            super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)
            
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        self.update_window_title()
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principale orizzontale
        main_layout = QHBoxLayout(central_widget)
        
        # Splitter per dividere chat e memoria
        splitter = QSplitter(Qt.Horizontal)
        
        # === SEZIONE CHAT (sinistra) ===
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        
        # Titolo chat dinamico
        self.chat_title = QLabel()
        self.update_chat_title() # Aggiornato per usare current_model_name
        chat_layout.addWidget(self.chat_title)
        
        # Area di visualizzazione chat
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Consolas", 10))
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        chat_layout.addWidget(self.chat_display)
        
        # Layout per input e pulsanti
        input_layout = QHBoxLayout()
        
        # Campo di input
        self.message_input = QTextEdit()
        self.message_input.setFont(QFont("Arial", 10))
        self.message_input.setPlaceholderText("Scrivi qui il tuo messaggio... (Ctrl+Enter per inviare)")
        self.message_input.setMaximumHeight(120)
        self.message_input.setMinimumHeight(50)
        self.message_input.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                border: 2px solid #2196F3;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        input_layout.addWidget(self.message_input)
        
        # Pulsante invio
        self.send_button = QPushButton("Invia")
        self.send_button.setFont(QFont("Arial", 10, QFont.Bold))
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setDefault(False)
        self.send_button.setAutoDefault(False)
        input_layout.addWidget(self.send_button)
        
        chat_layout.addLayout(input_layout)
        
        # === SEZIONE MEMORIA E CONTROLLI (destra) ===
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        
        # Titolo controlli
        control_title = QLabel("🧠 Memoria & Controlli")
        control_title.setFont(QFont("Arial", 14, QFont.Bold))
        control_title.setStyleSheet("color: #FF9800; margin: 10px;")
        control_layout.addWidget(control_title)
        
        # Pulsanti di controllo
        buttons_layout = QVBoxLayout()
        
        self.save_button = QPushButton("💾 Salva Memoria")
        self.save_button.clicked.connect(self.save_memory_manual)
        self.style_button(self.save_button, "#4CAF50")
        buttons_layout.addWidget(self.save_button)
        
        self.show_memory_button = QPushButton("👁️ Mostra Memoria")
        self.show_memory_button.clicked.connect(self.toggle_memory_display)
        self.style_button(self.show_memory_button, "#FF9800")
        buttons_layout.addWidget(self.show_memory_button)
        
        self.reset_button = QPushButton("🗑️ Reset Memoria")
        self.reset_button.clicked.connect(self.reset_memory)
        self.style_button(self.reset_button, "#F44336")
        buttons_layout.addWidget(self.reset_button)
        
        self.clear_chat_button = QPushButton("🧹 Pulisci Chat")
        self.clear_chat_button.clicked.connect(self.clear_chat)
        self.style_button(self.clear_chat_button, "#9C27B0")
        buttons_layout.addWidget(self.clear_chat_button)
        
        self.exit_button = QPushButton("🚪 Esci Senza Salvare")
        self.exit_button.clicked.connect(self.exit_without_saving)
        self.style_button(self.exit_button, "#607D8B")
        buttons_layout.addWidget(self.exit_button)
        
        self.exit_with_saving_button = QPushButton("💡 Esci con Salvataggio")
        self.exit_with_saving_button.clicked.connect(self.exit_with_saving)
        self.style_button(self.exit_with_saving_button, "#3F51B5")
        buttons_layout.addWidget(self.exit_with_saving_button)
        
        control_layout.addLayout(buttons_layout)
        
        # --- NUOVA SEZIONE: INFO MODELLO ---
        model_info_group = QGroupBox("Info Modello")
        model_info_group.setFont(QFont("Arial", 10, QFont.Bold))
        model_info_layout = QVBoxLayout(model_info_group)

        # Etichetta per il nome "friendly" del modello
        model_name_label = QLabel(f"Nome: {self.current_model_name}")
        model_name_label.setFont(QFont("Arial", 10))
        model_name_label.setStyleSheet("color: #FF9800;")

        # Etichetta per l'identificativo API del modello
        api_model_label = QLabel(f"API Model: {self.current_model_config['api_model']}")
        api_model_label.setFont(QFont("Arial", 10))
        api_model_label.setStyleSheet("color: #FF9800;")
        api_model_label.setWordWrap(True) # Per andare a capo se il nome è lungo
        
        model_info_layout.addWidget(model_name_label)
        model_info_layout.addWidget(api_model_label)
        
        control_layout.addWidget(model_info_group) # Aggiungi il gruppo al layout di destra
        # --- FINE NUOVA SEZIONE ---

        # Area memoria (inizialmente nascosta)
        self.memory_group = QGroupBox("Contenuto Memoria:")
        self.memory_group.setVisible(False)
        memory_group_layout = QVBoxLayout(self.memory_group)
        
        self.memory_display = QTextEdit()
        self.memory_display.setReadOnly(True)
        self.memory_display.setFont(QFont("Consolas", 9))
        self.memory_display.setMaximumHeight(300)
        self.memory_display.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffff99;
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        memory_group_layout.addWidget(self.memory_display)
        control_layout.addWidget(self.memory_group)
        
        # Status bar
        self.status_label = QLabel("Pronta! 💙")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold; margin: 10px;")
        control_layout.addWidget(self.status_label)
        
        # Aggiunge spazio elastico
        control_layout.addStretch()
        
        # Configura splitter
        splitter.addWidget(chat_widget)
        splitter.addWidget(control_widget)
        splitter.setSizes([800, 400])
        
        main_layout.addWidget(splitter)
        
        # Imposta stile generale
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                background-color: #f5f5f5;
            }
        """)
    
    def update_model_info(self):
        """Aggiorna le info del modello corrente (non più una toolbar)"""
        # Questa funzione non è più necessaria per l'interfaccia,
        # ma il modello è sempre accessibile tramite self.current_model_config
        pass 
    
    def update_chat_title(self):
        """Aggiorna il titolo della chat"""
        if "Sonnet 4" in self.current_model_name:
            title = "💬 Chat con Claudia"
            color = "#2196F3"
        else:
            title = f"🤖 Chat con {self.current_model_name}"
            color = "#FF9800"
            
        self.chat_title.setText(title) # Imposta il testo del QLabel esistente
        self.chat_title.setFont(QFont("Arial", 14, QFont.Bold))
        self.chat_title.setStyleSheet(f"color: {color}; margin: 10px;")
    
    def style_button(self, button, color):
        """Applica stile uniforme ai pulsanti"""
        button.setFont(QFont("Arial", 10, QFont.Bold))
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-size: 11px;
                margin: 2px;
            }}
            QPushButton:hover {{
                background-color: {color}CC;
            }}
            QPushButton:pressed {{
                background-color: {color}99;
            }}
        """)
    
    def load_memory(self):
        """Carica la memoria dal file JSON"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "profilo_utente": "",
            "progetti_attivi": [],
            "preferenze": [],
            "note_varie": [],
            "ultimo_aggiornamento": "",
            "sessioni_totali": 0
        }
    
    def save_memory(self):
        """Salva la memoria nel file JSON"""
        self.memory["ultimo_aggiornamento"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
        self.status_label.setText("💾 Memoria salvata!")
        QTimer.singleShot(3000, lambda: self.status_label.setText("Pronta! 💙"))
    
    def show_initial_message(self):
        """Mostra il messaggio iniziale"""
        if "Sonnet 4" in self.current_model_name:
            ai_name = "Claudia"
            if not any(self.memory.values()) or self.memory["sessioni_totali"] == 0:
                initial_msg = "Ciao Luca! Sono Claudia 💙\n\nPrima volta che usiamo la memoria persistente! Dimmi qualcosa di te così posso iniziare a ricordarmi le cose importanti."
            else:
                initial_msg = f"""Ciao Luca! Sono Claudia 💙

Quello che ricordo di te:
{self.format_memory_for_display()}

Sessioni totali: {self.memory['sessioni_totali']}
Ultimo aggiornamento: {self.memory['ultimo_aggiornamento']}

Di cosa parliamo oggi?"""
        else:
            ai_name = self.current_model_name
            initial_msg = f"Ciao! Sono {ai_name}. Come posso aiutarti oggi?"
        
        self.add_message_to_chat(ai_name, initial_msg, "#2196F3" if "Sonnet 4" in self.current_model_name else "#FF9800")
    
    def format_memory_for_display(self):
        """Formatta la memoria per la visualizzazione"""
        formatted = ""
        if self.memory["profilo_utente"]:
            formatted += f"• Profilo: {self.memory['profilo_utente']}\n"
        if self.memory["progetti_attivi"]:
            formatted += f"• Progetti: {', '.join(self.memory['progetti_attivi'])}\n"
        if self.memory["preferenze"]:
            formatted += f"• Preferenze: {', '.join(self.memory['preferenze'])}\n"
        if self.memory["note_varie"]:
            formatted += f"• Note: {', '.join(self.memory['note_varie'])}\n"
        return formatted or "Niente di specifico ancora salvato."
    
    def add_message_to_chat(self, sender, message, color):
        """Aggiunge un messaggio alla chat"""
        timestamp = datetime.now().strftime("%H:%M")
        
        self.chat_display.append(f"""
<div style="margin: 10px 0;">
    <strong style="color: {color};">[{timestamp}] {sender}:</strong><br>
    <span style="color: #FFFFFF; margin-left: 20px;">{message.replace(chr(10), '<br>')}</span>
</div>
        """)
        
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def send_message(self):
        """Invia un messaggio"""
        message = self.message_input.toPlainText().strip()
        if not message:
            return
        
        # Aggiungi messaggio utente alla chat
        self.add_message_to_chat("Tu", message, "#FF9800")
        self.message_input.clear()
        
        # Disabilita input durante l'attesa
        self.message_input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.status_label.setText("L'AI sta pensando... 🤔")
        
        # Avvia thread per risposta AI con configurazione modello corrente
        self.ai_thread = AIResponseThread(self.client, message, self.session_history, self.memory, self.current_model_config)
        self.ai_thread.response_received.connect(self.handle_ai_response)
        self.ai_thread.error_occurred.connect(self.handle_ai_error)
        self.ai_thread.start()
    
    def handle_ai_response(self, response):
        """Gestisce la risposta dell'AI"""
        ai_name = "Claudia" if "Sonnet 4" in self.current_model_name else self.current_model_name
        color = "#2196F3" if "Sonnet 4" in self.current_model_name else "#FF9800"
        
        self.add_message_to_chat(ai_name, response, color)
        
        # Aggiungi alla cronologia
        self.session_history.append({"role": "assistant", "content": response})
        
        # Riabilita input
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.message_input.setFocus()
        self.status_label.setText("Pronta! 💙")
    
    def handle_ai_error(self, error):
        """Gestisce gli errori dell'AI"""
        self.add_message_to_chat("Sistema", f"Errore: {error}", "#F44336")
        
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.message_input.setFocus()
        self.status_label.setText("Errore! ❌")
    
    def save_memory_manual(self):
        """Salva manualmente la memoria aggiornandola dalla sessione"""
        if not self.session_history:
            QMessageBox.information(self, "Info", "Nessun dialogo da salvare in memoria.")
            return
        
        self.status_label.setText("Aggiornando memoria... 🧠")
        self.update_memory_from_session()
    
    def update_memory_from_session(self):
        """Aggiorna la memoria dalla sessione"""
        if not self.session_history:
            return
        
        session_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.session_history[-10:]])
        
        prompt = f"""Aggiorna questo profilo utente con i nuovi concetti chiave dal dialogo.
        
PROFILO ATTUALE:
{json.dumps(self.memory, indent=2, ensure_ascii=False)}

NUOVO DIALOGO:
{session_text}

Rispondi SOLO con un JSON aggiornato che integra le nuove informazioni importanti, mantenendo la stessa struttura.
Estrai solo concetti significativi, non conversazione casuale."""
        
        # Usa il modello configurato per la memoria (che dovrebbe essere l'unico disponibile)
        self.memory_thread = AIResponseThread(self.client, prompt, [], self.memory, self.current_model_config)
        self.memory_thread.response_received.connect(self.handle_memory_update)
        self.memory_thread.error_occurred.connect(lambda e: self.status_label.setText("Errore aggiornamento memoria! ❌"))
        self.memory_thread.start()
    
    def handle_memory_update(self, response):
        """Gestisce l'aggiornamento della memoria"""
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                updated_memory = json.loads(json_str)
                self.memory.update(updated_memory)
                self.memory["sessioni_totali"] += 1
                self.save_memory()
                self.status_label.setText("🧠 Memoria aggiornata!")
                
                if self.memory_group.isVisible():
                    self.show_memory_content()
            else:
                self.status_label.setText("Errore nel parsing memoria! ❌")
        except Exception as e:
            self.status_label.setText(f"Errore aggiornamento memoria: {e} ❌") # Messaggio di errore più specifico
    
    def toggle_memory_display(self):
        """Mostra/nasconde la visualizzazione della memoria"""
        if self.memory_group.isVisible():
            self.memory_group.setVisible(False)
            self.show_memory_button.setText("👁️ Mostra Memoria")
        else:
            self.show_memory_content()
            self.memory_group.setVisible(True)
            self.show_memory_button.setText("🙈 Nascondi Memoria")
    
    def show_memory_content(self):
        """Mostra il contenuto della memoria"""
        self.memory_display.setText(json.dumps(self.memory, indent=2, ensure_ascii=False))
    
    def reset_memory(self):
        """Reset della memoria"""
        reply = QMessageBox.question(self, "Conferma Reset", 
                                     "Sei sicuro di voler cancellare tutta la memoria?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.memory = {
                "profilo_utente": "",
                "progetti_attivi": [],
                "preferenze": [],
                "note_varie": [],
                "ultimo_aggiornamento": "",
                "sessioni_totali": 0
            }
            self.save_memory()
            self.memory_display.clear()
            self.status_label.setText("🗑️ Memoria cancellata!")
            QMessageBox.information(self, "Reset Completato", "Memoria cancellata con successo!")
    
    def clear_chat(self):
        """Pulisce la cronologia chat visuale (non la memoria)"""
        reply = QMessageBox.question(self, "Pulisci Chat", 
                                     "Vuoi pulire la chat visuale? (La memoria rimane intatta)",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.chat_display.clear()
            self.session_history = [] # Svuota anche la session_history interna
            self.show_initial_message()
            self.status_label.setText("🧹 Chat pulita!")
    
    def exit_without_saving(self):
        """Esce senza salvare la memoria"""
        reply = QMessageBox.question(self, "Esci Senza Salvare", 
                                     "Sei sicuro di voler uscire senza salvare la sessione corrente?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            QApplication.quit()

    def exit_with_saving(self):
        """Salva automaticamente quando si chiude l'applicazione (chiamato da bottone)"""
        if self.session_history:
            reply = QMessageBox.question(self, "Salvataggio", 
                                         "Vuoi aggiornare la memoria prima di uscire?",
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.update_memory_from_session()
                # Aggiungiamo un timer per permettere al thread di salvataggio di finire
                QTimer.singleShot(1500, QApplication.quit) # Attendiamo un po' prima di chiudere
            elif reply == QMessageBox.No:
                QApplication.quit()
            # Se reply è QMessageBox.Cancel, non facciamo nulla e l'app rimane aperta
        else:
           QApplication.quit()    
    
    def closeEvent(self, event):
        """Gestisce l'evento di chiusura della finestra"""
        if self.session_history:
            reply = QMessageBox.question(self, "Salvataggio", 
                                         "Vuoi aggiornare la memoria prima di uscire?",
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.update_memory_from_session()
                # Ritarda l'accettazione dell'evento di chiusura per permettere il salvataggio
                QTimer.singleShot(1500, lambda: event.accept()) # Aumentato il ritardo
                event.ignore() # Ignora l'evento per non chiudere subito
                return
            elif reply == QMessageBox.Cancel:
                event.ignore() # Annulla la chiusura
                return
        
        event.accept() # Accetta la chiusura se non ci sono dati da salvare o l'utente ha scelto No

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MemoryChatGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
