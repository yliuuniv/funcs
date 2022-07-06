import math
import pandas as pd

def is_valid(x):
    return True if len(str(x).replace(" ","")) > 0 else False

def flatten_list_y(_2d_list):
    flat_list = []
    for element in _2d_list:
        if type(element) is list:
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list

def frequency_df_y(x, wt_list, variter):
    """
    The function is specifically designed for pandas DataFrame.
    variter: a string variable name, e.g. 'var1'
    x: corresponding pandas column of variter: pd.DataFrame(variter)
    """
    ctabs = pd.DataFrame({'var':x})
    ctabs['wt'] = wt_list
    
    freq_output = pd.DataFrame(ctabs.groupby('var').agg({'wt':['sum']}))
    freq_output.columns = ['count']
    freq_output = freq_output.rename_axis(index = None)

    freq_output['var'] = freq_output.index
    freq_output = freq_output.sort_values(by = 'var', ascending = False)
    return freq_output

def special_value_list_y(special_val_df, variter):
    """
    The function needs specific input format as:
    variter: a string variable name, e.g. 'var1'
    special_val_df: a N*2 dim pandas dataframe, and the column names are ['var', 'special'];column 'special' cell value will be a list, e.g. [0,1]
    """
    if special_val_df[special_val_df['var'] == variter].shape[0] > 0 :
        return list(special_val_df[special_val_df['var'] == variter]['special'])[0]
    else:
        return []
  
