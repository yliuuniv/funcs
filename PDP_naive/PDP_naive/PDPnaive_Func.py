

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
             temp_scr = model_obj.predict(xgb.DMatrix(data = temp_train_data[model_obj.feature_names]))'
             """,
             prefix_name = '',
             PDP_csv_path = '',             
             user_dir = '',
             multiple_page_together = True, 
             create_indiv_pdp_pdf = False):
    """
    author: yliu
    Model Log:
        V 1.0:  Publish first version PDP Naive
        V 1.1:  Fix the bug: first plot font
                Modify Func Msg
                
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
             multiple_page_together = True, 
             create_indiv_pdp_pdf = False
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
        prefix_name: 
            string; prefix for all outputs;
        PDP_csv_path: 
            if is to recreate PDP based on a given PDP csv dataframe; then provide the file path; otherwise, keep it as '', default is '';
        user_dir: 
            user directory to save all outputs;
        multiple_page_together: 
            default value is TRUE; When it's True, to create 4 plots per page PNG & PDF; otherwise, no multiple plots file will be created;
        create_indiv_pdp_pdf: 
            default False; when False, there is no individual plot per page pdf Created
            
    Model Outputs:
        PDP CSV File: 
            prefix_name+'_pdp_data.csv', with columns ['var', 'bars', 'pdp_cutoff_values', 'wtd_pdp_scr', 'def_tile', 'head_cutval', 'tail_cutval']
        Single PDPPNG File(s): 
            prefix_name+'_'+ varname + '_pdp.png'
        If create_indiv_pdp_pdf = TRUE :
            PDF File: prefix_name+'_singleplotPDF.pdf'
        If multiple_page_together = TRUE :
            PDF File: prefix_name+'_4PDP_page.pdf' 
            PNG File(s): prefix_name+'_4plots_pdppage'+varname.png

    """
    
    print('This is the PDPnaive func version 1.1 ')
    
    # check required python lib
    
    ERROR_flag = 0

    print('PDPNaive Func note: Preferred xgb version is 1.5.0')
    try:
        import xgboost as xgb
        print("Succesfully imported module 'xgboost'")   
        print('Current xgb version is '+ xgb.__version__)
    except ImportError:
        print("module 'xgboost' is not installed; install it first")
        ERROR_flag += 1     
    
    try:
        import pandas as pd
        print("Succesfully imported module 'pandas'")        
    except ImportError:
        print("module 'pandas' is not installed; install it first")
        ERROR_flag += 1 

    try:
        import numpy as np
        print("Succesfully imported module 'numpy'")        
    except ImportError:
        print("module 'numpy' is not installed; install it first")
        ERROR_flag += 1 

    print('PDPNaive Func note: Preferred matplotlib version is 3.5.0')
    try:
        import matplotlib
        print("Succesfully imported module 'matplotlib'")    
        print('Current matplotlib version is '+ matplotlib.__version__)
    except ImportError:
        print("module 'matplotlib' is not installed; install it first;")
        ERROR_flag += 1     
    
    try:
        import matplotlib.pyplot as plt
        print("Succesfully imported module 'matplotlib.pyplot'")    
    except ImportError:
        print("module 'matplotlib' is not installed; install it first;\nThe desired script is 'import matplotlib.pyplot as plt'")
        ERROR_flag += 1 
    try:
        from matplotlib.backends.backend_pdf import PdfPages
        print("Succesfully imported module 'matplotlib.backends.backend_pdf'")
    except ImportError:
        print("module 'matplotlib' is not installed; install it first;\nThe desired script is 'from matplotlib.backends.backend_pdf import PdfPages'")
        ERROR_flag += 1 
    
    print('PDPNaive Func note: Preferred PIL version is 8.4.0')    
    try:
        import PIL
        from PIL import Image
        print("Succesfully imported module 'PIL.Image'")
        print('Current PIL version is '+ PIL.__version__)
    except ImportError:
        print("module 'PIL' is NOT installed; install it first;\nThe desired script is 'from PIL import Image'")
        ERROR_flag += 1 

    
    if ERROR_flag > 0 :
        print('PDPNaive Func note: modules missing. Return.')
        return
    
    num_plts_page = 4
    
    if len(PDP_csv_path) == 0:
    
        n_len_var = len(by_importance_var)
        train_orig_df['weights_int'] = train_orig_df[weight_int_var].apply(lambda x: int(x))
        part_size = float(1.0/nbins)
        plt_part_no = int((n_len_var - n_len_var%num_plts_page)/num_plts_page)
        plt_left = n_len_var%num_plts_page 
        plt_page_no = plt_part_no if plt_left == 0 else (plt_part_no + 1)
        pdp_csvname =  prefix_name+'_pdp_data.csv'
        
        
        pdp_value_df = pd.DataFrame(columns = ['var', 'bars', 'pdp_cutoff_values', 'wtd_pdp_scr', 'def_tile', 'head_cutval', 'tail_cutval'])
        
        for var_pos in range(n_len_var):
            varname_iter = by_importance_var[var_pos]
            temp_train_data = train_orig_df.copy()
            value_wtd_list = train_orig_df[[varname_iter, weight_int_var]].loc[train_orig_df.index.repeat(train_orig_df.weights_int)]
            head_cutval = value_wtd_list[varname_iter].quantile(head_cut)
            tail_cutval = value_wtd_list[varname_iter].quantile(tail_cut)    
            value_wtd_list = value_wtd_list[(value_wtd_list[varname_iter] > head_cutval ) & (value_wtd_list[varname_iter] < tail_cutval )]
            
            # create x-axis evenly distributed list
            min_start = min(value_wtd_list[varname_iter])
            max_end = max(value_wtd_list[varname_iter])
            even_part = float((max_end - min_start)/nbins)
            pdp_cutoff_values = [(min_start + i * even_part) for i in range(nbins+1)]
            
            # labels
            bars = [str(round(x,1)) for x in pdp_cutoff_values]
            if train_orig_df[train_orig_df[varname_iter].isna()].shape[0] > 0 :
                pdp_cutoff_values = [np.NaN] + pdp_cutoff_values
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
        n_len_var = len(set(pdp_value_df['var']))

        plt_part_no = int((n_len_var - n_len_var%num_plts_page)/num_plts_page)
        plt_left = n_len_var%num_plts_page 
        plt_page_no = plt_part_no if plt_left == 0 else (plt_part_no + 1)
        
    
    if create_indiv_pdp_pdf : 
        individual_plot_pdf_name = prefix_name+'_singleplotPDF.pdf'
        pp = PdfPages(user_dir + individual_plot_pdf_name)

    plt.clf()
    f, ax = plt.subplots(1)
    plt.savefig(user_dir + prefix_name+'_onlysize_pdp.png', dpi = 1200)
    plt.rcParams.update({'font.size': 4})
    plt.close()
        
    for var_pos in range(n_len_var):
        varname_iter = by_importance_var[var_pos]
        bars = pdp_value_df[pdp_value_df['var'] == varname_iter]['bars'].tolist()
        wtd_pdp_scr = pdp_value_df[pdp_value_df['var'] == varname_iter]['wtd_pdp_scr'].tolist()
        
        plt.clf()
        f, ax = plt.subplots(1)
        ax.plot(bars, wtd_pdp_scr, 'ro', markersize = 2)
        ax.set_xticklabels(bars, rotation = 45, ha = "right")
        if bars[0] == 'Missing':
            ax.plot(bars[1:], wtd_pdp_scr[1:], '--')
        else:
            ax.plot(bars, wtd_pdp_scr, '--')
            
        plt.title(varname_iter + " PDP Plot", fontdict = {'size': 10})
        
        plt.xlabel(varname_iter + ' value')
        plt.ylabel('ModelScore')    
        plt.savefig(user_dir + prefix_name+'_'+ varname_iter + '_pdp.png', dpi = 1200)
        if create_indiv_pdp_pdf : 
            pp.savefig(plt.gcf())
        plt.close()
    

    if create_indiv_pdp_pdf :
        pp.close()
    
        
    
    # -------------------------------------------------------------------------------------------------------------------------------------------------
    # Part III create grouped PDP plots into one image
    # -------------------------------------------------------------------------------------------------------------------------------------------------
    
    if multiple_page_together:
        pp_4plts_name = user_dir + prefix_name+'_4PDP_page.pdf'
        appd_image_list = []
        create_pdf = 0 
        for page_iter in range(plt_page_no):
            if (page_iter < plt_part_no) | (plt_part_no == plt_page_no):
                image_lis = []
                for i_iter in range(1,5):
                    image_lis += [Image.open((user_dir + prefix_name+'_'+ by_importance_var[page_iter*4 + i_iter -1 ] + '_pdp.png'))]           
                
                w, h = image_lis[0].size
                
                new_image = Image.new('RGB', (w*2, h*2))
                
                new_image.paste(image_lis[0], (0,0))
                new_image.paste(image_lis[1], (w,0))
                new_image.paste(image_lis[2], (0,h))
                new_image.paste(image_lis[3], (w,h))
                
                new_image.save(user_dir +prefix_name+'_4plots_pdppage'+str(page_iter+1)+'.png', quality = 95)
                del image_lis
            else:
                image_lis = []
                left_plots = n_len_var - page_iter * 4
                for i_left in range(1,5):
                    if i_left <= left_plots:
                        image_lis += [Image.open((user_dir + prefix_name+'_'+ by_importance_var[page_iter*4 + i_left -1 ] + '_pdp.png'))]    
                    else:
                        image_lis += [Image.open((user_dir + prefix_name+'_onlysize_pdp.png'))]    
                
                w, h = image_lis[0].size    
                new_image = Image.new('RGB', (w*2, h*2))
                
                new_image.paste(image_lis[0], (0,0))
                new_image.paste(image_lis[1], (w,0))
                new_image.paste(image_lis[2], (0,h))
                new_image.paste(image_lis[3], (w,h))       
                new_image.save(user_dir +prefix_name+'_4plots_pdppage'+str(page_iter+1)+'.png', quality = 95)
                del image_lis
    
            if create_pdf == 0 :
                create_pdf += 1
                first_image = new_image
            else:
                appd_image_list += [new_image]
    
    
        first_image.save(pp_4plts_name, save_all = True, append_images = appd_image_list)
    
