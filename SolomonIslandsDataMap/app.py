# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/app.ipynb.

# %% auto 0
__all__ = ['sol_geo', 'geo_df', 'app', 'server', 'mytitle', 'mygraph', 'aggs', 'dropdown', 'update_graph']

# %% ../nbs/app.ipynb 2
from nbdev.showdoc import *
# TODO work out how to get around below hack
try:
    from SolomonIslandsDataMap.load_data import *
except: 
    from load_data import *
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio # Unless this is used graphs will not be dynamic?
import json
import pandas as pd
import numpy as np
from fastcore.test import *
from dash import Dash, dcc, Output, Input  # pip install dash
import dash_bootstrap_components as dbc    # pip install dash-bootstrap-components
import random

# %% ../nbs/app.ipynb 4
sol_geo = SolomonGeo.read_test()
geo_df = sol_geo.geo_df

# %% ../nbs/app.ipynb 6
# Build your components
# FYI the best themes seem to be: [Darkly, Flatly, Minty, Slate]
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
server = app.server


mytitle = dcc.Markdown(children='')
mygraph = dcc.Graph(figure={})
aggs = geo_df.loc[:, 'agg'].unique()
dropdown = dcc.Dropdown(options=aggs,
                        value=aggs[0],  # initial value displayed when page first loads
                        clearable=False)

# %% ../nbs/app.ipynb 8
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([mytitle], width = 10)
    ], justify = 'center'),
    dbc.Row([
        dbc.Col([mygraph], width = 12)
    ]),
    dbc.Row([
        dbc.Col([dropdown], width = 6)
    ], justify = 'center'),
], fluid = True)

# %% ../nbs/app.ipynb 10
# Callback allows components to interact
@app.callback(
    Output(mygraph, 'figure'),
    Output(mytitle, 'children'),
    Input(dropdown, 'value')
)
def update_graph(user_input):  # function arguments come from the component property of the Input
    fig = go.Figure(go.Choroplethmapbox(
                            geojson=sol_geo.get_geojson(agg_filter = user_input),
                           locations=sol_geo.get_df(agg_filter = user_input).index,
                           z = sol_geo.get_df(agg_filter = user_input)['total_pop'],
                           colorscale="deep",
                            marker_line_width = 0,
                            zauto=True))

    fig.update_layout(mapbox_style = 'carto-positron',
                        mapbox_zoom = 5,
                        mapbox_center={"lat": -9.565766, "lon": 162.012453},
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    # returned objects are assigned to the component property of the Output
    return fig, '# Solomon Islanda Data map - ' + user_input


# %% ../nbs/app.ipynb 12
#server
# Run app
if __name__=='__main__':
    app.run_server(debug=True)
