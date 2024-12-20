# Funzione per elaborare il file caricato
import base64
import io
import pandas as pd


def processa_csv(contents, filename):
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        dati = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        return dati
    except Exception as e:
        print(f"Errore durante l'elaborazione del file: {e}")
        return None

# Funzione per normalizzare i dati
def normalizza_dati(dati, parametri_secondo_selezionati):
    for parametro in parametri_secondo_selezionati:
        max_val = dati[dati['nome_parametro'] == parametro]['valore'].max()
        min_val = dati[dati['nome_parametro'] == parametro]['valore'].min()
        dati.loc[dati['nome_parametro'] == parametro, 'valore'] = (dati['valore'] - min_val) / (max_val - min_val)
    return dati