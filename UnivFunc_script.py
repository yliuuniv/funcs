

def UnivFunc(orig_col, varname):
    # version 1.0
    orig_vec = list(orig_col)
    import pandas as pd
    import math as math
    import numpy as np    
    import statistics
    
    #convert it it float if it's char, if it's a blank then np.nan
    orig_vec = [float(np.nan)  if len(str(x).strip())==0 else float(x) for x in orig_vec ]
    #total number of obs
    n_obs = len(orig_vec)
    # missing
    n_missing = np.count_nonzero(np.isnan(orig_vec))
    
    # Create Non- na vector
    mod_vec = [x for x in orig_vec if str(x) != 'nan'] 
    len_mod = len(mod_vec)
    
    if len_mod > 0 :
        avg = statistics.mean(mod_vec)
        min_val = min(mod_vec)
        max_val = max(mod_vec)
        mode = statistics.mode(mod_vec)
        std_val = statistics.stdev(mod_vec)
        
        #feature value distribution
        NZero = len([x for x in mod_vec if x == 0])
        NMin = len([x for x in mod_vec if x == min_val])
        NMax = len([x for x in mod_vec if x == max_val])
        Nmode = len([x for x in mod_vec if x == mode])
        
        PctMissing = float(n_missing/n_obs)
        PctZero = float(NZero/n_obs)
        Pct_Min = float(NMin/n_obs)
        Pct_Max = float(NMax/n_obs)
        Pct_Mode = float(Nmode/n_obs)
    
        ptile = [float(x) for x in np.percentile(mod_vec, [100,99.9,99,95,90,75,50,25,10,5,2,1,0.01,0])]
        Floor = ptile[-2]
        Cap = ptile[1]
        
        obs_LargerCap = len([x for x in mod_vec if x > Cap])
        obs_SmallFlr =  len([x for x in mod_vec if x < Floor])
        
        #create output format
        list_p = ['perc_'+str(x) for x in [100,99.9,99,95,90,75,50,25,10,5,2,1,0.01,0]]
        
        temp_output = pd.DataFrame([[varname, n_obs,n_missing,NZero,NMin,NMax,Nmode
                                     ,min_val, max_val, mode, avg,std_val,PctMissing,PctZero,Pct_Min,Pct_Max,Pct_Mode,Cap, obs_LargerCap,Floor,obs_SmallFlr]                                    
                                    +ptile[2:-3]]
                                   , columns=['varname','n_obs','n_missing','n_zero','n_min','n_max','n_mode','minval','maxval','mode','avg','std'
                                              ,'p_missing','p_zero','p_min','p_max','p_mode', 'capval_999', 'n_grtcap', 'flr_001','n_smlflr']
                                   +list_p[2:-3])
        
        
        # Add consideration for special values
        i, d = divmod(max_val, 1)
        ni, d = divmod(min_val, 1)
        
        string_len = len(str(int(i)))
        n_string_len = len(str(int(ni)))
        pos_special = []
        neg_special = []
        pos_spec_name = []
        neg_spec_name = []
        num_spec = []
        num_negspec = []
        for iter_num in range(1,10):
            pos_special = pos_special + [int('9'*string_len) - 9 + iter_num ]
            neg_special = neg_special + [-int('9'*n_string_len) + iter_num  - 1]
            num_spec = num_spec + [len([x for x in mod_vec if x == pos_special[-1]])]
            pos_spec_name = pos_spec_name + ['spec_'+str(iter_num)]
            neg_spec_name = neg_spec_name + ['negspec_'+str(iter_num)]
            num_negspec = num_negspec + [len([x for x in mod_vec if x == neg_special[-1]])]
        
        neg_special = neg_special[::-1]
        num_negspec = num_negspec[::-1]
        
        temp_output = temp_output.join(pd.DataFrame([num_spec+num_negspec], columns= pos_spec_name + neg_spec_name)) 
        
        #value after excluding special
        Minimum_exclspec = min([x for x in mod_vec if x > neg_special[0]])
        Maximum_exclspec = max([x for x in mod_vec if x < pos_special[0]])
        
        temp_output = temp_output.join(pd.DataFrame([[Minimum_exclspec, Maximum_exclspec]], columns= ['Minimum_exclspec','Maximum_exclspec']))
        
        return temp_output
        
        

