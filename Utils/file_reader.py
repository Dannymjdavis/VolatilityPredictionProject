import pandas as pd
import os

# READ FILE
def read_file(file_path, file_name, kind='parquet') -> pd.DataFrame :
    '''
    Opens local file

    Parameters
    ----------
    file_path: str
        Raw string of local folder to locate file.
    file_name: str
        Name of the file.
    kind: str
        Choose between parquet, csv, excel
    '''
    joint_path = os.path.join(file_path, file_name)

    if kind=='csv':
        df = pd.read_csv(joint_path)
    elif kind=='excel':
        df = pd.read_excel(joint_path)
    else:
        df = pd.read_parquet(joint_path)
    
    return df