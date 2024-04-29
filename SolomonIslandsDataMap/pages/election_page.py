# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/05_election_page.ipynb.

# %% auto 0
__all__ = ['init_init', 'dict_sol', 'layout', 'update_election_bar']

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
import plotly.graph_objects as go

# %% ../../nbs/05_election_page.ipynb 3
try:
    register_page(__name__, 
                        path='/electionmap',
                        title='Election Map',
                        name='Election Map')
except:
    pass

# %% ../../nbs/05_election_page.ipynb 5
init_init = dcc.Store(id="initial-initial", data='election')
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

# %% ../../nbs/05_election_page.ipynb 9
# Callback allows components to interact
@callback(
    Output('election_bar', 'figure'),
    Input("segmented_type", 'value'),
    Input('electionDropdown', 'value'),
    Input('locDropdown', 'value'),
    Input('initial-initial', 'data'),
    Input('elecYearDropdown', 'value'),
    State("segmented_geo", 'value'),
    #State('geo_df', 'data'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def update_election_bar(data_type:str, # User input of type of data
                     election:str, # A string contiaining the election type
                     loc_selection:[str], # The selected locations, may be none
                     init_load:{}, # An empty dictionary always, triggers initial load
                     elecYear:str, # The year of the election
                     geo_input:str, # User input from the geography dropdown
                     #dict_sol:dict, # The dataset in dictionary form
              )->(type(go.Figure())): # Returns a graph object figure after being updated and the dynamic title
    '''
    Updates the focus census variable or geography dispalayed on the map
    '''
    sol_geo = SolomonGeo.gen_stored(dict_sol) # reload the data

    # Create newly selected barplot
    print("Func: update_election_bargraph")
    loc = 'Central Honiara'
    if len(loc_selection) > 0: 
        loc = loc_selection[-1]

    bg = election_bar_plot(sol_geo, geo_input, elecYear, election, loc, data_type)

    # returned objects are assigned to the component property of the Output
    # After updating fileter, we always reset map selection 

    return  bg
