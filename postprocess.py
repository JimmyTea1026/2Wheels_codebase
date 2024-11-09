import re 
import pandas as pd
import os 
import df_setting
import cv2
import video_handler
from concurrent.futures import ThreadPoolExecutor, as_completed  

def main():
    camera_type = "front195"
    root_path = r"/media/alva/COMPAL02/Jimmy_2_wheel/road/F195/data/bad/to_run/test"
    save_path = r"/media/alva/COMPAL02/Jimmy_2_wheel/road/F195/v10_processed/test"
    batch_run(camera_type, root_path, save_path)
    
    # single_run(camera_type, root_path, save_path)

def batch_run(camera_type, root_path, save_path):
    # 將 filein 結束的 processed 資料夾放到 to_run 資料夾
    # 跑完的 rear/front.txt 要放到 processed 資料夾
    # 並在 to_run 資料夾中要有之前建立的 num.txt，以便後續切割
        
    processed_path = os.path.join(root_path, "processed")
    num_path = os.path.join(root_path, "num.txt")
    xlsx_path = os.path.join(processed_path, f"{camera_type}.xlsx")
        
    # 1. 將 txt 檔案中的 log 資訊提取出來，並寫入 xlsx 檔案
    # 2. 將 xlsx 檔案根據 num.txt 切割成多個 xlsx 檔案
    # 3. 將 processed 資料夾中的 yuv 檔案根據 num.txt 切割成多個資料夾
    extract_log(camera_type,processed_path)
    print("extract log done")
    
    split_xlsx(num_path, xlsx_path)
    print("split xlsx done")
     
    split_image(num_path, processed_path)
    print("split image done")
    
    # 4. 開始合成影片
    folders = [f for f in os.listdir(processed_path) if os.path.isdir(os.path.join(processed_path, f))] 
    # video_synthesis(folders[10], processed_path, save_path, camera_type)
    # return 
    with ThreadPoolExecutor(max_workers=6) as executor:  
        # 提交所有資料夾的處理任務  
        futures = {executor.submit(video_synthesis, folder, processed_path, save_path, camera_type): folder for folder in folders}  
        
        for future in as_completed(futures):  
            folder = futures[future]  
            try:  
                future.result()  
                print(f"Processed folder: {folder}")  
            except Exception as e:  
                print(f"Error processing folder {folder}: {e}")  
    
def single_run(camera_type, root_path, save_path):        
    # 1. 將 txt 檔案中的 log 資訊提取出來，並寫入 xlsx 檔案
    extract_log(camera_type,root_path)
    print("extract log done")
    xlsx_file = [f for f in os.listdir(root_path) if f.endswith('.xlsx')][0]
    xlsx_path = os.path.join(root_path, xlsx_file)
    # 2. 開始合成影片
    video_synthesis(root_path, xlsx_path, save_path, camera_type)
    

def video_synthesis(folder, processed_path, save_path, camera_type):
    infos = {
        "yuv_width":1920,
        "yuv_height":1280,
        "resize_width":1920,
        "resize_height":1280,
        "fourcc":cv2.VideoWriter_fourcc(*'mp4v'),
        "fps":9,
        "version":"v10_0.03test",
        "camera_type":camera_type
    }
    
    folder_path = os.path.join(processed_path, folder)  
    if os.path.isdir(folder_path):  
        # 過濾出所有 .xlsx 檔案  
        xlsx_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]  
        if xlsx_files:  
            xlsx_path = os.path.join(folder_path, xlsx_files[0])  
            video_handler.video_processing(folder_path, xlsx_path, save_path, infos) 
        else:  
            print(f"No .xlsx file found in {folder_path}")


