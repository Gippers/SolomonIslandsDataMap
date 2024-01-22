# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_app_data.ipynb.

# %% auto 0
__all__ = ['sol_geo', 'geos', 'cen_vars', 'NUM_GEOS', 'stored_data', 'dropdown_location', 'dd_age', 'dd_years_pop',
           'dropdown_geo', 'control_type', 'dd_dataset', 'dd_var', 'dd_measure', 'dd_var_pop', 'dd_measure_pop',
           'data_grid', 'grid_rows', 'download_button', 'year_slider', 'SIDEBAR_STYLE', 'sidebar', 'mytitle',
           'map_graph', 'selectedBarGraph', 'popPyramid', 'pyramidTitle', 'popKpi']

# %% ../nbs/02_app_data.ipynb 3
from nbdev.showdoc import *
# TODO work out how to get around below hack
try:
    from SolomonIslandsDataMap.load_data import *
    from SolomonIslandsDataMap.dash_components import *
except: 
    from load_data import *
    from dash_components import *
from fastcore.test import *
from dash import dcc, html
import dash_bootstrap_components as dbc 
import dash_mantine_components as dmc
from dash_bootstrap_templates import load_figure_template
from datetime import datetime

# %% ../nbs/02_app_data.ipynb 5
sol_geo = SolomonGeo.load_pickle(aws = True)

load_figure_template("minty")

geos = sol_geo.geo_levels
cen_vars = sol_geo.census_vars
NUM_GEOS = len(geos)

# %% ../nbs/02_app_data.ipynb 9
stored_data = sol_geo.get_store()

# %% ../nbs/02_app_data.ipynb 11
dropdown_location = html.Div(children = gen_dd(sol_geo.locations[sol_geo.geo_levels[0]], 
                                                'locDropdown', clear = True, place_holder='Select Dropdown Location',
                                                multi = True, 
                                                val = []))

# TODO maybe ages should be multi select
dd_age = html.Div(children = gen_dd(sol_geo.ages, 'age_dropdown'
                                    ,val = sol_geo.ages
                                    ,multi = True, clear = False))
dd_years_pop = html.Div(children = gen_dd(sol_geo.pop_years, 'years_dropdown', val = [datetime.now().year], #multi = True 
                                      ))

dropdown_geo = dmc.SegmentedControl(
                            id="segmented_geo",
                            value=geos[0],
                            data=geos,
                             orientation="vertical",
                            color = 'gray',
                            disabled = False, 
                            fullWidth = True,) # TODO consider redoing as theme is not consistent with this library
# Can only access province for population
control_type = dmc.SegmentedControl(
                        id="segmented_type",
                        value=sol_geo.data_type[0],
                        data=sol_geo.data_type,
                        orientation="vertical",
                        color = 'gray',
                        fullWidth = True,)

dd_dataset = dmc.SegmentedControl(
                        id="dataset_type",
                        value = "Census",
                        data=['Census', 'Population Projections'],
                        orientation="vertical",
                        color = 'gray',
                        fullWidth = True,)

dd_var = html.Div(children = gen_dd(list(sol_geo.census_vars.keys()), 'varDropdown', 
                                    val = list(sol_geo.census_vars.keys())[0],
                                    height = 75))
dd_measure = html.Div(children = gen_dd(sol_geo.census_vars['Key Statistics'], 'measureDropdown'
                                    ,val = sol_geo.census_vars['Key Statistics'][0]
                                      ))

dd_var_pop = html.Div(children = gen_dd(list(sol_geo.population_vars.keys()), 'varDropdownPop', 
                                    val = list(sol_geo.population_vars.keys())[0],
                                    height = 75))
dd_measure_pop = html.Div(children = gen_dd(sol_geo.population_vars[list(sol_geo.population_vars.keys())[0]], 'measureDropdownPop'
                                    ,val = 'Total'
                                      ))

# %% ../nbs/02_app_data.ipynb 12
data_grid = dbc.Container(
                children = gen_census_grid(sol_geo, sol_geo.geo_levels[0], "Key Statistics", 'Total Households')
            )
grid_rows = dcc.Input(id="grid-rows", type="number", min=1, max=len(sol_geo.locations['Province']), value=10)
download_button = dbc.Button("Download", id="csv-button", outline=True, n_clicks=0, color = "primary")

# %% ../nbs/02_app_data.ipynb 14
year_slider = dcc.Slider(sol_geo.pop_years[0], sol_geo.pop_years[-1], 1,  value = datetime.now().year, marks=None, id = 'year_slider',
                tooltip={"placement": "top", "always_visible": True},  included=False, dots = True, updatemode =  "drag"
                )

# %% ../nbs/02_app_data.ipynb 16
# Note, for now I am not using a sidebar style as I do not want to fix the width
# TODO fix the width of the sidebar, particular on different screens
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
                 html.Div(children = [
                    html.P("Select Dataset"), # TODO add a little info button here with link to geo explanation
                    dd_dataset,
                    html.Br(),],
                    id = "dataset-html",
                    style = {'display': 'none'},
                ),
                html.P("Geography"), # TODO add a tooltip button here with link to geo explanation
                dropdown_geo,
                html.Br(),
                html.Div(children = [
                    html.P("Age Group"), # TODO add a tooltip button here with link to geo explanation
                    dd_age,
                    html.Br(),],
                    id = "age-html",
                    style = {'display': 'none'},
                ),
                html.P("Location"), # TODO add a little info button here with link to geo explanation
                dropdown_location,
                html.Br(),
                html.Div(children = [
                    html.P("Data"), # TODO add a little info button here with link to geo explanation
                    dd_var,
                    dd_measure,
                    html.Br(),],
                    id = "census-vars-html",
                    style = {'display': 'block'},
                ),
                html.Div(children = [
                    html.P("Data"), # TODO add a little info button here with link to geo explanation
                    dd_var_pop,
                    dd_measure_pop,
                    html.Br(),],
                    id = "pop-vars-html",
                    style = {'display': 'none'},
                ),
                html.P("Data Type"), 
                control_type,
                html.Br(),
                html.Div(children = [
                    html.P("Dash Grid Rows"), 
                    grid_rows, # TODO add an info button here explaining that it is only for the dash grid
                    html.Br(),],
                    id = "rows-html",
                    style = {'display': 'none'},
                ),

            ],
            vertical=True,
            pills=True,
        ),
    ],
    #style=SIDEBAR_STYLE,
)

# %% ../nbs/02_app_data.ipynb 18
mytitle = dcc.Markdown(children="## " + list(cen_vars.keys())[0] + " by " + geos[0]) # TODO This needs a default title
map_graph = dcc.Graph(figure=define_map(sol_geo), selectedData=None,)

selectedBarGraph = dcc.Graph(figure = gen_bar_plot(sol_geo, sol_geo.geo_levels[0], 
                                               "Key Statistics", 'Total Households'),
                            id = 'bar_graph')
popPyramid = dcc.Graph(figure = gen_pyramid(sol_geo, 'Province', 2024), id = 'popPyramid')
pyramidTitle = dcc.Markdown(children ='## Projected Population Pyramid for Solomon Islands', id = 'pyramidTitle')
popKpi = dbc.Col(children = gen_kpi(sol_geo, datetime.now().year, 'Population', 'Total', sol_geo.ages), id = 'popKpi',
                 width = 2, align = 'center')
# testing
