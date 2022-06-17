```python
dataset = pd.read_csv('...' + 'titanic.csv')
```


```python
dataset.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>PassengerId</th>
      <th>Survived</th>
      <th>Pclass</th>
      <th>Name</th>
      <th>Sex</th>
      <th>Age</th>
      <th>SibSp</th>
      <th>Parch</th>
      <th>Ticket</th>
      <th>Fare</th>
      <th>Cabin</th>
      <th>Embarked</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>0</td>
      <td>3</td>
      <td>Braund, Mr. Owen Harris</td>
      <td>male</td>
      <td>22.0</td>
      <td>1</td>
      <td>0</td>
      <td>A/5 21171</td>
      <td>7.2500</td>
      <td>NaN</td>
      <td>S</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>1</td>
      <td>1</td>
      <td>Cumings, Mrs. John Bradley (Florence Briggs Th...</td>
      <td>female</td>
      <td>38.0</td>
      <td>1</td>
      <td>0</td>
      <td>PC 17599</td>
      <td>71.2833</td>
      <td>C85</td>
      <td>C</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>1</td>
      <td>3</td>
      <td>Heikkinen, Miss. Laina</td>
      <td>female</td>
      <td>26.0</td>
      <td>0</td>
      <td>0</td>
      <td>STON/O2. 3101282</td>
      <td>7.9250</td>
      <td>NaN</td>
      <td>S</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>1</td>
      <td>1</td>
      <td>Futrelle, Mrs. Jacques Heath (Lily May Peel)</td>
      <td>female</td>
      <td>35.0</td>
      <td>1</td>
      <td>0</td>
      <td>113803</td>
      <td>53.1000</td>
      <td>C123</td>
      <td>S</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>0</td>
      <td>3</td>
      <td>Allen, Mr. William Henry</td>
      <td>male</td>
      <td>35.0</td>
      <td>0</td>
      <td>0</td>
      <td>373450</td>
      <td>8.0500</td>
      <td>NaN</td>
      <td>S</td>
    </tr>
  </tbody>
</table>
</div>




```python
def weight_assign(row):
    if row['Sex']  == 'male':
        if row['Age']  >30:
            wt = 1.25
        else:
            wt = 2.25
    else:
        if row['Age']  >30:
            wt = 3.25
        else:
            wt = 4.25   
    return wt
```


```python
dataset['wt'] = dataset.apply(lambda row: weight_assign(row), axis = 1 )
```


```python
print(PSI_Calc.__doc__)
```

    
            Model Log:
                v 1.0:
                    Publish the first version
                v 2.0:
                    Add an new input 'documented_cutoff_dict', listing cutoff values for every var
                v 3.0:
                    Add weight consideration to PSI, orig_wt, and new_wt
                          
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
    
                    
            
    


```python
# Scenario 1 
PSI_Calc(feature_list=['Age', 'Fare']
         , tile_pct=0.3
         , round_digit=9
         , data_cutdf_path=''
         , fixed_pct=0.05
         , psi_sig_pct=0.005
         , userdir=userdir
         , prefix='PSI_test1'
         , special_value_df= pd.DataFrame({'var':['Age', 'Fare' , 'History'], 'special':[[0], [0,1,2], [99]]})
         , df_orig=dataset
         , df_new=dataset.iloc[0:20,:]
         , documented_cutoff_dict={}
         , orig_wt=''
         , new_wt='')
