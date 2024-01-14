# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/04_map_population.ipynb.

# %% auto 0
__all__ = ['init_load', 'init_init', 'layout', 'initial_load_pop', 'persist_dd_values_pop', 'update_measure_pop',
           'update_map_pop']

# %% ../../nbs/04_map_population.ipynb 2
# TODO minimise these imports a bit where possible
from nbdev.showdoc import *
# TODO work out how to get around below hack
try:
    from SolomonIslandsDataMap.dash_components import gen_bar_plot, gen_dd
    from SolomonIslandsDataMap.app_data import mytitle, map_graph, selectedBarGraph, stored_data, dropdown_location  \
        , control_type, dd_var_pop, dd_measure_pop, dropdown_geo, sidebar_population, dd_var_pop, dd_measure_pop, year_slider
    from SolomonIslandsDataMap.load_data import SolomonGeo
except: 
    from dash_components import gen_bar_plot, gen_dd
    from app_data import mytitle, map_graph, selectedBarGraph, stored_data, dropdown_location \
        , control_type, dd_var, dd_measure, dropdown_geo, sidebar_population, dd_var_pop, dd_measure_pop, year_slider
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

# %% ../../nbs/04_map_population.ipynb 4
# Creat some hacked init things
# TODO again as below, must be a better way
init_load = dcc.Store(id="initial-load-pop", data='')
init_init = dcc.Store(id="initial-initial", data='pop')

# %% ../../nbs/04_map_population.ipynb 7
def layout():
    return  dbc.Row(
        [dbc.Col(sidebar_population, width = 2),
        dbc.Col([
            mytitle,
            map_graph,
            year_slider,
            #selectedBarGraph,
            stored_data, 
            init_load, 
            init_init,], width = 10),
            # fires 1ms after page load
            dcc.Interval(id="interval-timer", interval=1, max_intervals=1),
        ], justify = 'center')

# %% ../../nbs/04_map_population.ipynb 11
# TODO this defintiely seems hacky, must be a better way

@callback(
    Output("varDropdownPop", "value"),
    Output("measureDropdownPop", "value"),
    Output("age_dropdown", "value"),
    Output("year_slider", "value"),
    Output('initial-load-pop', 'data'),
    Input("initial-initial", 'data'),
    State("stored_values", "data"),
    State('geo_df', 'data'),
)
def initial_load_pop(page_trigger:str, # Page that triggered initial load
                   js:str, # the current selection for the data
                   dict_sol:dict, # Dictionary of the solomon geo data
                         ) -> dict:
    """Load persistent starting values for all of the dropdowns"""
    print("****triggered load: ")
    print(js)
    val_state = json.loads(js)
    sol_geo = SolomonGeo.gen_stored(dict_sol)

    # In some circumstances, variable will not match measure. In which case reset measure
    if val_state['measure-pop'] not in sol_geo.population_vars[val_state['var-pop']]:
        val_state['measure-pop'] = sol_geo.population_vars[val_state['var-pop']][0]
        print("reset measure")

    # In some cirucumstances, None or Null values have crept into the save state. When this happens,
    # we should catch this and revert to a defualt state
    for key, value in val_state.items():
        if value is None:
            # If a value is None, do a hard reset and trigger a save
            val_state = {'type': 'Total',
                            'geo': 'Province',
                            'location': [],
                            'variable': 'Key Statistics',
                            'measure': 'Total Households',
                            'var-pop': 'Population',
                            'measure-pop': 'Total',
                            'age': '0-4',
                            'pop_year': 2024,
                            }
            persist_dd_values_pop(val_state['var-pop'], val_state['measure-pop'], val_state['age'], val_state['pop_year'], 
                                  js)

    return  val_state['var-pop'], val_state['measure-pop'], val_state['age'], val_state['pop_year'],  None

