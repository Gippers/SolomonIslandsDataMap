# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/03_map_page.ipynb.

# %% auto 0
__all__ = ['init_load', 'init_init', 'layout', 'initial_load', 'persist_dd_values', 'map_click', 'map_selections',
           'update_geography', 'update_measure', 'bar_click', 'update_map', 'update_bargraph']

# %% ../../nbs/03_map_page.ipynb 2
# TODO minimise these imports a bit where possible
from nbdev.showdoc import *
# TODO work out how to get around below hack
try:
    from SolomonIslandsDataMap.dash_components import gen_bar_plot, gen_dd
    from SolomonIslandsDataMap.app_data import mytitle, map_graph, selectedBarGraph, stored_data, dropdown_location \
        , control_type, dd_var, dd_measure, dropdown_geo, sidebar_census
    from SolomonIslandsDataMap.load_data import SolomonGeo
except: 
    from dash_components import gen_bar_plot, gen_dd
    from app_data import mytitle, map_graph, selectedBarGraph, stored_data, dropdown_location \
        , control_type, dd_var, dd_measure, dropdown_geo, sidebar_census
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

# %% ../../nbs/03_map_page.ipynb 3
# Try catch is added here so that the notebook can be tested without the app being run
try:
    register_page(__name__, 
                        path='/',
                        title='Census Map',
                        name='Census Map')
except:
    pass

# %% ../../nbs/03_map_page.ipynb 4
# Creat some hacked init things
# TODO again as below, must be a better way
init_load = dcc.Store(id="initial-load", data={})
init_init = dcc.Store(id="initial-initial", data='census')

# %% ../../nbs/03_map_page.ipynb 7
def layout():
    return  dbc.Row(
        [dbc.Col(sidebar_census, width = 2),
        dbc.Col([
            mytitle,
            map_graph,
            selectedBarGraph,
            stored_data, 
            init_load, 
            init_init,], width = 10),
            # fires 1ms after page load
            dcc.Interval(id="interval-timer", interval=1, max_intervals=1),
        ], justify = 'center')

# %% ../../nbs/03_map_page.ipynb 10
# TODO this defintiely seems hacky, must be a better way

@callback(
    Output("segmented_geo", "value"),
    Output("locDropdown", "value"),
    Output("varDropdown", "value"),
    Output("measureDropdown", "value"),
    Output("segmented_type", "value"),
    Output('initial-load', 'data'),
    Output('segmented_geo', 'disabled'), # On page load, allow for changing geography
    Input("initial-initial", 'data'),
    State("stored_values", "data"),
    State('geo_df', 'data'),
)
def initial_load(page_trigger:str, # Page that triggered initial load
                   js:str, # the current selection for the data
                   dict_sol:dict, # Dictionary of the solomon geo data
                         ) -> dict:
    """Load persistent starting values for all of the dropdowns"""
    print("****triggered load: ")
    print(js)
    val_state = json.loads(js)
    sol_geo = SolomonGeo.gen_stored(dict_sol)

    # Depending on the page loaded, geogrpahy will or will not be disabled
    geo_disable = False

    print("page")
    print(page_trigger)
    if page_trigger == 'pop':
        geo_disable = True

    # When the initial load id triggered by navigation to population page, 
    # if the geo isn't province we reset to this
    if page_trigger == 'pop' and val_state['geo'] != 'Province':
        val_state['geo'] = 'Province'
        val_state['location'] = []
        # TODO test that this works with multi tab

    # In some circumstances location will not match geo, in which case reset locations
    if val_state['location'] != [] and not (set(val_state['location']) <= set(sol_geo.locations[val_state['geo']])):
        val_state['location'] = []
        print("Had to reset location")

    # In some circumstances, variable will not match measure. In which case reset measure
    if val_state['measure'] not in sol_geo.census_vars[val_state['variable']]:
        val_state['measure'] = sol_geo.census_vars[val_state['variable']][0]
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
            persist_dd_values(val_state['geo'], val_state['location'], val_state['variable'], val_state['measure'], val_state['type'],
                              js)

    return val_state['geo'], val_state['location'], val_state['variable'], val_state['measure'], \
            val_state['type'], None, geo_disable


