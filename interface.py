from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QComboBox, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
import pyqtgraph as pg

class SynthInterface(QMainWindow):
    key_pressed = pyqtSignal(int)
    key_released = pyqtSignal(int)
    close_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Synthétiseur POO - Prototype")
        self.resize(900, 500)
        
        # Dictionnaire pour stocker nos boutons de touches 
        self.key_buttons = {}
        self.init_ui()

    def init_ui(self):
        # 1. Widget Central et Layout Principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 2. Choix de la forme d'onde
        self.combo = QComboBox()
        self.combo.addItems(["Sinus", "Carré", "Dents de scie"])
        self.combo.setFocusPolicy(Qt.NoFocus) #  pour que le clavier serve au piano 
        main_layout.addWidget(QLabel("Forme d'onde :"))
        main_layout.addWidget(self.combo)

        # 3. Visualisation (L'Oscilloscope)
        self.win_plt = pg.GraphicsLayoutWidget()
        main_layout.addWidget(self.win_plt)
        self.curve = self.win_plt.addPlot(title="Signal Temps Réel").plot(pen='y')
        # On fixe l'échelle verticale pour éviter que ça bouge trop
        self.win_plt.getItem(0,0).setYRange(-33000, 33000) 

      # --- 4. Le Clavier Visuel (Simple et Collé) ---
        keys_layout = QHBoxLayout()
        keys_layout.setSpacing(2) # Espace très fin entre les touches
        
        # Ordre chromatique pour placer les noires entre les blanches
        # Q=Do, Z=Do#, S=Ré, E=Ré#, D=Mi, F=Fa, T=Fa#, G=Sol, Y=Sol#, H=La, U=La#, J=Si, K=Do, O=Do#, L=Ré, P=Ré#
        sequence = ["Q", "Z", "S", "E", "D", "F", "T", "G", "Y", "H", "U", "J", "K", "O", "L", "P"]
        black_keys = ["Z", "E", "T", "Y", "U", "O", "P"]

        for note in sequence:
            btn = QPushButton(note)
            btn.setEnabled(False)
            btn.setFixedWidth(50) # Même taille pour tout le monde
            
            # Définition du style selon si c'est une noire ou une blanche
            if note in black_keys:
                style = "background-color: black; color: white; border: 1px solid gray; height: 100px; font-weight: bold;"
            else:
                style = "background-color: white; color: black; border: 1px solid black; height: 100px; font-weight: bold;"
            
            btn.setStyleSheet(style)
            
            # ASTUCE POO : On enregistre son style "normal" dans une propriété personnalisée
            btn.setProperty("original_style", style)
            
            self.key_buttons[note] = btn
            keys_layout.addWidget(btn)
        
        main_layout.addLayout(keys_layout)

    def get_wave_type(self):
        """Méthode pour que le 'Main' puisse savoir quelle onde est choisie"""
        return self.combo.currentText()

    def update_visual_key(self, key_code, pressed=True):
        """Change la couleur de la touche et la remet à l'état initial"""
        # On récupère le nom de la touche (ex: "Q")
        char = chr(key_code).upper() if 0 <= key_code <= 255 else None
        
        if char in self.key_buttons:
            btn = self.key_buttons[char]
            if pressed:
                # Quand on appuie : elle devient orange
                btn.setStyleSheet("background-color: orange; color: black; border: 1px solid black; height: 100px; font-weight: bold;")
            else:
                # Quand on relâche : on récupère le style qu'on avait stocké au début !
                original = btn.property("original_style")
                btn.setStyleSheet(original)

    def keyPressEvent(self, event):
        if not event.isAutoRepeat():
            self.update_visual_key(event.key(), True)
            self.key_pressed.emit(event.key())

    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat():
            self.update_visual_key(event.key(), False)
            self.key_released.emit(event.key())

    def update_display(self, t, data, freqs_list):
        """Met à jour le graphique"""
        self.curve.setData(t, data)

    def closeEvent(self, event):
        self.close_signal.emit()
        event.accept()
        
   """     
if __name__ == "__main__":
    import sys
    import numpy as np
    from PyQt5.QtWidgets import QApplication

    # 1. Création de l'application
    app = QApplication(sys.argv)
    
    # 2. Instanciation de TON interface
    fenetre = SynthInterface()
    fenetre.show()

    # 3. Simulation de données pour vérifier l'oscilloscope
    # On crée une sinusoïde factice
    t = np.linspace(0, 0.05, 1000)
    data = 15000 * np.sin(2 * np.pi * 440 * t) 
    
    # On appelle ta méthode pour voir si le dessin s'affiche
    fenetre.update_display(t, data, "Test Oscilloscope")

    # 4. Lancement de la boucle d'événements
    sys.exit(app.exec_())        
        
    # Petite fonction pour imprimer dans la console quand on appuie sur une touche
    def test_touche(key):
        print(f"Signal reçu ! Touche pressée : {key}")

    # On connecte le signal de ton interface à notre fonction de test
    fenetre.key_pressed.connect(test_touche)  
        
