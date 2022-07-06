import pandas as pd
import math
import numpy as np

def WOE(bin_goods, bin_bads, total_goods, total_bads):
    import math
    if bin_goods * bin_bads == 0 :
        tmp_woe = 0 
    else:
        tmp_woe = math.log(bin_goods/total_goods) - math.log(bin_bads/total_bads)
    
    return tmp_woe
    

def IV(bin_goods, bin_bads, total_goods, total_bads):
    import math
    if bin_goods * bin_bads == 0 :
        tmp_iv = 0 
    else:
        tmp_woe = math.log(bin_goods/total_goods) - math.log(bin_bads/total_bads)
        tmp_iv = tmp_woe * (bin_goods/total_goods - bin_bads/total_bads)
    return tmp_iv
    
    
def Bin_resprate(bin_goods, bin_bads):
    if bin_goods + bin_bads == 0 :
        return 0.0
    else:
        return bin_bads * 1.0/(bin_bads + bin_goods)
        

def fixed_value_bin(df, variter, wt_var, total_goods, total_bads, x, resp_var):
    n_wt_bin = df[df[variter] == x][wt_var].sum()
    n_abs_bin = df[df[variter] == x].shape[0]
    
    if n_wt_bin == 0 :
        return [x, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    else:
        n_wtresp_bin = df[(df[variter] == x) & (df[resp_var] == 1)][wt_var].sum()
        n_wtnpresp_bin = n_wt_bin - n_wtresp_bin
        n_absresp_bin = df[(df[variter] == x) & (df[resp_var] == 1)].shape[0]
        
        return [x, n_wt_bin, n_wt_bin*1.0/(total_goods + total_bads), n_wtresp_bin, n_wtresp_bin*1.0/(total_bads), n_abs_bin, n_absresp_bin]



def frequency_wtd_df(df, variter, wt_var, resp_var):
    df['wtd_response_calc'] = df[resp_var] * df[wt_var]
    freq_df = df.groupby(variter).agg({wt_var:['sum', 'count'], 'wtd_response_calc':['sum'], resp_var: ['sum']}).reset_index()
    freq_df.columns = ['var', 'wtd_popu', 'abs_obs', 'wtd_binary', 'abs_resp']
    freq_df = freq_df.sort_values(by = 'var', ascending = True)
    return freq_df[['var', 'wtd_popu', 'abs_obs', 'wtd_binary', 'abs_resp']]

def two_split(trend_flag, prev_bin_metrics, curr_bin_metrics, total_goods, total_bads, data_list,metrics_list,bin_info, metrics_name, curr_bin_tmp_index):
    if trend_flag == 'Decreasing':
        sign_str = '>'
    else:
        sign_str = '<'
    
    data_list = data_list.reset_index(drop = True)
    tail_index = data_list[['var', 'wtd_popu']].sort_values(by = 'var', ascending = False)
    tail_index['cumu_tail'] = tail_index['wtd_popu'].cumsum()
    tail_index = list(tail_index[tail_index['cumu_tail'] > curr_bin_metrics].index)[0]
    
    i_begin = (curr_bin_tmp_index + 1)
    if i_begin > tail_index:
        return metrics_list, bin_info, data_list[['var', 'wtd_popu', 'wtd_binary', 'abs_obs', 'abs_resp']], 1
    
    while i_begin <= tail_index:
        expand_bin_popu = data_list.iloc[0:i_begin].wtd_popu.sum()
        expand_bin_resp = data_list.iloc[0:i_begin].wtd_binary.sum()
        expand_bin_nonresp = data_list.iloc[0:i_begin].wtd_nonbinary.sum()
        
        remain_bin_popu = data_list.iloc[i_begin:].wtd_popu.sum()
        remain_bin_resp = data_list.iloc[i_begin:].wtd_binary.sum()
        remain_bin_nonresp = data_list.iloc[i_begin:].wtd_nonbinary.sum()
        
        if metrics_name.lower() == 'woe':
            expand_bin_metrics = WOE(expand_bin_nonresp, expand_bin_resp, total_goods, total_bads)
            remain_bin_metrics = WOE(remain_bin_nonresp, remain_bin_resp, total_goods, total_bads)
        if metrics_name.lower() == 'bin_resppct':
            expand_bin_metrics = (expand_bin_resp/expand_bin_popu)
            remain_bin_metrics = (remain_bin_resp/remain_bin_popu)
             
        if eval(' (prev_bin_metrics' + sign_str + 'expand_bin_metrics ) & ( expand_bin_metrics ' + sign_str + ' remain_bin_metrics )'):
            metrics_list = metrics_list[:-1] + [expand_bin_metrics, remain_bin_metrics]
            bin_info = pd.concat([bin_info, data_list.iloc[[i_begin - 1]]])
            data_list = data_list.iloc[i_begin:]
            return metrics_list, bin_info, data_list[['var', 'wtd_popu', 'wtd_binary', 'abs_obs', 'abs_resp']], 0
        
        i_begin += 1
        
    return metrics_list, bin_info, data_list[['var', 'wtd_popu', 'wtd_binary', 'abs_obs', 'abs_resp']], 1



def mono_analysis_func(data_list, total_goods, total_bads, wtd_tilesize, metrics_name, metrics_list, bin_info, trend_flag):
    
    import pandas as pd
    data_list = data_list.reset_index(drop = True)
    data_list.columns = ['var', 'wtd_popu', 'wtd_binary', 'abs_obs', 'abs_resp']
    total_obs = total_goods + total_bads
    data_list['wtd_nonbinary'] = data_list['wtd_popu'] - data_list['wtd_binary']
    
    # -----------------------
    
    # current bin metrics initiation
    prev_bin_metrics = metrics_list[-2]
    data_list['cumu_wt'] = data_list['wtd_popu'].cumsum()
    data_list['cumu_resp'] = data_list['wtd_binary'].cumsum()
    data_list['cumu_nonresp'] = data_list['wtd_nonbinary'].cumsum()
    data_list['begin_bin'] = data_list.cumu_wt.shift(1)
    data_list.iloc[0,-1] = 0.0
    data_list['cumu_absobs'] = data_list['abs_obs'].cumsum()
    data_list['cumu_absresp'] = data_list['abs_resp'].cumsum()
    
    if (list(data_list['cumu_wt'])[-1] <= wtd_tilesize) | (data_list.shape[0] == 1):
        curr_bin_tmp = data_list
    else:
        curr_bin_tmp = data_list[(data_list['begin_bin'] <= wtd_tilesize) & (data_list['cumu_wt'] >= wtd_tilesize)]

    curr_bin_tmp_index = list(curr_bin_tmp.index)[0]
    rest_all_popudf = data_list[data_list['var'] > list(curr_bin_tmp['var'])[-1]]
    
    # metrics calculation
    if metrics_name.lower() == 'woe':
        curr_bin_metrics = WOE(list(currr_bin_tmp['cumu_nonresp'])[-1], list(currr_bin_tmp['cumu_resp'])[-1], total_goods, total_bads)
        if rest_all_popudf.shape[0] == 0 :
            rest_all_popu_metrics = 0.0
        else:
            rest_all_popu_metrics = WOE(rest_all_popudf['wtd_nonbinary'].sum(), rest_all_popudf['wtd_binary'].sum(), total_goods, total_bads)


    if metrics_name.lower() == 'bin_resppct':
        curr_bin_metrics = (list(currr_bin_tmp['cumu_resp'])[-1]/list(currr_bin_tmp['cumu_wt'])[-1])
        if rest_all_popudf.shape[0] == 0 :
            rest_all_popu_metrics = 0.0
        else:
            rest_all_popu_metrics = (rest_all_popudf['wtd_binary'].sum()/rest_all_popudf['wtd_popu'].sum())

    if trend_flag == 'unknown':
        metrics_list = metrics_list[:-1] + [curr_bin_metrics, rest_all_popu_metrics]
        bin_info = curr_bin_tmp.iloc[[-1]]
        data_list = rest_all_popudf
        return metrics_list, bin_info, data_list[['var', 'wtd_popu', 'wtd_binary', 'abs_obs', 'abs_resp']], 0.0

    else:
        if trend_flag == 'Increasing':
            if (prev_bin_metrics < curr_bin_metrics) & (curr_bin_metrics < rest_all_popu_metrics):
                metrics_list = metrics_list[:-1] + [curr_bin_metrics, rest_all_popu_metrics]
                bin_info = pd.concat([bin_info, curr_bin_tmp.iloc[[-1]]])
                data_list = rest_all_popudf
                return metrics_list, bin_info, data_list[['var', 'wtd_popu', 'wtd_binary', 'abs_obs', 'abs_resp']], 0.0
            else:
                metrics_list, bin_info, data_list, stop_flag = two_split(trend_flag, prev_bin_metrics, curr_bin_metrics, total_goods, total_bads, data_list, metrics_list, bin_info, metrics_name, curr_bin_tmp_index)
                return metrics_list, bin_info, data_list[['var', 'wtd_popu', 'wtd_binary', 'abs_obs', 'abs_resp']], stop_flag

        if trend_flag == 'Descreasing':
            if (prev_bin_metrics > curr_bin_metrics) & (curr_bin_metrics > rest_all_popu_metrics):
                metrics_list = metrics_list[:-1] + [curr_bin_metrics, rest_all_popu_metrics]
                bin_info = pd.concat([bin_info, curr_bin_tmp.iloc[[-1]]])
                data_list = rest_all_popudf
                return metrics_list, bin_info, data_list[['var', 'wtd_popu', 'wtd_binary', 'abs_obs', 'abs_resp']], 0.0
            else:
                metrics_list, bin_info, data_list, stop_flag = two_split(trend_flag, prev_bin_metrics, curr_bin_metrics, total_goods, total_bads, data_list, metrics_list, bin_info, metrics_name, curr_bin_tmp_index)
                return metrics_list, bin_info, data_list[['var', 'wtd_popu', 'wtd_binary', 'abs_obs', 'abs_resp']], stop_flag



def special_value_list(special_val_df, variter):
    """
    Module Log:
       
    Parameters
    ----------
    special_val_df : a N*2 dim pandas dataframe
        Column names are ['var', 'special']
    variter : String.
        String based variable name, e.g. 'var1'.

    Returns
    -------
    list

    """
    if special_val_df[special_val_df['var'] == variter].shape[0] > 0 :
        return list(special_val_df[special_val_df['var'] == variter]['special'])[0]
    else:
        return []
        
        
def single_var_bin(variter, df_input, special_value, resp_var, metrics_name, total_wt_obs, total_wt_resp, total_wt_nonresp, wtd_tilesize, total_abs_obs, total_abs_resp):
    cutoff_df = pd.DataFrame(columns = ['varBin', 'var', 'type', 'sign', 'cutoff', 'wtd_obs', 'wtd_obspct', 'wtd_resp', 'wtd_resppct', 'abs_obs', 'abs_resp'])
    bin_no = 1
    local_copy_df = df_input[[variter, resp_var, 'localwtvar']].copy()
    local_copy_df['wtd_response_calc'] = local_copy_df[resp_var] * local_copy_df['localwtvar']
    
    # missing
    subset_missing = local_copy_df[local_copy_df[variter].isna()]
    
    n_wt_missing = subset_missing['localwtvar'].sum()
    n_abs_missing = subset_missing.shape[0]
    
    n_wtresp_missing = subset_missing['wtd_response_calc'].sum()
    # remove missing
    local_copy_df = local_copy_df[~local_copy_df[variter].isna()]
    n_resp_missing = (total_abs_resp - local_copy_df[resp_var].sum())
    
    cutoff_df = pd.concat([cutoff_df, pd.DataFrame([[str(bin_no), variter, 'Missing', '=', 'Missing', n_wt_missing, float(n_wt_missing/total_wt_obs), n_wtresp_missing, float(n_wtresp_missing/total_wt_resp),n_abs_missing, n_resp_missing]]
                                                   , columns = ['varBin', 'var', 'type', 'sign', 'cutoff', 'wtd_obs', 'wtd_obspct', 'wtd_resp', 'wtd_resppct', 'abs_obs', 'abs_resp'])])
    bin_no += 1
    
    # special values
    # -----------------------------------------------------------------------------------------------------------------
    if len(special_value) > 0 :
        spec_val_list = list(map(lambda x: fixed_value_bin(local_copy_df, variter, 'localwtvar', total_wt_nonresp, total_wt_resp, x, resp_var), special_value))
        spec_val_df = pd.DataFrame(spec_val_list, columns = ['special_value', 'wtd_obs', 'wtd_obspct', 'wtd_resp', 'wtd_resppct', 'abs_obs', 'abs_resp'])
        cutoff_df = pd.concat([cutoff_df
                               ,pd.concat([pd.DataFrame({'varBin': list(range(bin_no, bin_no+spec_val_df.shape[0])), 'var': [variter]*spec_val_df.shape[0], 'type': ['Special']*spec_val_df.shape[0], 'sign': ['=']*spec_val_df.shape[0], 'cutoff': special_value}), spec_val_df.iloc[:,1:]], axis = 1)], axis = 0)
    
        bin_no += spec_val_df.shape[0]
        local_copy_df = local_copy_df[~local_copy_df[variter].isin(special_value)]
        local_copy_df = local_copy_df.reset_index(drop = True)
        
    # -------
    cutoff_df = cutoff_df.reset_index(drop = True)
    if metrics_name.lower() == 'woe':
        bef_cont_list = cutoff_df.apply(lambda row: WOE((row.wtd_obs - row.wtd_resp), row.wtd_resp, total_wt_nonresp, total_wt_resp), axis = 1)

    if metrics_name.lower() == 'bin_resppct':
        bef_cont_list = cutoff_df.apply(lambda row: Bin_resprate((row.wtd_obs - row.wtd_resp), row.wtd_resp), axis = 1)

    cutoff_df['metrics'] = bef_cont_list
    
    # -----------------
    # monotonic bin metrics 
    remain_cumu_wt = local_copy_df['localwtvar'].sum()
    
    if (remain_cumu_wt <= wtd_tilesize) | (local_copy_df.shape[0] == 1):
        cont_bin_num = 1
        if metrics_name.lower() == 'woe':
            single_metrics =WOE((local_copy_df['localwtvar'].sum() - local_copy_df['wtd_response_calc'].sum()), local_copy_df['wtd_response_calc'].sum(), total_wt_nonresp, total_wt_resp)
        if metrics_name.lower() == 'bin_resppct':
            single_metrics = Bin_resprate((local_copy_df['localwtvar'].sum() - local_copy_df['wtd_response_calc'].sum()), local_copy_df['wtd_response_calc'].sum())

        tmp_cont_cutdf = pd.DataFrame({'varBin': list(range(bin_no, bin_no + cont_bin_num)), 'var': ['variter']*cont_bin_num, \
                                           'type': ['cont'] \
                                               ,'sign': ['ELSE']\
                                               , 'cutoff': ['ELSE']\
                                                   , 'wtd_obs': remain_cumu_wt, 'wtd_obspct': float(remain_cumu_wt/total_wt_obs) \
                                                    , 'wtd_resp': local_copy_df['wtd_response_calc'].sum(), 'wtd_resppct': float(local_copy_df['wtd_response_calc'].sum()/total_wt_resp)\
                                                        , 'abs_obs':local_copy_df.shape[0] \
                                                        , 'abs_resp': local_copy_df[resp_var].sum()
                                                        })
    
        metrics_list = [single_metrics]
        trend_flag = 'single'
    
    else:
        data_list = frequency_wtd_df(local_copy_df, variter, 'localwtvar', resp_var)
        # initial
        metrics_list = [999999.0,999999.0]
        metrics_list, bin_info, data_list, stop_flag = mono_analysis_func(data_list, total_wt_nonresp, total_wt_resp, wtd_tilesize, metrics_name, metrics_list, 'unknown', 'unknown')        
        rest_all_popu_metrics = metrics_list[-1]
        
        if metrics_list[-2] < rest_all_popu_metrics :
            trend_flag = 'Increasing'
        elif metrics_list[-2] > rest_all_popu_metrics:
            trend_flag = 'Decreasing'
        else:
            trend_flag = 'Flat'
            
        if trend_flag == 'Flat':
            cont_bin_num = 1 

            if metrics_name.lower() == 'woe':
                single_metrics =WOE((local_copy_df['localwtvar'].sum() - local_copy_df['wtd_response_calc'].sum()), local_copy_df['wtd_response_calc'].sum(), total_wt_nonresp, total_wt_resp)
            if metrics_name.lower() == 'bin_resppct':
                single_metrics = Bin_resprate((local_copy_df['localwtvar'].sum() - local_copy_df['wtd_response_calc'].sum()), local_copy_df['wtd_response_calc'].sum())
            
            tmp_cont_cutdf = pd.DataFrame({'varBin': list(range(bin_no, bin_no + cont_bin_num)), \
                                           'var': ['variter']*cont_bin_num, \
                                               'type': ['cont'] \
                                                   , 'sign': ['ELSE'] \
                                                       , 'cutoff': ['ELSE'] \
                                                           , 'wtd_obs': remain_cumu_wt, 'wtd_obspct': float(remain_cumu_wt/total_wt_obs) \
                                                               , 'wtd_resp': local_copy_df['wtd_response_calc'].sum(), 'wtd_resppct': float(local_copy_df['wtd_response_calc'].sum()/total_wt_resp) \
                                                                   , 'abs_obs':local_copy_df.shape[0], 'abs_resp': local_copy_df[resp_var].sum()
                                                                   })
    
            metrics_list = [single_metrics]
        else:
            
            while stop_flag == 0 :
                if data_list.shape[0] == 0 :
                    stop_flag = 1
                    break
                metrics_list, bin_info, data_list, stop_flag = mono_analysis_func(data_list, total_wt_nonresp, total_wt_resp, wtd_tilesize, metrics_name, metrics_list, bin_info, trend_flag)


            if data_list.shape[0] == 0 :
                cont_bin_num = (bin_info.shape[0])
                cutoff_l = list(bin_info['var'])[:-1] + ['ELSE']
                wtd_popu_cutoff = list(bin_info['cumu_wt'])
                wtd_popu_cutoff_pct = [float(x/total_wt_obs) for x in wtd_popu_cutoff]
                wtd_resp_cutoff = list(bin_info['cumu_resp'])
                wtd_resp_cutoff_pct = [float(x/total_wt_resp) for x in wtd_resp_cutoff]
                metrics_list = metrics_list[1:-1]
                abs_popu_l = list(bin_info['cumu_absobs'])
                abs_resp_l = list(bin_info['cumu_absresp'])
                
            else:
                
                cont_bin_num = (bin_info.shape[0] + 1 )
                cutoff_l = list(bin_info['var']) + ['ELSE']
                wtd_popu_cutoff = list(bin_info['cumu_wt']) + [data_list['wtd_popu'].sum()]
                wtd_resp_cutoff = list(bin_info['cumu_resp']) + [data_list['wtd_binary'].sum()]
                wtd_popu_cutoff_pct = [float(x/total_wt_obs) for x in wtd_popu_cutoff]
                wtd_resp_cutoff_pct = [float(x/total_wt_resp) for x in wtd_resp_cutoff]
                metrics_list = metrics_list[1:]
                abs_popu_l = list(bin_info['cumu_absobs']) + [data_list['abs_obs'].sum()]
                abs_resp_l = list(bin_info['cumu_absresp']) + [data_list['abs_resp'].sum()]
                
                
            tmp_cont_cutdf = pd.DataFrame({'varBin': list(range(bin_no, bin_no + cont_bin_num)), 'var': [variter]*cont_bin_num, \
                                           'type': ['cont']* cont_bin_num \
                                               , 'sign': ['<=']*(cont_bin_num - 1) + ['ELSE'] \
                                                   , 'cutoff': cutoff_l \
                                                       , 'wtd_obs': wtd_popu_cutoff, 'wtd_obspct': wtd_popu_cutoff_pct \
                                                           , 'wtd_resp': wtd_resp_cutoff, 'wtd_resppct': wtd_resp_cutoff_pct \
                                                               , 'abs_obs': abs_popu_l, 'abs_resp': abs_resp_l
                                                               })
                                
    tmp_cont_cutdf['metrics'] = metrics_list
    cutoff_df = pd.concat([cutoff_df, tmp_cont_cutdf], axis = 0)
    
    return variter, metrics_list, trend_flag, cutoff_df
    
        
def flatten_list(_2d_list):
    flat_list = []
    for element in _2d_list:
        if type(element) is list:
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
            
    return flat_list
    
        
def Monotonic_Bin_creation(feature_list = []
                           ,    wtd_tile_pct = 0.01
                           ,    metrics_name = 'woe'
                           ,    resp_var = ''
                           ,    wt_var = ''
                           ,    userdir = ''
                           ,    prefix = 'Prefix'
                           ,    special_value_df = pd.DataFrame(columns = ['var', 'special'])
                           ,    df_input = pd.DataFrame()
                           ):
    """
    author: yliu
    
    Module Log:
        version 1.0: initial Monotonic_Bin_creation Func

    Example:
        Monotonic_Bin_creation(feature_list = ['var1', 'var2', 'var3']
        , wtd_tile_pct = 0.1
        , metrics_name = 'bin_resppct'
        , resp_var = 'dep_var'
        , wt_var = 'weights'
        , userdir = 'C:/'
        , prefix = 'MonoTrend_prefix'
        , special_value_df = pd.DataFrame({'var': ['var1', 'var2'], 'special': [[0],[-1,0]]})
        , df_input = a_original_pandas_dataframe
        )

    Parameters
    ----------
    wtd_tile_pct = 0.1:
    The desired weighted population proportion for each bin;
    
    metrics_name: metrics_name = 'woe' either 'woe' or 'bin_resppct':
    Please note that, either metrics is calculated based on weighted population.
    
    resp_var: resp_var = 'dep_var'
    The string based Binary Response Variable Name.
    
    wt_var = 'a_weight_var_name':
    A weight variable name in dataframe indicating weight column
    
    userdir = '':
    A string path to define where output will be created, e.g. 'C:/'
    
    prefix = 'MonoTrend_file':
    The string prefix for output files
    
    special_value_df = pd.DataFrame(columns = ['var', 'special']):
    The special pandas dataframe indicating special values.
    
    df_input:
    The input pandasdataframe
    
    Returns
    -------
    The detailed cutoff dataframe indicating a monotonic trending for given metrics: prefix + '_monodetail_df.csv'\
        The general trend Value dataframe: prefix + '_monoTrend_df.csv' ('Increasing', 'Decreasing', or 'Flat')

    """
    
    
    df_input = df_input.reset_index(drop = True)
    if len(wt_var) == 0:
        df_input['localwtvar'] = 1.0
    else:
        df_input['localwtvar'] = df_input[wt_var]
        
    df_input = df_input.reset_index(drop = True)
    
    
    total_wt_obs = df_input['localwtvar'].sum()
    total_wt_resp = sum(df_input['localwtvar']*df_input[resp_var])
    total_wt_nonresp = total_wt_obs - total_wt_resp
    
    if total_wt_obs == 0:
        print('dataframe is empty')
        return
    if total_wt_resp == 0 :
        print('no response in given dataset') 
        return 
    if total_wt_nonresp == 0 :
        print('non non-response in given dataset')
        return 
        
    wtd_tilesize = (1 if int(total_wt_obs * wtd_tile_pct) < 1 else int(total_wt_obs*wtd_tile_pct) )

    total_abs_obs = df_input.shape[0]
    total_abs_resp = df_input[resp_var].sum()
    total_abs_nonresp = total_abs_obs - total_abs_resp
    
    orig_cutoff_pack = list(map(lambda x: single_var_bin(x, df_input, special_value_list(special_value_df,x), resp_var, metrics_name, total_wt_obs, total_wt_resp, total_wt_nonresp, wtd_tilesize, total_abs_obs, total_abs_resp), feature_list))

    combine_mono_df_detail = pd.concat([x[3] for x in orig_cutoff_pack])
    trend_list = flatten_list([x[2] for x in orig_cutoff_pack])
    name_list = flatten_list([x[0] for x in orig_cutoff_pack])
    combine_mono_df_trend = pd.DataFrame({'var': name_list, 'trend': trend_list})
    
    combine_mono_df_detail.to_csv(userdir + prefix + '_monodetail_df.csv', header = True, index = False)

    combine_mono_df_trend.to_csv(userdir + prefix + '_monoTrend_df.csv', header = True, index = False)    
