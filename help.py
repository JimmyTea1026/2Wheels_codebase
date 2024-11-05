import pandas as pd
import os

def main():
    target_path = r"H:\Jimmy_2_wheel\road\R195\data\old_speed\bad"
    for folder in os.listdir(target_path):
        if folder == "to_run":
            continue
        folder_path = os.path.join(target_path, folder)
        folder_process(folder_path)
        
def folder_process(folder_path):
    folder = os.path.basename(folder_path)
    xlsx_path = os.path.join(folder_path, f"{folder}.xlsx")
    df = pd.read_excel(xlsx_path)
    df = fill_speed_gyro(df)
    df = cut_xlsx(folder_path, df)
    old_path = xlsx_path.replace(".xlsx", "_old.xlsx")
    os.rename(xlsx_path, old_path)
    df.to_excel(xlsx_path, index=False)
        
def cut_xlsx(folder_path, df):
    slice_path = os.path.join(folder_path, "sliced")
    if not os.path.exists(slice_path):
        return df
    frame_num = len(os.listdir(slice_path))
    # 第一行為header，把header與往下frame_num行的資料切出來
    df = df.iloc[:frame_num]
    return df

def fill_speed_gyro(df):  
    """  
    Fill the missing values of speed and gyro columns with the last valid value.  
    If the first value is missing, fill it with the first non-missing value in the column.  
    """  
    # Rename columns if they exist  
    if 'Speed' in df.columns:  
        df = df.rename(columns={'Speed': 'our_speed'})  
    if 'Pitch' in df.columns:  
        df = df.rename(columns={'Pitch': 'our_pitch'})  
    if 'Yaw' in df.columns:  
        df = df.rename(columns={'Yaw': 'our_yaw'})  
    if 'Roll' in df.columns:  
        df = df.rename(columns={'Roll': 'our_roll'})  

    # Fill missing values  
    for column in ['our_speed', 'our_pitch', 'our_yaw', 'our_roll']:  
        if column in df.columns:  
            # Check if the first value is NaN  
            if pd.isna(df[column].iloc[0]):  
                # Find the first non-missing value  
                first_valid_index = df[column].first_valid_index()  
                if first_valid_index is not None:  
                    first_valid_value = df[column].iloc[first_valid_index]  
                    # Fill the first NaN with the first valid value  
                    df[column].iloc[0] = first_valid_value  

            # Forward fill the rest  
            df[column] = df[column].fillna(method='ffill')  

    return df 

if __name__ == '__main__':
    main()