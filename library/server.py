# Funzione per aprire il browser
import sys
from threading import Timer
import webbrowser

def apri_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")


# Gestore del segnale di chiusura
def termina_server(signum, frame):
    print("\nChiusura del server Dash...")
    sys.exit(0)