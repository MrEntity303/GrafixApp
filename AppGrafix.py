import signal
from threading import Timer
import dash  # type: ignore
from dash import dcc, html  # type: ignore
from dash.dependencies import Input, Output, State  # type: ignore
from library.graphic import aggiorna_grafico, aggiorna_dropdown, aggiorna_grafico_on
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
        html.Div([
            html.H3("Grafico 1: Parametri Generali", style={'textAlign': 'center'}),
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
        ]),
        html.Div([
            html.H3("Grafico 2: Tempo di Lavoro", style={'textAlign': 'center'}),
            dcc.Dropdown(
                id='parametro-on-dropdown',
                multi=True,
                clearable=True,
                style={'width': '50%', 'margin': '10px auto', 'display': 'none'}
            ),
            dcc.Dropdown(
                id='secondo-parametro-on-dropdown',
                multi=True,
                clearable=True,
                style={'width': '50%', 'margin': '10px auto', 'display': 'none'}
            ),
            dcc.Checklist(
                id='normalizza-on-checklist',
                options=[{'label': 'Normalizza i Dati', 'value': 'normalizza'}],
                value=[],
                style={'width': '50%', 'margin': '10px auto', 'display': 'none'}
            ),
            dcc.Graph(id='grafico-interattivo-on', style={'display': 'none'})
        ])
    ])


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



    @app.callback(
        Output('grafico-interattivo-on', 'figure'),
        [Input('parametro-on-dropdown', 'value'),
         Input('secondo-parametro-on-dropdown', 'value'),
         Input('normalizza-on-checklist', 'value')],
        [State('upload-data', 'contents'),
         State('upload-data', 'filename')]
    )
    def update_graph_on(parametro_on, secondo_parametro_on, normalizza_on, contents, filename):
        return aggiorna_grafico_on(parametro_on, secondo_parametro_on, normalizza_on, contents, filename)

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
        return aggiorna_dropdown(contents, filename)

    @app.callback(
        [Output('parametro-on-dropdown', 'options'),
         Output('parametro-on-dropdown', 'value'),
         Output('secondo-parametro-on-dropdown', 'options'),
         Output('secondo-parametro-on-dropdown', 'value'),
         Output('normalizza-on-checklist', 'style'),
         Output('parametro-on-dropdown', 'style'),
         Output('secondo-parametro-on-dropdown', 'style'),
         Output('grafico-interattivo-on', 'style')],
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename')]
    )
    def update_dropdown_on(contents, filename):
        return aggiorna_dropdown(contents, filename)

    

    Timer(1, apri_browser).start()

    signal.signal(signal.SIGINT, termina_server)

    # Avvia il server Dash
    app.run_server(debug=False)


if __name__ == "__main__":
    crea_app_dash()