```

    This is the PSI_Calc func version 3.0
    Processing Age
    Processing Fare
    PSI Calculation Finished.
    


```python
PSI_output_test1 = pd.read_csv( userdir + 'PSI_test1_detailedCut_df.csv')
```


```python
PSI_output_test1
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>var</th>
      <th>type</th>
      <th>sign</th>
      <th>cutoff</th>
      <th>varBin</th>
      <th>obs</th>
      <th>obsPct</th>
      <th>newobs</th>
      <th>newpct</th>
      <th>psi_bin</th>
      <th>raw_obs</th>
      <th>raw_obsPct</th>
      <th>raw_newobs</th>
      <th>raw_newpct</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Age</td>
      <td>Missing</td>
      <td>=</td>
      <td>-9.999999e+06</td>
      <td>0</td>
      <td>177.0</td>
      <td>0.198653</td>
      <td>3.0</td>
      <td>0.15</td>
      <td>1.366791e-02</td>
      <td>177</td>
      <td>0.198653</td>
      <td>3</td>
      <td>0.15</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Age</td>
      <td>Special</td>
      <td>=</td>
      <td>0.000000e+00</td>
      <td>0</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>0.000000e+00</td>
      <td>0</td>
      <td>0.000000</td>
      <td>0</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Age</td>
      <td>cont</td>
      <td>&gt;=</td>
      <td>3.250000e+01</td>
      <td>0</td>
      <td>268.0</td>
      <td>0.300786</td>
      <td>7.0</td>
      <td>0.35</td>
      <td>7.457715e-03</td>
      <td>268</td>
      <td>0.300786</td>
      <td>7</td>
      <td>0.35</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Age</td>
      <td>cont</td>
      <td>ELSE</td>
      <td>1.000000e+09</td>
      <td>0</td>
      <td>446.0</td>
      <td>0.500561</td>
      <td>10.0</td>
      <td>0.50</td>
      <td>6.294641e-07</td>
      <td>446</td>
      <td>0.500561</td>
      <td>10</td>
      <td>0.50</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Fare</td>
      <td>Missing</td>
      <td>=</td>
      <td>-9.999999e+06</td>
      <td>0</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>0.000000e+00</td>
      <td>0</td>
      <td>0.000000</td>
      <td>0</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Fare</td>
      <td>Special</td>
      <td>=</td>
      <td>0.000000e+00</td>
      <td>0</td>
      <td>15.0</td>
      <td>0.016835</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>1.000000e+00</td>
      <td>15</td>
      <td>0.016835</td>
      <td>0</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Fare</td>
      <td>Special</td>
      <td>=</td>
      <td>1.000000e+00</td>
      <td>0</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>0.000000e+00</td>
      <td>0</td>
      <td>0.000000</td>
      <td>0</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Fare</td>
      <td>Special</td>
      <td>=</td>
      <td>2.000000e+00</td>
      <td>0</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>0.000000e+00</td>
      <td>0</td>
      <td>0.000000</td>
      <td>0</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Fare</td>
      <td>cont</td>
      <td>&gt;=</td>
      <td>2.772080e+01</td>
      <td>0</td>
      <td>267.0</td>
      <td>0.299663</td>
      <td>6.0</td>
      <td>0.30</td>
      <td>3.781026e-07</td>
      <td>267</td>
      <td>0.299663</td>
      <td>6</td>
      <td>0.30</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Fare</td>
      <td>cont</td>
      <td>&gt;=</td>
      <td>1.050000e+01</td>
      <td>0</td>
      <td>285.0</td>
      <td>0.319865</td>
      <td>7.0</td>
      <td>0.35</td>
      <td>2.713119e-03</td>
      <td>285</td>
      <td>0.319865</td>
      <td>7</td>
      <td>0.35</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Fare</td>
      <td>cont</td>
      <td>ELSE</td>
      <td>1.000000e+09</td>
      <td>0</td>
      <td>324.0</td>
      <td>0.363636</td>
      <td>7.0</td>
      <td>0.35</td>
      <td>5.211984e-04</td>
      <td>324</td>
      <td>0.363636</td>
      <td>7</td>
      <td>0.35</td>
    </tr>
  </tbody>
</table>
</div>




```python
# Scenario 2 
PSI_Calc(feature_list=['Age', 'Fare']
         , data_cutdf_path= userdir + 'PSI_test1_detailedCut_df.csv'
         , psi_sig_pct=0.005
         , userdir=userdir
         , prefix='PSI_test2'
         , special_value_df= pd.DataFrame({'var':['Age', 'Fare' , 'History'], 'special':[[0], [0,1,2], [99]]})
         , df_new=dataset.iloc[0:800,:]
         , documented_cutoff_dict={}
         , orig_wt=''
         , new_wt='')
```

    This is the PSI_Calc func version 3.0
    Processing Age
    Processing Fare
    PSI Calculation Finished.
    