def append_psi_cell_y(variter = ''
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
            
    new_copy_df = df_new[[variter, 'nwt']].copy()
    tmp_cut = cutoff_df[cutoff_df['var'] == variter]
    n_new = new_copy_df['nwt'].sum()
    raw_new_obs = []
    raw_new_npct = []
    raw_n_new = new_copy_df.shape[0]
    
    
    for varbin in range(tmp_cut.shape[0]):
        if list(tmp_cut.type)[varbin] == 'Missing':
            new_copy_df = new_copy_df.dropna()
            
            new_copy_df = new_copy_df[new_copy_df[variter].apply(is_valid)]
            
            n_new_missing = n_new - int(new_copy_df['nwt'].sum())
            pct_new_missing = n_new_missing*1.0/n_new
            
            raw_n_new_missing = raw_n_new - int(new_copy_df.shape[0])
            raw_pct_new_missing = raw_n_new_missing*1.0/raw_n_new
            
            new_obs +=[n_new_missing]
            new_npct += [pct_new_missing]
            
            raw_new_obs += [raw_n_new_missing]
            raw_new_npct += [raw_pct_new_missing]
        
        elif (list(tmp_cut.type)[varbin] == 'Special') | (list(tmp_cut.type)[varbin] == 'fixed'):
            fixed_iter = list(tmp_cut.cutoff)[varbin]
            n_new_fixed = new_copy_df.loc[new_copy_df[variter] == float(fixed_iter)]['nwt'].sum()
            pct_new_fixed = n_new_fixed*1.0/n_new
            
            raw_n_new_fixed = new_copy_df.loc[new_copy_df[variter] == float(fixed_iter)].shape[0]
            raw_pct_new_fixed = raw_n_new_fixed*1.0/raw_n_new
            
            new_copy_df = new_copy_df[new_copy_df[variter] != float(fixed_iter)]
            new_obs += [n_new_fixed]
            new_npct += [pct_new_fixed]
            
            raw_new_obs += [raw_n_new_fixed]
            raw_new_npct += [raw_pct_new_fixed]                
            
        elif (list(tmp_cut.type)[varbin] == 'cont') & (list(tmp_cut.sign)[varbin] == '>='):
            cutoff_iter = list(tmp_cut.cutoff)[varbin]
            n_new_cont = new_copy_df.loc[new_copy_df[variter] >= float(cutoff_iter)]['nwt'].sum()
            pct_new_cont = n_new_cont*1.0/n_new

            raw_n_new_cont = new_copy_df.loc[new_copy_df[variter] >= float(cutoff_iter)].shape[0]
            raw_pct_new_cont = raw_n_new_cont*1.0/raw_n_new

            new_copy_df = new_copy_df[new_copy_df[variter] < float(cutoff_iter)]
            new_obs += [n_new_cont]
            new_npct += [pct_new_cont]
            
            raw_new_obs += [raw_n_new_cont]
            raw_new_npct += [raw_pct_new_cont] 

        else:
            n_new_cont = new_copy_df['nwt'].sum()
            pct_new_cont = n_new_cont*1.0/n_new
            new_obs += [n_new_cont] 
            new_npct += [pct_new_cont]
            
            raw_new_obs += [new_copy_df.shape[0]]
            raw_new_npct += [new_copy_df.shape[0]*1.0/raw_n_new] 
            
        # PSI Calc
        if max(tmp_cut.iloc[varbin, 6], new_npct[-1]) < psi_sig_pct:
            psi_list += [float(0.00)]
        elif min(new_npct[-1], tmp_cut.iloc[varbin, 6]) == 0:
            psi_list += [float(1.00)]  
        elif new_npct[-1] == tmp_cut.iloc[varbin, 6]:
            psi_list += [float(0.00)]
        else:
            psi_list += [(new_npct[-1] - tmp_cut.iloc[varbin,6]) * (math.log(new_npct[-1]/tmp_cut.iloc[varbin,6]))]
    
    # add special case - new datasets have some values which cannot be captured by orig. Say orig has two fixed values only, but new has three;
            
    cutoff_df[['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct', 'raw_obs', 'raw_obsPct']]
    
    if sum(new_obs) == n_new:
        output_list = [tmp_cut['var'].to_list()
                       , tmp_cut['type'].to_list()
                       , tmp_cut['sign'].to_list()
                       , tmp_cut['cutoff'].to_list()
                       , tmp_cut['varBin'].to_list()
                       , tmp_cut['obs'].to_list()                       
                       , tmp_cut['obsPct'].to_list()                       
                       , tmp_cut['raw_obs'].to_list()    
                       , tmp_cut['raw_obsPct'].to_list() 
                       , new_obs, new_npct, psi_list,raw_new_obs,raw_new_npct ]
    else:
        if ((n_new - sum(new_obs))*1.0/n_new) < psi_sig_pct:
            psi_extra = float(0.00)
        else:
            psi_extra = float(1.00)
        
        output_list = [tmp_cut['var'].to_list() + [variter]
                       , tmp_cut['type'].to_list() + ['extraNew']
                       , tmp_cut['sign'].to_list() + ['extraNew']
                       , tmp_cut['cutoff'].to_list() + [999999999]
                       , tmp_cut['varBin'].to_list() + [999999999]
                       , tmp_cut['obs'].to_list() + [float(0.00)]                      
                       , tmp_cut['obsPct'].to_list() + [float(0.00)]                           
                       , tmp_cut['raw_obs'].to_list() + [float(0.00)]        
                       , tmp_cut['raw_obsPct'].to_list() + [float(0.00)]     
                       , new_obs + [(n_new - sum(new_obs))]
                       , new_npct + [(n_new - sum(new_obs))*1.0/n_new]
                       , psi_list +[psi_extra]
                       , raw_new_obs + [(raw_n_new - sum(raw_new_obs))]
                       ,raw_new_npct + [(raw_n_new - sum(raw_new_obs))/raw_n_new] ]        
        

    n_bin_recalc = len(output_list[4])
    output_list[4] = [ (x+1) for x in range(n_bin_recalc)]
    print("Processing "+variter)    
    return output_list


def orig_bin_cut_y(variter
                , Special_values
                , tile_pct
                , round_digit
                , fixed_pct
                , dflist
                , documented_cutoffs
                , wtlist):
    """
    The function needs specific input format as:
    variter: 
        a string variable name, e.g. 'var1'
    Special_values: 
        a list with special values for variter, e.g [9998, 9999]
    round_digit: 
        an integer which indicates that how many digits will be rounded for given variter
    fixed_pct: 
        a percentage, which indicates the minimum bin size to define a fixed value
    dflist: 
        the original (base population for PSI calculation) data list for variter.
    documented_cutoffs:
        the cutoff list found documents
    wtlist:
        the weight list for origin variter
    """
    
    cutoff_df = pd.DataFrame(columns = ['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct', 'raw_obs', 'raw_obsPct'])
    bin_no = 0
    orig_copy_df = pd.DataFrame({variter: dflist})
    orig_copy_df['owt'] = wtlist
    
    n_orig = int(orig_copy_df['owt'].sum())
    raw_n_orig = int(orig_copy_df.shape[0])
    
    fixed_val_obs = int(n_orig*fixed_pct)
    tile_size = int(n_orig*tile_pct)
    if round_digit > 0:
        orig_copy_df[variter] = orig_copy_df[variter].apply(lambda x: round(x, round_digit))
    
    # missing value removal
    orig_copy_df = orig_copy_df.dropna(subset = [variter])
    
    orig_copy_df = orig_copy_df[orig_copy_df[variter].apply(is_valid)]
    
    n_orig_missing = n_orig - int(orig_copy_df['owt'].sum())
    pct_orig_missing = n_orig_missing*1.0/n_orig
    
    raw_n_orig_missing = raw_n_orig - int(orig_copy_df.shape[0])
    raw_pct_orig_missing = raw_n_orig_missing*1.0/raw_n_orig
    
    cutoff_df = pd.concat([cutoff_df,pd.DataFrame([[variter, 'Missing', '=', str(-9999999), bin_no, n_orig_missing, pct_orig_missing,raw_n_orig_missing,raw_pct_orig_missing]]
                                                  , columns = ['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct', 'raw_obs', 'raw_obsPct'])])
    orig_copy_df = orig_copy_df.reset_index(drop = True)

    #Special Value removal
    if len(Special_values) > 0 :
        for special_iter in Special_values:
            orig_nobs = int(orig_copy_df[orig_copy_df[variter] == special_iter]['owt'].sum())               
            pct_orig_special = orig_nobs*1.0/n_orig
            
            raw_orig_nobs = int(orig_copy_df[orig_copy_df[variter] == special_iter].shape[0])               
            raw_pct_orig_special = raw_orig_nobs*1.0/raw_n_orig

            
            cutoff_df = pd.concat([cutoff_df,pd.DataFrame([[variter, 'Special', '=', str(special_iter), bin_no, orig_nobs, pct_orig_special,raw_orig_nobs,raw_pct_orig_special]]
                                                          , columns = ['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct', 'raw_obs', 'raw_obsPct'])])
            orig_copy_df = orig_copy_df[orig_copy_df[variter] != special_iter]
            orig_copy_df = orig_copy_df.reset_index(drop = True)
  
    #Fixed Value removal
            
            
    if len(documented_cutoffs) == 0:
        
        fix_val_list = frequency_df_y(orig_copy_df[variter],orig_copy_df['owt'],variter)
        fixedval = fix_val_list[fix_val_list['count'] >= fixed_val_obs]
        
        if fixedval.shape[0] > 0 :
            for fixed_iter in list(fixedval['var']):
                orig_nobs = fixedval.loc[fixedval['var'] == fixed_iter, 'count'].values[0]
                p_orig_fixed = orig_nobs*1.0/n_orig                    
                
                raw_orig_nobs = fixedval.loc[fixedval['var'] == fixed_iter].shape[0]
                raw_p_orig_fixed = raw_orig_nobs*1.0/raw_n_orig
                
                cutoff_df = pd.concat([cutoff_df,pd.DataFrame([[variter, 'fixed', '=', str(fixed_iter), bin_no, orig_nobs, p_orig_fixed,raw_orig_nobs,raw_p_orig_fixed]]
                                                              , columns = ['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct', 'raw_obs', 'raw_obsPct'])])
                orig_copy_df = orig_copy_df[orig_copy_df[variter] != fixed_iter]
                orig_copy_df = orig_copy_df.reset_index(drop = True)
    
    #cont bin
    if len(documented_cutoffs) == 0 :

        if orig_copy_df['owt'].sum() > tile_size:
            cont_list = frequency_df_y(orig_copy_df[variter], orig_copy_df['owt'],variter)
            cont_list = cont_list.sort_values(by = 'var', ascending = False)
            
            n_tile = int(cont_list['count'].sum()/tile_size)
            remain_iter_max = max(cont_list['var'])
            quartiles = [x*tile_size for x in range(1, n_tile+1)]
            
            cumul = cont_list['count'].cumsum()
            index = [sum(cumul < x) for x in quartiles]
            
            min_values = [cont_list['var'].iloc[x] for x in index ]
            agg_check_uniq = sorted(list(set(min_values)), reverse = True)
            
            for cont_iter in range(len(agg_check_uniq)):
                orig_nobs = orig_copy_df.loc[orig_copy_df[variter] >= agg_check_uniq[cont_iter]]['owt'].sum()
                p_orig_obs = orig_nobs*1.0/n_orig                    
                
                raw_orig_nobs = orig_copy_df.loc[orig_copy_df[variter] >= agg_check_uniq[cont_iter]].shape[0]
                raw_p_orig_obs = raw_orig_nobs*1.0/raw_n_orig
                
                if len(agg_check_uniq) == 1:
                    cutoff_df = pd.concat([cutoff_df,pd.DataFrame([[variter, 'cont_min', '>=', str(agg_check_uniq[cont_iter]), bin_no, orig_nobs, p_orig_obs,raw_orig_nobs,raw_p_orig_obs]]
                                                                  , columns = ['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct', 'raw_obs', 'raw_obsPct'])])
                    orig_copy_df = orig_copy_df[orig_copy_df[variter] < agg_check_uniq[cont_iter]]
                    orig_copy_df = orig_copy_df.reset_index(drop = True)
                else:
                    if agg_check_uniq[cont_iter] != agg_check_uniq[-1]:
                        cutoff_df = pd.concat([cutoff_df,pd.DataFrame([[variter, 'cont', '>=', str(agg_check_uniq[cont_iter]), bin_no, orig_nobs, p_orig_obs,raw_orig_nobs,raw_p_orig_obs]]
                                                                      , columns = ['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct', 'raw_obs', 'raw_obsPct'])])
                        orig_copy_df = orig_copy_df[orig_copy_df[variter] < agg_check_uniq[cont_iter]]
                        orig_copy_df = orig_copy_df.reset_index(drop = True)
                    else:
                        break

        if orig_copy_df['owt'].sum() > 0 :
            cutoff_df = pd.concat([cutoff_df,pd.DataFrame([[variter, 'cont', 'ELSE', str(999999999), bin_no, orig_copy_df['owt'].sum(), (orig_copy_df['owt'].sum()*1.0)/n_orig,orig_copy_df.shape[0], (orig_copy_df.shape[0]*1.0)/raw_n_orig]]
                                                          , columns = ['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct', 'raw_obs', 'raw_obsPct'])])
        
    else:
        no_doc_cutoffs = (len(documented_cutoffs) - 1 )
        for cont_iter in range(no_doc_cutoffs):
            orig_nobs =  orig_copy_df.loc[orig_copy_df[variter] >= documented_cutoffs[cont_iter]]['owt'].sum()
            p_orig_obs =   orig_nobs*1.0/n_orig
            
            raw_orig_nobs =  orig_copy_df.loc[orig_copy_df[variter] >= documented_cutoffs[cont_iter]].shape[0]
            raw_p_orig_obs =   raw_orig_nobs*1.0/raw_n_orig     
            
            cutoff_df = pd.concat([cutoff_df,pd.DataFrame([[variter, 'cont', '>=', str(documented_cutoffs[cont_iter]), bin_no, orig_nobs, p_orig_obs,raw_orig_nobs,raw_p_orig_obs]]
                                                                  , columns = ['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct', 'raw_obs', 'raw_obsPct'])])
            orig_copy_df = orig_copy_df[orig_copy_df[variter] < documented_cutoffs[cont_iter]]
        
        cutoff_df = pd.concat([cutoff_df,pd.DataFrame([[variter, 'cont', 'ELSE', str(999999999), bin_no, orig_copy_df['owt'].sum(), (orig_copy_df['owt'].sum()*1.0)/n_orig,orig_copy_df.shape[0], (orig_copy_df.shape[0]*1.0)/raw_n_orig]]
                                                          , columns = ['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct', 'raw_obs', 'raw_obsPct'])])
    orig_copy_df = orig_copy_df.reset_index(drop = True)    
    orig_copy_df['varBin'] = orig_copy_df.index + 1
        
    
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
             , documented_cutoff_dict = dict()
             , orig_wt = ''
             , new_wt = ''
             ):
    """
    author: yliu
    
    Model Log:
        v 1.0:
            Publish the first version
        v 2.0:
            Add an new input 'documented_cutoff_dict', listing cutoff values for every var
        v 3.0:
            Add weight consideration to PSI, orig_wt, and new_wt
        v 3.1:
            Consider special senario: values found in new data but not in orig data 
            
    Example:
        PSI_Calc(feature_list = []
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
             , documented_cutoff_dict = dict()
             , orig_wt = ''
             , new_wt = ''
             )
              
    Model Inputs:
        feature_list: 
            a list of string based variable names for PSI calculation, e.g. ['var1', 'var2', 'var3']
        tile_pct:
            the desired population for each bin
        round_digit:
            an integer which indicates that how many digits will be rounded for given variter
        data_cutdf_path:
            the csv path for pre-created cutoff dataframe. If it is a brand new PSI calculation for origdata and new data, define an empty string.
        fixed_pct: 
            a percentage, which indicates the minimum bin size to define a fixed value
        psi_sig_pct: 
            a float value, e.g. 0.001, indicating a threshold that if a psi_bin population's ratio is less than psi_sig, then 0 is assigned as psi for this bin.
        userdir: 
            a string indicated where the output file will be saved.
        prefix: 
            a string used as prefix for final outputs;
        special_value_df: 
            a N*2 dim pandas dataframe, and the column names are ['var', 'special'];column 'special' cell value will be a list, e.g. [0,1]
        df_orig: 
            the pandas dataframe which will be used as base population for PSI
        df_new:  
            the pandas dataframe which will be used as test population to calculate PSI on top of df_orig                
        documented_cutoff_dict:
            a dictionary for pre-defined cutoff values, format as : {'var1': [1,2,3], 'var2':[4,5,6]}
        orig_wt:
            a string variable name, for weight variable of original dataset
        new_wt:
            a string variable name, for weight variable of new dataset                
            
    Model Outputs:
        csv file 1: userdir + prefix + '_PSIvalue_df.csv'
        csv file 2: userdir + prefix + '_DetailedCut_df.csv'

            
    """
    print('This is the PSI_Calc func version 3.0')

    if 1 in [len(v) for name, v in documented_cutoff_dict.items()]:
        print("There is only one given cutoff value in documented_cutoff_dict. Please make sure there are at least two bins.")
        return
    
    for variter in feature_list:
        if variter not in documented_cutoff_dict:
            documented_cutoff_dict[variter] = []
    
    
    if len(data_cutdf_path) > 0 :
        cutoff_df = pd.read_csv(data_cutdf_path)
        cutoff_df = cutoff_df[['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct', 'raw_obs', 'raw_obsPct']]
        cutoff_df = cutoff_df[cutoff_df['var'].isin(feature_list)]
   
    else:
        if len(orig_wt) == 0:
            orig_wt = 'iden_wt'
            df_orig[orig_wt] = 1.0            
        orig_cutoff_pack = list(map(lambda x: orig_bin_cut_y(x, special_value_list_y(special_value_df, x), tile_pct, round_digit, (1.0 if len(documented_cutoff_dict[x]) > 0 else fixed_pct), list(df_orig[x]), documented_cutoff_dict[x], list(df_orig[orig_wt])),feature_list))
        cutoff_df = pd.concat(orig_cutoff_pack)

    
    if len(new_wt) == 0:
        df_new['nwt'] = 1.0
    else:
        df_new['nwt'] = df_new[new_wt]
    
    values_pack = list(map(lambda x: append_psi_cell_y(x, psi_sig_pct, cutoff_df, df_new), feature_list))
    sub_cutoff = pd.DataFrame(columns =['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct','newobs', 'newpct', 'psi_bin','raw_obs','raw_obsPct' ,'raw_newobs','raw_newpct' ])

    sub_cutoff['var'] = flatten_list_y([x[0] for x in values_pack])
    sub_cutoff['type'] = flatten_list_y([x[1] for x in values_pack])
    sub_cutoff['sign'] = flatten_list_y([x[2] for x in values_pack])
    sub_cutoff['cutoff'] = flatten_list_y([x[3] for x in values_pack])
    sub_cutoff['varBin'] = flatten_list_y([x[4] for x in values_pack])
    sub_cutoff['obs'] = flatten_list_y([x[5] for x in values_pack])
    sub_cutoff['obsPct'] = flatten_list_y([x[6] for x in values_pack])
    
    sub_cutoff['newobs'] = flatten_list_y([x[9] for x in values_pack])
    sub_cutoff['newpct'] = flatten_list_y([x[10] for x in values_pack])
    
    sub_cutoff['psi_bin'] = flatten_list_y([x[11] for x in values_pack])
    
    sub_cutoff['raw_obs'] = flatten_list_y([x[7] for x in values_pack])
    sub_cutoff['raw_obsPct'] = flatten_list_y([x[8] for x in values_pack])
    
    sub_cutoff['raw_newobs'] = flatten_list_y([x[12] for x in values_pack])
    sub_cutoff['raw_newpct'] = flatten_list_y([x[13] for x in values_pack])    
    

    
    sub_cutoff = sub_cutoff.reset_index(drop = True)

    psi_df = sub_cutoff.groupby('var').agg({'psi_bin':['sum']}).reset_index()
    psi_df.columns = ['var', 'PSI']
    psi_df['rounded_4digit_PSI'] = psi_df['PSI'].apply(lambda x: round(x, 4))
    
    
    sub_cutoff = sub_cutoff[['var', 'type', 'sign', 'cutoff', 'varBin', 'obs', 'obsPct','newobs', 'newpct', 'psi_bin','raw_obs','raw_obsPct' ,'raw_newobs','raw_newpct' ]]
    
    psi_df.to_csv(userdir + prefix+'_PSIvalue_df.csv', header = True, index = False)
    sub_cutoff.to_csv(userdir + prefix+'_detailedCut_df.csv', header = True, index = False)  
    
    
    print('PSI Calculation Finished.')
    # print('Output 1:\n'+userdir + prefix+'_PSIvalue_df.csv')
    # print('Output 2:\n'+userdir + prefix+'_detailedCut_df.csv')