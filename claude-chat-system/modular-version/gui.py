import json
import sys
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QTextEdit, QLineEdit, QPushButton, QLabel,
                            QMessageBox, QSplitter, QGroupBox, QScrollArea, QComboBox, QToolBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCursor, QPalette, QColor

# Importa i moduli personalizzati
from anthropic_client_setup import setup_anthropic_client
from config_manager import ModelConfigManager
from memory_manager import MemoryManager
from ai_thread import AIResponseThread

class MemoryChatGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.client = setup_anthropic_client()
        self.config_manager = ModelConfigManager()
        self.memory_manager = MemoryManager()
        
        self.session_history = []
        
        # Imposta modello corrente
        self.current_model_name = self.config_manager.current_model_name
        self.current_model_config = self.config_manager.get_model_config()
        
        self.init_ui()
        self.show_initial_message()
        
    def on_model_changed(self, model_name):
        """Gestisce il cambio di modello."""
        if self.config_manager.set_current_model(model_name):
            self.current_model_name = model_name
            self.current_model_config = self.config_manager.get_model_config()
            
            self.update_window_title()
            self.update_model_info()
            self.update_chat_title() # Aggiorna il titolo della chat con il nome del nuovo modello
            self.status_label.setText(f"Modello cambiato: {model_name} 🔄")
            QTimer.singleShot(3000, lambda: self.status_label.setText("Pronta! 💙"))
            
            print(f"DEBUG: Modello cambiato a {model_name}")
            print(f"API Model: {self.current_model_config['api_model']}")
        else:
            print(f"Errore: Tentativo di selezionare modello non esistente: {model_name}")
    
    def update_window_title(self):
        """Aggiorna il titolo della finestra in base al modello corrente."""
        model_display = self.current_model_name
        if "Sonnet 4" in self.current_model_name:
            title = f"💙 Chat con Claudia - {model_display}"
        else:
            title = f"🤖 Chat con AI - {model_display}"
        self.setWindowTitle(title)
        
    def keyPressEvent(self, event):
        """Gestisce i tasti premuti globalmente per l'invio messaggio."""
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
        """Inizializza l'interfaccia utente."""
        self.update_window_title()
        self.setGeometry(100, 100, 1200, 800)
        
        # TOOLBAR per selezione modello
        toolbar = QToolBar("Modelli")
        self.addToolBar(toolbar)
        
        # Label per modello
        model_label = QLabel("Modello AI:")
        model_label.setStyleSheet("font-weight: bold; margin-right: 10px;")
        toolbar.addWidget(model_label)
        
        # ComboBox per selezione modello
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(200)
        self.model_combo.setStyleSheet("""
            QComboBox {
                padding: 5px 10px;
                border: 2px solid #2196F3;
                border-radius: 5px;
                font-weight: bold;
                background-color: white;
            }
            QComboBox:drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        
        # Popola ComboBox
        for model_name in self.config_manager.get_all_model_names():
            self.model_combo.addItem(model_name)
        
        # Seleziona modello corrente
        self.model_combo.setCurrentText(self.current_model_name)
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        
        toolbar.addWidget(self.model_combo)
        toolbar.addSeparator()
        
        # Info modello corrente
        self.model_info_label = QLabel()
        self.update_model_info()
        toolbar.addWidget(self.model_info_label)
        
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
        self.update_chat_title()
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
        self.message_input.setPlaceholderText("Scrivi qui il tuo messaggio... (Ctrl+Invio per inviare)")
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
        """Aggiorna le info del modello corrente nella toolbar."""
        model_config = self.config_manager.get_model_config()
        if model_config:
            api_model = model_config['api_model']
            info_text = f"API: {api_model}"
            self.model_info_label.setText(info_text)
            self.model_info_label.setStyleSheet("color: #666; font-size: 10px; margin-left: 10px;")
        else:
            self.model_info_label.setText("Nessun modello selezionato")
            self.model_info_label.setStyleSheet("color: red; font-size: 10px; margin-left: 10px;")
    
    def update_chat_title(self):
        """Aggiorna il titolo della chat principale."""
        if "Sonnet 4" in self.current_model_name:
            title = "💬 Chat con Claudia"
            color = "#2196F3"
        else:
            title = f"🤖 Chat con {self.current_model_name}"
            color = "#FF9800"
            
        self.chat_title.setText(title) # Aggiorna il testo della QLabel esistente
        self.chat_title.setStyleSheet(f"color: {color}; margin: 10px;")
    
    def style_button(self, button, color):
        """Applica stile uniforme ai pulsanti."""
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
    
    def show_initial_message(self):
        """Mostra il messaggio iniziale all'avvio della chat."""
        current_memory = self.memory_manager.get_memory_content()
        ai_name = "Claudia" if "Sonnet 4" in self.current_model_name else self.current_model_name
        
        if "Sonnet 4" in self.current_model_name:
            if not any(value for key, value in current_memory.items() if key not in ["ultimo_aggiornamento", "sessioni_totali"]) or current_memory["sessioni_totali"] == 0:
                initial_msg = "Ciao Luca! Sono Claudia 💙\n\nPrima volta che usiamo la memoria persistente! Dimmi qualcosa di te così posso iniziare a ricordarmi le cose importanti."
            else:
                initial_msg = f"""Ciao Luca! Sono Claudia 💙

Quello che ricordo di te:
{self.memory_manager.format_memory_for_display()}

Sessioni totali: {current_memory['sessioni_totali']}
Ultimo aggiornamento: {current_memory['ultimo_aggiornamento']}

Di cosa parliamo oggi?"""
        else:
            initial_msg = f"Ciao! Sono {ai_name}. Come posso aiutarti oggi?"
        
        self.add_message_to_chat(ai_name, initial_msg, "#2196F3" if "Sonnet 4" in self.current_model_name else "#FF9800")
    
    def add_message_to_chat(self, sender, message, color):
        """Aggiunge un messaggio alla chat display."""
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
        """Invia il messaggio dell'utente all'AI."""
        message = self.message_input.toPlainText().strip()
        if not message:
            return
        
        self.add_message_to_chat("Tu", message, "#FF9800")
        self.message_input.clear()
        
        self.message_input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.status_label.setText("L'AI sta pensando... 🤔")
        
        self.ai_thread = AIResponseThread(
            self.client, 
            message, 
            self.session_history, 
            self.memory_manager.get_memory_content(), 
            self.current_model_config
        )
        self.ai_thread.response_received.connect(self.handle_ai_response)
        self.ai_thread.error_occurred.connect(self.handle_ai_error)
        self.ai_thread.start()
    
    def handle_ai_response(self, response):
        """Gestisce la risposta ricevuta dall'AI."""
        ai_name = "Claudia" if "Sonnet 4" in self.current_model_name else self.current_model_name
        color = "#2196F3" if "Sonnet 4" in self.current_model_name else "#FF9800"
        
        self.add_message_to_chat(ai_name, response, color)
        
        self.session_history.append({"role": "assistant", "content": response})
        
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.message_input.setFocus()
        self.status_label.setText("Pronta! 💙")
    
    def handle_ai_error(self, error):
        """Gestisce gli errori durante la comunicazione con l'AI."""
        self.add_message_to_chat("Sistema", f"Errore: {error}", "#F44336")
        
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.message_input.setFocus()
        self.status_label.setText("Errore! ❌")
    
    def save_memory_manual(self):
        """Salva manualmente la memoria dopo averla aggiornata dalla sessione."""
        if not self.session_history:
            QMessageBox.information(self, "Info", "Nessun dialogo da salvare in memoria.")
            return
        
        self.status_label.setText("Aggiornando memoria... 🧠")
        self.update_memory_from_session()
    
    def update_memory_from_session(self):
        """Invia un prompt all'AI per aggiornare la memoria basandosi sulla sessione."""
        if not self.session_history:
            return
        
        session_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.session_history[-10:]])
        
        prompt = f"""Aggiorna questo profilo utente con i nuovi concetti chiave dal dialogo.
        
PROFILO ATTUALE:
{json.dumps(self.memory_manager.get_memory_content(), indent=2, ensure_ascii=False)}

NUOVO DIALOGO:
{session_text}

Rispondi SOLO con un JSON aggiornato che integra le nuove informazioni importanti, mantenendo la stessa struttura.
Estrai solo concetti significativi, non conversazione casuale."""
        
        # Usa sempre Sonnet 4 per aggiornare la memoria (più intelligente)
        sonnet4_config = self.config_manager.get_model_config("Claude Sonnet 4 (multimodale)")
        if not sonnet4_config:
            # Fallback se Sonnet 4 non è configurato o non trovato
            sonnet4_config = self.current_model_config 
        
        self.memory_update_thread = AIResponseThread(
            self.client, 
            prompt, 
            [], # Nessuna cronologia conversazione per l'aggiornamento della memoria
            self.memory_manager.get_memory_content(), 
            sonnet4_config
        )
        self.memory_update_thread.response_received.connect(self.handle_memory_update)
        self.memory_update_thread.error_occurred.connect(lambda e: self.status_label.setText(f"Errore aggiornamento memoria: {e} ❌"))
        self.memory_update_thread.start()
    
    def handle_memory_update(self, response):
        """Gestisce la risposta dell'AI per l'aggiornamento della memoria."""
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                updated_memory_data = json.loads(json_str)
                self.memory_manager.update_memory_data(updated_memory_data)
                self.status_label.setText("🧠 Memoria aggiornata!")
                
                if self.memory_group.isVisible():
                    self.show_memory_content()
            else:
                self.status_label.setText("Errore nel parsing JSON della memoria! ❌")
        except Exception as e:
            self.status_label.setText(f"Errore gestione aggiornamento memoria: {e} ❌")
    
    def toggle_memory_display(self):
        """Mostra/nasconde la visualizzazione del contenuto della memoria."""
        if self.memory_group.isVisible():
            self.memory_group.setVisible(False)
            self.show_memory_button.setText("👁️ Mostra Memoria")
        else:
            self.show_memory_content()
            self.memory_group.setVisible(True)
            self.show_memory_button.setText("🙈 Nascondi Memoria")
    
    def show_memory_content(self):
        """Aggiorna il QTextEdit con il contenuto della memoria formattato."""
        self.memory_display.setText(json.dumps(self.memory_manager.get_memory_content(), indent=2, ensure_ascii=False))
    
    def reset_memory(self):
        """Reset della memoria utente."""
        reply = QMessageBox.question(self, "Conferma Reset", 
                                   "Sei sicuro di voler cancellare tutta la memoria?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.memory_manager.reset_memory()
            self.memory_display.clear()
            self.status_label.setText("🗑️ Memoria cancellata!")
            QMessageBox.information(self, "Reset Completato", "Memoria cancellata con successo!")
    
    def clear_chat(self):
        """Pulisce la cronologia chat visuale."""
        reply = QMessageBox.question(self, "Pulisci Chat", 
                                   "Vuoi pulire la chat visuale? (La memoria rimane intatta)",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.chat_display.clear()
            self.session_history = [] # Resetta anche la cronologia in memoria
            self.show_initial_message()
            self.status_label.setText("🧹 Chat pulita!")
    
    def exit_without_saving(self):
        """Esce dall'applicazione senza salvare la memoria della sessione."""
        reply = QMessageBox.question(self, "Esci Senza Salvare", 
                                   "Sei sicuro di voler uscire senza salvare la sessione corrente?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            QApplication.quit()

    def exit_with_saving(self):
        """Salva la memoria della sessione e poi esce dall'applicazione."""
        if self.session_history:
            reply = QMessageBox.question(self, "Salvataggio", 
                                       "Vuoi aggiornare la memoria prima di uscire?",
                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.update_memory_from_session()
                # Non chiamare QApplication.quit() immediatamente qui per dare tempo al thread
                # di aggiornamento memoria di completare. La chiusura avverrà tramite closeEvent.
                QTimer.singleShot(1000, QApplication.quit) # Chiude dopo 1 secondo, sperando che il thread finisca
                return
            elif reply == QMessageBox.Cancel:
                # Se l'utente annulla, ignora l'evento di chiusura
                return
        # Se non c'è session_history o l'utente non vuole salvare, chiudi subito
        QApplication.quit()
    
    def closeEvent(self, event):
        """Gestisce l'evento di chiusura della finestra."""
        if self.session_history:
            reply = QMessageBox.question(self, "Salvataggio", 
                                       "Vuoi aggiornare la memoria prima di uscire?",
                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.update_memory_from_session()
                # Accetta l'evento di chiusura solo quando il thread di aggiornamento ha finito (o dopo un timeout)
                # Questo è un approccio semplificato; un sistema più robusto userebbe un segnale dal thread
                QTimer.singleShot(1000, lambda: event.accept()) 
                event.ignore() # Ignora l'evento corrente per aspettare il salvataggio
                return
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        
        event.accept() # Accetta l'evento di chiusura se non c'è nulla da salvare o l'utente ha detto No