```python
PSI_output_test2 = pd.read_csv( userdir + 'PSI_test2_detailedCut_df.csv')
PSI_output_test2
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>var</th>
      <th>type</th>
      <th>sign</th>
      <th>cutoff</th>
      <th>varBin</th>
      <th>obs</th>
      <th>obsPct</th>
      <th>newobs</th>
      <th>newpct</th>
      <th>psi_bin</th>
      <th>raw_obs</th>
      <th>raw_obsPct</th>
      <th>raw_newobs</th>
      <th>raw_newpct</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Age</td>
      <td>Missing</td>
      <td>=</td>
      <td>-9.999999e+06</td>
      <td>0</td>
      <td>177.0</td>
      <td>0.198653</td>
      <td>163.0</td>
      <td>0.20375</td>
      <td>1.291181e-04</td>
      <td>177</td>
      <td>0.198653</td>
      <td>163</td>
      <td>0.20375</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Age</td>
      <td>Special</td>
      <td>=</td>
      <td>0.000000e+00</td>
      <td>0</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>0.0</td>
      <td>0.00000</td>
      <td>0.000000e+00</td>
      <td>0</td>
      <td>0.000000</td>
      <td>0</td>
      <td>0.00000</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Age</td>
      <td>cont</td>
      <td>&gt;=</td>
      <td>3.250000e+01</td>
      <td>0</td>
      <td>268.0</td>
      <td>0.300786</td>
      <td>241.0</td>
      <td>0.30125</td>
      <td>7.163553e-07</td>
      <td>268</td>
      <td>0.300786</td>
      <td>241</td>
      <td>0.30125</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Age</td>
      <td>cont</td>
      <td>ELSE</td>
      <td>1.000000e+09</td>
      <td>0</td>
      <td>446.0</td>
      <td>0.500561</td>
      <td>396.0</td>
      <td>0.49500</td>
      <td>6.212959e-05</td>
      <td>446</td>
      <td>0.500561</td>
      <td>396</td>
      <td>0.49500</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Fare</td>
      <td>Missing</td>
      <td>=</td>
      <td>-9.999999e+06</td>
      <td>0</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>0.0</td>
      <td>0.00000</td>
      <td>0.000000e+00</td>
      <td>0</td>
      <td>0.000000</td>
      <td>0</td>
      <td>0.00000</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Fare</td>
      <td>Special</td>
      <td>=</td>
      <td>0.000000e+00</td>
      <td>0</td>
      <td>15.0</td>
      <td>0.016835</td>
      <td>12.0</td>
      <td>0.01500</td>
      <td>2.117809e-04</td>
      <td>15</td>
      <td>0.016835</td>
      <td>12</td>
      <td>0.01500</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Fare</td>
      <td>Special</td>
      <td>=</td>
      <td>1.000000e+00</td>
      <td>0</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>0.0</td>
      <td>0.00000</td>
      <td>0.000000e+00</td>
      <td>0</td>
      <td>0.000000</td>
      <td>0</td>
      <td>0.00000</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Fare</td>
      <td>Special</td>
      <td>=</td>
      <td>2.000000e+00</td>
      <td>0</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>0.0</td>
      <td>0.00000</td>
      <td>0.000000e+00</td>
      <td>0</td>
      <td>0.000000</td>
      <td>0</td>
      <td>0.00000</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Fare</td>
      <td>cont</td>
      <td>&gt;=</td>
      <td>2.772080e+01</td>
      <td>0</td>
      <td>267.0</td>
      <td>0.299663</td>
      <td>240.0</td>
      <td>0.30000</td>
      <td>3.781026e-07</td>
      <td>267</td>
      <td>0.299663</td>
      <td>240</td>
      <td>0.30000</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Fare</td>
      <td>cont</td>
      <td>&gt;=</td>
      <td>1.050000e+01</td>
      <td>0</td>
      <td>285.0</td>
      <td>0.319865</td>
      <td>259.0</td>
      <td>0.32375</td>
      <td>4.689423e-05</td>
      <td>285</td>
      <td>0.319865</td>
      <td>259</td>
      <td>0.32375</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Fare</td>
      <td>cont</td>
      <td>ELSE</td>
      <td>1.000000e+09</td>
      <td>0</td>
      <td>324.0</td>
      <td>0.363636</td>
      <td>289.0</td>
      <td>0.36125</td>
      <td>1.571212e-05</td>
      <td>324</td>
      <td>0.363636</td>
      <td>289</td>
      <td>0.36125</td>
    </tr>
  </tbody>
</table>
</div>




```python
# Scenario 3 
PSI_Calc(feature_list=['Age', 'Fare']
         , tile_pct=0.2
         , round_digit=9
         , data_cutdf_path=''
         , fixed_pct=0.05
         , psi_sig_pct=0.005
         , userdir=userdir
         , prefix='PSI_test3'
         , df_orig=dataset
         , df_new=dataset.iloc[0:800,:]
         , documented_cutoff_dict={}
         , orig_wt='wt'
         , new_wt='wt')
