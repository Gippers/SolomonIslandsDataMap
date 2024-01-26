# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/03_map_page.ipynb.

# %% auto 0
__all__ = ['init_init', 'layout', 'maintain_sidebar', 'dataset_selection', 'update_title', 'map_click', 'map_selections',
           'update_geography', 'update_measure', 'bar_click', 'update_map', 'update_bargraph']

# %% ../../nbs/03_map_page.ipynb 2
# TODO minimise these imports a bit where possible
from nbdev.showdoc import *
# TODO work out how to get around below hack
try:
    from SolomonIslandsDataMap.dash_components import gen_bar_plot, gen_dd
    from SolomonIslandsDataMap.app_data import mytitle, map_graph, selectedBarGraph, fake_slider
    from SolomonIslandsDataMap.load_data import SolomonGeo
except: 
    from dash_components import gen_bar_plot, gen_dd
    from app_data import mytitle, map_graph, selectedBarGraph, fake_slider
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
init_init = dcc.Store(id="initial-initial", data='census')

# %% ../../nbs/03_map_page.ipynb 7
def layout():
    return  mytitle, map_graph, selectedBarGraph, init_init, fake_slider

# %% ../../nbs/03_map_page.ipynb 10
@callback(
    Output("segmented_geo", "value"),
    Output('segmented_geo', 'disabled'), # On page load, allow for changing geography
    Output("dataset-html", "style"),
    Output("age-html", "style"),
    Output("rows-html", "style"),
    Output("census-vars-html", "style"),
    Output("pop-vars-html", "style"),
    Input("initial-initial", 'data'),
    Input("dataset_type", "value"),
    State("segmented_geo", "value"),
)
def maintain_sidebar(page_trigger:str, # Page that triggered initial load
                        dataset:str, # Currently selected dataset
                        geo:str, # the current geo level selection
                         ) -> dict:
    """Manages the dropdowns actively visable in sidebar based on page loaded"""

    # Depending on the page loaded, geogrpahy will or will not be disabled
    geo_disable = False

    # Based on page, update hidden style
    hide = {'display': 'none'}
    show = {'display': 'block'} 
    displayDataset = ''
    if page_trigger == 'census':
        displayDataset = hide
        displayAges = hide
        displayRows = hide
        censusVars = show
        popVars = hide
    elif page_trigger == 'pop':
        displayDataset = hide
        displayAges = show
        displayRows = hide
        # Disable geo selection on population page and set geo to province
        geo_disable = True 
        censusVars = hide
        popVars = show
        if geo != 'Province':
            # When the initial load id triggered by navigation to population page, 
            # if the geo isn't province we reset to this
            geo = 'Province'

    elif page_trigger == 'table':
        displayDataset = show
        displayAges = hide
        displayRows = show
        if dataset == 'Census':
            censusVars = show
            popVars = hide
        elif dataset == 'Population Projections':
            censusVars = hide
            popVars = show
        else:
            ValueError("Dataset must be Census or Population")


    if dataset == 'Population Projections':
        geo_disable = True

    return geo, geo_disable, displayDataset, displayAges, displayRows, censusVars, popVars

# %% ../../nbs/03_map_page.ipynb 13
@callback(
    Output("dataset_type", "value"), # Based on page loaded, change value of current dataset
    Input("initial-initial", 'data'),
    State("dataset_type", "value"),
    allow_duplicate=True,
    prevent_initial_call=True,
)
def dataset_selection(page_trigger:str, # Newly loaded page
                      currDataset:str, # Currenly selected data
                         ) -> str: # New dataset
    """Based on the page selected, update the dataset selected"""
    if page_trigger == 'census':
        dataset = 'Census'
    elif page_trigger == 'pop':
        dataset = 'Population Projections'
    else:
        dataset = currDataset
    
    return dataset

# %% ../../nbs/03_map_page.ipynb 16
@callback(
    Output('title', 'children'),
    Input("segmented_geo", 'value'),
    Input("segmented_type", 'value'),
    Input('measureDropdown', 'value'),
    Input('varDropdown', 'value'),
    Input('measureDropdownPop', 'value'),
    Input("year_slider", "value"),
    Input('locDropdown', 'value'),
    Input("dataset_type", 'value'),
    Input('initial-initial', 'data'),
    allow_duplicate=True,
    prevent_initial_call=True)
def update_title(geo_input:str, # User input from the geography dropdown
                data_type:str, # User input of type of data
                measure:str, # A string contiaining the census variable and measure split by ':'
                variable:str, # The state of the variable dropdown
                measurePop:str,
                year:str, # The currently selected year
                loc_selection:[str], # The selected locations, may be none
                dataset:str, # The currently selected dataset
                load_trigger:str, # The currently loaded page
              )->(str): # Returns a graph object figure after being updated and the dynamic title
    '''
    Updates the title for each of the pages
    '''
    title = ''
    if load_trigger == 'census':
      title = '## ' + data_type + " " + measure + ' by ' + geo_input
      if data_type == 'Proportion': title = '## ' + data_type + " of " + measure + ' by ' + geo_input
    elif load_trigger == 'pop':
      # Create a title for the pyramid
      if loc_selection == []:
          title = '## Projected Population Pyramid for Solomon Islands'
      else:
          title = '## Aggregated Projected Population Pyramid for ' + ', '.join(loc_selection)
      title += ' in ' + str(year)
    elif load_trigger == 'table':
      title = '## Solomon Islands Data map - ' + geo_input
      if dataset == 'Census':
        title = '## Census ' + variable + " by " + geo_input
      elif dataset == 'Population Projections':
        title = '## Projections of ' + measurePop + " population by " + geo_input
  

    return title