def split_xlsx(num_path, xlsx_path):
    # 透過 num.txt 中紀錄的各影片的幀數，將 xlsx 檔案切割成多個 xlsx 檔案並放進影片的資料夾中
    
    root_path = os.path.dirname(xlsx_path)
    start = 0
    df = pd.read_excel(xlsx_path)
    
    with open(num_path, "r") as rf:
        lines = rf.readlines()
        for line in lines:
            infos = line.strip().split(" ")
            folder, num = infos[0], infos[1]
            target_folder = os.path.join(root_path, folder)
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
            
            # 讀取指定範圍的行
            selected_rows = df.iloc[start:start+int(num)]
            
            # selected_rows 第一行是數字，把他從0開始重新編號
            selected_rows.iloc[:, 0] = range(len(selected_rows))
        
            # 讀取標題行
            header = pd.DataFrame(columns=df.columns)
            
            # 將標題行與選定的行合併
            selected_rows_with_header = pd.concat([header, selected_rows])
            
            folder_name = os.path.basename(os.path.normpath(target_folder))
            output_file_path = os.path.join(target_folder, f"{folder_name}.xlsx")
            # 將選定的行另存為新的 Excel 檔案
            selected_rows_with_header.to_excel(output_file_path, index=False)
                    
            start += int(num)

def split_image(num_path, processed_path):
    # 透過 num.txt 中紀錄的各影片的幀數，將 yuv 檔案切割成多個資料夾，並重新命名成 00000.yuv, 00001.yuv, ...
    
    all_images = os.listdir(processed_path)
    # 去掉格式不是.yuv的文件
    all_images = [image for image in all_images if image.endswith(".yuv")]
    all_images.sort()
    
    start = 0
    with open(num_path, "r") as rf:
        lines = rf.readlines()
        for line in lines:
            infos = line.strip().split(" ")
            folder, num = infos[0], infos[1]
            target_folder = os.path.join(processed_path, folder)
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
            
            idx = 0
            for i in range(start, start + int(num)):
                if i >= len(all_images):
                    break
                src_path = os.path.join(processed_path, all_images[i])
                dst_path = os.path.join(target_folder, "{:05d}.yuv".format(idx))
                os.rename(src_path, dst_path)
                idx += 1
            start += int(num)    
    
def extract_log(camera_type,root_path):
    # 透過 rear195.txt等 Log檔案，提取出所需的資訊，並寫入 xlsx 檔案

    df=df_setting.get_df(camera_type)
    frame=0
    message_dicarded=set()
    txt_path = os.path.join(root_path, f"{camera_type}.txt")
    with open(txt_path,'r') as f:
        for line in f:
            event=line
            if 'frame_number' in event:
                match_f=re.search('\d+',event)
                if not match_f:
                    print("no frame matched")
                    continue     
                frame=int(match_f.group())
                df.loc[len(df)] = [None] * len(df.columns)
                df.at[len(df) - 1, 'frame'] = frame
                # df.at[len(df) - 1, 'time']=time_stamp

            if 'Speed' in event:
                match_speed=re.search('\d+',event)
                speed = int(match_speed.group())
                df.at[len(df) - 1, 'speed']=int(speed)
            
            if 'Yaw' in event:
                match_yaw=re.search('\d+.\d+',event)
                yaw = float(match_yaw.group())
                df.at[len(df) - 1, 'yaw']=yaw
                
            if 'Roll' in event:
                match_roll=re.search('\d+.\d+',event)
                roll = float(match_roll.group())
                df.at[len(df) - 1, 'roll']=roll
                
            if 'Pitch' in event:
                match_pitch=re.search('\d+.\d+',event)
                pitch = float(match_pitch.group())
                df.at[len(df) - 1, 'pitch']=pitch
                
            df_setting.process_event(camera_type,event,df,message_dicarded)
           
    df_to_excel(df,camera_type, root_path)
    msg_discard=f"{root_path}/message_discarded_"+camera_type+".txt"
    with open(msg_discard,'w') as f:
        for i in message_dicarded:
            f.writelines(i)
            f.writelines('\n')
                  
def df_to_excel(df,camera_type, root_path):
    if camera_type == 'rear195':
        df.to_excel(os.path.join(root_path, "rear195.xlsx"), index=False)
    elif camera_type == 'front60':
        df.to_excel(os.path.join(root_path, "front60.xlsx"), index=False)
    elif camera_type == 'front195':
        df.to_excel(os.path.join(root_path, "front195.xlsx"), index=False)
    else:
        print("please check camera_type")
        input()

if __name__== '__main__':
    main()