# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_load_data.ipynb.

# %% auto 0
__all__ = ['s3_client', 'SolomonGeo']

# %% ../nbs/00_load_data.ipynb 3
from nbdev.showdoc import *
import geopandas as gpd
import pandas as pd
import numpy as np
from git import Repo
import json
from fastcore import *
from fastcore.basics import patch
from fastcore.test import *
import sys
import topojson as tp
import pickle
from urllib.request import urlopen
import boto3
from dotenv import load_dotenv
from dash import dcc
import os
import copy


load_dotenv()

# %% ../nbs/00_load_data.ipynb 10
def s3_client()-> boto3.client:
    '''Return a connection to teh AWS s3 client'''
    ACCESS_KEY = os.getenv("ACCESS_KEY")
    SECRET_ACCCESS_KEY = os.getenv("SECRET_ACCESS_KEY")
    REGION_NAME = os.getenv("REGION_NAME")
    if len(ACCESS_KEY) == 0:
        # If not in .env, then use environment variables
        ACCESS_KEY = os.environ["ACCESS_KEY"]
        SECRET_ACCCESS_KEY = os.environ["SECRET_ACCESS_KEY"]
        REGION_NAME = os.environ["REGION_NAME"]
    session = boto3.Session(region_name='ap-southeast-2')
    # Creating the low level functional client
    return session.client(
        's3',
        endpoint_url='https://s3.ap-southeast-2.amazonaws.com',
        aws_access_key_id = ACCESS_KEY,
        aws_secret_access_key = SECRET_ACCCESS_KEY,
        region_name = REGION_NAME,
    )

