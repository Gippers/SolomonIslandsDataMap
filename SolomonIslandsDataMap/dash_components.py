# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_dash_components.ipynb.

# %% auto 0
__all__ = ['define_map', 'election_map', 'gen_bar_plot', 'election_bar_plot', 'gen_census_grid', 'gen_pop_grid', 'gen_kpi',
           'gen_dd', 'gen_pyramid']

# %% ../nbs/01_dash_components.ipynb 2
from nbdev.showdoc import *
# TODO work out how to get around below hack
try:
    from SolomonIslandsDataMap.load_data import *
except: 
    from load_data import *
import plotly.graph_objects as go
import plotly.express as px
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
import numpy as np

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
        z_vals = sol_df.get_census(geo_filter = value, var = 'Key Statistics', 
                                                 measure = 'Total Households').values
        z_vals = z_vals.reshape((z_vals.shape[0],))
        traces.append(go.Choroplethmapbox(
                                geojson=sol_df.get_geojson(geo_filter = value),
                               locations=sol_df.locations[value],
                               customdata = sol_df.locations[value],
                               # TODO undo hardcoding
                               z = z_vals,
                               zmin = np.min(z_vals),
                               zmax = np.min(z_vals),
                               colorscale="deep",
                                marker_line_width = 0.5,
                                #zauto=True,
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


# %% ../nbs/01_dash_components.ipynb 18
def election_map(sol_df:SolomonGeo # Solomon geo object containing census data to input into map
                )->type(go.Figure()): # Returns a graph object figure
    '''
    Creates and returns a chloreopath map for election
    '''
    # define traces and buttons at once
    traces = []

    for i, winner in enumerate(sol_df.elec_wide["Winning Party"].unique()):
        dfp = sol_geo.elec_wide[sol_geo.elec_wide["Winning Party"] == winner]
        traces.append(go.Choroplethmapbox(
                                geojson=sol_df.get_geojson(geo_filter = "Constituency"),
                               locations=dfp.loc_name,
                               customdata = np.stack((dfp.loc_name, dfp["Winning Party"], dfp.iloc[:, 4]), axis = 1), # Stack to make it display in the right order # TODO change column names so I don't need iloc
                               # TODO undo hardcoding
                               z = [i, ] * len(dfp),
                               colorscale=sol_df.colorscales[i],
                               showscale = False,
                                marker_line_width = 0.5,
                                #zauto=True,
                                selectedpoints=None,
                                hovertemplate = '%{customdata[0]} <extra><b>Winning Party</b>: %{customdata[1]}<br><b>Candidate</b>: %{customdata[2]}</extra>',
                                legend = "legend1",
                                showlegend = True,
                                legendgroup = winner,
                                name = winner,
                #visible= True if value==cols_dd[0] else False,
                ))
        
    # Show figure
    fig = go.Figure(data=traces)
    # This is in order to get the first title displayed correctly
    #first_title = cols_dd[0]
    fig.update_layout(#title=f"<b>{"Constituency"}</b>",
                        title_x=0.5,
                        mapbox_style = 'carto-positron',
                        mapbox_zoom = 5,
                        mapbox_center={"lat": -9.565766, "lon": 162.012453},
                        margin={"r":0,"t":0,"l":0,"b":0},
                        showlegend = True,
                        legend_title = "Party",
    )
    
    return fig


# %% ../nbs/01_dash_components.ipynb 22
def gen_bar_plot(sol_geo:SolomonGeo, # Solomon geo object containing census data to input into map
                    geo_filter:str, # The desired aggregation of the geography
                    variable:str, # The variable to use to create the bar plot
                    measure:str, # The measure to highlight on the bar graph
                    locations:[str] = [], # Desired location within aggregation
                    type_filter:str = 'Total', # The type aggregartion
                )->type(go.Figure()): # Returns a graph object figure of a barplot
    '''Create a bar plot that show the census selected census data'''
    figtext = 'Showing ' + variable + ' for '
    if locations == []:
        df = sol_geo.get_census(geo_filter, variable, type_filter = type_filter, agg = True)
        df = pd.DataFrame(df).transpose()
        df.index = ['Total']
        locations = ['Total']
        figtext += 'Solomon Islands'
    else:
        df = sol_geo.get_census(geo_filter, variable, loc_filter = locations, type_filter = type_filter)
        figtext += ', '.join(locations)
    fig = go.Figure()
    measures = list(df.columns)
    for loc in locations:
        fig.add_trace(go.Bar(
            x = measures,
            y = df.loc[df.index == loc].values[0],
            name = loc,
            customdata = np.repeat(loc, len(measures)),
            hovertemplate = '%{customdata} <extra>%{x}<br><b>%{y}</extra>',
        ))
    # TODO create dynamic text with Location name and Variable
    # TODO add standout text
    # TODO should this be ordered? Hinders comparison. Can I order the dataset somewhere else?
    fig.update_layout(barmode='group', xaxis_tickangle=-45, title_text=figtext
                      , xaxis={'categoryorder':'total descending'})
    return fig

# %% ../nbs/01_dash_components.ipynb 28
def election_bar_plot(sol_geo:SolomonGeo, # Solomon geo object containing census data to input into map
                    geo_filter:str = "Constituency", # The desired aggregation of the geography
                    year:int = 2024, # The year of the elections data
                    election:str = 'National Parilament', # The type of election.	
                    location:str = 'Auki-Langalanga', # Desired location within aggregation
                    type_filter:str = 'Votes', # The type of data, eitehr Votes of Proportion
                )->type(go.Figure()): # Returns a graph object figure of a barplot
    '''Create a bar plot that show the census selected election data'''
    df = sol_geo.elec

    df = df.loc[df['loc_name'] == location and df['Type'] == election  and df['Year'] == year, :]

    figtext = year + " " + election + ' results in ' + location

    fig = go.Figure()
    measures = list(df.columns)
    fig.add_trace(go.Bar(
        x = df.loc[df['loc_name'] == loc, 'Candidate'].values,
        y = df.loc[df['loc_name'] == loc, 'Votes'].values,
        name = loc,
        marker = dict(color = list(map(lambda y: sol_geo.colormap[y], df.loc[df['loc_name'] == loc, 'Party'].values))),
        hovertemplate = '%{x} <extra>%{y}</extra>',
    ))
    fig.update_layout(barmode='group', xaxis_tickangle=-45, title_text="Title",
                    xaxis={'categoryorder':'total descending'})
    return fig

# %% ../nbs/01_dash_components.ipynb 32
# TODO should this method be appended to sol_geo??
def gen_census_grid(sol_geo:SolomonGeo, # Solomon geo object containing census data to input into map
                    geo_filter:str, # The desired aggregation of the geography
                    variable:str, # The variable to use to create the bar plot
                    measure:str, # The measure to highlight on the bar graph
                    locations:[str] = None, # Desired location within aggregation
                    type_filter:str = 'Total', # The type aggregartion
                    grid_rows:int = 10, # The number of rows to display
                )->dag.AgGrid: # Returns a graph object figure of a barplot
    '''Creates a basic data table using dash grid'''
    figtext = 'Showing ' + variable + ' by ' + geo_filter
    df = sol_geo.get_census(geo_filter, variable, loc_filter = locations, type_filter = type_filter)
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
        dashGridOptions={"pagination": True, "domLayout": "autoHeight", "paginationPageSize": grid_rows},
        style={"height": None},
        csvExportParams={
                "fileName": "Solomons 2009 Census Data " + variable + " by " + geo_filter + " - " + type_filter + ".csv",
            },
    )

    return dt

# %% ../nbs/01_dash_components.ipynb 36
# TODO should this method be appended to sol_geo??
def gen_pop_grid(sol_geo:SolomonGeo, # Solomon geo object containing census data to input into map
                    years:str, # Selected data years
                    variable:str, # The variable to use to create the bar plot
                    measure:str, # The measure to highlight on the bar graph
                    geo_filter:str = 'Province', # The desired aggregation of the geography
                    locations:[str] = None, # Desired location within aggregation
                    type_filter:str = 'Total', # The type aggregartion
                    grid_rows:int = 10, # The number of rows to display
                ) -> dag.AgGrid: # Returns a graph object figure of a barplot
    '''Creates a basic data table using dash grid'''
    figtext = 'Showing ' + variable + ' Projected Population by ' + geo_filter
    df = sol_geo.get_pop(years, variable, measure, type_filter = type_filter,)
    # Remove hierarchical columns
    df.columns = df.columns.get_level_values(1)
    df['location'] = df.index 
    df = pd.pivot(df, index = ['location', 'year'], columns = 'Age_Bracket', values = measure)

    # Change index 
    df.insert(0, 'Year', df.index.get_level_values(1))
    df.insert(0, geo_filter, df.index.get_level_values(0))
    df = df.reindex(columns = ['Year', geo_filter, '0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34',
        '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69',
        '70-74', '75-79', '80+'])
    
    # pre define the column definitions, with extra speficiations for the locations
    # TODO care of hardcoding, will break in future if projections are available for other geos
    colDef = [{"field": geo_filter, "headerName": geo_filter, "filter": True, "lockPinned": True, "cellClass": "lock-pinned"}]
    colDef += [{"field": 'Year', "headerName": 'Year', "filter": True, "lockPinned": True, "cellClass": "lock-pinned"}]                    
    colDef += [{"field": i, "headerName": i} for i in df.columns[2:]]
    dt = dag.AgGrid(
        id = 'dash-grid',
        rowData = df.to_dict('records'),
        columnDefs = colDef,
        columnSize="sizeToFit",
        defaultColDef={"resizable": True, "sortable": True},
        dashGridOptions={"pagination": True, "domLayout": "autoHeight", "paginationPageSize": grid_rows},
        style={"height": None},
        csvExportParams={
                "fileName": "Solomons 2009 Population Projections for " + variable + " Population by " + geo_filter + " - " + type_filter + ".csv",
            },
        )

    return dt

# %% ../nbs/01_dash_components.ipynb 40
# TODO create bottom padding

def gen_kpi(sg:SolomonGeo, # Input data object
                year:str, # Year of the kpi
                variable:str, # Variable to dispaly
                measure:str, # Measure to display
                ages:[str], # ages to display
                loc:[str] = [], # Desired location within aggregation
                type_filter:str = 'Total', # The type 
            )-> (dcc.Markdown, dcc.Markdown): # Returns a column containing a title and accordian items
    '''
    Create a list accordians for each variable, where each accordian contains a card for 
    each measure of that variable
    '''
    # TODO work out how to wrap kpi into text
    if loc == []:
        df = sg.get_pop(years = [year],
                        var = variable,
                        measure = measure, 
                        ages = ages,
                        type_filter = type_filter,
                        agg = True).values[0]
    else:
        df = sg.get_pop(years = [year], 
                        var = variable,
                        measure = measure, 
                        ages = ages,
                        loc_filter = loc,
                        type_filter = type_filter,
                        agg = True).values[0]
    if type_filter == 'Total':
        kpi = dcc.Markdown(children = "# " + str(format(int(df[0]), ",d")))
        text = dcc.Markdown(children = type_filter.lower() + " persons in current selection")
    elif type_filter == 'Proportion':
        kpi = dcc.Markdown(children = "# " + str(format(float(df[0]), ".1%")))
        text = dcc.Markdown(children = "projected population in current selection")
    else:
        raise ValueError('The type passed to the gen_kpi function must be one of the following: \'Total\', \'Proportion\'.')
    
    return kpi, text

# %% ../nbs/01_dash_components.ipynb 44
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

# %% ../nbs/01_dash_components.ipynb 47
def gen_pyramid(sol_geo:SolomonGeo, # Solomon geo object containing census data to input into map
                    geo_filter:str, # The desired aggregation of the geography
                    year:str, # Selected year to display on the graph
                    variable:str = 'Population', # The variable to use to create the bar plot
                    locations:[str] = [], # Desired location within aggregation
                    type_filter:str = 'Total', # The type aggregartion
                    ages:[str] = [], # Currenly selected ages for highlighting
                )->type(go.Figure()): # Returns a population pyramid and it's title
    '''Create a population pyramid of selected population data'''
    # TODO Can't make a comparative pop pyrmid. Should I do this??
    
    # Load Data
    if locations == []:
        pop_data = sol_geo.get_pop(years = [year], var = "Population", agg = True, agg_ages = True
                                   , type_filter=type_filter)
    else:
        pop_data = sol_geo.get_pop(years = [year], var = "Population", agg = True, agg_ages = True
                                   , type_filter=type_filter, loc_filter = locations)

    # Manipulate data for pyramid
    age_df = pop_data.loc[year]
    age_df.index.name = 'age'
    age_df.drop(columns = ('Population', 'Total'))

    y_age = age_df.index
    x_male = age_df.loc[:, ('Population', 'Males')] * -1
    x_female = age_df.loc[:, ('Population', 'Females')]

    # Create instance of the figure
    pyramid_fig = go.Figure()


    # Add Trace to figure
    pyramid_fig.add_trace(go.Bar(
            y=y_age,
            x=x_female,
            name='Female',
            orientation='h'
    ))
    # Add Trace to Figure
    pyramid_fig.add_trace(go.Bar(
            y=y_age,
            x=x_male,
            name='Male',
            orientation='h'
    ))


    # Update Figure Layout
    pyramid_fig.update_layout(
        title_font_size = 24,
        barmode='relative',
        bargap=0.0,
        bargroupgap=0,
        xaxis=dict(
            tickvals=[-30000, -20000, -10000,0, 10000, 20000, 30000],
            ticktext=['30k', '20k', '10k','0','10k','20k', '30k'],
            title='Population',
            title_font_size=14
        ),
        yaxis = dict(title = 'Age Group')
    )
    # TODO overtext labelling, should be flipped for female
    
    return pyramid_fig