# %% ../../nbs/03_map_page.ipynb 13
@callback(
    Output("stored_values", "data"),
    Input("segmented_geo", "value"),
    Input("locDropdown", "value"),
    Input("measureDropdown", "value"),
    Input("segmented_type", "value"),
    Input("varDropdown", "value"),
    State("stored_values", "data"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def persist_dd_values(geo:str,
                        location:[str],
                        measure:str,
                        type:str, # Data type to save
                        variable:str, 
                        json_store:dict,
                    ) -> str:
        """Update the data type to persistent on load"""
        store = json.loads(json_store)
        
        store['type'] = type
        store['geo'] = geo
        store['location'] = location
        store['variable'] = variable
        store['measure'] = measure
                
        print("****triggered save: ")
        print(store)
        return json.dumps(store)

# %% ../../nbs/03_map_page.ipynb 16
@callback(
    Output('locDropdown', 'value', allow_duplicate=True),
    Output(map_graph, "clickData"),
    Output(map_graph, "selectedData"),
    Input(map_graph, 'clickData'),
    Input(map_graph, 'selectedData'),
    State('locDropdown', 'value'),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def map_click(clickData:dict, # The currently clicked location on the map
              selectedData:dict, # The currently selected locations on the map
                prev_locs:[str], # The previously selected locations
                )->[str]: # Returns the new value for the dropdown
    """This function updates the dropdown menu based on the map click data"""

    print("map clicked updating to:")
    if clickData is None and selectedData is None:
        # TODO when none, maybe in future return current saved state, for now doing total
        # TODO add a heading and maybe put in an acordian
        print("Click data was none")
        return prev_locs, None, None
    else:
        # The locations are list of dictionaries
        if selectedData is not None:
            print(selectedData)
            selections = list(map(lambda x: x['location'], selectedData['points']))
            print(selections)

        elif clickData is not None:
            selections = list(map(lambda x: x['location'], clickData['points']))
            print(selections)
        locations = []
        if prev_locs: locations = prev_locs
        print(locations)
        # Check whether the new location is already in the prev locations
        for selection in selections:
            if selection in locations: locations.remove(selection)
            else: locations.append(selection)
        print("Returning Location " + ', '.join(locations) )
    
        # returned objects are assigned to the component property of the Output
        # After updating fileter, we always reset map selection 
        return locations, None, None
        


# %% ../../nbs/03_map_page.ipynb 20
@callback(
    Output(map_graph, "figure", allow_duplicate=True),
    # TODO - make this a Row object with children, then use function to recontruct
    # a group of them
    Input('locDropdown', 'value'),
    State("stored_values", "data"),
    State('geo_df', 'data'),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def map_selections(locations:[str], # The previously selected locations
                json_store:json, # The currently selected data values
                dict_sol:dict, # The dataset in dictionary form
                )->[str]: # Returns the new value for the dropdown
    '''
    Update the selected data on the map for the selected locations
    Selections is an array of integers indicating the index of the selected points
    '''
    # Using geo from stored values
    store = json.loads(json_store)
    geo_input = store['geo']
    print("Changing map selections")
    sol_geo = SolomonGeo.gen_stored(dict_sol)
    print(geo_input)
    patched_figure = Patch()
    print(sol_geo.geo_levels == geo_input)
    ct = np.where(sol_geo.geo_levels == geo_input)[0][0] # Tracks the trace number
    pot_locs = map_graph.figure['data'][ct]['locations']
    print(locations)
    if locations: 
        selections = np.nonzero(np.in1d(pot_locs, locations))[0]
    else: 
        selections = None 

    print(selections)
    patched_figure['data'][ct]['selectedpoints'] = selections
    
    # returned objects are assigned to the component property of the Output
    # After updating fileter, we always reset map selection 
    return patched_figure
        


# %% ../../nbs/03_map_page.ipynb 23
@callback(
    Output(dropdown_location, 'children'),
    Input(dropdown_geo, 'value'),
    State('geo_df', 'data'),
    State('locDropdown', 'value'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def update_geography(geo_input:str, # User input from the geography dropdown
                    dict_sol:dict, # The dataset in dictionary form
                    locations:[str], # Currently selected locations
              )->[str]: # Returns a new list of locations to display
    '''
    Updates the dropdown_location dropdown based on the currently selected data aggregation.
    Check to see if current locations are in geography, if they are not then reset them.
    '''
    sol_geo = SolomonGeo.gen_stored(dict_sol) # reload the data
    
    # If all selected locations are in new geo, then keep old locations
    print("Does this bit fail")
    new_locations = []
    if locations != [] and set(locations) <= set(sol_geo.locations[geo_input]):
        new_locations = locations
        print("reset locations - mismatched")

    print('catch this here')

    return gen_dd(sol_geo.locations[geo_input], 'locDropdown', "Select a location", clear = True, multi = True, 
                  val = new_locations)

# %% ../../nbs/03_map_page.ipynb 26
@callback(
    Output(dd_measure, 'children', allow_duplicate=True),
    Input('varDropdown', 'value'),
    State('geo_df', 'data'),
    State('measureDropdown', 'value'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def update_measure(new_var:str, # Selected variable
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
    if measure not in sol_geo.census_vars[new_var]:
        measure = sol_geo.census_vars[new_var][0]

    # When a variable is selected, the measure will be set as the first one
    return gen_dd(sol_geo.census_vars[new_var], 'measureDropdown', 
                  val = measure)

# %% ../../nbs/03_map_page.ipynb 29
@callback(
    Output('measureDropdown', 'value', allow_duplicate=True),
    Output(selectedBarGraph, "clickData"),
    Input(selectedBarGraph, 'clickData'),
    State('varDropdown', 'value'),
    State('geo_df', 'data'),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def bar_click(clickData:dict, # The currently clicked location on bar graph
                variable:str, # The currently selected variable
                dict_sol:dict, # The dataset in dictionary form
                )->[str]: # Returns the new value for the dropdown
    """This function updates the dropdown menu based on the bar graph click data"""
    print("func bc")
    sol_geo = SolomonGeo.gen_stored(dict_sol) # reload the data
    if clickData is None:
        print("Click data was none")
        return sol_geo.census_vars[variable][0], None
    else:
        # The measure are list of dictionaries
        selection = list(map(lambda x: x['x'], clickData['points']))[0]
    
        # returned objects are assigned to the component property of the Output
        # After updating fileter, we always reset map selection 
        return selection, None
        


# %% ../../nbs/03_map_page.ipynb 32
@callback(
    Output(map_graph, 'figure', allow_duplicate=True),
    Output(mytitle, 'children'),
    Input(dropdown_geo, 'value'),
    Input("segmented_type", 'value'),
    Input('measureDropdown', 'value'),
    Input('varDropdown', 'value'),
    Input('initial-load', 'data'),
    State('geo_df', 'data'),
    allow_duplicate=True,
    prevent_initial_call=True)
def update_map(geo_input:str, # User input from the geography dropdown
                data_type:str, # User input of type of data
                measure:str, # A string contiaining the census variable and measure split by ':'
                variable:str, # The state of the variable dropdown
                init_load:{}, # An empty dictionary always
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
    print(geo_input)
    print(data_type)
    print(measure)

    # A None value is passed when the page is first loaded, hence
    # the the values are reset.
    if button_clicked in [dropdown_geo.id, dropdown_location.id, 'initial-load']:
        # Update disaplayed geography 
        for geo in sol_geo.geo_levels:
            tn = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
            patched_figure['data'][tn]['visible'] = geo_input == geo
            print(geo)
            print(geo_input == geo)
        
    if button_clicked in [control_type.id, 'initial-load']:
        # Update the type of data displayed on map and the hover template
        for geo in sol_geo.geo_levels:
            tn = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
            ar = sol_geo.get_census(geo_filter = geo, type_filter=data_type, var = variable, measure = measure).values
            ar = ar.reshape((ar.shape[0],))
            if data_type == 'Total':
                ht = '%{customdata} <extra>%{z}</extra>'
            elif data_type == 'Proportion':
                ht = '%{customdata} <extra>%{z:.1%}</extra>'
            else:
                ValueError("Data type of map not recognised and note accounted for")
            patched_figure['data'][tn]['z'] = ar
            patched_figure['data'][tn]['zmin'] = np.min(ar)
            patched_figure['data'][tn]['hovertemplate'] = ht

            
        

    if button_clicked in ['measureDropdown', 'initial-load']:
        # Update the z values in map to the data for the requested census variable
        for geo in sol_geo.geo_levels:
        # Ar updates the z value ie. data disaplyed each time
        # TODO this is fairly inefficient, as we are processing each time
        # Maybe faster framework like polars could help? or caching but would require a lot of caching
            tn = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
            ar = sol_geo.get_census(geo_filter = geo, type_filter=data_type, var = variable, measure=measure).values
            ar = ar.reshape((ar.shape[0],))
            patched_figure['data'][tn]['z'] = ar
        
    # returned objects are assigned to the component property of the Output
    # After updating fileter, we always reset map selection 

    return patched_figure, '## Solomon Islands Data map - ' + geo_input

# %% ../../nbs/03_map_page.ipynb 36
# Callback allows components to interact
@callback(
    Output(selectedBarGraph, 'figure'),
    Input("segmented_type", 'value'),
    Input('measureDropdown', 'value'),
    Input('locDropdown', 'value'),
    Input('initial-load', 'data'),
    State(dropdown_geo, 'value'),
    State('varDropdown', 'value'),
    State('geo_df', 'data'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def update_bargraph(data_type:str, # User input of type of data
                     measure:str, # A string contiaining the census variable and measure split by ':'
                     loc_selection:[str], # The selected locations, may be none
                     init_load:{}, # An empty dictionary always, triggers initial load
                     geo_input:str, # User input from the geography dropdown
                     variable:str, # The state of the variable dropdown
                     dict_sol:dict, # The dataset in dictionary form
              )->(type(go.Figure())): # Returns a graph object figure after being updated and the dynamic title
    '''
    Updates the focus census variable or geography dispalayed on the map
    '''
    sol_geo = SolomonGeo.gen_stored(dict_sol) # reload the data

    # Create newly selected barplot
    print("input")
    print(loc_selection)
    locs = []
    # Multi dropdown can return None or a list of None.
    if len(loc_selection) > 0: 
        locs = loc_selection
    print("Going in to function")
    print(locs)
    bg = gen_bar_plot(sol_geo, geo_input, variable, measure, locs, data_type)

    # returned objects are assigned to the component property of the Output
    # After updating fileter, we always reset map selection 

    return  bg
