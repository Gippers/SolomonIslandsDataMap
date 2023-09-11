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
    # TODO work out how to format this?
    # Look at nbdev docs maybe?
    '''
    Load the solomon islands geography data 
    Attributes:
        adm3    Geopandas dataframe containing admin 3 geographies.
    '''
    def __init__(self):
        self.adm3 = self.elt('ward', '2009')

    def elt(self, 
            aggregation:str, # Inicates the aggregation of the data
            year:str, # The year of that data, only relevant for census data
           )-> gpd.GeoDataFrame: # The geojason dataset for given aggregation
        '''
        Load and transform given filepath into a geejason geopandas dataframe
        '''
        repo = Repo('.', search_parent_directories=True)
        pw = str(repo.working_tree_dir) + "/testData/"
        
        geo = self.load_geo(pw + 'geo_' + aggregation + '.json')
        df = self.load_census(pw + 'census_' + aggregation + '_' + year + '.csv')
        adm3 = geo.merge(df, on="WID").set_index("ward_name")
        return adm3

    def load_geo(self, pw:str, # The pathway to the dataset
           )-> gpd.GeoDataFrame: # The geojason dataset for given aggregation
        '''
        Load and transform given filepath into a geejason geopandas dataframe
        '''
        geo = gpd.read_file(pw)
        #geo = adm3.set_index(adm3["WID"].values)
        return geo

    def load_census(self, pw:str, # Pathway of the dataset
           )-> pd.DataFrame: # A pandas dataframe
        '''
        Load and transform data from filepath into pandas dataset
        '''
        df = pd.read_csv(pw)
        df['id'] = df['id'].apply(str)  # Change type of id
        df = df.rename(columns = {'id':'WID'})
        return df


    def get_geojson(self,
                   ) -> dict: # Geo JSON formatted dataset
        '''
        A getter method for the GeoDataFrame that returns a Geo JSON
        '''
        return json.loads(self.adm3.to_json())

