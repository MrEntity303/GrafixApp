import pandas as pd
from library.data_csv_tool import normalizza_dati, processa_csv
from plotly.subplots import make_subplots  # type: ignore
import plotly.graph_objects as go  # type: ignore


def aggiorna_dropdown(contents, filename):
        if contents is None:
            return [], [], [], [], {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}

        dati = processa_csv(contents, filename)
        if dati is None or 'data_registrazione' not in dati.columns or 'nome_parametro' not in dati.columns or 'valore' not in dati.columns:
            return [], [], [], [], {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}

        parametri_unici = dati['nome_parametro'].unique()
        options = [{'label': parametro, 'value': parametro} for parametro in parametri_unici]

        return options, [], options, [], {'display': 'block'}, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}


def aggiorna_grafico(parametri_selezionati, parametri_secondo_selezionati, normalizza, contents, filename):
    if contents is None or not parametri_selezionati:
        return {}

    dati = processa_csv(contents, filename)
    if dati is None:
        return {}

    dati['data_registrazione'] = pd.to_datetime(dati['data_registrazione'])
    original_values = {}

    dati_filtrati_1 = dati[dati['nome_parametro'].isin(parametri_selezionati)]
    dati_filtrati_2 = dati[dati['nome_parametro'].isin(parametri_secondo_selezionati)]

    if 'normalizza' in normalizza:
        for parametro in parametri_secondo_selezionati:
            original_values[parametro] = dati_filtrati_2[dati_filtrati_2['nome_parametro'] == parametro]['valore'].copy()
        dati_filtrati_2 = normalizza_dati(dati_filtrati_2, parametri_secondo_selezionati)

    fig = make_subplots(
        rows=1, cols=1, 
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("Grafico Parametri Selezionati"),
        specs=[[{"secondary_y": True}]]
    )

    for parametro in parametri_selezionati:
        dati_parametro = dati_filtrati_1[dati_filtrati_1['nome_parametro'] == parametro]
        fig.add_trace(
            go.Scatter(
                x=dati_parametro['data_registrazione'],
                y=dati_parametro['valore'],
                mode='lines',
                name=parametro
            ),
            row=1, col=1, secondary_y=False
        )

    for parametro in parametri_secondo_selezionati:
        dati_parametro = dati_filtrati_2[dati_filtrati_2['nome_parametro'] == parametro]
        fig.add_trace(
            go.Scatter(
                x=dati_parametro['data_registrazione'],
                y=dati_parametro['valore'],
                mode='lines',
                name=parametro,
                customdata=original_values.get(parametro, dati_parametro['valore']),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Valore Normalizzato: %{y}<br>"
                    "Valore Originale: %{customdata}<br>"
                    "<extra></extra>"
                )
            ),
            row=1, col=1, secondary_y=True
        )

    fig.update_layout(
        title_text="Grafico Interattivo di Parametri Selezionati",
        xaxis_title='Data',
        yaxis_title='Valore',
        yaxis2_title='Valore Secondo Parametro',
        template='plotly_dark',
        showlegend=True
    )

    return fig

def aggiorna_grafico_on(parametri_selezionati, parametri_secondo_selezionati, normalizza, contents, filename):
    if contents is None or not parametri_selezionati:
        return {}

    dati = processa_csv(contents, filename)
    if dati is None:
        return {}

    dati['data_registrazione'] = pd.to_datetime(dati['data_registrazione'])
    original_values = {}

    # Verifica se, per ogni data, "PV38_StatoMacchina" ha valore 1
    dati_stato_macchina = dati[dati['nome_parametro'] == "PV38_StatoMacchina"]
    dati_filtrati_stato_macchina = dati_stato_macchina[dati_stato_macchina['valore'] == 1]

    # Prendi le date in cui "PV38_StatoMacchina" è 1
    date_valide = dati_filtrati_stato_macchina['data_registrazione'].unique()

    # Filtra i dati per le date valide
    dati_filtrati_1 = dati[(dati['nome_parametro'].isin(parametri_selezionati)) & (dati['data_registrazione'].isin(date_valide))]
    dati_filtrati_2 = dati[(dati['nome_parametro'].isin(parametri_secondo_selezionati)) & (dati['data_registrazione'].isin(date_valide))]

    if 'normalizza' in normalizza:
        for parametro in parametri_secondo_selezionati:
            original_values[parametro] = dati_filtrati_2[dati_filtrati_2['nome_parametro'] == parametro]['valore'].copy()
        dati_filtrati_2 = normalizza_dati(dati_filtrati_2, parametri_secondo_selezionati)

    fig = make_subplots(
        rows=1, cols=1, 
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("Grafico Parametri Selezionati"),
        specs=[[{"secondary_y": True}]]
    )

    for parametro in parametri_selezionati:
        dati_parametro = dati_filtrati_1[dati_filtrati_1['nome_parametro'] == parametro]
        fig.add_trace(
            go.Scatter(
                x=dati_parametro['data_registrazione'],
                y=dati_parametro['valore'],
                mode='markers',
                name=parametro
            ),
            row=1, col=1, secondary_y=False
        )

    for parametro in parametri_secondo_selezionati:
        dati_parametro = dati_filtrati_2[dati_filtrati_2['nome_parametro'] == parametro]
        fig.add_trace(
            go.Scatter(
                x=dati_parametro['data_registrazione'],
                y=dati_parametro['valore'],
                mode='markers',
                name=parametro,
                customdata=original_values.get(parametro, dati_parametro['valore']),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Valore Normalizzato: %{y}<br>"
                    "Valore Originale: %{customdata}<br>"
                    "<extra></extra>"
                )
            ),
            row=1, col=1, secondary_y=True
        )

    fig.update_layout(
        title_text="Grafico Interattivo di Parametri Selezionati",
        xaxis_title='Data',
        yaxis_title='Valore',
        yaxis2_title='Valore Secondo Parametro',
        template='plotly_dark',
        showlegend=True
    )

    return fig