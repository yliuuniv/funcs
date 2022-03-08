import pandas as pd

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
  special_val_df: a N*2 dim pandas dataframe, and the column names are
  ['var', 'special']; column 'special' cell value will be a list, e.g. [0,1]
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
  special_val_df: a N*2 dim pandas dataframe, and the column names are
  ['var', 'special']; column 'special' cell value will be a list, e.g. [0,1]
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
      
      new_nobs += [n_new_missing]
      new_npct += [pct_new_missing]
    
    elif (list(tmp_cut.type)[varbin] == 'Special') | (list(tmp_cut.type)[varbin] == 'fixed'):
      fixed_iter = 
    