# %% ../nbs/00_load_data.ipynb 12
class SolomonGeo:
    # TODO work out how to format the attributes
    # Look at nbdev docs maybe?
    # TODO change all data to int?
    # TODO - should I make this a dataclass for the auto functionaliy? potentially should try it out
    '''
    Load the solomon islands geography data 
    Attributes:
        cen_df    Geopandas dataframe containing geographies and census data
        geo_levels    A list of the types of available aggregations
        census_vars    A dictionary of census variables in the dataset 
        data_type   Specifies whether the variable is a percentage or number
        locations A dictionary of locations accessed by the geography level
    '''
    def __init__(self, 
                cen_df:pd.DataFrame, # A dataset containing the census data,
                pop_df:pd.DataFrame, # A dataset contain the population projection data
                geos:gpd.GeoDataFrame, # A geodataframe containing geographies of data
    ):
        self.census = cen_df
        self.population = pop_df
        self.geo = geos

        # variable that tracks the types of aggregations
        self.geo_levels = cen_df.loc[:, ('core', 'agg')].unique()

        # Save a list of census variables, ignoring the core variables
        # Use a dictionary that maps the upper level column names to lower level ones
        var_df = cen_df.drop(columns = "core", level=0)
        vars = {}
        for col in var_df.columns:
            if col[0] not in vars:
                vars[col[0]] = [col[1]]
            else:
                vars[col[0]].append(col[1])
        self.census_vars = vars

        # Save a list of population variables, ignoring the core variables
        # Use a dictionary that maps the upper level column names to lower level ones
        var_df = pop_df.drop(columns = ["core", "Age"], level=0)
        vars = {}
        for col in var_df.columns:
            if col[0] not in vars:
                vars[col[0]] = [col[1]]
            else:
                vars[col[0]].append(col[1])
        self.population_vars = vars
        # Seperately save the age groupings
        self.ages = list(np.unique(pop_df['Age']['Age_Bracket'].values))
        self.pop_years = list(np.unique(pop_df['core']['year'].values))

        # TODO should captialise first letter
        self.data_type = cen_df.loc[:, ('core', 'type')].unique()

        # save a list of locations as a dictionary access by geography level
        locations = {}
        for geo in self.geo_levels:
            locations[geo] = cen_df.loc[cen_df['core']['agg'] == geo, ('core', 'location')].unique()
        self.locations = locations
    
        # TODO: need a list of column sub headings: get from column name split by `:`

        self.type_default = 'Total'


    @classmethod
    def read_test(cls,
                 ): # A solmon geo class TODO work out how to return self here... (can't?)
        '''
        Contsructor that initialises the object from files using the local testing data
        '''

        repo = Repo('.', search_parent_directories=True)
        pw = str(repo.working_tree_dir) + "/testData/"
        df = pd.read_csv(pw + 'sol_census_all_2009_v2.csv')
        pop = pd.read_csv(pw + 'solo_pop_proj_2009.csv')
        aggs = df.loc[:, 'agg'].unique()
        geos = []
        for agg in aggs:
            geo = gpd.read_file(pw + 'sol_geo_' + agg.lower() + '.json')
            # Add an agg column, as the data and geometry need to be joined by id and agg
            geo.loc[:, 'agg'] = agg
            geos.append(geo)

        ret = cls.__transform(df, pop, geos)
        return cls(
            cen_df = ret[0],
            pop_df = ret[1],
            geos = ret[2],
        )
    
    @classmethod
    def load_pickle(cls,
                    folder:str = "/testData/", #file path of the folder to save in
                    aws:bool = True, # Whether to load from github or local
                    file_name:str = 'sol_geo.pickle' # file name of the saved class
                 ):
        '''
        A constuctor that initialises the object from aws pickle
        '''
        # Create a connection to AWS server
        client = s3_client()

        if aws:
            # Create the S3 object
            obj = client.get_object(
                Bucket = 'hobby-data',
                Key = file_name, 
            )

            # Read in the pickle
            try:
                tmp_geo = pickle.load(obj['Body'])
            except:
                raise ValueError("Issue dowloading pickle file from AWS.")
                
        else:
            # TODO work out how to make this a class method
            repo = Repo('.', search_parent_directories=True)
            pw = str(repo.working_tree_dir) + folder + file_name
            
            with open(pw, 'rb') as f:
                tmp_geo = pickle.load(f)
 
        
        return cls(
            cen_df = gpd.GeoDataFrame(tmp_geo['census']),
            pop_df = gpd.GeoDataFrame(tmp_geo['population']),
            geos = gpd.GeoDataFrame(tmp_geo['geo']),
        )
        
    
    @classmethod
    def gen_stored(cls,
                  json_sol:dict, # A geojson dataset
                 ): # A solmon geo class TODO work out how to return self here... (can't?)
        '''
        A constructor that creates a JSON serialised SolomonGeo object from a stored geopandas dataframe.
        The purpose of this is to allow the object to be stored JSON serialised in a DCC.Store object in 
        the browser before being deserialised and as an object.

        Note that storing and the reloading, will result in dropping the geometry.
        '''
        def df_to_hier(df:pd.DataFrame, # dataframe to convert to hierarchical
                       ) -> pd.DataFrame: # Converted dataframe back to hierachical
            cols = df.columns.str.extract(r'(.*): (.+)', expand=True)
            df.columns = pd.MultiIndex.from_arrays((cols[0], cols[1]))
            df.columns.names = [None]*2
            return df
        
        json_sol = json_sol["data"]

        census = pd.DataFrame(json_sol['census'])
        census = df_to_hier(census)
        # Index is unique by type and geoname
        census = census.set_index(census['core']['location'] + "_" + census['core']["type"] ) 
        census.index.name = 'pk'

        population = pd.DataFrame(json_sol['population'])
        population = df_to_hier(population)
        population.set_index(('core', 'location'), inplace = True)

        geo = gpd.GeoDataFrame(json_sol['geojson'])

        return cls(
            cen_df = census,
            pop_df = population,
            geos = geo,
        )
    
    @classmethod
    def __transform(cls, 
                    df:pd.DataFrame, # The dataframe containing census data
                    pop_df:pd.DataFrame, # The dataset containing the population projection data
                    l_geos:[gpd.GeoDataFrame], # A list of geopandas dataframes containing 
                                                # the geographies 
                 ) -> gpd.GeoDataFrame: # Returns combined dataset
        '''
        Extract and return input datasets from file. Assumes correct format of input dataset, then
        Transform given raw input dataset into a cleaned and combined geopandas dataframe
        '''
        # TODO seperate out the geometry from the data.
        # TODO - make a function that tests that the geo and datasets both join

        geos = gpd.GeoDataFrame()
        for geo in l_geos:
            # Before combining, need to rename like columns
            # Rename columns and keep only necessary ones, Note that id can be province id, contsituency id etc.
            geo.columns = geo.columns.str.replace(r'^[a-zA-Z]+name$', 'geo_name', case = False, regex = True)
            # TODO this assumes the id key column is the first one (which so far it is...)
            geo.rename(columns = {geo.columns[0]:'id'}, inplace=True)

            geo = geo.loc[:, ['id', 'agg', 'geometry']] 

            # simplify the geography, use topo to preserver the topology between shapes
            topo = tp.Topology(geo, prequantize=False)
            geo = topo.toposimplify(720/43200).to_gdf() # old 360/43200

            geos = pd.concat([geos, geo])
            
        # Clean the geospatial dataframe
        geos.loc[:, 'year'] = '2009'
        
        # Clean the census data
        df = df.dropna()
        # Rename columns to be consistent across geography
        df.columns = df.columns.str.replace(r'^[a-zA-Z]+_name$', 'location', case = False, regex = True)
        # id needs to change types twice so that it is a string of an int
        df = df.astype({'id': 'int'})#, 'male_pop':'int', 	'female_pop':'int', 'total_pop':'int'})
        df = df.astype({'id': 'str'})

        pop_df = pop_df.astype({'core: id': 'int'})
        pop_df = pop_df.astype({'core: id': 'str'})

        # Add location names to geography dataset
        locations = copy.copy(df)
        locations = locations.loc[:, ['id', 'agg', 'location']].drop_duplicates()
        geos = geos.merge(locations, on=['id', 'agg'], how = 'left')

        # Index is unique by type and geoname
        df['pk'] = df['location'] + "_" + df["type"] 
        df = df.set_index("pk") 

        # Rename some of the census data
        df = df.rename(columns = {
                                'id':'core: id', 'agg':'core: agg', 'location':'core: location',
                                'year':'core: year', 'type':'core: type'})

        # Test that the datasets all have geographies
        test_geo(df, geos)
        test_geo(pop_df, geos.loc[geos['agg'] == 'Province'])         

        # Convert into a multiindex dataframe, with hiearchical columns
        try:
            cols = df.columns.str.extract(r'(.*): (.+)', expand=True)
            df.columns = pd.MultiIndex.from_arrays((cols[0], cols[1]))
            df.columns.names = [None]*2

            cols2 = pop_df.columns.str.extract(r'(.*): (.+)', expand=True)
            pop_df.columns = pd.MultiIndex.from_arrays((cols2[0], cols2[1])) 
            pop_df.columns.names = [None]*2
        except:
            raise ValueError("Issue converting geopandas dataframe to multindex. \
                             Check that all columns have \': \' beside the following\
                             core columns: geometry, id, agg, year, type.")
        
        # Set index of geography and population data
        geos = geos.set_index(geos.loc[:, 'location']) 
        pop_df.set_index(('core', 'location'), inplace = True)

        # Set all non core and age columns of population to int variables
        # TODO must be a better way to do this
        cols = pop_df.columns.get_level_values(0)
        ignore = ['core', 'Age']
        cols = [c for c in cols if c not in ignore]
        cols = list(set(cols))
        for c1 in cols:
            to_change = pop_df[c1].columns
            for c2 in to_change:
                pop_df[(c1, c2)] = pop_df[(c1, c2)].apply(lambda x: int(x.split()[0].replace(',', '')))

        # Add proportion to the populdation data
        pop_p = copy.copy(pop_df)   
        pop_p.loc[:, ('core', 'type')] = 'Proportion'
        
        for col in cols:
            # For each non core and age column:
            pop_p[col] = pop_p[col] / pop_p[col].sum() * 100
            pop_p.loc[:, (col, 'Total')].sum()
            
        pop_df = pd.concat([pop_df, pop_p], axis = 0)
        
                
        # return the transformed dataset
        return df, pop_df, geos


