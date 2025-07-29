import sys
from PyQt5.QtWidgets import QApplication
from gui import MemoryChatGUI

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion') # Applica uno stile moderno
    
    window = MemoryChatGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
