# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/05_table_page.ipynb.

# %% auto 0
__all__ = ['title', 'init_load', 'init_init', 'layout', 'update_grid', 'update_page_rows', 'update_page_size',
           'export_data_as_csv']

# %% ../../nbs/05_table_page.ipynb 2
# TODO minimise these imports a bit where possible
from nbdev.showdoc import *
# TODO work out how to get around below hack
try:
    from SolomonIslandsDataMap.dash_components import gen_dash_grid, gen_dd
    from SolomonIslandsDataMap.app_data import mytitle, data_grid, stored_data, dropdown_location \
        , control_type, dd_var, dd_measure, dropdown_geo, download_button, sidebar_table
    from SolomonIslandsDataMap.load_data import SolomonGeo
except: 
    from dash_components import gen_dash_grid, gen_dd
    from app_data import mytitle, data_grid, stored_data, dropdown_location \
        , control_type, dd_var, dd_measure, dropdown_geo, download_button, sidebar_table
    from load_data import SolomonGeo
from fastcore.test import *
from dash import Dash, dcc, callback, Output, Input, State, html, Patch, ctx, register_page, callback_context 
import dash_bootstrap_components as dbc    
import dash_ag_grid as dag

# %% ../../nbs/05_table_page.ipynb 3
try:
    register_page(__name__, 
                        path='/datatable',
                        title='Data Table',
                        name='Data Table')
except:
    pass

# %% ../../nbs/05_table_page.ipynb 6
title = dcc.Markdown(children="## This is a placeholder test!!") # TODO This needs a default title, shift to 02

# %% ../../nbs/05_table_page.ipynb 7
# TODO again as below, must be a better way
init_load = dcc.Store(id="initial-load", data={})
init_init = dcc.Store(id="initial-initial", data='table')
def layout():
    return dbc.Row(
        [dbc.Col(sidebar_table, width = 2),
         dbc.Col([
          dbc.Row([
                dbc.Col(title, width = 8),
                dbc.Col(download_button, width = {"size": 2})
                      ]),
              data_grid,
              stored_data,
              init_load,
              init_init,
            # fires 1ms after page load
            #dcc.Interval(id="interval-timer", interval=1, max_intervals=1),
            ], width = 10)
          ], justify = 'center')

# %% ../../nbs/05_table_page.ipynb 13
@callback(
    Output(data_grid, 'children'),
    Output(title, 'children'),
    Input(dropdown_geo, 'value'),
    Input(control_type, 'value'),
    Input('measureDropdown', 'value'),
    Input('varDropdown', 'value'),
    State('geo_df', 'data'),
    State('grid-rows', 'value'),
    allow_duplicate=True,
)
def update_grid(geo_input:str, # User input from the geography dropdownk
                    data_type:str, # User input of type of data
                    measure:str, # A string contiaining the census variable and measure split by ':'
                    variable:str, # The state of the variable dropdown
                    dict_sol:dict, # The dataset in dictionary form
                    grid_rows:int, # The number of rows to display
              )->(dag.AgGrid, str): # Returns a graph object figure after being updated and the dynamic title
    '''
    Updates the focus census variable or geography dispalayed on the map
    '''
    # TODO add proportion functionality
    # TODO add add an option for first call to be a default rebuild
    # TODO decide wether to implment patch later
    patched_figure = Patch()
    button_clicked = ctx.triggered_id
    print("What happens when auto triggered?")
    print(button_clicked)

    sol_geo = SolomonGeo.gen_stored(dict_sol) # reload the data

    print(button_clicked)
    if button_clicked == dropdown_location.id:
        # Update disaplayed geography 
        # TODO in future update row highlighting
        print("locationsleected")
        
    elif button_clicked in [control_type.id, dropdown_geo.id,  'varDropdown',  'measureDropdown', None]:
        # Rebuild the table given updated selection
        # None is the initial call
        patched_figure = gen_dash_grid(sol_geo, geo_input,variable, measure, 
            type_filter = data_type, grid_rows=grid_rows)


    #elif button_clicked == 'measureDropdown':
        # TODO in future update for column highlighting/ordering
    #    print("measure selected")
        
    # returned objects are assigned to the component property of the Output
    # After updating fileter, we always reset map selection 

    return patched_figure, '## ' + variable + " by " + geo_input

# %% ../../nbs/05_table_page.ipynb 16
@callback(
    Output("grid-rows", "value"),
    Output("grid-rows", "max"),
    Input(dropdown_geo, 'value'),
    State(stored_data, 'data'),
    suppress_callback_exceptions = True,
)
def update_page_rows(geo_input:str, # User input from the geography dropdown
                    dict_sol:dict, # The dataset in dictionary form
                    ) -> (int, int): # New value and max size of the grid selection
    ''' Updates the page size and max of the input selection based on updated geography'''
    sol_geo = SolomonGeo.gen_stored(dict_sol) # reload the data
    return 10, len(sol_geo.locations[geo_input])

# %% ../../nbs/05_table_page.ipynb 18
@callback(
    Output("dash-grid", "dashGridOptions"),
    Input("grid-rows", "value"),
    State("dash-grid", "dashGridOptions"),
    suppress_callback_exceptions = True,
)
def update_page_size(page_size:int, # The input page size
                    grid_options:dict, # The current grid page size option
                    ) -> dict: # The updated grid page size option
    ''' Updates the page size of the grid based on input'''
    page_size = 1 if page_size is None else page_size
    grid_options["paginationPageSize"] = page_size
    return grid_options

# %% ../../nbs/05_table_page.ipynb 21
@callback(
    Output("dash-grid", "exportDataAsCsv"),
    [Input('csv-button', "n_clicks")],
)
def export_data_as_csv(n_clicks:int, # Listening for click inputs
                       ) -> bool: # Whether to download csv
    trigger = callback_context.triggered[0]
    if trigger['prop_id'] ==  'csv-button.n_clicks':
        return True
    return False
