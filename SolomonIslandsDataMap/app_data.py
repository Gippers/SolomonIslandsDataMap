# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_app_data.ipynb.

# %% auto 0
__all__ = ['sol_geo', 'geo_df', 'geos', 'cen_vars', 'NUM_GEOS', 'stored_data', 'dropdown_location', 'dropdown_geo',
           'control_type', 'dd_var', 'dd_measure', 'SIDEBAR_STYLE', 'sidebar', 'mytitle', 'map_graph',
           'selectedBarGraph', 'data_grid']

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

# %% ../nbs/02_app_data.ipynb 5
sol_geo = SolomonGeo.load_pickle(aws = True)
geo_df = sol_geo.geo_df

load_figure_template("minty")

geos = sol_geo.geo_levels
cen_vars = sol_geo.census_vars
NUM_GEOS = len(geos)

# %% ../nbs/02_app_data.ipynb 9
stored_data = sol_geo.get_store()

# %% ../nbs/02_app_data.ipynb 11
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

# %% ../nbs/02_app_data.ipynb 13
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


# %% ../nbs/02_app_data.ipynb 15
# TODO - not sure whether this should be imported from app_data or built here.
# if building it here causes it to reload each time, I should probably move it later
# TODO downside of having it here is that it is a little more seperated.
mytitle = dcc.Markdown(children="## " + list(cen_vars.keys())[0] + " by " + geos[0]) # TODO This needs a default title
map_graph = dcc.Graph(figure=define_map(sol_geo), selectedData=None,)

selectedBarGraph = dcc.Graph(figure = gen_bar_plot(sol_geo, sol_geo.geo_levels[0], 
                                               "Key Statistics", 'Total Households'),
                            id = 'bar_graph')

# %% ../nbs/02_app_data.ipynb 17
data_grid = gen_dash_grid(sol_geo, 'Ward', "Main source of household income in last 12 months", 'Wages Salary')
