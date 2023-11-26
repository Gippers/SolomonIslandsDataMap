# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/04_table_page.ipynb.

# %% auto 0
__all__ = ['mytitle', 'layout']

# %% ../../nbs/04_table_page.ipynb 2
# TODO minimise these imports a bit where possible
from nbdev.showdoc import *
# TODO work out how to get around below hack
try:
    from SolomonIslandsDataMap.dash_components import *
except: 
    from dash_components import *
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio # Unless this is used graphs will not be dynamic?
import numpy as np
from fastcore.test import *
from dash import Dash, dcc, Output, Input, State, html, Patch, ctx, register_page  # pip install dash
import dash_bootstrap_components as dbc    # pip install dash-bootstrap-components
from dash_bootstrap_templates import load_figure_template
import dash_mantine_components as dmc
import os

# %% ../../nbs/04_table_page.ipynb 3
register_page(__name__, 
                    path='/datatable',
                    title='Data Table',
                    name='Data Table')

# %% ../../nbs/04_table_page.ipynb 6
mytitle = dcc.Markdown(children="## This is a placeholder test!!") # TODO This needs a default title

# %% ../../nbs/04_table_page.ipynb 7
def layout():
    return dbc.Container([mytitle,
                        map_graph,
                        selectedBarGraph,
                        ])