# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_dash_components.ipynb.

# %% auto 0
__all__ = ['define_map', 'card_list']

# %% ../nbs/01_dash_components.ipynb 2
from nbdev.showdoc import *
# TODO work out how to get around below hack
try:
    from SolomonIslandsDataMap.load_data import *
except: 
    from load_data import *
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

# %% ../nbs/01_dash_components.ipynb 6
# TODO I should build figures and maps in another script
def define_map(sol_df:SolomonGeo # Solomon geo object containing census data to input into map
                )->type(go.Figure()): # Returns a graph object figure
    '''
    Creates and returns the base cloreopath map
    '''
    # TODO - should I update this into a class with methods for updating
    # the other things? Acutally maybe as another function if the update is done through patch
    
    # cols_dd dictates the aggregation that will be visable
    cols_dd = sol_df.geo_levels
    # define traces and buttons at once
    traces = []
    # TODO if fails remember I changed visible from cols_dd
    for value in cols_dd:
        traces.append(go.Choroplethmapbox(
                                geojson=sol_df.get_geojson(agg_filter = value),
                               locations=sol_df.get_df(agg_filter = value).index,
                               z = sol_df.get_df(agg_filter = value)['Total Households'],
                               colorscale="deep",
                                marker_line_width = 0.5,
                                zauto=True,
                visible= True if value==cols_dd[0] else False))
        
    # Show figure
    fig = go.Figure(data=traces)
    # This is in order to get the first title displayed correctly
    first_title = cols_dd[0]
    fig.update_layout(title=f"<b>{first_title}</b>",
                        title_x=0.5,
                        mapbox_style = 'carto-positron',
                        mapbox_zoom = 5,
                        mapbox_center={"lat": -9.565766, "lon": 162.012453},
                        margin={"r":0,"t":0,"l":0,"b":0},
                        # TODO in future consider going back to multiselect, currently too hard
                        #clickmode = 'event+select',
    )
    
    return fig


# %% ../nbs/01_dash_components.ipynb 11
# todo - turn this eventually into a function

# TODO - make it in future so that clicking on a card updates the current census variable
# selection and it highlights it as clicked.
# TODO - workout how to make this into a collection of cards, potentially cardgroup
# TODO - need to rename this
# TODO create bottom padding
# TODO - should I have some graphs here instead of cards??

def card_list(sg:SolomonGeo, # Input data object
                header:str, # Header of Accordian
                agg:str, #Desired aggregation of data in card
                var:str, # Desired variable to display in card
                loc:str = None, # Desired location within aggregation
                    )->[dbc.AccordionItem]: # Returns an accordian with selected data
    '''
    Create a list of cards to put in a cardgroup
    '''
    # TODO should try not to call get for each var. What if instead, I 
    # called get once, then looped for each column locally.
    cards = []
    for var in sg.census_vars:
        cards.append(dbc.Col([
            dbc.Card(
            children = [
                dbc.CardHeader(
                    [html.H4(var)]

                ),
                dbc.CardBody(
                    [
                    html.H5(sg.get_df(agg_filter = agg, 
                                        var_filter = var, 
                                        loc_filter = loc).sum(), 
                            className = "text-center")
                    ] # TODO - in future will need to do weighted sum for some: might need an aggregate feature in class that 
                        # aggregates correctly based on the variable (i.e. sum or weighted sum), maybe work out in get_df function
                )]
            , class_name ="border-primary" #m-2 mb-3
            
            )])
        )

    return [dbc.AccordionItem(
                 dbc.Row(cards),
                title=header,
            )]