# %% ../nbs/00_load_data.ipynb 22
@patch
def save_pickle(self:SolomonGeo,
                aws:bool = True, # Whether to save to aws or locally
                folder:str = "/testData/", #file path of the folder to save in, only necesasry for local saving
                file_name:str = 'sol_geo.pickle' # file name of the saved class
             ):
    '''
    Save a pickle of the SolomonGeo class in backblaze b2
    '''
    if aws:
      body_pickle = pickle.dumps(self.__dict__)
      try:
        client = s3_client()
        client.put_object(
            Bucket = 'hobby-data',
            Key = file_name, 
            Body = body_pickle
        )
      except:
         raise ValueError("Issue uploading pickle file to AWS.")
    else:
      repo = Repo('.', search_parent_directories=True)
      pw = str(repo.working_tree_dir) + folder + file_name
      
      f = open(pw, 'wb')
      pickle.dump(self.__dict__, f, 2)
      f.close()


# %% ../nbs/00_load_data.ipynb 25
@patch
def get_geojson(self:SolomonGeo, 
                geo_filter:str = None, # Filters the geojson to the requested aggregation 
               ) -> dict: # Geo JSON formatted dataset
    '''
    A getter method for the SolomonGeo class that returns a Geo JSON formatted dataset
    '''
    ret = self.geo
    # Return only required aggregation if specified
    if geo_filter is not None:
        ret = ret.loc[ret['agg'] == geo_filter, :]
    # Return only the geometry (plus location name in id)
    # to minise file size
    return json.loads(ret.loc[:, 'geometry'].to_json())

