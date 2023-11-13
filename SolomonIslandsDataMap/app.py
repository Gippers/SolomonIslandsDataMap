# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_app.ipynb.

# %% auto 0
__all__ = ['sol_geo', 'geo_df', 'fig', 'app', 'server', 'geos', 'cen_vars', 'NUM_GEOS', 'mytitle', 'map_graph', 'cards',
           'selectedBarGraph', 'selection', 'dropdown_location', 'dropdown_geo', 'control_type', 'dd_var', 'dd_measure',
           'navbar', 'SIDEBAR_STYLE', 'sidebar', 'map_click', 'map_selections', 'update_geography', 'update_measure',
           'update_map', 'update_bargraph']

# %% ../nbs/02_app.ipynb 2
from nbdev.showdoc import *
# TODO work out how to get around below hack
try:
    from SolomonIslandsDataMap.load_data import *
    from SolomonIslandsDataMap.dash_components import *
except: 
    from load_data import *
    from dash_components import *
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio # Unless this is used graphs will not be dynamic?
import json
from git import Repo
import pandas as pd
import numpy as np
from fastcore.test import *
from dash import Dash, dcc, Output, Input, State, html, Patch, ctx  # pip install dash
import dash_bootstrap_components as dbc    # pip install dash-bootstrap-components
from dash_bootstrap_templates import load_figure_template
import random
import dash_mantine_components as dmc

# %% ../nbs/02_app.ipynb 4
sol_geo = SolomonGeo.load_pickle("/testData/", github = True)
geo_df = sol_geo.geo_df
fig = define_map(sol_geo)

# %% ../nbs/02_app.ipynb 7
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY], use_pages=True)
server = app.server
load_figure_template("minty")

geos = sol_geo.geo_levels
cen_vars = sol_geo.census_vars
NUM_GEOS = len(geos)


# %% ../nbs/02_app.ipynb 9
mytitle = dcc.Markdown(children="## " + list(cen_vars.keys())[0] + " by " + geos[0]) # TODO This needs a default title
map_graph = dcc.Graph(figure=define_map(sol_geo), selectedData=None,)
# TODO entire accordian will need to be the child
cards = dbc.Accordion(children= 
        card_list(sol_geo, "Current Selection: Total"),
        always_open=True,
        class_name = "accordion-header",
    )
selectedBarGraph = dcc.Graph(figure = gen_bar_plot(sol_geo, sol_geo.geo_levels[0], 
                                               "Key Statistics", 'Total Households'),
                            id = 'bar_graph')
# Selections tracks the currently selected map locations
selection = dcc.Store(id = 'selection',data = {})

# %% ../nbs/02_app.ipynb 12
dropdown_location = html.Div(children = gen_dd(sol_geo.locations[sol_geo.geo_levels[0]], 
                                                'locDropdown', clear = True, place_holder='Select Dropdown Location',
                                                multi = True))

dropdown_geo = dmc.SegmentedControl(
                            id="segmented_geo",
                            value=geos[0],
                            data=geos,
                             orientation="vertical",
                            color = 'gray',
                            fullWidth = True,) # TODO consider redoing as theme is not consistent with this library
control_type = dmc.SegmentedControl(
                        id="segmented_type",
                        value=sol_geo.data_type[0],
                        data=sol_geo.data_type,
                        orientation="vertical",
                        color = 'gray',
                        fullWidth = True,)

dd_var = html.Div(children = gen_dd(list(sol_geo.census_vars.keys()), 'varDropdown', 
                                    val = 'Key Statistics', height = 75))
dd_measure = html.Div(children = gen_dd(sol_geo.census_vars['Key Statistics'], 'measureDropdown',
                                      val = sol_geo.census_vars['Key Statistics'][0]))

# %% ../nbs/02_app.ipynb 15
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Census Data", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages coming soon", header=True),
                
                dbc.DropdownMenuItem("Population Projection", href="#"),
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


# %% ../nbs/02_app.ipynb 17
# Note, for now I am not using a sidebar style as I do not want to fix the width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "24rem",
    "padding": "2rem 1rem",
    #"background-color": "#f8f9fa",
}


sidebar = html.Div(
    [
        html.H2("Filters"),
        html.Hr(),
        dbc.Nav(
            [
                html.P("Geography"), # TODO add a tooltip button here with link to geo explanation
                dropdown_geo,
                html.Br(),
                html.P("Location"), # TODO add a little info button here with link to geo explanation
                dropdown_location,
                html.Br(),
                html.P("Data"), # TODO add a little info button here with link to geo explanation
                dd_var,
                dd_measure,
                html.Br(),
                html.P("Data Type"), 
                control_type,
                #html.Br(),
                #dcc.Dropdown(id = 'three')

            ],
            vertical=True,
            pills=True,
        ),
    ],
    #style=SIDEBAR_STYLE,
)


# %% ../nbs/02_app.ipynb 19
app.layout = dbc.Container([
                dbc.Row([
                    navbar
                ]),
                dbc.Row(
                    [dbc.Col(sidebar, width = 2),
                    dbc.Col([mytitle,
                            map_graph,
                            selectedBarGraph,
                            #dbc.Row([cards])
                            ], width = 10)
                     ], justify = 'center'),                    
                ], fluid = True)

# %% ../nbs/02_app.ipynb 22
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
        


# %% ../nbs/02_app.ipynb 24
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
        


# %% ../nbs/02_app.ipynb 28
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

# %% ../nbs/02_app.ipynb 31
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

# %% ../nbs/02_app.ipynb 33
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
        


# %% ../nbs/02_app.ipynb 35
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

# %% ../nbs/02_app.ipynb 38
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

# %% ../nbs/02_app.ipynb 48
# Run app
if __name__=='__main__':
    try:
        app.run_server(debug=True, port=9999) # Random int mitigates port collision
    except:
        print("Cannot run server here")