# %% ../../nbs/03_map_page.ipynb 18
@callback(
    Output('locDropdown', 'value', allow_duplicate=True),
    Output('map', "clickData"),
    Output('map', "selectedData"),
    Input('map', 'clickData'),
    Input('map', 'selectedData'),
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
        return prev_locs, None, None
    else:
        # The locations are list of dictionaries
        if selectedData is not None:
            selections = list(map(lambda x: x['location'], selectedData['points']))

        elif clickData is not None:
            selections = list(map(lambda x: x['location'], clickData['points']))
        locations = []
        if prev_locs: locations = prev_locs
        # Check whether the new location is already in the prev locations
        for selection in selections:
            if selection in locations: locations.remove(selection)
            else: locations.append(selection)
    
        # returned objects are assigned to the component property of the Output
        # After updating fileter, we always reset map selection 
        return locations, None, None
        


# %% ../../nbs/03_map_page.ipynb 22
# TODO merge back into 
@callback(
    Output('map', "figure", allow_duplicate=True),
    # TODO - make this a Row object with children, then use function to recontruct
    # a group of them
    Input('locDropdown', 'value'),
    State("segmented_geo", "value"),
    State('geo_df', 'data'),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def map_selections(locations:[str], # The previously selected locations
                geo_input, # Currently selected geography
                dict_sol:dict, # The dataset in dictionary form
                )->[str]: # Returns the new value for the dropdown
    '''
    Update the selected data on the map for the selected locations
    Selections is an array of integers indicating the index of the selected points
    '''
    # Using geo from stored values
    sol_geo = SolomonGeo.gen_stored(dict_sol)

    patched_figure = Patch()

    ct = np.where(sol_geo.geo_levels == geo_input)[0][0] # Tracks the trace number
    pot_locs = map_graph.figure['data'][ct]['locations']

    if locations: 
        selections = np.nonzero(np.in1d(pot_locs, locations))[0]
    else: 
        selections = None 

    patched_figure['data'][ct]['selectedpoints'] = selections
    
    # returned objects are assigned to the component property of the Output
    # After updating fileter, we always reset map selection 
    return patched_figure
        


# %% ../../nbs/03_map_page.ipynb 25
@callback(
    Output('locationDiv', 'children'),
    Input("segmented_geo", 'value'),
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
    new_locations = []
    if locations != [] and set(locations) <= set(sol_geo.locations[geo_input]):
        new_locations = locations


    return gen_dd(sol_geo.locations[geo_input], 'locDropdown', "Select a location", clear = True, multi = True, 
                  val = new_locations)

# %% ../../nbs/03_map_page.ipynb 28
@callback(
    Output('measureDiv', 'children', allow_duplicate=True),
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
    sol_geo = SolomonGeo.gen_stored(dict_sol) # reload the data

    # Sometimes this callback is triggered when the measure doesn't need to be reset.
    # Check whether measure is in variable, if not reset to 0
    if measure not in sol_geo.census_vars[new_var]:
        measure = sol_geo.census_vars[new_var][0]

    # When a variable is selected, the measure will be set as the first one
    return gen_dd(sol_geo.census_vars[new_var], 'measureDropdown', 
                  val = measure)

# %% ../../nbs/03_map_page.ipynb 31
@callback(
    Output('measureDropdown', 'value', allow_duplicate=True),
    Output('bar_graph', "clickData"),
    Input('bar_graph', 'clickData'),
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
    sol_geo = SolomonGeo.gen_stored(dict_sol) # reload the data
    if clickData is None:
        return sol_geo.census_vars[variable][0], None
    else:
        # The measure are list of dictionaries
        selection = list(map(lambda x: x['x'], clickData['points']))[0]
    
        # returned objects are assigned to the component property of the Output
        # After updating fileter, we always reset map selection 
        return selection, None
        


# %% ../../nbs/03_map_page.ipynb 34
@callback(
    Output('map', 'figure', allow_duplicate=True),
    Input("segmented_geo", 'value'),
    Input("segmented_type", 'value'),
    Input('measureDropdown', 'value'),
    Input('varDropdown', 'value'),
    Input('initial-initial', 'data'),
    Input('measureDropdownPop', 'value'),
    Input('varDropdownPop', 'value'),
    Input('age_dropdown', 'value'),
    Input("year_slider", "value"),
    Input('segmented_geo', 'disabled'),
    State('geo_df', 'data'),
    allow_duplicate=True,
    prevent_initial_call=True)
def update_map(geo_input:str, # User input from the geography dropdown
                data_type:str, # User input of type of data
                measure:str, # A string contiaining the census variable and measure split by ':'
                variable:str, # The state of the variable dropdown
                page:str, # The current page
                measurePop:str, # A string contiaining the census variable and measure split by ':'
                variablePop:str, # The state of the variable dropdown
                age:[str], # Age Brackets to display
                year:int, # The selected projection year
                geo_trigger:int, # Listening for whether segmented geo is locked, signaling that map
                                        # page was loaded after geo data was updated.
                dict_sol:dict, # The dataset in dictionary form
              )->(type(go.Figure())): # Returns a graph object figure after being updated and the dynamic title
    '''
    Updates the focus census variable or geography dispalayed on the map
    '''
    # TODO the None workaround might be taxing on the load times, is there a better way
    # or maybe I can check it it needs updating?
    patched_figure = Patch()
    button_clicked = ctx.triggered_id
    print("Updating map for " + page)

    sol_geo = SolomonGeo.gen_stored(dict_sol) # reload the data

    if page == 'census':
        '''Process of updating map when the selected page is census'''

        # A None value is passed when the page is first loaded, hence
        # the the values are reset.
        if button_clicked in ['segmented_geo', 'initial-initial']:
            # Update disaplayed geography 
            for geo in sol_geo.geo_levels:
                tn = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
                patched_figure['data'][tn]['visible'] = geo_input == geo
            
        if button_clicked in ["segmented_type", 'initial-initial']:
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
                patched_figure['data'][tn]['zmax'] = np.max(ar)
                patched_figure['data'][tn]['hovertemplate'] = ht

                
            

        if button_clicked in ['measureDropdown', 'initial-initial']:
            # Update the z values in map to the data for the requested census variable
            for geo in sol_geo.geo_levels:
            # Ar updates the z value ie. data disaplyed each time
            # TODO this is fairly inefficient, as we are processing each time
            # Maybe faster framework like polars could help? or caching but would require a lot of caching
                tn = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
                ar = sol_geo.get_census(geo_filter = geo, type_filter=data_type, var = variable, measure=measure).values
                ar = ar.reshape((ar.shape[0],))
                patched_figure['data'][tn]['z'] = ar
                patched_figure['data'][tn]['zmin'] = np.min(ar)
                patched_figure['data'][tn]['zmax'] = np.max(ar)

    elif page == 'pop':
        '''Process of updating map when the selected page is population projections'''
        init_load = False
        if geo_trigger == True: init_load = True

        sol_geo = SolomonGeo.gen_stored(dict_sol) # reload the data

        # A None value is passed when the page is first loaded, hence
        # the the values are reset.
        # Hardcoded to province as we only have forcasts by province
        if button_clicked in ["segmented_geo"] or init_load == True:
            # Update disaplayed geography 
            for geo in sol_geo.geo_levels:
                tn = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
                patched_figure['data'][tn]['visible'] = geo_input == geo
            
        if button_clicked in ["segmented_type"] or init_load == True:
            # Update the type of data displayed on map and the hover template
            for geo in sol_geo.geo_levels:
                tn = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
                # All years allows us to set the min and max colour as the min and max across all years
                all_years = sol_geo.get_pop(years = sol_geo.pop_years, var = variablePop, measure = measurePop, type_filter=data_type,
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

                
            

        if button_clicked in ['measureDropdownPop', 'year_slider', 'age_dropdown'] or init_load == True:
            # Update the z values in map to the data for the requested census variable
            for geo in sol_geo.geo_levels:
            # Ar updates the z value ie. data disaplyed each time
            # TODO this is fairly inefficient, as we are processing each time
            # Maybe faster framework like polars could help? or caching but would require a lot of caching
                tn = np.where(sol_geo.geo_levels == geo)[0][0] # Tracks the trace number
                
                # All years allows us to set the min and max colour as the min and max across all years
                all_years = sol_geo.get_pop(years = sol_geo.pop_years, var = variablePop, measure = measurePop, type_filter=data_type,
                                    agg = True, agg_location = True, ages = age)
                ar = all_years.loc[year].values[:, -1]
                all_years = all_years.values[:, -1]
                ar = ar.reshape((ar.shape[0],))
                patched_figure['data'][tn]['z'] = ar
                patched_figure['data'][tn]['zmin'] = np.min(all_years)
                patched_figure['data'][tn]['zmax'] = np.max(all_years)

    # returned objects are assigned to the component property of the Output
    # After updating fileter, we always reset map selection 

    return patched_figure

# %% ../../nbs/03_map_page.ipynb 38
# Callback allows components to interact
@callback(
    Output('bar_graph', 'figure'),
    Input("segmented_type", 'value'),
    Input('measureDropdown', 'value'),
    Input('locDropdown', 'value'),
    Input('initial-initial', 'data'),
    State("segmented_geo", 'value'),
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
    locs = []
    # Multi dropdown can return None or a list of None.
    if len(loc_selection) > 0: 
        locs = loc_selection
    bg = gen_bar_plot(sol_geo, geo_input, variable, measure, locs, data_type)

    # returned objects are assigned to the component property of the Output
    # After updating fileter, we always reset map selection 

    return  bg
