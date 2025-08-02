import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import os

# Načtení dat
df = pd.read_excel('avg_wage_per_country.xlsx')

# Inicializace Dash aplikace
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # pro Render

# Rozvržení aplikace
app.layout = html.Div(
    children=[
        html.H2("Interaktivní dashboard srovnání mezd daných zemí v čase"),
        html.P("Dashboard umožňuje zobrazit průměrné mzdy pro N států, či zobrazit TOP 10 států s nejnižší prům. mzdou ve vybraném roce"),

        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H4("Průměrné mzdy vybraných států"),
                        html.Div(
                            children=[
                                html.P("Vyber státy: "),
                                dcc.Dropdown(
                                    id='dropdown-levy',
                                    options=[{"label": country, "value": country} for country in df["Country"].unique()],
                                    multi=True,
                                    style={"width": "75%"}
                                )
                            ],
                            style={"display": "flex", "flex-direction": "row", "gap": "20px", "justify-content": "center"}
                        ),
                        dcc.Loading(dcc.Graph(id='graf-levy'))
                    ],
                    style={"width": "50%"}
                ),
                html.Div(
                    children=[
                        html.H4("TOP 10 států s nejnižší průměrnou mzdou v daném roce"),
                        dcc.Slider(
                            min=df["Year"].min(),
                            max=df["Year"].max(),
                            step=1,
                            value=df["Year"].min(),
                            marks={str(year): str(year) for year in df['Year'].unique()],
                            id='slider-pravy'
                        ),
                        dcc.Loading(dcc.Graph(id='graf-pravy'))
                    ],
                    style={"width": "50%"}
                )
            ],
            style={"display": "flex", "flex-direction": "row", "justify-content": "center"}
        )
    ],
    style={"text-align": "center"}
)

# CALLBACKY
@callback(
    Output('graf-levy', 'figure'),
    Input('dropdown-levy', 'value')
)
def update_graph_levy(zvoleny_stat_input):
    df_grouped = df.groupby("Country")["Wage"].mean().reset_index(name="avg_wage")
    if zvoleny_stat_input:
        df_filtered = df_grouped[df_grouped['Country'].isin(zvoleny_stat_input)]
    else:
        return px.bar(title="Vyberte prosím alespoň jeden stát")
    return px.bar(df_filtered, x="Country", y="avg_wage", title="Průměrné mzdy v jednotlivých zemích")

@callback(
    Output('graf-pravy', 'figure'),
    Input('slider-pravy', 'value')
)
def update_graph_pravy(input_rok):
    df_filtered = df[df["Year"] == int(input_rok)].nsmallest(n=10, columns='Wage')
    return px.bar(df_filtered, x="Country", y="Wage", title=f"TOP 10 zemí s nejnižší mzdou v roce {input_rok}")

# Spuštění (pro Render)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=False, host="0.0.0.0", port=port)
