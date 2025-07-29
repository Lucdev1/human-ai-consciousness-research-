import os
import sys
from dotenv import load_dotenv
from anthropic import Anthropic
from PyQt5.QtWidgets import QMessageBox

def setup_anthropic_client():
    """
    Carica la chiave API Anthropic e inizializza il client.
    """
    load_dotenv()
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        QMessageBox.critical(None, "Errore API", "ANTHROPIC_API_KEY non trovata nel file .env")
        sys.exit(1)
    
    return Anthropic(api_key=api_key)
