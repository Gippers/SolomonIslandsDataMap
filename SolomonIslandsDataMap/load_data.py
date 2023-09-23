# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_load_data.ipynb.

# %% auto 0
__all__ = ['SolomonGeo']

# %% ../nbs/00_load_data.ipynb 3
from nbdev.showdoc import *
import geopandas as gpd
import pandas as pd
from git import Repo
import json
from fastcore import *
from fastcore.basics import patch
from fastcore.test import *
import sys
import topojson as tp
import pickle

# %% ../nbs/00_load_data.ipynb 6
class SolomonGeo:
    # TODO work out how to format the attributes
    # Look at nbdev docs maybe?
    # TODO change all data to int?
    # TODO - should I make this a dataclass for the auto functionaliy? potentially should try it out
    '''
    Load the solomon islands geography data 
    Attributes:
        geo_df    Geopandas dataframe containing geographies and census data
    '''
    def __init__(self, 
                geo_df:gpd.GeoDataFrame): # A geopandas dataset containing population and geography boundaries for each aggregation
        self.geo_df = geo_df

    @classmethod
    def read_test(cls,
                 ): # A solmon geo class TODO work out how to return self here... (can't?)
        '''
        Initialise the object using the local testing data
        '''
        # TODO might need to further abstract this concatenation process
        df, geo = cls.extract_from_file('ward', '2009')
        gdf_ward = cls.transform('ward', '2009', df, geo)
        
        df, geo = cls.extract_from_file('constituency', '2009')
        gdf_const = cls.transform('constituency', '2009', df, geo)

        df, geo = cls.extract_from_file('province', '2009')
        gdf_prov = cls.transform('province', '2009', df, geo)
        
        # Append the datasets together
        geo_df = pd.concat([gdf_ward, gdf_const, gdf_prov])

        # simplify the geography, use topo to preserver the topology between shapes
        topo = tp.Topology(geo_df, prequantize=False)
        geo_df = topo.toposimplify(360/43200).to_gdf()


        return cls(
            geo_df = geo_df
        )

    @classmethod
    def extract_from_file(cls, 
                            aggregation:str, # Indicates the aggregation of the data
                            year:str, # The year of that data, only relevant for census data
                 ) -> (pd.DataFrame, 
                      gpd.GeoDataFrame): # Returns input pandas and geopandas datasets
        '''
        Extract and return input datasets from file
        '''
        repo = Repo('.', search_parent_directories=True)
        pw = str(repo.working_tree_dir) + "/testData/"
        return (
            pd.read_csv(pw + 'sol_census_' + aggregation + '_' + year + '.csv'), 
            gpd.read_file(pw + 'sol_geo_' + aggregation + '.json')
        )

    @classmethod
    def transform(cls, 
            aggregation:str, # Inicates the aggregation of the data
            year:str, # The year of that data, only relevant for census data
            df:pd.DataFrame, # Uncleaned input census dataset
            geo:gpd.GeoDataFrame, # Uncleaned input geospatial dataset
           )-> gpd.GeoDataFrame: # The geopandas dataset for given aggregation
        '''
        Tranform given raw input dataset into a cleaned and combined geopandas dataframe
        '''
        # Clean the geospatial dataframe
        # Rename columns and keep only necessary ones, Note that id can be province id, contsituency id etc.
        geo.columns = geo.columns.str.replace(r'^[a-zA-Z]+name$', 'geo_name', case = False, regex = True)
        # TODO this assume the key column is the first one (which so far it is...)
        geo.rename(columns = {geo.columns[0]:'id'}, inplace=True)
        # Dropping geo_name from the geography dataset and relying on census data naming
        geo = geo.loc[:, ['id', 'geometry']] 
        
        # Add a column that indicates level of aggregation and one for the year
        geo.loc[:, 'agg'] = aggregation
        geo.loc[:, 'year'] = year
        
        # Clean the census data
        df = df.dropna()
        # Rename columns to be consistent across geography
        df.columns = df.columns.str.replace(r'^[a-zA-Z]+_name$', 'geo_name', case = False, regex = True)
        # id needs to change types twice so that it is a string of an int
        df = df.astype({'id': 'int', 'male_pop':'int', 	'female_pop':'int', 'total_pop':'int'})
        df = df.astype({'id': 'str'})
        
        # Merge the data together
        geo_df = geo.merge(df, on=['id']).set_index("geo_name") # , 'geo_name'
        return geo_df

    @classmethod
    def load_pickle(cls,
                    folder:str, #file path of the folder to save in
                    file_name:str = 'sol_geo.pickle' # file name of the saved class
                 ):
        '''
        Initialise the object from a saved filepath
        '''
        # TODO work out how to make this a class method
        repo = Repo('.', search_parent_directories=True)
        pw = str(repo.working_tree_dir) + folder + file_name
        
        with open(pw, 'rb') as f:
            tmp_geo = pickle.load(f)

        # TODO  guide said do below line, don't think relevant though
        #cls.__dict__.update(tmp_dict) 
        
        return cls(
            geo_df = gpd.GeoDataFrame(tmp_geo['geo_df'])
        )
        

# %% ../nbs/00_load_data.ipynb 11
@patch
def save_pickle(self:SolomonGeo,
              folder:str, #file path of the folder to save in
                file_name:str = 'sol_geo.pickle' # file name of the saved class
             ):
    '''
    Save a pickle of the SolomonGeo class
    '''
    repo = Repo('.', search_parent_directories=True)
    pw = str(repo.working_tree_dir) + folder + file_name
    
    f = open(pw, 'wb')
    pickle.dump(self.__dict__, f, 2)
    f.close()

    # For now I will also save the goegraphy in an assets folder
    # TODO update this process in future - may need to save elsewhere
    # TODO I think I need to save in multiple spots
    pw_asset = str(repo.working_tree_dir) + "/assets/sol_geo.json"
    with open(pw_asset, 'w') as f:
        json.dump(self.get_geojson(), f)


# %% ../nbs/00_load_data.ipynb 15
@patch
def get_geojson(self:SolomonGeo, 
                agg_filter:str = None, # Filters the geojson to the requested aggregation 
               ) -> dict: # Geo JSON formatted dataset
    '''
    A getter method for the SolomonGeo class that returns a Geo JSON formatted dataset
    '''
    ret = self.geo_df
    if agg_filter is not None:
        ret = ret.loc[ret['agg'] == agg_filter, :]
    # Return only the core data to minimise the html size
    return json.loads(ret.loc[:, ['geometry']].to_json())

# %% ../nbs/00_load_data.ipynb 17
@patch
def get_df(self:SolomonGeo, 
                agg_filter:str = None, # Filters the dataframe to the requested aggregation 
               ) -> pd.DataFrame: # Pandas Dataframe containing population data
    '''
    A getter method for the SolomonGeo class that returns a pandas dataset containg
    the id variable and the total population variable. This is the minimal data required
    to display on the map. 
    '''
    ret = self.geo_df
    # TODO check that filter is valid
    if agg_filter is not None:
        ret = ret.loc[ret['agg'] == agg_filter, :]
    # Return only the core data to minimise the html size
    return pd.DataFrame(ret.loc[:, ['total_pop']])
