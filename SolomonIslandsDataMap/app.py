# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/06_app.ipynb.

# %% auto 0
__all__ = ['repo', 'fp', 'server', 'pages', 'navbar']

# %% ../nbs/06_app.ipynb 2
from nbdev.showdoc import *
try:
    from SolomonIslandsDataMap.app_data import stored_data
except: 
    from app_data import stored_data

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio # Unless this is used graphs will not be dynamic?
import numpy as np
from fastcore.test import *
from dash import page_container, Dash, dcc, Output, Input, State, html, Patch, page_registry, ctx  # pip install dash
import dash_bootstrap_components as dbc    # pip install dash-bootstrap-components
from dash_bootstrap_templates import load_figure_template
from git import Repo
import json


# %% ../nbs/06_app.ipynb 5
# Find the absoulte path to the pages folder
repo = Repo('.', search_parent_directories=True)
fp = str(repo.working_tree_dir) + "/SolomonIslandsDataMap/pages/"

try:
    app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY], use_pages=True, pages_folder = fp)
except:
    # When running in a notebook, the below trick should get the notebook to still execute
    import __main__ as main
    main.__file__ = "main_file"
    app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY], use_pages=True, pages_folder = fp)
server = app.server
load_figure_template("minty")

# %% ../nbs/06_app.ipynb 8
pages = {}
for page in page_registry.values():
    pages[page["title"]] = page["relative_path"]
    
navbar = dbc.NavbarSimple(
    children=[
        # TODO make this a dbc tab with calbback to make it active
        dbc.NavItem(dbc.NavLink('Census Map', href=pages['Census Map'], active=True)),
        dbc.NavItem(dbc.NavLink('Population Projections', href=pages['Population Projections'])),
        dbc.NavItem(dbc.NavLink('Data Table', href=pages['Data Table'])),
        dbc.DropdownMenu(
            children=[
                #dbc.DropdownMenuItem("More pages coming soon", header=True),
                
                dbc.DropdownMenuItem('Census Map', href=pages['Census Map']),
                dbc.DropdownMenuItem('Population Projections', href=pages['Population Projections']),
                dbc.DropdownMenuItem('Data Table', href=pages['Data Table']),
            ],
            nav=True,
            in_navbar=True,
            label="Select Page",
        ),
    ],
    brand="Solomon Islands Data Explorer",
    brand_href="#",
    color="primary",
    #dark=True,
    class_name="navbar navbar-expand-lg bg-primary"
)


# %% ../nbs/06_app.ipynb 11
app.layout = dbc.Container([
                dbc.Row([
                    navbar
                ]),
                page_container, 
                stored_data, 
                dcc.Store('stored_values', storage_type="session", 
                          data = json.dumps({'type': 'Total',
                                    'geo': 'Province',
                                    'location': [],
                                    'variable': 'Key Statistics',
                                    'measure': 'Total Households',
                                    'var-pop': 'Population',
                                    'measure-pop': 'Total',
                                    'age': '0-4',
                                    'pop_year': [2024],
                                    }))                 
                ], fluid = True)

# %% ../nbs/06_app.ipynb 13
# Run app
if __name__=='__main__':
    try:
        app.run_server(debug=True, port=9999) # Random int mitigates port collision
    except:
        print("Cannot run server here")