```

    This is the PSI_Calc func version 3.0
    Processing Age
    Processing Fare
    PSI Calculation Finished.
    


```python
PSI_output_test3 = pd.read_csv( userdir + 'PSI_test3_detailedCut_df.csv')
PSI_output_test3
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>var</th>
      <th>type</th>
      <th>sign</th>
      <th>cutoff</th>
      <th>varBin</th>
      <th>obs</th>
      <th>obsPct</th>
      <th>newobs</th>
      <th>newpct</th>
      <th>psi_bin</th>
      <th>raw_obs</th>
      <th>raw_obsPct</th>
      <th>raw_newobs</th>
      <th>raw_newpct</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Age</td>
      <td>Missing</td>
      <td>=</td>
      <td>-9.999999e+06</td>
      <td>0</td>
      <td>504.00</td>
      <td>0.216588</td>
      <td>467.00</td>
      <td>0.222912</td>
      <td>0.000182</td>
      <td>177</td>
      <td>0.198653</td>
      <td>163</td>
      <td>0.20375</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Age</td>
      <td>cont</td>
      <td>&gt;=</td>
      <td>3.400000e+01</td>
      <td>0</td>
      <td>483.75</td>
      <td>0.207886</td>
      <td>433.75</td>
      <td>0.207041</td>
      <td>0.000003</td>
      <td>251</td>
      <td>0.281706</td>
      <td>227</td>
      <td>0.28375</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Age</td>
      <td>cont</td>
      <td>&gt;=</td>
      <td>2.500000e+01</td>
      <td>0</td>
      <td>480.25</td>
      <td>0.206382</td>
      <td>422.25</td>
      <td>0.201551</td>
      <td>0.000114</td>
      <td>185</td>
      <td>0.207632</td>
      <td>161</td>
      <td>0.20125</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Age</td>
      <td>cont</td>
      <td>ELSE</td>
      <td>1.000000e+09</td>
      <td>0</td>
      <td>859.50</td>
      <td>0.369360</td>
      <td>772.25</td>
      <td>0.368616</td>
      <td>0.000001</td>
      <td>278</td>
      <td>0.312009</td>
      <td>249</td>
      <td>0.31125</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Fare</td>
      <td>Missing</td>
      <td>=</td>
      <td>-9.999999e+06</td>
      <td>0</td>
      <td>0.00</td>
      <td>0.000000</td>
      <td>0.00</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>0</td>
      <td>0.000000</td>
      <td>0</td>
      <td>0.00000</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Fare</td>
      <td>cont</td>
      <td>&gt;=</td>
      <td>4.710000e+01</td>
      <td>0</td>
      <td>465.25</td>
      <td>0.199936</td>
      <td>424.75</td>
      <td>0.202745</td>
      <td>0.000039</td>
      <td>165</td>
      <td>0.185185</td>
      <td>151</td>
      <td>0.18875</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Fare</td>
      <td>cont</td>
      <td>&gt;=</td>
      <td>2.325000e+01</td>
      <td>0</td>
      <td>466.75</td>
      <td>0.200580</td>
      <td>404.50</td>
      <td>0.193079</td>
      <td>0.000286</td>
      <td>183</td>
      <td>0.205387</td>
      <td>162</td>
      <td>0.20250</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Fare</td>
      <td>cont</td>
      <td>&gt;=</td>
      <td>1.247500e+01</td>
      <td>0</td>
      <td>469.00</td>
      <td>0.201547</td>
      <td>434.00</td>
      <td>0.207160</td>
      <td>0.000154</td>
      <td>164</td>
      <td>0.184063</td>
      <td>152</td>
      <td>0.19000</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Fare</td>
      <td>cont</td>
      <td>&gt;=</td>
      <td>7.895800e+00</td>
      <td>0</td>
      <td>463.50</td>
      <td>0.199183</td>
      <td>408.50</td>
      <td>0.194988</td>
      <td>0.000089</td>
      <td>194</td>
      <td>0.217733</td>
      <td>170</td>
      <td>0.21250</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Fare</td>
      <td>cont</td>
      <td>ELSE</td>
      <td>1.000000e+09</td>
      <td>0</td>
      <td>463.25</td>
      <td>0.199076</td>
      <td>423.25</td>
      <td>0.202029</td>
      <td>0.000043</td>
      <td>185</td>
      <td>0.207632</td>
      <td>165</td>
      <td>0.20625</td>
    </tr>
  </tbody>
