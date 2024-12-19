import pandas as pd  # type: ignore
import dash  # type: ignore
from dash import dcc, html  # type: ignore
from dash.dependencies import Input, Output, State  # type: ignore
import plotly.graph_objects as go  # type: ignore
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

    # Callback per aggiornare dropdown e grafico in base al file caricato
    @app.callback(
        [Output('parametro-dropdown', 'options'),
         Output('parametro-dropdown', 'value'),
         Output('parametro-dropdown', 'style'),
         Output('grafico-interattivo', 'style')],
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename')]
    )
    def aggiorna_dropdown(contents, filename):
        if contents is None:
            return [], [], {'display': 'none'}, {'display': 'none'}

        dati = processa_csv(contents, filename)
        if dati is None or 'data_registrazione' not in dati.columns or 'nome_parametro' not in dati.columns or 'valore' not in dati.columns:
            return [], [], {'display': 'none'}, {'display': 'none'}

        parametri_unici = dati['nome_parametro'].unique()
        options = [{'label': parametro, 'value': parametro} for parametro in parametri_unici]
        return options, [], {'display': 'block'}, {'display': 'block'}

    # Callback per aggiornare il grafico in base alla selezione
    @app.callback(
        Output('grafico-interattivo', 'figure'),
        [Input('parametro-dropdown', 'value')],
        [State('upload-data', 'contents'),
         State('upload-data', 'filename')]
    )
    def aggiorna_grafico(parametri_selezionati, contents, filename):
        if contents is None or not parametri_selezionati:
            return {}

        dati = processa_csv(contents, filename)
        if dati is None:
            return {}

        dati['data_registrazione'] = pd.to_datetime(dati['data_registrazione'])

        # Filtra i dati per i parametri selezionati
        dati_filtrati = dati[dati['nome_parametro'].isin(parametri_selezionati)]

        # Determina la scala basata sul primo parametro selezionato
        primo_parametro = parametri_selezionati[0]
        dati_primo_parametro = dati_filtrati[dati_filtrati['nome_parametro'] == primo_parametro]
        y_min, y_max = dati_primo_parametro['valore'].min(), dati_primo_parametro['valore'].max()

        # Crea il grafico
        fig = go.Figure()

        # Aggiungi le tracce dei parametri selezionati
        for parametro in parametri_selezionati:
            dati_parametro = dati_filtrati[dati_filtrati['nome_parametro'] == parametro]
            if parametro == primo_parametro:
                # Non normalizza il primo parametro
                y_values = dati_parametro['valore']
            else:
                # Normalizza graficamente gli altri parametri
                y_values = (dati_parametro['valore'] - dati_parametro['valore'].min()) / (
                        dati_parametro['valore'].max() - dati_parametro['valore'].min()
                ) * (y_max - y_min) + y_min

            fig.add_trace(go.Scatter(
                x=dati_parametro['data_registrazione'],
                y=y_values,
                mode='lines',
                name=parametro,
                hoverinfo='text+name',  # Mostra i valori originali nel tooltip
                text=[f"Valore originale: {val}" for val in dati_parametro['valore']]  # Tooltip con valore originale
            ))

        # Configura il layout del grafico
        fig.update_layout(
            title=f'Grafico Interattivo (Scala basata su {primo_parametro})',
            xaxis=dict(title='Data'),
            yaxis=dict(title=f'Scala Basata su {primo_parametro}'),
            template='plotly_dark'
        )

        return fig

    # Funzione per aprire il browser
    def apri_browser():
        webbrowser.open_new("http://127.0.0.1:8050/")

    Timer(1, apri_browser).start()

    def termina_server(signum, frame):
        print("\nChiusura del server Dash...")
        sys.exit(0)

    signal.signal(signal.SIGINT, termina_server)
    app.run_server(debug=False)

if __name__ == "__main__":
    crea_app_dash()





# import pandas as pd  # type: ignore
# import dash  # type: ignore
# from dash import dcc, html  # type: ignore
# from dash.dependencies import Input, Output, State  # type: ignore
# import plotly.express as px  # type: ignore
# import io
# import base64
# import webbrowser
# from threading import Timer
# import signal
# import sys

# def crea_app_dash():
#     # Crea l'app Dash
#     app = dash.Dash(__name__, suppress_callback_exceptions=True)

