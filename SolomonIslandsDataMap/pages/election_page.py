# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/05_election_page.ipynb.

# %% auto 0
__all__ = ['init_init', 'dict_sol', 'layout']

# %% ../../nbs/05_election_page.ipynb 2
# TODO minimise these imports a bit where possible
from nbdev.showdoc import *
# TODO work out how to get around below hack
try:
    from SolomonIslandsDataMap.dash_components import election_bar_plot, gen_dd
    from SolomonIslandsDataMap.app_data import mytitle, election_map, election_bar, stored_data, fake_slider
    from SolomonIslandsDataMap.load_data import SolomonGeo
except: 
    from dash_components import election_bar_plot, gen_dd
    from app_data import mytitle, election_map, election_bar, stored_data, fake_slider
    from load_data import SolomonGeo
from fastcore.test import *
from dash import Dash, dcc, callback, Output, Input, State, html, Patch, ctx, register_page, callback_context 
import dash_bootstrap_components as dbc    
import dash_ag_grid as dag

# %% ../../nbs/05_election_page.ipynb 3
try:
    register_page(__name__, 
                        path='/electionmap',
                        title='Election Map',
                        name='Election Map')
except:
    pass

# %% ../../nbs/05_election_page.ipynb 5
init_init = dcc.Store(id="initial-initial", data='table')
def layout():
    return dbc.Col(mytitle, width = 8),\
                dcc.Loading(
                    id="loading-election-map",
                    type="default",
                    children = election_map,
                ),\
                dcc.Loading(
                    id="loading-election-bar",
                    type="default",
                    children = election_bar,), init_init, fake_slider


# %% ../../nbs/05_election_page.ipynb 7
dict_sol = stored_data.data
