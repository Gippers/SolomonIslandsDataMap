# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/04_map_population.ipynb.

# %% auto 0
__all__ = ['init_init', 'layout', 'update_measure_pop', 'update_pyramid', 'update_kpi']

# %% ../../nbs/04_map_population.ipynb 2
# TODO minimise these imports a bit where possible
from nbdev.showdoc import *
# TODO work out how to get around below hack
try:
    from SolomonIslandsDataMap.dash_components import gen_pyramid, gen_dd, gen_kpi
    from SolomonIslandsDataMap.app_data import map_graph, year_slider\
        , popPyramid, popKpi, mytitle
    from SolomonIslandsDataMap.load_data import SolomonGeo
except: 
    from dash_components import gen_pyramid, gen_dd, gen_kpi
    from app_data import  map_graph, year_slider\
        , popPyramid,  popKpi, mytitle
    from load_data import SolomonGeo
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio # Unless this is used graphs will not be dynamic?
import numpy as np
from fastcore.test import *
from dash import Dash, callback, dcc, Output, Input, State, html, Patch, ctx, register_page  # pip install dash
import dash_bootstrap_components as dbc    # pip install dash-bootstrap-components
from dash_bootstrap_templates import load_figure_template
import dash_mantine_components as dmc
import os
import json

# %% ../../nbs/04_map_population.ipynb 3
# Try catch is added here so that the notebook can be tested without the app being run
try:
    register_page(__name__, 
                        path='/population_projections',
                        title='Population Projections',
                        name='Population Projections')
except:
    pass

# %% ../../nbs/04_map_population.ipynb 5
# this initial data store is used to trigger callbacks on page load and know
init_init = dcc.Store(id="initial-initial", data='pop')


# %% ../../nbs/04_map_population.ipynb 8
def layout():
    return  init_init, mytitle, \
            dcc.Loading(
                id="loading-map",
                type="default",
                children = map_graph,
            ),\
            year_slider,\
            dbc.Row([
                       html.Div([
                    dcc.Loading(
                        id="loading-kpi",
                        type="default",
                        children = popKpi,
                    ),]),
                    #dbc.Col([
                           html.Div([
                        dcc.Loading(
                                id="loading-pyramid",
                                type="default",
                                children = popPyramid,)])
                                #]
                            #,width = 8, align = 'center'),
                ], justify = 'around'), 

# %% ../../nbs/04_map_population.ipynb 12
@callback(
    Output('measurePopDiv', 'children', allow_duplicate=True),
    Input('varDropdownPop', 'value'),
    State('geo_df', 'data'),
    State('measureDropdownPop', 'value'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def update_measure_pop(new_var:str, # Selected variable
                   dict_sol:dict, # The dataset in dictionary form
                   measure:str, # Currently selected measure
              )->dcc.Dropdown: # Returns a dropdown of measures for selected variable
    '''
    Updates the dropdown_location dropdown based on the currently selected data aggregation.
    '''
    sol_geo = SolomonGeo.gen_stored(dict_sol) # reload the data

    # Sometimes this callback is triggered when the measure doesn't need to be reset.
    # Check whether measure is in variable, if not reset to 0
    if measure not in sol_geo.population_vars[new_var]:
        measure = sol_geo.population_vars[new_var][0]

    # When a variable is selected, the measure will be set as the first one
    return gen_dd(sol_geo.population_vars[new_var], 'measureDropdownPop', 
                  val = measure)

# %% ../../nbs/04_map_population.ipynb 15
# TODO add the population pyramid clicks one here. Needs population pyramid, use below markdown for inspiration
        


# %% ../../nbs/04_map_population.ipynb 20
# Callback allows components to interact
@callback(
    Output('popPyramid', 'figure'),
    Input("segmented_type", 'value'),
    Input('measureDropdownPop', 'value'),
    Input('locDropdown', 'value'),
    Input('age_dropdown', 'value'),
    Input("year_slider", "value"),
    State("segmented_geo", 'value'),
    State('varDropdownPop', 'value'),
    State('geo_df', 'data'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def update_pyramid(data_type:str, # User input of type of data
                     measure:str, # A string contiaining the census variable and measure split by ':'
                     loc_selection:[str], # The selected locations, may be none
                     ages:[str], # Currently selected locations for highlighting
                     year:str, # Year of projection data
                     geo_input:str, # User input from the geography dropdown
                     variable:str, # The state of the variable dropdown
                     dict_sol:dict, # The dataset in dictionary form
                     #init_trigger:str, # uncessary variable inside the callback
              )->(type(go.Figure()), str): # Returns a graph object figure after being updated and the dynamic title
    '''
    Updates the focus census variable or geography dispalayed on the map
    '''
    sol_geo = SolomonGeo.gen_stored(dict_sol) # reload the data
    fig = gen_pyramid(sol_geo = sol_geo, geo_filter = geo_input, year = year, 
                      variable = variable, locations = loc_selection, type_filter = data_type, ages = ages)
    
    return fig

# %% ../../nbs/04_map_population.ipynb 24
# Callback allows components to interact
@callback(
    Output('popKpi', 'children'),
    Input("segmented_type", 'value'),
    Input('measureDropdownPop', 'value'),
    Input('locDropdown', 'value'),
    Input('age_dropdown', 'value'),
    Input("year_slider", "value"),
    State('varDropdownPop', 'value'),
    State('geo_df', 'data'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def update_kpi(data_type:str, # User input of type of data
                     measure:str, # A string contiaining the census variable and measure split by ':'
                     loc_selection:[str], # The selected locations, may be none
                     ages:[str], # Currently selected locations for highlighting
                     year:str, # Year of projection data
                     variable:str, # The state of the variable dropdown
                     dict_sol:dict, # The dataset in dictionary form
              )->(dcc.Markdown, dcc.Markdown): # Returns a graph object figure after being updated and the dynamic title
    '''
    Updates the focus census variable or geography dispalayed on the map
    '''
    sol_geo = SolomonGeo.gen_stored(dict_sol) # reload the data    

    return gen_kpi(sol_geo, year, variable, measure, ages, loc = loc_selection, type_filter = data_type)