#     # Layout dell'app
#     app.layout = html.Div([
#         html.H1("Visualizzatore di Grafici Interattivi", style={'textAlign': 'center'}),
#         dcc.Upload(
#             id='upload-data',
#             children=html.Div([
#                 'Trascina un file CSV oppure ',
#                 html.A('clicca qui per caricarlo')
#             ]),
#             style={
#                 'width': '50%',
#                 'height': '60px',
#                 'lineHeight': '60px',
#                 'borderWidth': '1px',
#                 'borderStyle': 'dashed',
#                 'borderRadius': '5px',
#                 'textAlign': 'center',
#                 'margin': '10px auto'
#             },
#             accept='.csv'
#         ),
#         dcc.Dropdown(
#             id='parametro-dropdown',
#             multi=True,  # Consente selezione multipla
#             clearable=True,
#             style={'width': '50%', 'margin': '10px auto', 'display': 'none'}  # Inizialmente nascosto
#         ),
#         dcc.Graph(id='grafico-interattivo', style={'display': 'none'})  # Grafico inizialmente nascosto
#     ])

#     # Funzione per elaborare il file caricato
#     def processa_csv(contents, filename):
#         try:
#             # Decodifica il contenuto del file
#             content_type, content_string = contents.split(',')
#             decoded = base64.b64decode(content_string)
#             # Legge il file CSV in un DataFrame
#             dati = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
#             return dati
#         except Exception as e:
#             print(f"Errore durante l'elaborazione del file: {e}")
#             return None

#     # Callback per aggiornare dropdown e grafico in base al file caricato
#     @app.callback(
#         [Output('parametro-dropdown', 'options'),
#          Output('parametro-dropdown', 'value'),
#          Output('parametro-dropdown', 'style'),
#          Output('grafico-interattivo', 'style')],
#         [Input('upload-data', 'contents')],
#         [State('upload-data', 'filename')]
#     )
#     def aggiorna_dropdown(contents, filename):
#         if contents is None:
#             # Niente file caricato, lascia nascosti dropdown e grafico
#             return [], [], {'display': 'none'}, {'display': 'none'}

#         # Elabora il file CSV
#         dati = processa_csv(contents, filename)
#         if dati is None or 'data_registrazione' not in dati.columns or 'nome_parametro' not in dati.columns or 'valore' not in dati.columns:
#             return [], [], {'display': 'none'}, {'display': 'none'}

#         # Parametri unici dal file CSV
#         parametri_unici = dati['nome_parametro'].unique()
#         options = [{'label': parametro, 'value': parametro} for parametro in parametri_unici]

#         # Mostra il dropdown e il grafico
#         return options, [], {'display': 'block'}, {'display': 'block'}

#     # Callback per aggiornare il grafico in base alla selezione
#     @app.callback(
#         Output('grafico-interattivo', 'figure'),
#         [Input('parametro-dropdown', 'value')],
#         [State('upload-data', 'contents'),
#          State('upload-data', 'filename')]
#     )
#     def aggiorna_grafico(parametri_selezionati, contents, filename):
#         if contents is None or not parametri_selezionati:
#             # Nessun file o nessun parametro selezionato, ritorna un grafico vuoto
#             return {}

#         # Elabora il file CSV
#         dati = processa_csv(contents, filename)
#         if dati is None:
#             return {}

#         # Converte la colonna 'data_registrazione' in formato datetime
#         dati['data_registrazione'] = pd.to_datetime(dati['data_registrazione'])

#         # Filtra i dati per i parametri selezionati
#         dati_filtrati = dati[dati['nome_parametro'].isin(parametri_selezionati)]

#         # Crea il grafico interattivo
#         fig = px.line(
#             dati_filtrati,
#             x='data_registrazione',
#             y='valore',
#             color='nome_parametro',
#             title='Grafico Interattivo di Parametri Selezionati',
#             labels={'data_registrazione': 'Data', 'valore': 'Valore', 'nome_parametro': 'Parametro'},
#             template='plotly_dark'
#         )
#         return fig

#     # Funzione per aprire il browser
#     def apri_browser():
#         webbrowser.open_new("http://127.0.0.1:8050/")  # URL dell'app Dash

#     # Usa un timer per aprire il browser dopo l'avvio del server
#     Timer(1, apri_browser).start()

#     # Gestore del segnale di chiusura
#     def termina_server(signum, frame):
#         print("\nChiusura del server Dash...")
#         sys.exit(0)

#     # Intercetta il segnale di interruzione (es. Ctrl+C)
#     signal.signal(signal.SIGINT, termina_server)

#     # Avvia il server Dash
#     app.run_server(debug=False)  # Disattiva il comportamento di apertura automatica

# if __name__ == "__main__":
#     crea_app_dash()