

import pandas as pd
import numpy as np

def PDPNaive(head_cut = 0.001,
             tail_cut = 0.999,
             nbins = 20,
             by_importance_var = [],
             train_orig_df = pd.DataFrame(),
             weight_int_var = '',
             model_obj = np.NaN,
             scr_script = """
             temp_scr = model_obj.predict(xgb.DMatrix(data = <temp_train_data>[model_obj.feature_names]))'
             """,
             prefix_name = '',
             PDP_csv_path = '',             
             user_dir = '',
             given_var_cutoff = dict()
             ):
    """
    author: yliu
    Model Log:
        V 1.0:  Publish first version PDP Naive
        V 1.1:  Fix the bug: first plot font
                Modify Func Msg
        V 2.0:  Update capping/flooring info from >= to >;
                Change PDP plot core codes and simplify logic;
                Remove Parameter multiple_page_together, create_indiv_pdp_pdf.
                Instead, add Parameter NumberofPlots_PerPage
        V 3.0:  Add Pre-Defined var cutoff values;
        V 3.1:  Fix Major Bugs;
        V 3.2:  20231219: Fix an uppercase lowercase problem;        
                
    Example:
        PDPNaive(head_cut = 0.001,
             tail_cut = 0.999,
             nbins = 20,
             by_importance_var = ['varA', 'varB', 'varC'],
             train_orig_df = pd.DataFrame(),
             weight_int_var = 'wt_var',
             model_obj = np.NaN,
             scr_script = '',
             prefix_name = 'prefix_str',
             PDP_csv_path = '',             
             user_dir = 'c:/',
             given_var_cutoff = {'var1': [1,2,3]}
        )

        
    Model Inputs:
        head_cut: 
            the perct% where outliers will be removed; e.g. head_cut = 0.001 will remove values lower than 0.1% percentile;
        tail_cut: 
            the perct% where outliers will be removed; e.g. tail_cut = 0.999 will remove values higher than 99.9% percentile;
        nbins: 
            int. Number of evenly distributed tiles of value, from  lowest - highest;
        by_importance_var: 
            []. List of character variable names;
        train_orig_df: 
            pd.DataFrame(); pandas DataFrame used in original model training;
        weight_int_var: 
            string weight variable name;
        model_obj:
            model python obj; really needs to be customized; as different model has totally different modeling algorithm;
        scr_script: 
            scoring script; really needs to be customized; as different model has totally different modeling algorithm;
            Note; keep temp_scr, temp_train_data, model_obj as hardcoded in script.
        prefix_name: 
            string; prefix for all outputs;
        PDP_csv_path: 
            if is to recreate PDP based on a given PDP csv dataframe; then provide the file path; otherwise, keep it as '', default is '';
        user_dir: 
            user directory to save all outputs;
        given_var_cutoff: 
            dict: as {'var1': [1,2,3]}; to create PDP on specific cutoff values;
            
    Model Outputs:
        PDP CSV File: 
            prefix_name+'_pdp_data.csv', with columns ['var', 'bars', 'pdp_cutoff_values', 'wtd_pdp_scr', 'def_tile', 'head_cutval', 'tail_cutval']
        PDP PDF Plots:
            PDF File: prefix_name + '_PDP_plots.pdf'

    """
    
    print('This is the PDPnaive func version 3.1 ')
    
    # check required python lib
    
    ERROR_flag = 0

    print('PDPNaive Func note: Preferred xgb version is 1.5.0')
    try:
        import xgboost as xgb
        # print("Succesfully imported module 'xgboost'")   
        # print('Current xgb version is '+ xgb.__version__)
    except ImportError:
        print("PDPnaive notes: module 'xgboost' is not installed; install it first")
        ERROR_flag += 1     
    
    try:
        import pandas as pd
        # print("Succesfully imported module 'pandas'")        
    except ImportError:
        print("PDPnaive notes: module 'pandas' is not installed; install it first")
        ERROR_flag += 1 

    try:
        import numpy as np
        # print("Succesfully imported module 'numpy'")        
    except ImportError:
        print("PDPnaive notes: module 'numpy' is not installed; install it first")
        ERROR_flag += 1 

    # print('PDPNaive Func note: Preferred matplotlib version is 3.5.0')
    try:
        import matplotlib
        # print("Succesfully imported module 'matplotlib'")    
        # print('Current matplotlib version is '+ matplotlib.__version__)
    except ImportError:
        print("PDPnaive notes: module 'matplotlib' is not installed; install it first;Preferred matplotlib version is 3.5.0'")
        ERROR_flag += 1     
    
    try:
        import matplotlib.pyplot as plt
        # print("Succesfully imported module 'matplotlib.pyplot'")    
    except ImportError:
        print("PDPnaive notes: module 'matplotlib' is not installed; install it first;\nThe desired script is 'import matplotlib.pyplot as plt'")
        ERROR_flag += 1 
    try:
        from matplotlib.backends.backend_pdf import PdfPages
        # print("Succesfully imported module 'matplotlib.backends.backend_pdf'")
    except ImportError:
        print("PDPnaive notes: module 'matplotlib' is not installed; install it first;\nThe desired script is 'from matplotlib.backends.backend_pdf import PdfPages'")
        ERROR_flag += 1 
    
    # print('PDPNaive Func note: Preferred PIL version is 8.4.0')    
    try:
        import PIL
        from PIL import Image
        # print("Succesfully imported module 'PIL.Image'")
        # print('Current PIL version is '+ PIL.__version__)
    except ImportError:
        print("PDPnaive notes: module 'PIL' is NOT installed; install it first;\nThe desired script is 'from PIL import Image'. Preferred PIL version is 8.4.0'")
        ERROR_flag += 1 

    
    if ERROR_flag > 0 :
        print('PDPNaive Func note: modules missing. Return.')
        return
    
    if len(PDP_csv_path) == 0:
        actual_pdp_csv = PDP_csv_path
    
    skip_vars = []
    
    if len(PDP_csv_path) == 0:
    
        n_len_var = len(by_importance_var)

        part_size = float(1.0/nbins)


        pdp_csvname =  prefix_name+'_pdp_data.csv'
        actual_pdp_csv = user_dir + pdp_csvname
        
        pdp_value_df = pd.DataFrame(columns = ['var', 'bars', 'pdp_cutoff_values', 'wtd_pdp_scr', 'def_tile', 'head_cutval', 'tail_cutval'])
        
        
        for var_pos in range(len(by_importance_var)):
            varname_iter = by_importance_var[var_pos]
            temp_train_data = train_orig_df.copy()
            temp_train_data['weights_int'] = temp_train_data[weight_int_var].apply(lambda x: int(x))

            if varname_iter not in list(given_var_cutoff.keys()):
                value_wtd_list = train_orig_df[[varname_iter, weight_int_var]].loc[train_orig_df.index.repeat(train_orig_df.weights_int)]
                head_cutval = value_wtd_list[varname_iter].quantile(head_cut)
                tail_cutval = value_wtd_list[varname_iter].quantile(tail_cut)    
                value_wtd_list = value_wtd_list[(value_wtd_list[varname_iter] > head_cutval ) & (value_wtd_list[varname_iter] < tail_cutval )]
            
            
                # create x-axis evenly distributed list
                if len(value_wtd_list[varname_iter]) > 0 :
                    min_start = min(value_wtd_list[varname_iter])
                    max_end = max(value_wtd_list[varname_iter])
                    even_part = float((max_end - min_start)/nbins)
                    pdp_cutoff_values = [(min_start + i * even_part) for i in range(nbins+1)]
                    crt_nbins = nbins
                else:
                    pdp_cutoff_values = []
                    crt_nbins = 0
                    skip_vars += [varname_iter]
            else:
                pdp_cutoff_values = sorted(given_var_cutoff[varname_iter])
                head_cutval = pdp_cutoff_values[0]
                tail_cutval = pdp_cutoff_values[-1]
                crt_nbins = len(pdp_cutoff_values)
                
                    
            
            # labels - add Missing
            if len(pdp_cutoff_values) > 0 :
                bars = [str(round(x,1)) for x in pdp_cutoff_values]
            else:
                bars = []
            
            pdp_cutoff_values = [np.NAN] + pdp_cutoff_values
            bars = ['Missing'] + bars

            
            wtd_pdp_scr = []
            for value_cut in pdp_cutoff_values:
                temp_train_data[varname_iter] = value_cut
                exec(scr_script)
                exec("temp_train_data['partial_scr'] = temp_scr")
                wtd_pdp_scr += [sum(temp_train_data['partial_scr'] * temp_train_data[weight_int_var])/ sum(temp_train_data[weight_int_var])]
                
            pdp_value_df = pd.concat([pdp_value_df
                                      , pd.DataFrame(list(zip([varname_iter]*len(bars), bars, pdp_cutoff_values, wtd_pdp_scr, [nbins]*len(bars),  [round(head_cutval, 2)]*len(bars), [round(tail_cutval, 2)]*len(bars) ))
                                                     , columns = ['var', 'bars', 'pdp_cutoff_values', 'wtd_pdp_scr', 'def_tile', 'head_cutval', 'tail_cutval'])])
            
            
        pdp_value_df.to_csv(user_dir + pdp_csvname)    
    
    
    # -------------------------------------------------------------------------------------------------------------------------------------------------
    # Part II create individual PDP plots
    # -------------------------------------------------------------------------------------------------------------------------------------------------
    
    
    # Create one Plot per Page PDP
    if len(PDP_csv_path) > 0 :
        pdp_value_df = pd.read_csv(PDP_csv_path)

    plots = []
    for varname in by_importance_var :
        if varname not in skip_vars:
            bars = list(pdp_value_df[pdp_value_df['var'] == varname]['bars'])
            wtd_pdp_scr = list(pdp_value_df[pdp_value_df['var'] == varname]['wtd_pdp_scr'])
            plots += [[bars, wtd_pdp_scr, varname]]
            
    pdf_Pages = PdfPages(user_dir + prefix_name + '_PDP_plots.pdf')
    fig = plt.figure(figsize = (11.69, 8.27))
    page_num = 1
    
    for i, (bars, wtd_pdp_scr, varname_iter) in enumerate(plots):
        ax = fig.add_subplot(2,2,i%4+1)
        ax.plot(bars, wtd_pdp_scr, 'ro', markersize = 2)
        ax.set_xticklabels(bars, rotation = 45, ha = "right")
        if bars[0] == 'Missing':
            ax.plot(bars[1:], wtd_pdp_scr[1:], '--')
        else:
            ax.plot(bars, wtd_pdp_scr, '--')
            
        plt.title(varname_iter + " PDP Plot", fontdict = {'size':10})
        plt.xlabel(varname_iter + ' value', fontsize = 10)
        plt.ylabel('ModelScore', fontsize = 10)
        plt.xticks(fontsize=6)
        plt.yticks(fontsize=6)
        
        if (i+1)%4 == 0:
            plt.tight_layout()
            pdf_Pages.savefig(fig)
            plt.close()
            page_num += 1
            fig = plt.figure(figsize = (11.69,8.27))
    
    if len(plots) %4 != 0 :
        plt.tight_layout()
        pdf_Pages.savefig(fig)
        plt.close()
        page_num += 1
    
    pdf_Pages.close()
        