# %% ../../nbs/04_map_population.ipynb 14
@callback(
    Output("stored_values", "data", allow_duplicate=True),
    Input("varDropdownPop", "value"),
    Input("measureDropdownPop", "value"),
    Input("age_dropdown", "value"),
    Input("year_slider", "value"),
    State("stored_values", "data"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def persist_dd_values_pop(popVariable:str,
                      popMeasure:str, 
                      age:str,
                      years:int,
                      json_store:dict,
                    ) -> str:
    """Update the data type to persistent on load"""
    store = json.loads(json_store)
    store['var-pop'] = popVariable
    store['measure-pop'] = popMeasure
    store['age'] = age
    store['pop_year'] = years

    print("****triggered save: ")
    print(store)
    return json.dumps(store)

# %% ../../nbs/04_map_population.ipynb 17
@callback(
    Output(dd_measure_pop, 'children', allow_duplicate=True),
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
    print("func um")
    sol_geo = SolomonGeo.gen_stored(dict_sol) # reload the data

    # Sometimes this callback is triggered when the measure doesn't need to be reset.
    # Check whether measure is in variable, if not reset to 0
    if measure not in sol_geo.population_vars[new_var]:
        measure = sol_geo.population_vars[new_var][0]

    # When a variable is selected, the measure will be set as the first one
    return gen_dd(sol_geo.population_vars[new_var], 'measureDropdownPop', 
                  val = measure)

# %% ../../nbs/04_map_population.ipynb 20
# TODO add the population pyramid clicks one here. Needs population pyramid, use below markdown for inspiration
        


# %% ../../nbs/04_map_population.ipynb 25
# TODO - this could quite liekly be in map_page calbback as well
# TODO - add age here
@callback(
    Output(map_graph, 'figure', allow_duplicate=True),
    Output(mytitle, 'children', allow_duplicate=True),
    Input("segmented_geo", 'value'),
    Input("segmented_type", 'value'),
    Input('measureDropdownPop', 'value'),
    Input('varDropdownPop', 'value'),
    Input('initial-load-pop', 'data'),
    Input('age_dropdown', 'value'),
    Input("year_slider", "value"),
    State('geo_df', 'data'),
    allow_duplicate=True,
    prevent_initial_call=True)
def update_map_pop(geog:str, # current geography
    data_type:str, # User input of type of data
                measure:str, # A string contiaining the census variable and measure split by ':'
                variable:str, # The state of the variable dropdown
                init_load:{}, # An empty dictionary always
                age:str, # Age Bracket to display
                year:int, # The selected projection year
                dict_sol:dict, # The dataset in dictionary form
              )->(type(go.Figure()), str): # Returns a graph object figure after being updated and the dynamic title
    '''
    Updates the focus census variable or geography dispalayed on the map
    '''
    # TODO the None workaround might be taxing on the load times, is there a better way
    # or maybe I can check it it needs updating?
    patched_figure = Patch()
    button_clicked = ctx.triggered_id

    sol_geo = SolomonGeo.gen_stored(dict_sol) # reload the data
    print("first run, updating map")
    print(button_clicked)

    print(data_type)
    print(measure)

    # A None value is passed when the page is first loaded, hence
    # the the values are reset.
    # Hardcoded to province as we only have forcasts by province
    if button_clicked in [dropdown_geo.id, dropdown_location.id, 'initial-load-pop']:
        # Update disaplayed geography 
        for geo in sol_geo.geo_levels:
            tn = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
            patched_figure['data'][tn]['visible'] = geog == geo
            print(geo)
        
    if button_clicked in [control_type.id, 'initial-load-pop']:
        # Update the type of data displayed on map and the hover template
        for geo in sol_geo.geo_levels:
            tn = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
            ar = sol_geo.get_pop(years = [year], var = variable, measure = measure, #type_filter=data_type,
                                 ages = [age]).values[:, -1]
            ar = ar.reshape((ar.shape[0],))
            if data_type == 'Total':
                ht = '%{customdata} <extra>%{z}</extra>'
            elif data_type == 'Proportion':
                ht = '%{customdata} <extra>%{z:.1%}</extra>'
            else:
                ValueError("Data type of map not recognised and note accounted for")
            patched_figure['data'][tn]['z'] = ar
            patched_figure['data'][tn]['zmin'] = np.min(ar)
            patched_figure['data'][tn]['zmax'] = np.max(ar)
            patched_figure['data'][tn]['hovertemplate'] = ht

            
        

    if button_clicked in ['measureDropdownPop', 'initial-load-pop', 'year_slider', 'age_dropdown']:
        # Update the z values in map to the data for the requested census variable
        for geo in sol_geo.geo_levels:
        # Ar updates the z value ie. data disaplyed each time
        # TODO this is fairly inefficient, as we are processing each time
        # Maybe faster framework like polars could help? or caching but would require a lot of caching
            tn = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
            ar = sol_geo.get_pop(years = [year], var = variable, measure = measure, # type_filter=data_type,
                                 ages = [age]).values[:, -1]
            ar = ar.reshape((ar.shape[0],))
            patched_figure['data'][tn]['z'] = ar
            patched_figure['data'][tn]['zmin'] = np.min(ar)
            patched_figure['data'][tn]['zmax'] = np.max(ar)
        
    # returned objects are assigned to the component property of the Output
    # After updating fileter, we always reset map selection 

    return patched_figure, '## Solomon Islands Population Projections - ' + 'Province'
