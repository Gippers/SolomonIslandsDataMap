# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/03_map_page.ipynb.

# %% auto 0
__all__ = ['mytitle', 'map_graph', 'selectedBarGraph', 'map_click', 'map_selections', 'update_geography', 'update_measure',
           'update_map', 'update_bargraph', 'layout']

# %% ../../nbs/03_map_page.ipynb 2
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

# %% ../../nbs/03_map_page.ipynb 3
register_page(__name__, 
                    path='/',
                    title='Data Map',
                    name='Data Map')

# %% ../../nbs/03_map_page.ipynb 6
# TODO - not sure whether this should be imported from app_data or built here.
# if building it here causes it to reload each time, I should probably move it later
mytitle = dcc.Markdown(children="## " + list(cen_vars.keys())[0] + " by " + geos[0]) # TODO This needs a default title
map_graph = dcc.Graph(figure=define_map(sol_geo), selectedData=None,)

selectedBarGraph = dcc.Graph(figure = gen_bar_plot(sol_geo, sol_geo.geo_levels[0], 
                                               "Key Statistics", 'Total Households'),
                            id = 'bar_graph')


# %% ../../nbs/03_map_page.ipynb 11
@app.callback(
    Output('locDropdown', 'value'),
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
        return None
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
        


# %% ../../nbs/03_map_page.ipynb 13
@app.callback(
    Output(map_graph, "figure", allow_duplicate=True),
    # TODO - make this a Row object with children, then use function to recontruct
    # a group of them
    Input('locDropdown', 'value'),
    State(dropdown_geo, 'value'),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def map_selections(locations:[str], # The previously selected locations
                geo_input:str, # The currently selected geography
                )->[str]: # Returns the new value for the dropdown
    '''
    Update the selected data on the map for the selected locations
    Selections is an array of integers indicating the index of the selected points
    '''
    patched_figure = Patch()
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
        


# %% ../../nbs/03_map_page.ipynb 17
@app.callback(
    Output(dropdown_location, 'children'),
    Input(dropdown_geo, 'value'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def update_geography(geo_input:str, # User input from the geography dropdown
              )->[str]: # Returns a new list of locations to display
    '''
    Updates the dropdown_location dropdown based on the currently selected data aggregation.
    '''
    return gen_dd(sol_geo.locations[geo_input], 'locDropdown', "Select a location", clear = True, multi = True)

# %% ../../nbs/03_map_page.ipynb 20
@app.callback(
    Output(dd_measure, 'children'),
    Input('varDropdown', 'value'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def update_measure(new_var:str, # Selected variable
              )->dcc.Dropdown: # Returns a dropdown of measures for selected variable
    '''
    Updates the dropdown_location dropdown based on the currently selected data aggregation.
    '''
    # When a variable is selected, the measure will be set as the first one
    return gen_dd(sol_geo.census_vars[new_var], 'measureDropdown', 
                  val = sol_geo.census_vars[new_var][0])

# %% ../../nbs/03_map_page.ipynb 22
@app.callback(
    Output('measureDropdown', 'value'),
    Output(selectedBarGraph, "clickData"),
    Input(selectedBarGraph, 'clickData'),
    State('varDropdown', 'value'),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def map_click(clickData:dict, # The currently clicked location on bar graph
                variable:str, # The currently selected variable
                )->[str]: # Returns the new value for the dropdown
    """This function updates the dropdown menu based on the bar graph click data"""

    if clickData is None:
        print("Click data was none")
        return None
    else:
        # The measure are list of dictionaries
        selection = list(map(lambda x: x['x'], clickData['points']))[0]
    
        # returned objects are assigned to the component property of the Output
        # After updating fileter, we always reset map selection 
        return selection, None
        


# %% ../../nbs/03_map_page.ipynb 24
@app.callback(
    Output(map_graph, 'figure', allow_duplicate=True),
    Output(mytitle, 'children'),
    Input(dropdown_geo, 'value'),
    Input(control_type, 'value'),
    Input('measureDropdown', 'value'),
    Input('varDropdown', 'value'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def update_map(geo_input:str, # User input from the geography dropdown
                     data_type:str, # User input of type of data
                     measure:str, # A string contiaining the census variable and measure split by ':'
                     variable:str, # The state of the variable dropdown
              )->(type(go.Figure()), str): # Returns a graph object figure after being updated and the dynamic title
    '''
    Updates the focus census variable or geography dispalayed on the map
    '''
    # TODO can i roll the geo and measure into one trigger of the callback?
    patched_figure = Patch()
    button_clicked = ctx.triggered_id


    if button_clicked == dropdown_geo.id or button_clicked == dropdown_location.id:
        # Update disaplayed geography 
        for geo in sol_geo.geo_levels:
            tn = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
            patched_figure['data'][tn]['visible'] = geo_input == geo
        
    elif button_clicked == control_type.id:
        # Update the type of data displayed on map
        # TODO currently displayed data will need to be tracked. Can't be tracked in object, use hidden 
        # TODO will need to track this update also in var dropdown clicked
        # TODO this also needs to trigger cards
        for geo in sol_geo.geo_levels:
            tn = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
            ar = sol_geo.get_df(geo_filter = geo, type_filter=data_type, var = variable, measure = measure).values
            ar = ar.reshape((ar.shape[0],))
            patched_figure['data'][tn]['z'] = ar
        

    elif button_clicked == 'measureDropdown':
        # Update the z values in map to the data for the requested census variable
        for geo in sol_geo.geo_levels:
        # Ar updates the z value ie. data disaplyed each time
        # TODO this is fairly inefficient, as we are processing each time
        # Maybe faster framework like polars could help? or caching but would require a lot of caching
            tn = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
            ar = sol_geo.get_df(geo_filter = geo, type_filter=data_type, var = variable, measure=measure).values
            ar = ar.reshape((ar.shape[0],))
            patched_figure['data'][tn]['z'] = ar
        
    # returned objects are assigned to the component property of the Output
    # After updating fileter, we always reset map selection 

    return patched_figure, '## Solomon Islands Data map - ' + geo_input

# %% ../../nbs/03_map_page.ipynb 27
# Callback allows components to interact
@app.callback(
    Output(selectedBarGraph, 'figure'),
    Input(dropdown_geo, 'value'),
    Input(control_type, 'value'),
    Input('measureDropdown', 'value'),
    Input('locDropdown', 'value'),
    State('varDropdown', 'value'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def update_bargraph(geo_input:str, # User input from the geography dropdown
                     data_type:str, # User input of type of data
                     measure:str, # A string contiaining the census variable and measure split by ':'
                     loc_selection:[str], # The selected locations, may be none
                     variable:str, # The state of the variable dropdown
              )->(type(go.Figure())): # Returns a graph object figure after being updated and the dynamic title
    '''
    Updates the focus census variable or geography dispalayed on the map
    '''
        
    # Create newly selected barplot
    print("input")
    print(loc_selection)
    locs = None
    # Multi dropdown can return None or a list of None.
    if loc_selection: 
        locs = loc_selection
    print("Going in to function")
    print(locs)
    bg = gen_bar_plot(sol_geo, geo_input, variable, measure, locs, data_type)

    # returned objects are assigned to the component property of the Output
    # After updating fileter, we always reset map selection 

    return  bg

# %% ../../nbs/03_map_page.ipynb 37
def layout():
    return dbc.Container([mytitle,
                        map_graph,
                        selectedBarGraph,
                        ])
