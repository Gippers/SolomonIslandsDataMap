# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_app.ipynb.

# %% auto 0
__all__ = ['sol_geo', 'geo_df', 'app', 'server', 'geos', 'cen_vars', 'mytitle', 'map_graph', 'cards', 'dropdown_location',
           'dropdown_geo', 'control_type', 'dropdown_var', 'navbar', 'SIDEBAR_STYLE', 'sidebar', 'map_click',
           'update_kpis', 'update_geography']

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
from dash import Dash, dcc, Output, Input, html, Patch, ctx  # pip install dash
import dash_bootstrap_components as dbc    # pip install dash-bootstrap-components
from dash_bootstrap_templates import load_figure_template
import random
import dash_mantine_components as dmc

# %% ../nbs/02_app.ipynb 5
sol_geo = SolomonGeo.load_pickle("/testData/")
geo_df = sol_geo.geo_df

# %% ../nbs/02_app.ipynb 10
# Build your components
# FYI the best themes seem to be: [Darkly, Flatly, Minty, Slate, JOURNAL]
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
server = app.server
load_figure_template("minty")

geos = geo_df.loc[:, 'agg'].unique()
cen_vars = sol_geo.census_vars


# %% ../nbs/02_app.ipynb 12
mytitle = dcc.Markdown(children="## " + cen_vars[-1] + " by " + geos[0]) # TODO This needs a default title
map_graph = dcc.Graph(figure=define_map(sol_geo), selectedData=None)
# TODO entire accordian will need to be the child
cards = dbc.Accordion(children= 
        card_list(sol_geo, "Current Selection: Total"),
        always_open=True,
        class_name = "accordion-header",
    )


# %% ../nbs/02_app.ipynb 14
# TODO options gets changed in callback?
# TODO need to store locations in data class
dropdown_location = html.Div(children = gen_loc_dd(sol_geo.locations[sol_geo.geo_levels[0]]))
               

#dropdown_geo = dbc.Dropdown(options=geos,
#                        value=geos[0],  # initial value displayed when page first loads
#                        clearable=False)
dropdown_geo = dmc.SegmentedControl(
                            id="segmented_geo",
                            value=geos[0],
                            data=geos,
                             orientation="vertical",
                            color = 'gray',
                            fullWidth = True,
                            # TODO - think there is a version issue with class_name on the server, need to fix
                            #className="btn-group btn-primary",
                            #class_name = "btn btn-primary"
                            #color = dmc.theme.DEFAULT_COLORS["teal"][3]
    # TODO this color functionality is beyond stupid...
    # TODO definitely change to dbc, even though more complicated get consistent theme.s..
                        ) # TODO consider redoing as theme is not consistent with this library
# TODO based on the value selected above, make a dropdown with children set to starting list of
# locations in that geo. on update of dropdown_geo, update children list then update value in main one.
# then get rid of function
control_type = dmc.SegmentedControl(
                        id="segmented_type",
                        value=sol_geo.data_type[0],
                        data=sol_geo.data_type,
                        orientation="vertical",
                        color = 'gray',
                        fullWidth = True,)

dropdown_var = dcc.Dropdown(options=cen_vars,
                        value=cen_vars[-1],  # initial value displayed when page first loads
                        searchable=True,
                        clearable=False,
                        optionHeight=100)


# %% ../nbs/02_app.ipynb 16
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


# %% ../nbs/02_app.ipynb 18
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
                dropdown_var,
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


# %% ../nbs/02_app.ipynb 20
app.layout = dbc.Container([
                dbc.Row([
                    navbar
                ]),
                dbc.Row(
                    [dbc.Col(sidebar, width = 2),
                    dbc.Col([mytitle,
                             map_graph,
                            dbc.Row([cards])
                            ], width = 10)#, style = {'margin-left':'15px', 'margin-top':'7px', 'margin-right':'15px'})
                     ], justify = 'center'),                    
                ], fluid = True)

