import pandas as pd
import math

def flatten_list(_2d_list):
    flat_list = []
    for element in _2d_list:
        if type(element) is list:
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list

def frequency_df(x, variter):
    """
    The function is specifically designed for pandas DataFrame.
    variter: a string variable name, e.g. 'var1'
    x: corresponding pandas column of variter: pd.DataFrame(variter)
    """
    ctabs = {}
    ctabs[variter] = pd.crosstab(index = x, columns = "count")
    freq_output = pd.DataFrame(list(ctabs.items())[0][1])
    freq_output['var'] = freq_output.index
    freq_output.columns = ['count', 'var']
    freq_output = freq_output.sort_values(by = 'var', ascending = False)
    return freq_output

def special_value_list(special_val_df, variter):
    """
    The function needs specific input format as:
    variter: a string variable name, e.g. 'var1'
    special_val_df: a N*2 dim pandas dataframe, and the column names are ['var', 'special'];column 'special' cell value will be a list, e.g. [0,1]
    """
    if special_val_df[special_val_df['var'] == variter].shape[0] > 0 :
        return list(special_val_df[special_val_df['var'] == variter]['special'])[0]
    else:
        return []
  
def append_psi_cell(variter = ''
                   , psi_sig_pct = 0.001
                   , cutoff_df = pd.DataFrame()
                   , df_new = pd.DataFrame()):
    """
    The function needs specific input format as:
    variter: a string variable name, e.g. 'var1'
    psi_sig_pct: a float value, e.g. 0.001, indicating a threshold that if a psi_bin population's ratio is less than psi_sig, then 0 is assigned as psi for this bin.
    cutoff_df: the input cutoff_df is with specific format, and must be an output of previous iteration of this function; in which the columns are: var, type, sign, cutoff, varBin, obs, obsPct, test_obs, test_pct, psi_bin.
    df_new: a pandas dataframe which has the desired variter, and will be calcualted PSI based on cutoff_df
    """
    new_obs = []
    new_npct = []
    psi_list = []
    new_copy_df = pd.DataFrame({variter: list(df_new[variter])})
    tmp_cut = cutoff_df[cutoff_df['var'] == variter]
    n_new = new_copy_df.shape[0]
    
    for varbin in range(tmp_cut.shape[0]):
        if list(tmp_cut.type)[varbin] == 'Missing':
            new_copy_df = new_copy_df.dropna()
            new_copy_df = pd.DataFrame([x for x in list(new_copy_df[variter]) if len(str(x).replace(" ", "")) > 0  ], columns = [variter])
            n_new_missing = n_new - new_copy_df.shape[0]
            pct_new_missing = n_new_missing*1.0/n_new
            new_obs += [n_new_missing]
            new_npct += [pct_new_missing]
        
        elif (list(tmp_cut.type)[varbin] == 'Special') | (list(tmp_cut.type)[varbin] == 'fixed'):
            fixed_iter = list(tmp_cut.cutoff)[varbin]
            n_new_fixed = new_copy_df.loc[new_copy_df[variter] == float(fixed_iter)].shape[0]
            pct_new_fixed = n_new_fixed*1.0/n_new
            new_copy_df = new_copy_df[new_copy_df[variter] != float(fixed_iter)]
            new_obs += [n_new_fixed]
            new_npct += [pct_new_fixed]
        
        elif (list(tmp_cut.type)[varbin] == 'cont') & (list(tmp_cut.sign)[varbin] == '>='):
            cutoff_iter = list(tmp_cut.cutoff)[varbin]
            n_new_cont = new_copy_df.loc[new_copy_df[variter] >= float(cutoff_iter)].shape[0]
            pct_new_cont = n_new_cont*1.0/n_new
            new_copy_df = new_copy_df[new_copy_df[variter] < float(cutoff_iter)]
            new_obs += [n_new_cont]
            new_npct += [pct_new_cont]
        else:
            n_new_cont = new_copy_df.shape[0]
            pct_new_cont = n_new_cont*1.0/n_new
            new_obs += [n_new_cont]
            new_npct += [pct_new_cont]
        
        # PSI Calc
        if max(tmp_cut.iloc[varbin, 6], new_npct[-1]) < psi_sig_pct:
            psi_list += [float(0.00)]
        elif min(new_npct[-1], tmp_cut.iloc[varbin, 6]) == 0:
            psi_list += [float(1.00)]  
        elif new_npct[-1] == tmp_cut.iloc[varbin, 6]:
            psi_list += [float(0.00)]
        else:
            psi_list += [(new_npct[-1] - tmp_cut.iloc[varbin,6]) * (math.log(new_npct[-1]/tmp_cut.iloc[varbin,6]))]
    
    return [new_obs, new_npct, psi_list]

