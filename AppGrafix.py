import pandas as pd  # type: ignore
import dash  # type: ignore
from dash import dcc, html  # type: ignore
from dash.dependencies import Input, Output, State  # type: ignore
import plotly.graph_objects as go  # type: ignore
from plotly.subplots import make_subplots  # type: ignore
import io
import base64
import webbrowser
from threading import Timer
import signal
import sys

def crea_app_dash():
    # Crea l'app Dash
    app = dash.Dash(__name__, suppress_callback_exceptions=True)

    # Layout dell'app
    app.layout = html.Div([
        html.H1("Visualizzatore di Grafici Interattivi", style={'textAlign': 'center'}),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Trascina un file CSV oppure ',
                html.A('clicca qui per caricarlo')
            ]),
            style={
                'width': '50%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px auto'
            },
            accept='.csv'
        ),
        dcc.Dropdown(
            id='parametro-dropdown',
            multi=True,  # Consente selezione multipla
            clearable=True,
            style={'width': '50%', 'margin': '10px auto', 'display': 'none'}  # Inizialmente nascosto
        ),
        dcc.Dropdown(
            id='secondo-parametro-dropdown',
            multi=True,  # Consente selezione multipla
            clearable=True,
            style={'width': '50%', 'margin': '10px auto', 'display': 'none'}  # Inizialmente nascosto
        ),
        dcc.Checklist(
            id='normalizza-checklist',
            options=[{'label': 'Normalizza i Dati', 'value': 'normalizza'}],
            value=[],  # Non è selezionato inizialmente
            style={'width': '50%', 'margin': '10px auto', 'display': 'none'}  # Inizialmente nascosto
        ),
        dcc.Graph(id='grafico-interattivo', style={'display': 'none'})  # Grafico inizialmente nascosto
    ])

    # Funzione per elaborare il file caricato
    def processa_csv(contents, filename):
        try:
            # Decodifica il contenuto del file
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            # Legge il file CSV in un DataFrame
            dati = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            return dati
        except Exception as e:
            print(f"Errore durante l'elaborazione del file: {e}")
            return None

    # Funzione per normalizzare i dati
    def normalizza_dati(dati, parametri_secondo_selezionati):
        # Normalizza i dati per i parametri selezionati (scalando tra 0 e 1)
        for parametro in parametri_secondo_selezionati:
            max_val = dati[dati['nome_parametro'] == parametro]['valore'].max()
            min_val = dati[dati['nome_parametro'] == parametro]['valore'].min()
            dati.loc[dati['nome_parametro'] == parametro, 'valore'] = (dati['valore'] - min_val) / (max_val - min_val)
        return dati

    # Callback per aggiornare dropdown, casella da spuntare e grafico in base al file caricato
    @app.callback(
        [Output('parametro-dropdown', 'options'),
         Output('parametro-dropdown', 'value'),
         Output('secondo-parametro-dropdown', 'options'),
         Output('secondo-parametro-dropdown', 'value'),
         Output('normalizza-checklist', 'style'),
         Output('parametro-dropdown', 'style'),
         Output('secondo-parametro-dropdown', 'style'),
         Output('grafico-interattivo', 'style')],
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename')]
    )
    def aggiorna_dropdown(contents, filename):
        if contents is None:
            # Niente file caricato, lascia nascosti dropdown, checklist e grafico
            return [], [], [], [], {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}

        # Elabora il file CSV
        dati = processa_csv(contents, filename)
        if dati is None or 'data_registrazione' not in dati.columns or 'nome_parametro' not in dati.columns or 'valore' not in dati.columns:
            return [], [], [], [], {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}

        # Parametri unici dal file CSV
        parametri_unici = dati['nome_parametro'].unique()
        options = [{'label': parametro, 'value': parametro} for parametro in parametri_unici]

        # Mostra i dropdown e la casella da spuntare
        return options, [], options, [], {'display': 'block'}, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}

    # Callback per aggiornare il grafico in base alla selezione e alla normalizzazione
    @app.callback(
        Output('grafico-interattivo', 'figure'),
        [Input('parametro-dropdown', 'value'),
         Input('secondo-parametro-dropdown', 'value'),
         Input('normalizza-checklist', 'value')],
        [State('upload-data', 'contents'),
         State('upload-data', 'filename')]
    )
    def aggiorna_grafico(parametri_selezionati, parametri_secondo_selezionati, normalizza, contents, filename):
        if contents is None or not parametri_selezionati:
            # Nessun file o nessun parametro selezionato, ritorna un grafico vuoto
            return {}

        # Elabora il file CSV
        dati = processa_csv(contents, filename)
        if dati is None:
            return {}

        # Converte la colonna 'data_registrazione' in formato datetime
        dati['data_registrazione'] = pd.to_datetime(dati['data_registrazione'])

        # Filtra i dati per i parametri selezionati
        dati_filtrati_1 = dati[dati['nome_parametro'].isin(parametri_selezionati)]
        dati_filtrati_2 = dati[dati['nome_parametro'].isin(parametri_secondo_selezionati)]

        # Se è selezionata la normalizzazione, normalizza i dati
        if 'normalizza' in normalizza:
            dati_filtrati_2 = normalizza_dati(dati_filtrati_2, parametri_secondo_selezionati)

        # Crea il grafico con due assi Y
        fig = make_subplots(
            rows=1, cols=1, 
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=("Grafico Parametri Selezionati"),
            specs=[[{"secondary_y": True}]]  # Aggiunge il supporto per il secondo asse Y
        )

        # Traccia il primo grafico (per il primo set di parametri)
        for parametro in parametri_selezionati:
            dati_parametro = dati_filtrati_1[dati_filtrati_1['nome_parametro'] == parametro]
            fig.add_trace(
                go.Scatter(x=dati_parametro['data_registrazione'], y=dati_parametro['valore'], mode='lines', name=parametro),
                row=1, col=1, secondary_y=False  # Asse Y principale
            )

        # Traccia il secondo grafico (per il secondo set di parametri) su un asse Y separato
        for parametro in parametri_secondo_selezionati:
            dati_parametro = dati_filtrati_2[dati_filtrati_2['nome_parametro'] == parametro]
            fig.add_trace(
                go.Scatter(x=dati_parametro['data_registrazione'], y=dati_parametro['valore'], mode='lines', name=parametro),
                row=1, col=1, secondary_y=True  # Asse Y secondario
            )

        # Aggiungi i titoli e personalizza l'asse
        fig.update_layout(
            title_text="Grafico Interattivo di Parametri Selezionati",
            xaxis_title='Data',
            yaxis_title='Valore',
            yaxis2_title='Valore Secondo Parametro',
            template='plotly_dark',
            showlegend=True
        )

        # Restituisce il grafico con due assi Y
        return fig

    # Funzione per aprire il browser
    def apri_browser():
        webbrowser.open_new("http://127.0.0.1:8050/")  # URL dell'app Dash

    # Usa un timer per aprire il browser dopo l'avvio del server
    Timer(1, apri_browser).start()

    # Gestore del segnale di chiusura
    def termina_server(signum, frame):
        print("\nChiusura del server Dash...")
        sys.exit(0)

    # Intercetta il segnale di interruzione (es. Ctrl+C)
    signal.signal(signal.SIGINT, termina_server)

    # Avvia il server Dash
    app.run_server(debug=False)  # Disattiva il comportamento di apertura automatica

if __name__ == "__main__":
    crea_app_dash()