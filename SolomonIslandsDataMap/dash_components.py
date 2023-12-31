# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_dash_components.ipynb.

# %% auto 0
__all__ = ['define_map', 'gen_bar_plot', 'gen_dash_grid', 'card_list', 'gen_dd']

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
from dash import Dash, dcc, Output, Input, html, ctx  # pip install dash
import dash_ag_grid as dag
import dash_bootstrap_components as dbc    # pip install dash-bootstrap-components
from dash_bootstrap_templates import load_figure_template
import random
import dash_mantine_components as dmc

# %% ../nbs/01_dash_components.ipynb 7
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
        z_vals = sol_df.get_df(geo_filter = value, var = 'Key Statistics', 
                                                 measure = 'Total Households').values
        z_vals = z_vals.reshape((z_vals.shape[0],))
        traces.append(go.Choroplethmapbox(
                                geojson=sol_df.get_geojson(geo_filter = value),
                               locations=sol_df.locations[value],
                               customdata = sol_df.locations[value],
                               # TODO undo hardcoding
                               z = z_vals,
                               colorscale="deep",
                                marker_line_width = 0.5,
                                zauto=True,
                                selectedpoints=None,
                                hovertemplate = '%{customdata} <extra>%{z}</extra>',
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
    )
    
    return fig


# %% ../nbs/01_dash_components.ipynb 12
def gen_bar_plot(sol_geo:SolomonGeo, # Solomon geo object containing census data to input into map
                    geo_filter:str, # The desired aggregation of the geography
                    variable:str, # The variable to use to create the bar plot
                    measure:str, # The measure to highlight on the bar graph
                    locations:[str] = None, # Desired location within aggregation
                    type_filter:str = 'Total', # The type aggregartion
                )->type(go.Figure()): # Returns a graph object figure of a barplot
    # TODO setup so that the graph highlights the selected measure
    figtext = 'Showing ' + variable + ' for '
    if locations is None:
        df = sol_geo.agg_df(geo_filter, variable, loc_filter = locations, type_filter = type_filter)
        df = pd.DataFrame(df).transpose()
        df.index = ['Total']
        locations = ['Total']
        figtext += 'Solomon Islands'
    else:
        df = sol_geo.get_df(geo_filter, variable, loc_filter = locations, type_filter = type_filter)
        figtext += ', '.join(locations)
    fig = go.Figure()
    measures = list(df.columns)
    for loc in locations:
        fig.add_trace(go.Bar(
            x = measures,
            y = df.loc[df.index == loc].values[0],
            name = loc,
        ))
    # TODO create dynamic text with Location name and Variable
    # TODO add standout text
    # TODO should this be ordered? Hinders comparison. Can I order the dataset somewhere else?
    fig.update_layout(barmode='group', xaxis_tickangle=-45, title_text=figtext
                      , xaxis={'categoryorder':'total descending'})
    return fig

# %% ../nbs/01_dash_components.ipynb 17
# TODO should this method be appended to sol_geo??
def gen_dash_grid(sol_geo:SolomonGeo, # Solomon geo object containing census data to input into map
                    geo_filter:str, # The desired aggregation of the geography
                    variable:str, # The variable to use to create the bar plot
                    measure:str, # The measure to highlight on the bar graph
                    locations:[str] = None, # Desired location within aggregation
                    type_filter:str = 'Total', # The type aggregartion
                    grid_rows:int = 10, # The number of rows to display
                )->dag.AgGrid: # Returns a graph object figure of a barplot
    '''Creates a basic data table using dash grid'''
    figtext = 'Showing ' + variable + ' by ' + geo_filter
    df = sol_geo.get_df(geo_filter, variable, loc_filter = locations, type_filter = type_filter)
    df.insert(0, geo_filter, df.index) # Put geo locations at the front
    
    # pre define the column definitions, with extra speficiations for the locations
    colDef = [{"field": geo_filter, "headerName": geo_filter, "filter": True, "lockPinned": True, "cellClass": "lock-pinned"}]                    
    colDef += [{"field": i, "headerName": i} for i in df.columns[1:]]
    dt = dag.AgGrid(
        id = 'dash-grid',
        rowData = df.to_dict('records'),
        columnDefs = colDef,
        columnSize="sizeToFit",
        defaultColDef={"resizable": True, "sortable": True},
        dashGridOptions={"pagination": True, "domLayout": "autoHeight", "paginationPageSize": 10},
        style={"height": None},
        csvExportParams={
                "fileName": "Solomons 2009 Census Data " + variable + " by " + geo_filter + " - " + type_filter + ".csv",
            },
    )

    return dt

# %% ../nbs/01_dash_components.ipynb 22
# todo - turn this eventually into a function

# TODO - make it in future so that clicking on a card updates the current census variable
# selection and it highlights it as clicked.
# TODO - workout how to make this into a collection of cards, potentially cardgroup
# TODO - need to rename this
# TODO create bottom padding
# TODO - should I have some graphs here instead of cards??

def card_list(sg:SolomonGeo, # Input data object
                header:str, # Header of Accordian
                loc:[str] = None, # Desired location within aggregation
                type_filter:str = 'Total', # The type 
                    )->dbc.Col: # Returns a column containing a title and accordian items
    '''
    Create a list accordians for each variable, where each accordian contains a card for 
    each measure of that variable
    '''
    # If location is none, set agg to any location.
    # This means if not location is selected, we always return the total
    geo = None
    if loc == None:
        geo = sg.geo_levels[0]

    accordians = []
    # TODO this needs to be in a row above the accordians
    accordians.append(dcc.Markdown(children="## " + header))
    # TODO iter through keys
    for key in sg.census_vars:
        cards = []
        for var in sg.census_vars[key]:
            # Create an accordian with the header of the variable and such
            if loc == None:
                df = sg.agg_df(geo_filter = geo,
                                var = key,
                                measure = var, 
                                loc_filter = loc,
                                type_filter = type_filter).values[0]
            else:
                df = sg.get_df(geo_filter = geo, 
                                var = key,
                                measure = var, 
                                loc_filter = loc,
                                type_filter = type_filter).values[0]
            cards.append(#dbc.Col([
                dbc.Card(
                children = [
                    dbc.CardHeader(
                        [html.H4(var)]

                    ),
                    dbc.CardBody(
                        [
                        html.H5(df, 
                                className = "text-center")
                        ] # TODO - add a rank here and colour code based on rank (i.e. 2nd highest of provinces)
                    )]
                , class_name ="border-primary" #m-2 mb-3
                
                #)]
                )
            )
        accordians.append(dbc.Row([dbc.AccordionItem(
                 dbc.Row(cards),
                title=key,
            )]))

    # TODO return list of accordiants in a column?
    return dbc.Col(accordians)

# %% ../nbs/01_dash_components.ipynb 26
def gen_dd(location_list:[str], # a list of locations
           id:str, # Id of the dropdown
           place_holder:str = None, # a placeholder message to display
           val:str = None, # The starting value of the dropdown
           clear:bool = False, # pick whether the ]
           height:int = 35, # height of the dropdown text
           multi:bool = False, # Is the dropdown multi select
                        )->dcc.Dropdown: # Returns a dropdown
    '''
    Create the location dropdown from given list
    '''
    # TODO is this really necessary? I anm
    dd = dcc.Dropdown(options=location_list,
                        value=val,  # initial value displayed when page first loads
                        searchable=True,
                        clearable=clear,
                        placeholder=place_holder, 
                        id = id, 
                        optionHeight=height,
                        multi=multi)
    return dd
