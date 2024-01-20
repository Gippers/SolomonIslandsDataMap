# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/04_map_population.ipynb.

# %% auto 0
__all__ = ['init_init', 'layout', 'update_measure_pop', 'update_map_pop', 'update_pyramid']

# %% ../../nbs/04_map_population.ipynb 2
# TODO minimise these imports a bit where possible
from nbdev.showdoc import *
# TODO work out how to get around below hack
try:
    from SolomonIslandsDataMap.dash_components import gen_pyramid, gen_dd
    from SolomonIslandsDataMap.app_data import mytitle, map_graph, selectedBarGraph, stored_data, dropdown_location  \
        , control_type, dd_var_pop, dd_measure_pop, dropdown_geo, dd_var_pop, dd_measure_pop, year_slider\
        , popPyramid, pyramidTitle, popKpi
    from SolomonIslandsDataMap.load_data import SolomonGeo
except: 
    from dash_components import gen_pyramid, gen_dd
    from app_data import mytitle, map_graph, selectedBarGraph, stored_data, dropdown_location \
        , control_type, dd_var, dd_measure, dropdown_geo, dd_var_pop, dd_measure_pop, year_slider\
        , popPyramid, pyramidTitle, popKpi
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
    return pyramidTitle, map_graph, year_slider,\
        dbc.Row([
                popKpi,
                dbc.Col([popPyramid], width = 8, align = 'center')
            ], justify = 'around'), stored_data, init_init

# %% ../../nbs/04_map_population.ipynb 12
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

# %% ../../nbs/04_map_population.ipynb 15
# TODO add the population pyramid clicks one here. Needs population pyramid, use below markdown for inspiration
        


# %% ../../nbs/04_map_population.ipynb 20
# TODO - this could quite liekly be in map_page calbback as well
# TODO - add age here
@callback(
    Output(map_graph, 'figure', allow_duplicate=True),
    Input("segmented_geo", 'value'),
    Input("segmented_type", 'value'),
    Input('measureDropdownPop', 'value'),
    Input('varDropdownPop', 'value'),
    Input('age_dropdown', 'value'),
    Input("year_slider", "value"),
    State('geo_df', 'data'),
    allow_duplicate=True,
    prevent_initial_call=True)
def update_map_pop(geog:str, # current geography
    data_type:str, # User input of type of data
                measure:str, # A string contiaining the census variable and measure split by ':'
                variable:str, # The state of the variable dropdown
                age:[str], # Age Brackets to display
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
    print(age)

    # A None value is passed when the page is first loaded, hence
    # the the values are reset.
    # Hardcoded to province as we only have forcasts by province
    if button_clicked in [dropdown_geo.id, dropdown_location.id]:
        # Update disaplayed geography 
        for geo in sol_geo.geo_levels:
            tn = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
            patched_figure['data'][tn]['visible'] = geog == geo
            print(geo)
        
    if button_clicked in [control_type.id]:
        # Update the type of data displayed on map and the hover template
        for geo in sol_geo.geo_levels:
            tn = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
            # All years allows us to set the min and max colour as the min and max across all years
            all_years = sol_geo.get_pop(years = sol_geo.pop_years, var = variable, measure = measure, #type_filter=data_type,
                                  agg = True, agg_location = True, ages = age)
            ar = all_years.loc[year].values[:, -1]
            all_years = all_years.values[:, -1]
            ar = ar.reshape((ar.shape[0],))
            if data_type == 'Total':
                ht = '%{customdata} <extra>%{z}</extra>'
            elif data_type == 'Proportion':
                ht = '%{customdata} <extra>%{z:.1%}</extra>'
            else:
                ValueError("Data type of map not recognised and note accounted for")
            patched_figure['data'][tn]['z'] = ar
            patched_figure['data'][tn]['zmin'] = np.min(all_years)
            patched_figure['data'][tn]['zmax'] = np.max(all_years)
            patched_figure['data'][tn]['hovertemplate'] = ht

            
        

    if button_clicked in ['measureDropdownPop', 'year_slider', 'age_dropdown']:
        # Update the z values in map to the data for the requested census variable
        for geo in sol_geo.geo_levels:
        # Ar updates the z value ie. data disaplyed each time
        # TODO this is fairly inefficient, as we are processing each time
        # Maybe faster framework like polars could help? or caching but would require a lot of caching
            tn = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
            
            # All years allows us to set the min and max colour as the min and max across all years
            all_years = sol_geo.get_pop(years = sol_geo.pop_years, var = variable, measure = measure, #type_filter=data_type,
                                  agg = True, agg_location = True, ages = age)
            ar = all_years.loc[year].values[:, -1]
            all_years = all_years.values[:, -1]
            ar = ar.reshape((ar.shape[0],))
            print(all_years)
            patched_figure['data'][tn]['z'] = ar
            patched_figure['data'][tn]['zmin'] = np.min(all_years)
            patched_figure['data'][tn]['zmax'] = np.max(all_years)
        
    # returned objects are assigned to the component property of the Output
    # After updating fileter, we always reset map selection 

    return patched_figure

# %% ../../nbs/04_map_population.ipynb 24
# Callback allows components to interact
@callback(
    Output('popPyramid', 'figure'),
    Output('pyramidTitle', 'children'),
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
              )->(type(go.Figure()), str): # Returns a graph object figure after being updated and the dynamic title
    '''
    Updates the focus census variable or geography dispalayed on the map
    '''
    sol_geo = SolomonGeo.gen_stored(dict_sol) # reload the data
    print("type: " + data_type)
    fig = gen_pyramid(sol_geo = sol_geo, geo_filter = geo_input, year = year, 
                      variable = variable, locations = loc_selection, type_filter = data_type, ages = ages)
    
    
    # Create a title for the pyramid
    if loc_selection == []:
        figtext = '## Projected Population Pyramid for Solomon Islands'
    else:
        figtext = '## Aggregated Projected Population Pyramid for ' + ', '.join(loc_selection)
    figtext += ' in ' + str(year)

    # returned objects are assigned to the component property of the Output
    # After updating fileter, we always reset map selection 
    

    return fig, figtext