# %% ../nbs/02_app.ipynb 23
@app.callback(
    Output('locDropdown', 'value'),
    # TODO - make this a Row object with children, then use function to recontruct
    # a group of them
    Input(map_graph, 'clickData'),
    prevent_initial_call=True
)
def map_click(clickData:str, # The currently clicked location on the map
                )->str: # Returns the new value for the dropdown
    # TODO - What this should do, is on click set the location dropdown selection. Then that triggers data update.
    # TODO - I also need to reset this when the filter is changed
    # TODO - This callback should be triggered by the main callback https://dash.plotly.com/advanced-callbacks see callbacks as an indirect
    # result section
    # TODO add a hidden state tracker - update var and geo based on this
    # TODO workout how to make multi point selection work - hard todo - might need to find open source web example
    
    print("map clicked updating to:")
    if clickData is None:
        # TODO when none, maybe in future return current saved state, for now doing total
        # TODO add a heading and maybe put in an acordian
        return None
    else:
        # The locations are list of dictionaries
        locations = list(map(lambda x: x['location'], clickData['points']))
        print(locations)
        return locations[0]
        


# %% ../nbs/02_app.ipynb 24
@app.callback(
    Output(cards, 'children'),
    # TODO - make this a Row object with children, then use function to recontruct
    # a group of them
    Input('locDropdown', 'value'),
    Input(control_type, 'value'),
    #Input(dropdown_location, 'options'),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def update_kpis(locations:str, # The currently selected location. Including defualt of none
                data_type:str, # The currently selected data type (Total or Proportion)
                #dd_updated:[str], # The currently selected data type (Total or Proportion)
                )->type(dbc.Card):
    '''
    Based on updates to either te dropdown location (which is triggered by map clicks) or 
    changes to the type of data dispalyed, update the cards
    '''
    print("triggered update cards")
    #if the dropdown_locations options was just updated, then we overwrite
    # TODO workout how to make multi point selection work - hard todo - might need to find open source web example
    # filter dataframe by store location, then sum all orders of that store.
    header_text = "Total"
    if locations is not None:
        header_text = locations
        locations = [locations]
    new_cards = card_list(sol_geo, 
                            "Current Selection: "  + header_text,
                            loc = locations, 
                            type_filter = data_type)

    return new_cards

# %% ../nbs/02_app.ipynb 27
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
    return gen_loc_dd(sol_geo.locations[geo_input])

# %% ../nbs/02_app.ipynb 30
# Callback allows components to interact

# TODO put title in it's own callback
@app.callback(
    Output(map_graph, 'figure'),
    Output(mytitle, 'children'),
    Input(dropdown_geo, 'value'),
    Input(control_type, 'value'),
    Input(dropdown_var, 'value'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def update_geography(geo_input:str, # User input from the geography dropdown
                     data_type:str, # User input of type of data
                     census_var:str, # User input for the census variable
              )->(type(go.Figure()), str): # Returns a graph object figure after being updated and the dynamic title
    '''
    Updates the focus census variable or geography dispalayed on the map
    '''
    patched_figure = Patch()
    button_clicked = ctx.triggered_id
    if button_clicked == dropdown_geo.id:
        # Update disaplayed geography based on 
        for geo in sol_geo.geo_levels:
            i = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
            patched_figure['data'][i]['visible'] = geo_input == geo
        
    elif button_clicked == control_type.id:
        # Update the type of data displayed
        # TODO currently displayed data will need to be tracked. Can't be tracked in object, use hidden 
        # TODO will need to track this update also in var dropdown clicked
        # TODO will also need to track current census_var in here
        # TODO this also needs to trigger cards
        for geo in sol_geo.geo_levels:
            i = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
            ar = sol_geo.get_df(geo_filter = geo, type_filter=data_type, var_filter = census_var).values
            ar = ar.reshape((ar.shape[0],))
            patched_figure['data'][i]['z'] = ar

    elif button_clicked == dropdown_var.id:
        # Update the z values in map to the data for the requested
        # census variable
        
        for geo in sol_geo.geo_levels:
        # Ar updates the z value ie. data disaplyed each time
        # TODO this is fairly inefficient, as we are processing each time
        # Maybe faster framework like polars could help? or caching but would require a lot of caching
            i = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
            ar = sol_geo.get_df(geo_filter = geo, type_filter=data_type, var_filter = census_var).values
            ar = ar.reshape((ar.shape[0],))
            patched_figure['data'][i]['z'] = ar

    print(census_var)
    # returned objects are assigned to the component property of the Output
    # After updating fileter, we always reset map selection 
    # TODO - potentially not with census updates though...
    #update_kpis(selectedData = map_selection)

    return patched_figure, '## Solomon Islands Data map - ' + geo_input

# %% ../nbs/02_app.ipynb 40
# Run app
if __name__=='__main__':
    try:
        app.run_server(debug=True, port=9999) # Random int mitigates port collision
    except:
        print("Cannot run server here")