</table>
</div>




```python
# Scenario 4 
PSI_Calc(feature_list=['Age', 'Fare']
         , round_digit=9
         , data_cutdf_path=''
         , psi_sig_pct=0.005
         , userdir=userdir
         , prefix='PSI_test4'
         , df_orig=dataset
         , df_new=dataset.iloc[0:800,:]
         , documented_cutoff_dict={'Age':[60,40,20], 'Fare':[25,20,15]}
         , orig_wt='wt'
         , new_wt='wt')
```

    This is the PSI_Calc func version 3.0
    Processing Age
    Processing Fare
    PSI Calculation Finished.
    


```python
PSI_output_test4 = pd.read_csv( userdir + 'PSI_test4_detailedCut_df.csv')
PSI_output_test4
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>var</th>
      <th>type</th>
      <th>sign</th>
      <th>cutoff</th>
      <th>varBin</th>
      <th>obs</th>
      <th>obsPct</th>
      <th>newobs</th>
      <th>newpct</th>
      <th>psi_bin</th>
      <th>raw_obs</th>
      <th>raw_obsPct</th>
      <th>raw_newobs</th>
      <th>raw_newpct</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Age</td>
      <td>Missing</td>
      <td>=</td>
      <td>-9999999</td>
      <td>0</td>
      <td>504.00</td>
      <td>0.216588</td>
      <td>467.00</td>
      <td>0.222912</td>
      <td>1.819950e-04</td>
      <td>177</td>
      <td>0.198653</td>
      <td>163</td>
      <td>0.20375</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Age</td>
      <td>cont</td>
      <td>&gt;=</td>
      <td>60</td>
      <td>0</td>
      <td>40.50</td>
      <td>0.017404</td>
      <td>36.00</td>
      <td>0.017184</td>
      <td>2.814288e-06</td>
      <td>26</td>
      <td>0.029181</td>
      <td>24</td>
      <td>0.03000</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Age</td>
      <td>cont</td>
      <td>&gt;=</td>
      <td>40</td>
      <td>0</td>
      <td>271.25</td>
      <td>0.116566</td>
      <td>242.25</td>
      <td>0.115632</td>
      <td>7.512885e-06</td>
      <td>137</td>
      <td>0.153760</td>
      <td>125</td>
      <td>0.15625</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Age</td>
      <td>cont</td>
      <td>ELSE</td>
      <td>999999999</td>
      <td>0</td>
      <td>1511.75</td>
      <td>0.649656</td>
      <td>1350.00</td>
      <td>0.644391</td>
      <td>4.283967e-05</td>
      <td>551</td>
      <td>0.618406</td>
      <td>488</td>
      <td>0.61000</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Fare</td>
      <td>Missing</td>
      <td>=</td>
      <td>-9999999</td>
      <td>0</td>
      <td>0.00</td>
      <td>0.000000</td>
      <td>0.00</td>
      <td>0.000000</td>
      <td>0.000000e+00</td>
      <td>0</td>
      <td>0.000000</td>
      <td>0</td>
      <td>0.00000</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Fare</td>
      <td>cont</td>
      <td>&gt;=</td>
      <td>25</td>
      <td>0</td>
      <td>890.50</td>
      <td>0.382682</td>
      <td>797.50</td>
      <td>0.380668</td>
      <td>1.062007e-05</td>
      <td>334</td>
      <td>0.374860</td>
      <td>302</td>
      <td>0.37750</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Fare</td>
      <td>cont</td>
      <td>&gt;=</td>
      <td>20</td>
      <td>0</td>
      <td>127.50</td>
      <td>0.054792</td>
      <td>117.75</td>
      <td>0.056205</td>
      <td>3.601149e-05</td>
      <td>42</td>
      <td>0.047138</td>
      <td>39</td>
      <td>0.04875</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Fare</td>
      <td>cont</td>
      <td>ELSE</td>
      <td>999999999</td>
      <td>0</td>
      <td>1309.75</td>
      <td>0.562849</td>
      <td>1179.75</td>
      <td>0.563126</td>
      <td>1.366135e-07</td>
      <td>515</td>
      <td>0.578002</td>
      <td>459</td>
      <td>0.57375</td>
    </tr>
  </tbody>
</table>
</div>