# %% ../nbs/00_load_data.ipynb 28
@patch
def get_store(self:SolomonGeo, 
            ) -> dcc.Store: # Geo JSON formatted dataset
    '''
    A getter method that returns a dcc.Store object with the data of the `SolomonGeo` class
    converted to a dictionary for storing with dash. 
    '''
    def hier_to_pandas(df:pd.DataFrame) -> pd.DataFrame:
        cols = df.columns.droplevel(1) + ": " + df.columns.droplevel(0)
        cols = cols.tolist()
        df.columns = cols
        return df

    cen_df = copy.copy(self.census)
    cen_df = hier_to_pandas(cen_df)

    pop_df = copy.copy(self.population)
    pop_df.loc[:, ('core', 'location')] = pop_df.index
    pop_df = hier_to_pandas(pop_df)
    
    geos = copy.copy(self.geo)  
    # Need to drop geometry as it won't serialize
    geos.drop(columns = 'geometry', inplace = True)  

    return dcc.Store(id="geo_df", data={"data": {
                                            "census": cen_df.to_dict("records"),
                                            "population": pop_df.to_dict("records"),
                                            "geojson": geos.to_dict()}})

# %% ../nbs/00_load_data.ipynb 31
@patch
def get_census(self:SolomonGeo, 
                geo_filter:str = None, # Filters the dataframe to the requested geography 
                var:str = None, # Selects an upper level 
                measure:str = None, # Selects the lower level variable, if var 1 is used, measure must be used.
                loc_filter:[str] = None, # Filters one of more locations
                # TODO remove hardcoding here?
                type_filter:str = 'Total', # Return either number of proportion
                agg = False, # Whether to return the dataset aggregated for the given selection
               ) -> pd.DataFrame: # Pandas Dataframe containing population data
    '''
    A getter method for the SolomonGeo class that returns a pandas dataset containg
    the id variable and the requested census data. This is the minimal data required
    to display on the map. 
    - Optionally can aggregate the dataset, uses weighted aggregation for proportional data
    '''
    ret = self.census
    ret = ret.loc[ret['core']['type'] == type_filter, :] 
    ret = ret.set_index(ret.loc[:, ('core', 'location')]) # Change index to location as it's more desriptive
    # TODO check that filter is valid
    if geo_filter is not None:
        try:
            assert(geo_filter in ['Ward', 'Constituency', 'Province'])
        except:
            ValueError("Geo filter must be one of: ['Ward', 'Constituency', 'Province']")
        ret = ret.loc[ret['core']['agg'] == geo_filter, :]

    if loc_filter is not None:
        ret = ret.loc[ret['core']['location'].isin(loc_filter), :]

    # Return no core data to minimise the html size
    ret = ret.drop(columns = 'core', level=0)

    # Keep only selected column if required
    if measure is not None:
        try:
            assert(var is not None)
            assert(measure in self.census_vars[var])
        except:
            ValueError("If measure is set, var 1 must be set and the key value pair of var and measure must match")
        ret = ret[var].filter(items = [measure])
    elif var is not None:
        # Keep all values from upper level column
        ret = ret[var]

    ret = pd.DataFrame(ret)

    # If required, aggregate dataset based on data type
    if agg == True:
        if type_filter == 'Total':
            ret = ret.sum()
        elif type_filter == 'Proportion':
            ret = ret.sum() / ret.sum().sum() * 100
        else:
            raise ValueError('The type passed to the aggregate function must be one of the following: \'Total\', \'Proportion\'.')
    
    return ret

