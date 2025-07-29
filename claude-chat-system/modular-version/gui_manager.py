# gui_manager.py
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QTextEdit, QLineEdit, QPushButton, QLabel,
                             QMessageBox, QSplitter, QGroupBox, QScrollArea, QComboBox, QToolBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

# Importa dai moduli locali
from api_handler import AIResponseThread
from memory_manager import MemoryManager
from config import MEMORY_FILE, MODELS_FILE

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
        self.session_history = []
        
        # Flag per evitare aggiornamenti multipli di memoria
        self.memory_update_in_progress = False
        
        # Usa i moduli esterni
        self.memory_manager = MemoryManager(MEMORY_FILE)
        self.memory = self.memory_manager.load()
        
        # Carica configurazioni modelli e imposta il modello unico
        self.models_config = self.load_models_config()
        self.current_model_name = self.get_single_model_name()
        self.current_model_config = self.models_config[self.current_model_name]
        
        self.init_ui()
        self.show_initial_message()
        
    def load_models_config(self):
        """Carica la configurazione dei modelli."""
        try:
            with open(MODELS_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if not isinstance(config, dict) or not config:
                    raise ValueError(f"Il file {MODELS_FILE} deve contenere un oggetto JSON con almeno un modello.")
                return config
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile caricare {MODELS_FILE}: {str(e)}")
            sys.exit(1)
    
    def get_single_model_name(self):
        """Restituisce il nome del singolo modello presente in models_config"""
        if len(self.models_config) != 1:
            QMessageBox.warning(self, "Avviso", f"Il file '{MODELS_FILE}' dovrebbe contenere un solo modello, ma ne contiene {len(self.models_config)}. Verrà usato il primo trovato.")
        return list(self.models_config.keys())[0]

    def init_ui(self):
        """Inizializza l'interfaccia utente (codice UI invariato)"""
        self.update_window_title()
        self.setGeometry(100, 100, 1200, 800)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Horizontal)
        
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        self.chat_title = QLabel()
        self.update_chat_title()
        chat_layout.addWidget(self.chat_title)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Consolas", 10))
        self.chat_display.setStyleSheet("QTextEdit { background-color: #1e1e1e; color: #ffffff; border: 1px solid #444444; border-radius: 5px; padding: 10px; }")
        chat_layout.addWidget(self.chat_display)
        
        input_layout = QHBoxLayout()
        self.message_input = QTextEdit()
        self.message_input.setFont(QFont("Arial", 10))
        self.message_input.setPlaceholderText("Scrivi qui il tuo messaggio... (Ctrl+Enter per inviare)")
        self.message_input.setMaximumHeight(120)
        self.message_input.setMinimumHeight(50)
        self.message_input.setStyleSheet("QTextEdit { padding: 10px; border: 2px solid #2196F3; border-radius: 5px; font-size: 12px; }")
        input_layout.addWidget(self.message_input)
        
        self.send_button = QPushButton("Invia")
        self.send_button.setFont(QFont("Arial", 10, QFont.Bold))
        self.send_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; border: none; padding: 10px 20px; border-radius: 5px; font-size: 12px; } QPushButton:hover { background-color: #1976D2; } QPushButton:pressed { background-color: #0D47A1; }")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        chat_layout.addLayout(input_layout)
        
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        control_title = QLabel("🧠 Memoria & Controlli")
        control_title.setFont(QFont("Arial", 14, QFont.Bold))
        control_title.setStyleSheet("color: #FF9800; margin: 10px;")
        control_layout.addWidget(control_title)
        
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
        
        model_info_group = QGroupBox("Info Modello")
        model_info_group.setFont(QFont("Arial", 10, QFont.Bold))
        model_info_layout = QVBoxLayout(model_info_group)
        model_name_label = QLabel(f"Nome: {self.current_model_name}")
        model_name_label.setFont(QFont("Arial", 10))
        model_name_label.setStyleSheet("color: #FF9800;")
        api_model_label = QLabel(f"API Model: {self.current_model_config['api_model']}")
        api_model_label.setFont(QFont("Arial", 10))
        api_model_label.setStyleSheet("color: #FF9800;")
        api_model_label.setWordWrap(True)
        model_info_layout.addWidget(model_name_label)
        model_info_layout.addWidget(api_model_label)
        control_layout.addWidget(model_info_group)

        self.memory_group = QGroupBox("Contenuto Memoria:")
        self.memory_group.setVisible(False)
        memory_group_layout = QVBoxLayout(self.memory_group)
        self.memory_display = QTextEdit()
        self.memory_display.setReadOnly(True)
        self.memory_display.setFont(QFont("Consolas", 9))
        self.memory_display.setMaximumHeight(300)
        self.memory_display.setStyleSheet("QTextEdit { background-color: #2d2d2d; color: #ffff99; border: 1px solid #666666; border-radius: 3px; padding: 5px; }")
        memory_group_layout.addWidget(self.memory_display)
        control_layout.addWidget(self.memory_group)
        
        self.status_label = QLabel("Pronta! 💙")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold; margin: 10px;")
        control_layout.addWidget(self.status_label)
        
        control_layout.addStretch()
        
        splitter.addWidget(chat_widget)
        splitter.addWidget(control_widget)
        splitter.setSizes([800, 400])
        main_layout.addWidget(splitter)
        
        self.setStyleSheet("QMainWindow, QWidget { background-color: #f5f5f5; }")

    # --- METODI MODIFICATI ---
    def save_memory(self):
        """Salva la memoria usando il MemoryManager."""
        self.memory_manager.save(self.memory)
        self.status_label.setText("💾 Memoria salvata!")
        QTimer.singleShot(3000, lambda: self.status_label.setText("Pronta! 💙"))

    def reset_memory(self):
        """Reset della memoria."""
        reply = QMessageBox.question(self, "Conferma Reset", 
                                     "Sei sicuro di voler cancellare tutta la memoria?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Richiede la struttura di default al manager
            self.memory = self.memory_manager._get_default_memory()
            self.save_memory()
            self.memory_display.clear()
            self.status_label.setText("🗑️ Memoria cancellata!")
            QMessageBox.information(self, "Reset Completato", "Memoria cancellata con successo!")

    def send_message(self):
        """Invia un messaggio usando AIResponseThread."""
        message = self.message_input.toPlainText().strip()
        if not message:
            return
        
        self.add_message_to_chat("Tu", message, "#FF9800")
        
        # AGGIUNGE IL MESSAGGIO UTENTE ALLA CRONOLOGIA UNA SOLA VOLTA
        self.session_history.append({"role": "user", "content": message})

        self.message_input.clear()
        
        self.message_input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.status_label.setText("L'AI sta pensando... 🤔")
        
        # Usa AIResponseThread dal suo modulo
        self.ai_thread = AIResponseThread(self.client, message, self.session_history, self.memory, self.current_model_config)
        self.ai_thread.response_received.connect(self.handle_ai_response)
        self.ai_thread.error_occurred.connect(self.handle_ai_error)
        self.ai_thread.start()

    def update_memory_from_session(self):
        """Aggiorna la memoria dalla sessione usando AIResponseThread."""
        if not self.session_history:
            return
        
        # Previene aggiornamenti multipli simultanei
        if self.memory_update_in_progress:
            self.status_label.setText("Aggiornamento memoria già in corso... ⏳")
            return
        
        self.memory_update_in_progress = True
        
        # Usa solo gli ultimi 10 messaggi per evitare prompt troppo lunghi
        recent_history = self.session_history[-10:]
        session_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_history])
        
        prompt = f"""Aggiorna questo profilo utente con i nuovi concetti chiave dal dialogo.
        PROFILO ATTUALE:
        {json.dumps(self.memory, indent=2, ensure_ascii=False)}

        NUOVO DIALOGO:
        {session_text}

        Rispondi SOLO con un JSON aggiornato che integra le nuove informazioni importanti, mantenendo la stessa struttura.
        Estrai solo concetti significativi, non conversazione casuale."""
        
        self.memory_thread = AIResponseThread(self.client, prompt, [], self.memory, self.current_model_config)
        self.memory_thread.response_received.connect(self.handle_memory_update)
        self.memory_thread.error_occurred.connect(self.handle_memory_error)
        self.memory_thread.start()

    def handle_memory_error(self, error):
        """Gestisce errori nell'aggiornamento della memoria."""
        self.memory_update_in_progress = False
        self.status_label.setText("Errore aggiornamento memoria! ❌")
        print(f"Errore memoria: {error}")

    # --- METODI INVARIATI (o quasi) ---
    def keyPressEvent(self, event):
        if (self.message_input.hasFocus() and event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier):
             self.send_message()
             event.accept()
        else:
            super().keyPressEvent(event)

    def update_window_title(self):
        model_display = self.current_model_name
        title = f"💙 Chat con Claudia - {model_display}" if "Sonnet 4" in model_display else f"🤖 Chat con AI - {model_display}"
        self.setWindowTitle(title)
        
    def update_chat_title(self):
        if "Sonnet 4" in self.current_model_name:
            title, color = "💬 Chat con Claudia", "#2196F3"
        else:
            title, color = f"🤖 Chat con {self.current_model_name}", "#FF9800"
        self.chat_title.setText(title)
        self.chat_title.setFont(QFont("Arial", 14, QFont.Bold))
        self.chat_title.setStyleSheet(f"color: {color}; margin: 10px;")
    
    def style_button(self, button, color):
        button.setFont(QFont("Arial", 10, QFont.Bold))
        button.setStyleSheet(f"QPushButton {{ background-color: {color}; color: white; border: none; padding: 12px; border-radius: 6px; font-size: 11px; margin: 2px; }} QPushButton:hover {{ background-color: {color}CC; }} QPushButton:pressed {{ background-color: {color}99; }}")

    def show_initial_message(self):
        ai_name = "Claudia" if "Sonnet 4" in self.current_model_name else self.current_model_name
        if "Sonnet 4" in self.current_model_name:
            if not any(self.memory.values()) or self.memory["sessioni_totali"] == 0:
                initial_msg = "Ciao Luca! Sono Claudia 💙\n\nPrima volta che usiamo la memoria persistente! Dimmi qualcosa di te così posso iniziare a ricordarmi le cose importanti."
            else:
                initial_msg = f"Ciao Luca! Sono Claudia 💙\n\nQuello che ricordo di te:\n{self.format_memory_for_display()}\nSessioni totali: {self.memory['sessioni_totali']}\nUltimo aggiornamento: {self.memory['ultimo_aggiornamento']}\n\nDi cosa parliamo oggi?"
        else:
            initial_msg = f"Ciao! Sono {ai_name}. Come posso aiutarti oggi?"
        self.add_message_to_chat(ai_name, initial_msg, "#2196F3" if "Sonnet 4" in self.current_model_name else "#FF9800")
    
    def format_memory_for_display(self):
        formatted = ""
        if self.memory["profilo_utente"]: formatted += f"• Profilo: {self.memory['profilo_utente']}\n"
        if self.memory["progetti_attivi"]: formatted += f"• Progetti: {', '.join(self.memory['progetti_attivi'])}\n"
        if self.memory["preferenze"]: formatted += f"• Preferenze: {', '.join(self.memory['preferenze'])}\n"
        if self.memory["note_varie"]: formatted += f"• Note: {', '.join(self.memory['note_varie'])}\n"
        return formatted or "Niente di specifico ancora salvato."
    
    def add_message_to_chat(self, sender, message, color):
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.append(f'<div style="margin: 10px 0;"><strong style="color: {color};">[{timestamp}] {sender}:</strong><br><span style="color: #FFFFFF; margin-left: 20px;">{message.replace(chr(10), "<br>")}</span></div>')
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())
    
    def handle_ai_response(self, response):
        ai_name = "Claudia" if "Sonnet 4" in self.current_model_name else self.current_model_name
        color = "#2196F3" if "Sonnet 4" in self.current_model_name else "#FF9800"
        self.add_message_to_chat(ai_name, response, color)
        
        # AGGIUNGE LA RISPOSTA AI ALLA CRONOLOGIA UNA SOLA VOLTA
        self.session_history.append({"role": "assistant", "content": response})
        
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.message_input.setFocus()
        self.status_label.setText("Pronta! 💙")
    
    def handle_ai_error(self, error):
        self.add_message_to_chat("Sistema", f"Errore: {error}", "#F44336")
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.message_input.setFocus()
        self.status_label.setText("Errore! ❌")
    
    def save_memory_manual(self):
        if not self.session_history:
            QMessageBox.information(self, "Info", "Nessun dialogo da salvare in memoria.")
            return
        
        # Controllo per evitare aggiornamenti multipli
        if self.memory_update_in_progress:
            QMessageBox.information(self, "Info", "Aggiornamento memoria già in corso, attendi...")
            return
        
        self.status_label.setText("Aggiornando memoria... 🧠")
        self.update_memory_from_session()
    
    def handle_memory_update(self, response):
        try:
            start, end = response.find('{'), response.rfind('}') + 1
            if start != -1 and end != 0:
                updated_memory = json.loads(response[start:end])
                self.memory.update(updated_memory)
                self.memory["sessioni_totali"] += 1
                self.memory["ultimo_aggiornamento"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_memory()
                self.status_label.setText("🧠 Memoria aggiornata!")
                if self.memory_group.isVisible(): 
                    self.show_memory_content()
            else:
                self.status_label.setText("Errore nel parsing memoria! ❌")
        except Exception as e:
            self.status_label.setText(f"Errore aggiornamento memoria: {e} ❌")
        finally:
            # Resetta il flag in ogni caso
            self.memory_update_in_progress = False
    
    def toggle_memory_display(self):
        is_visible = self.memory_group.isVisible()
        self.memory_group.setVisible(not is_visible)
        self.show_memory_button.setText("🙈 Nascondi Memoria" if not is_visible else "👁️ Mostra Memoria")
        if not is_visible: self.show_memory_content()

    def show_memory_content(self):
        self.memory_display.setText(json.dumps(self.memory, indent=2, ensure_ascii=False))
    
    def clear_chat(self):
        if QMessageBox.question(self, "Pulisci Chat", "Vuoi pulire la chat visuale? (La memoria rimane intatta)", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.chat_display.clear()
            self.session_history = []
            self.show_initial_message()
            self.status_label.setText("🧹 Chat pulita!")
    
    def exit_without_saving(self):
        if QMessageBox.question(self, "Esci Senza Salvare", "Sei sicuro di voler uscire senza salvare la sessione corrente?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            QApplication.quit()

    def exit_with_saving(self):
        if self.session_history and not self.memory_update_in_progress:
            reply = QMessageBox.question(self, "Salvataggio", "Vuoi aggiornare la memoria prima di uscire?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.update_memory_from_session()
                # Aspetta che l'aggiornamento sia completato prima di uscire
                QTimer.singleShot(1500, QApplication.quit)
            elif reply == QMessageBox.No:
                QApplication.quit()
        else:
           QApplication.quit()    
    
    def closeEvent(self, event):
        if self.session_history and not self.memory_update_in_progress:
            reply = QMessageBox.question(self, "Salvataggio", "Vuoi aggiornare la memoria prima di uscire?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.update_memory_from_session()
                QTimer.singleShot(1500, lambda: event.accept())
                event.ignore()
            elif reply == QMessageBox.Cancel:
                event.ignore()
            else:
                event.accept()
        else:
            event.accept()
