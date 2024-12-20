import signal
from threading import Timer
import dash  # type: ignore
from dash import dcc, html  # type: ignore
from dash.dependencies import Input, Output, State  # type: ignore
from library.graphic import aggiorna_grafico, aggiorna_dropdown
from library.server import apri_browser, termina_server


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
            multi=True,
            clearable=True,
            style={'width': '50%', 'margin': '10px auto', 'display': 'none'}
        ),
        dcc.Dropdown(
            id='secondo-parametro-dropdown',
            multi=True,
            clearable=True,
            style={'width': '50%', 'margin': '10px auto', 'display': 'none'}
        ),
        dcc.Checklist(
            id='normalizza-checklist',
            options=[{'label': 'Normalizza i Dati', 'value': 'normalizza'}],
            value=[],
            style={'width': '50%', 'margin': '10px auto', 'display': 'none'}
        ),
        dcc.Graph(id='grafico-interattivo', style={'display': 'none'})
    ])

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
    def update_dropdown(contents, filename):
        # La funzione aggiorna_dropdown deve restituire una tupla con 8 valori
        return aggiorna_dropdown(contents, filename)


    @app.callback(
        Output('grafico-interattivo', 'figure'),
        [Input('parametro-dropdown', 'value'),
         Input('secondo-parametro-dropdown', 'value'),
         Input('normalizza-checklist', 'value')],
        [State('upload-data', 'contents'),
         State('upload-data', 'filename')]
    )
    def update_graph(parametro, secondo_parametro, normalizza, contents, filename):
        return aggiorna_grafico(parametro, secondo_parametro, normalizza, contents, filename)
    

    Timer(1, apri_browser).start()

    signal.signal(signal.SIGINT, termina_server)

    # Avvia il server Dash
    app.run_server(debug=False)


if __name__ == "__main__":
    crea_app_dash()