# %% ../nbs/00_load_data.ipynb 34
@patch
def get_pop(self:SolomonGeo, 
                years:[str], # Selects the year/years of data to return
                var:str = None, # Selects an upper level variable
                measure:str = None, # Selects the lower level variable, if var 1 is used, measure must be used.
                loc_filter:[str] = None, # Filters one of more locations
                type_filter:str = 'Total', # Return either number of proportion
                agg = False, # Whether to return the dataset aggregated for the given selection
                agg_location = False, # If true, don't aggregate the population data by location
                agg_ages = False, # If true, don't aggregate the population data by age
                ages:[str] = None, # Filters for one or more Age Brackets, if none returns all
               ) -> pd.DataFrame: # Pandas Dataframe containing population data
    '''
    A getter method for the SolomonGeo class that returns a pandas dataset containg
    the id variable and the requested popultion data. This is the minimal data required
    to display on the map. 
    '''
    geo_filter = 'Province'
    ret = self.population
    ret = ret.loc[ret['core']['type'] == type_filter, :] 
    # TODO check that filter is valid
    if geo_filter is not None:
        try:
            assert(geo_filter in ['Ward', 'Constituency', 'Province'])
        except:
            ValueError("Geo filter must be one of: ['Ward', 'Constituency', 'Province']")
        ret = ret.loc[ret['core']['agg'] == geo_filter, :]

    # Filter to years
    ret = ret.loc[ret['core']['year'].isin(years), :]

    if loc_filter is not None:
        ret = ret.loc[ret.index.isin(loc_filter), :]

    if ages is not None:
        ret = ret.loc[ret['Age']['Age_Bracket'].isin(ages), :]

    # Return no core data to minimise the html size
    age_year = copy.copy(ret)
    age_year = age_year[[('core', 'year'), ('Age', 'Age_Bracket')]]
    # WARNING - don't reorder before the concat below
    ret = ret.drop(columns = ['core', 'Age'], level=0)
    ret = ret.drop(columns = "Numerical_Bracket", level = 1)

    # Keep only selected column if required
    if measure is not None:
        try:
            assert(var is not None)
            assert(measure in self.population_vars[var])
        except:
            ValueError("If measure is set, var 1 must be set and the key value pair of var and measure must match")
        ret = ret[var].filter(items = [measure])
        # Make it multiindex again
        ret.columns = pd.MultiIndex.from_arrays(([var], [measure]))
        
        ret = pd.concat([age_year, ret], axis = 1)
    elif var is not None:
        # Keep all values from upper level column
        ret = ret[var]
        # Make it multiindex again
        measures = self.population_vars[var]
        n_measures = len(measures)
        vars = list(np.repeat(var, n_measures))
        ret.columns = pd.MultiIndex.from_arrays((vars, measures))
        ret = pd.concat([age_year, ret], axis = 1)
    else:
        ret = pd.concat([age_year, ret], axis = 1)
        ret.columns = ret.columns.get_level_values(1)
        # TODO incosistent column naming based on variable, measure or no selection

    ret = pd.DataFrame(ret)

    # Set the group by variables
    group_by = [('core', 'year')]
    if agg_location == True:
        group_by.append(ret.index)
    if agg_ages == True:
        group_by.append(('Age', 'Age_Bracket'))
     # If required, aggregate dataset based on data type
    if agg == True:
        if type_filter == 'Total':
            ret = ret.groupby(group_by, sort = False).sum(numeric_only= True)
        elif type_filter == 'Proportion':
            ret = ret.groupby(group_by, sort = False).sum(numeric_only= True) / ret.groupby(group_by, sort = False).sum(numeric_only= True).sum(numeric_only= True) * 100
        else:
            raise ValueError('The type passed to the aggregate function must be one of the following: \'Total\', \'Proportion\'.')
        
    return ret
