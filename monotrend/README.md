
### MonoTrend Bin Calculation
#### Pre defined user variables 
feature_list = ['var1', 'var2', 'var3']:\
The variable list of which to calculate PSI

                           ,    metrics_name = 'woe'
                           ,    resp_var = ''
                           ,    wt_var = ''
                           ,    userdir = ''
                           ,    prefix = 'Prefix'
                           ,    special_value_df = pd.DataFrame(columns = ['var', 'special'])
                           ,    df_input = pd.DataFrame()
                           
                           
wtd_tile_pct = 0.1:\
The desired weighted population proportion for each bin;

metrics_name: metrics_name = 'woe' either 'woe' or 'bin_resppct':\
Please note that, either metrics is calculated based on weighted population.

resp_var: resp_var = 'dep_var'\
The string based Binary Response Variable Name.

wt_var = 'a_weight_var_name':\
A weight variable name in dataframe indicating weight column

userdir = '':\
A string path to define where output will be created, e.g. 'C:/'

prefix = 'MonoTrend_file':\
The string prefix for output files

special_value_df = pd.DataFrame(columns = ['var', 'special']): \
The special pandas dataframe indicating special values.

df_input:\
The input pandasdataframe

Monotonic_Bin_creation(feature_list = ['var1', 'var2', 'var3']\
             , wtd_tile_pct = 0.1\
             , metrics_name = 'bin_resppct' \
             , resp_var = 'dep_var' \
             , wt_var = 'weights' \
             , userdir = 'C:/'\
             , prefix = 'MonoTrend_prefix'\
             , special_value_df = pd.DataFrame({'var': ['var1', 'var2'], 'special': [[0],[-1,0]]})\
             , df_input = a_original_pandas_dataframe \
             )
             
#### Outputs          
1. The detailed cutoff dataframe indicating a monotonic trending for given metrics: prefix + '_monodetail_df.csv'\
2. The general trend Value dataframe: prefix + '_monoTrend_df.csv' ('Increasing', 'Decreasing', or 'Flat')                       

 
