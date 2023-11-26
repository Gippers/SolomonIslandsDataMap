# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/05_app.ipynb.

# %% auto 0
__all__ = ['repo', 'fp', 'app', 'server', 'navbar']

# %% ../nbs/05_app.ipynb 2
from nbdev.showdoc import *
try:
    from SolomonIslandsDataMap.app_data import sidebar
except: 
    from app_data import sidebar

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio # Unless this is used graphs will not be dynamic?
import numpy as np
from fastcore.test import *
from dash import page_container, Dash, dcc, Output, Input, State, html, Patch, ctx  # pip install dash
import dash_bootstrap_components as dbc    # pip install dash-bootstrap-components
from dash_bootstrap_templates import load_figure_template
from git import Repo

# %% ../nbs/05_app.ipynb 5
# Find the absoulte path to the pages folder
repo = Repo('.', search_parent_directories=True)
fp = str(repo.working_tree_dir) + "/SolomonIslandsDataMap/pages/"

app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY], use_pages=True, pages_folder = fp)
server = app.server
load_figure_template("minty")

# %% ../nbs/05_app.ipynb 8
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Census Data", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages coming soon", header=True),
                
                dbc.DropdownMenuItem("Population Projection", href="#"),
                # TODO populate this with the pages
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="Solomon Islands Data Map",
    brand_href="#",
    color="primary",
    #dark=True,
    class_name="navbar navbar-expand-lg bg-primary"
)


# %% ../nbs/05_app.ipynb 12
app.layout = dbc.Container([
                dbc.Row([
                    navbar
                ]),
                dbc.Row(
                    [dbc.Col(sidebar, width = 2),
                    dbc.Col(page_container, width = 10)
                     ], justify = 'center'),                    
                ], fluid = True)

# %% ../nbs/05_app.ipynb 14
# Run app
if __name__=='__main__':
    try:
        app.run_server(debug=True, port=9999) # Random int mitigates port collision
    except:
        print("Cannot run server here")