def orig_bin_cut(variter
                , Special_values
                , tile_pct
                , round_digit
                , fixed_pct
                , dflist):
    """
    The function needs specific input format as:
    variter: a string variable name, e.g. 'var1'
    Special_values: a list with special values for variter, e.g [9998, 9999]
    round_digit: an integer which indicates that how many digits will be rounded for given variter
    fixed_pct: a percentage, which indicates the minimum bin size to define a fixed value
    dflist: the original (base population for PSI calculation) data list for variter.
    """
    
    cutoff_df = pd.DataFrame(columns = ['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct'])
    bin_no = 1
    orig_copy_df = pd.DataFrame({variter: dflist})
    n_orig = orig_copy_df.shape[0]
    fixed_val_obs = int(n_orig*fixed_pct)
    tile_size = int(n_orig*tile_pct)
    if round_digit > 0:
        orig_copy_df[variter] = orig_copy_df[variter].apply(lambda x: round(x, round_digit))
    
    # missing value removal
    orig_copy_df = orig_copy_df.dropna()
    orig_copy_df = pd.DataFrame([x for x in list(orig_copy_df[variter]) if len(str(x).replace(" ", "")) > 0  ], columns = [variter])
    n_orig_missing = n_orig - orig_copy_df.shape[0]
    pct_orig_missing = n_orig_missing*1.0/n_orig
    cutoff_df = pd.concat([cutoff_df,pd.DataFrame([[variter, 'Missing', '=', str(-9999999), bin_no, n_orig_missing, pct_orig_missing]], columns = ['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct'])])
    bin_no += 1
    orig_copy_df = orig_copy_df.reset_index(drop = True)

    #Special Value removal
    if len(Special_values) > 0 :
        for special_iter in Special_values:
            orig_nobs = orig_copy_df[orig_copy_df[variter] == special_iter].shape[0]
            pct_orig_special = orig_nobs*1.0/n_orig
            cutoff_df = pd.concat([cutoff_df,pd.DataFrame([[variter, 'Special', '=', str(special_iter), bin_no, orig_nobs, pct_orig_special]], columns = ['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct'])])
            bin_no += 1
            orig_copy_df = orig_copy_df[orig_copy_df[variter] != special_iter]
            orig_copy_df = orig_copy_df.reset_index(drop = True)
  
    #Fixed Value removal
    fix_val_list = frequency_df(orig_copy_df[variter], variter)
    fixedval = fix_val_list[fix_val_list['count'] >= fixed_val_obs]
    if fixedval.shape[0] > 0 :
        for fixed_iter in list(fixedval['var']):
            orig_nobs = fixedval.loc[fixedval['var'] == fixed_iter, 'count'].values[0]
            p_orig_fixed = orig_nobs*1.0/n_orig
            cutoff_df = pd.concat([cutoff_df,pd.DataFrame([[variter, 'fixed', '=', str(fixed_iter), bin_no, orig_nobs, p_orig_fixed]], columns = ['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct'])])
            bin_no += 1
            orig_copy_df = orig_copy_df[orig_copy_df[variter] != fixed_iter]
            orig_copy_df = orig_copy_df.reset_index(drop = True)
    
    #cont bin
    if orig_copy_df.shape[0] > tile_size:
        cont_list = frequency_df(orig_copy_df[variter], variter)
        n_tile = int(orig_copy_df.shape[0]/tile_size)
        quartiles = pd.qcut(orig_copy_df[variter].rank(method = 'first'), n_tile, range(1, n_tile + 1))
        orig_copy_df['tileno'] = quartiles.values
        agg_check = orig_copy_df.groupby('tileno').agg({variter: ['min']}).reset_index()
        agg_check.columns = ['tileno', 'min']
        agg_check = agg_check.sort_values(by = 'tileno', ascending = False)
        agg_check_uniq = sorted(list(set(agg_check['min'])), reverse = True)
        
        for cont_iter in range(len(agg_check_uniq)):
            orig_nobs = orig_copy_df.loc[orig_copy_df[variter] >= agg_check_uniq[cont_iter]].shape[0]
            p_orig_obs = orig_nobs*1.0/n_orig
            bin_no += 1
            
            if len(agg_check_uniq) == 1:
                cutoff_df = pd.concat([cutoff_df,pd.DataFrame([[variter, 'cont_min', '>=', str(agg_check_uniq[cont_iter]), bin_no, orig_nobs, p_orig_obs]], columns = ['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct'])])
                orig_copy_df = orig_copy_df[orig_copy_df[variter] < agg_check_uniq[cont_iter]]
                orig_copy_df = orig_copy_df.reset_index(drop = True)
            else:
                if agg_check_uniq[cont_iter] != agg_check_uniq[-1]:
                    cutoff_df = pd.concat([cutoff_df,pd.DataFrame([[variter, 'cont', '>=', str(agg_check_uniq[cont_iter]), bin_no, orig_nobs, p_orig_obs]], columns = ['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct'])])
                    orig_copy_df = orig_copy_df[orig_copy_df[variter] < agg_check_uniq[cont_iter]]
                    orig_copy_df = orig_copy_df.reset_index(drop = True)
                else:
                    break

    if orig_copy_df.shape[0] > 0 :
        cutoff_df = pd.concat([cutoff_df,pd.DataFrame([[variter, 'cont', 'ELSE', str(999999999), bin_no, orig_copy_df.shape[0], (orig_copy_df.shape[0]*1.0)/n_orig]], columns = ['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct'])])
      
    return cutoff_df  
      
      
   
