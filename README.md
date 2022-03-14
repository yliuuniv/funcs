# funcs
Functions for data manipulation, processing, and cleaning 

### PSI Calculation
#### Pre defined user variables 

feature_lis = ['var1', 'var2', 'var3']
  The variable list of which to calculate PSI
tile_pct = 0.1
  The desired population proportion for each bin;
round_digit = 9
  The integer of which to round each feature;
fixed_pct = 0.05
  The minimum proportion percentage to decide a fixed value;
psi_sig_pct = 0.001
  If a bin's size proportion is smaller than psi_sig_pct, then assign 0 as PSI to this bin;
userdir = ''
  A string path to define where output will be created, e.g. 'C:/'
prefix = 'PSI_file'
  The string prefix for output files
             , special_value_df = pd.DataFrame(columns = ['var', 'special'])


#### 1. If it is the first time creating PSI for given variables...

PSI_Calc(feature_list = feature_lis
             , tile_pct = 0.1
             , round_digit = 9
             , data_cutdf_path = ''
             , fixed_pct = 0.05
             , psi_sig_pct = 0.001
             , userdir = 'C:/'
             , prefix = 'PSI_firstrun'
             , special_value_df = pd.DataFrame({'var': ['var1', 'var2'], 'special': [[0],[-1,0]]})
             , df_orig = a_original_pandas_dataframe
             , df_new = a_test_pandas+dataframe
             )
             
