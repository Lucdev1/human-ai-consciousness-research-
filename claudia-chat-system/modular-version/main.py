# main.py
import sys
from PyQt5.QtWidgets import QApplication
from gui_manager import MemoryChatGUI

def main():
    """
    Funzione principale per avviare l'applicazione.
    """
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MemoryChatGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()