def PSI_Calc(feature_list = []
             , tile_pct = 0.1
             , round_digit = 9
             , data_cutdf_path = ''
             , fixed_pct = 0.05
             , psi_sig_pct = 0.001
             , userdir = ''
             , prefix = 'PSI_file'
             , special_value_df = pd.DataFrame(columns = ['var', 'special'])
             , df_orig = pd.DataFrame()
             , df_new = pd.DataFrame()
             ):
    """
    The function needs specific input format as:
    feature_list: a list of string based variable names for PSI calculation, e.g. ['var1', 'var2', 'var3']
    tile_pct: the desired population for each bin
    round_digit: an integer which indicates that how many digits will be rounded for given variter
    data_cutdf_path: the csv path for pre-created cutoff dataframe. If it is a brand new PSI calculation for origdata and new data, define an empty string.
    fixed_pct: a percentage, which indicates the minimum bin size to define a fixed value
    psi_sig_pct: a float value, e.g. 0.001, indicating a threshold that if a psi_bin population's ratio is less than psi_sig, then 0 is assigned as psi for this bin.
    userdir: a string indicated where the output file will be saved.
    prefix: a string used as prefix for final outputs;
    special_value_df: a N*2 dim pandas dataframe, and the column names are ['var', 'special'];column 'special' cell value will be a list, e.g. [0,1]
    df_orig: the pandas dataframe which will be used as base population for PSI
    df_new:  the pandas dataframe which will be used as test population to calculate PSI on top of df_orig
    """
    
    if len(data_cutdf_path) > 0 :
        cutoff_df = pd.read_csv(data_cutdf_path)
        cutoff_df = cutoff_df[['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct']]
    else:
        orig_cutoff_pack = list(map(lambda x: orig_bin_cut(x, special_value_list(special_value_df, x), tile_pct, round_digit, fixed_pct, list(df_orig[x])),feature_list))
        cutoff_df = pd.concat(orig_cutoff_pack)
    
    values_pack = list(map(lambda x: append_psi_cell(x, psi_sig_pct, cutoff_df, df_new), feature_list))
    val_nobs = flatten_list([x[0] for x in values_pack])
    val_pct = flatten_list([x[1] for x in values_pack])
    val_psi = flatten_list([x[2] for x in values_pack])
    
    if len(data_cutdf_path) > 0 :
        sub_cutoff = cutoff_df
    else:
        sub_cutoff = cutoff_df[cutoff_df['var'].isin(feature_list)]
    
    sub_cutoff = sub_cutoff.reset_index(drop = True)
    sub_cutoff['newobs'] = val_nobs
    sub_cutoff['newpct'] = val_pct
    sub_cutoff['psi_bin'] = val_psi 
    psi_df = sub_cutoff.groupby('var').agg({'psi_bin':['sum']}).reset_index()
    psi_df.columns = ['var', 'PSI']
    psi_df['rounded_4digit_PSI'] = psi_df['PSI'].apply(lambda x: round(x, 4))
    
    psi_df.to_csv(userdir + prefix+'_PSIvalue_df.csv', header = True, index = False)
    sub_cutoff.to_csv(userdir + prefix+'_detailedCut_df.csv', header = True, index = False)  
  
