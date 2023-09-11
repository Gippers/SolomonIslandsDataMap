# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_load_data.ipynb.

# %% auto 0
__all__ = ['SolomonGeo']

# %% ../nbs/00_load_data.ipynb 2
from nbdev.showdoc import *
import geopandas as gpd
import pandas as pd
from git import Repo
import json

# %% ../nbs/00_load_data.ipynb 5
class SolomonGeo:
    # TODO work out how to format the attributes
    # Look at nbdev docs maybe?
    # TODO change all data to int?
    '''
    Load the solomon islands geography data 
    Attributes:
        adm3    Geopandas dataframe containing admin 3 geographies.
    '''
    def __init__(self):
        self.adm3 = self.elt('ward', '2009')
        #self.adm3 = self.elt('constituency', '2009')

    def elt(self, 
            aggregation:str, # Inicates the aggregation of the data
            year:str, # The year of that data, only relevant for census data
           )-> gpd.GeoDataFrame: # The geojason dataset for given aggregation
        '''
        Load and transform given filepath into a geojason geopandas dataframe
        '''
        repo = Repo('.', search_parent_directories=True)
        pw = str(repo.working_tree_dir) + "/testData/"
        
        geo = self.load_geo(pw + 'sol_geo_' + aggregation + '.json')
        df = self.load_census(pw + 'sol_census_' + aggregation + '_' + year + '.csv')
        # Add a column that indicates level of aggregation
        geo['agg'] = aggregation
        adm3 = geo.merge(df, on=['id', 'geo_name']).set_index("geo_name")
        return adm3

    def load_geo(self, pw:str, # The pathway to the dataset
           )-> gpd.GeoDataFrame: # The geojason dataset for given aggregation
        '''
        Load and transform given filepath into a geojason geopandas dataframe
        '''
        geo = gpd.read_file(pw)
        # Rename columns and keep only necessary ones.
        # Note that id can be province id, contsituency id etc.
        geo.columns = geo.columns.str.replace(r'^[a-zA-Z]+name$', 'geo_name', case = False, regex = True)
        geo.rename(columns = {geo.columns[0]:'id'}, inplace=True)
        geo = geo[['id', 'geo_name', 'geometry']]
        return geo

    def load_census(self, pw:str, # Pathway of the dataset
           )-> pd.DataFrame: # A pandas dataframe
        '''
        Load and transform data from filepath into pandas dataset
        '''
        df = pd.read_csv(pw)
        # Remove any missing 
        df = df.dropna()
        # Rename columns to be consistent across geography
        df.columns = df.columns.str.replace(r'^[a-zA-Z]+_name$', 'geo_name', case = False, regex = True)
        df['id'] = df['id'].astype(int).astype(str)  # Change type of id
        return df


    def get_geojson(self,
                   ) -> dict: # Geo JSON formatted dataset
        '''
        A getter method for the GeoDataFrame that returns a Geo JSON
        '''
        return json.loads(self.adm3.to_json())

