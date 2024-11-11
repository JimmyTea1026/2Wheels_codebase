import shutil
import os
import cv2
import pandas as pd
  
def main():
    root_path = r"/media/alva/COMPAL02/Jimmy_2_wheel/road/R195/data/bad/to_run"
    run_video(root_path)
    
    
    # 將所有 yuv 檔案搬移到 all 資料夾中，並將 speed_gyro.txt 合併，將各個影片的frame數量寫入 num.txt
    # combine(root_path)
    # 檢查 all 資料夾中的 yuv 檔案是否有缺漏，若有缺漏則複製前後的 yuv 檔案
    # check(root_path)
    # 待all資料夾複製到SD卡後，將yuv還原至各自的資料夾中
    # put_images_back(root_path)
    

def video_to_yuv(video_path, dst_path, time_limit=1e9, FPS=0, flip=False):
    print(f"Processing video: {video_path}")
    
    # Check if destination folder exists, if not, create it
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)
    
    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    f = int(video_fps / FPS) + 1 if FPS > 0 else 1

    frame_count = 0
    idx = 0
    
    while True:
        frame_count += 1
        # Read next frame
        ret, frame = cap.read()

        # If we've processed the desired time limit, stop processing
        if frame_count >= video_fps * time_limit:
            break
        
        if not ret:
            # Skip corrupted frames or end of video
            if frame_count < total_frame_count:
                print(f"Warning: Skipping corrupted or unreadable frame {frame_count}")
                continue
            else:
                break  # End of video
        
        # If FPS is set, skip frames according to the frame interval (frame_count % f != 0)
        if FPS > 0 and frame_count % f != 0:
            continue
        
        # Resize and optionally flip the frame
        frame = cv2.resize(frame, (1920, 1280))
        if flip:
            frame = cv2.flip(frame, -1)

        # Convert to YUV I420 color format
        frame_yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV_I420)
        
        # Write to the destination file as a .yuv
        dst_file = os.path.join(dst_path, f"{idx:05d}.yuv")
        with open(dst_file, "wb") as wf:
            wf.write(frame_yuv.tobytes())
        
        # Increment index for the next frame
        idx += 1
    
    # Release video capture object when done
    cap.release()
 
def combine(root_path):
    # Travese all the subfolder in root_path, copy all the images in yuv folder into all folder

    dst_folder = os.path.join(root_path, "all")
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)
    
    idx = 0
    for folder in os.listdir(root_path):
        if not os.path.isdir(os.path.join(root_path, folder)) or folder=='all':
            continue
        tar_folder = os.path.join(root_path, folder)
        yuv_folder = os.path.join(tar_folder, "yuv")
        files = os.listdir(yuv_folder)
        files = [file for file in files if file.endswith(".yuv")]
        files.sort()
        # 搬移 yuv 檔案
        for file in files:
            tar_file = os.path.join(yuv_folder, file)
            dst_file = os.path.join(dst_folder, "{:05d}.yuv".format(idx))
            os.rename(tar_file, dst_file)
            idx += 1

        speed_line_num = 0       
        if os.path.exists(os.path.join(yuv_folder, "speed_gyro.txt")):
            with open(os.path.join(dst_folder, "speed_gyro.txt"), "a") as wf:
                with open(os.path.join(yuv_folder, "speed_gyro.txt"), "r") as rf:
                    lines = rf.readlines()
                    speed_line_num = len(lines)
                    for line in lines:
                        wf.write(line)
                    
        # 紀錄張數
        num_path = os.path.join(root_path, "num.txt")
        with open(num_path, "a") as wf:
            wf.write(f"{folder} {len(files)} {speed_line_num}\n")
    
def extract_from_sliced(input_folder, mp4_path):
    # Based on slices folder, find out which frame in the video should be extracted and save into yuv file

    plot_path = os.path.join(input_folder, "sliced")
    dst_path = os.path.join(input_folder, "yuv")
    
    image_names = []
    images = os.listdir(plot_path)
    images = [image.split(".")[0] for image in images]
    for image in images:
        image_names.append(int(image.split("_")[-1]))
    image_names.sort()
    
    # 用opencv讀取 mp4 影片，並將影片中的每一幀，依照 images 的順序，寫入到 dst_path 中
    # 存的格式為 yuv420，解析度為 1920x1280，檔名為 00000.yuv, 00001.yuv, ...
    cap = cv2.VideoCapture(mp4_path)
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)
    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx in image_names:
            frame = cv2.resize(frame, (1920, 1280))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV_I420)
            dst_file = os.path.join(dst_path, "{:05d}.yuv".format(idx))
            with open(dst_file, "wb") as wf:
                wf.write(frame.tobytes())
        idx += 1
    cap.release()

def reorder(dst_path):
    # #最後將 dst_path 中的 yuv 檔案，重新命名為 00000.yuv, 00001.yuv, ...
    files = os.listdir(dst_path)
    files.sort()
    for idx, file in enumerate(files):
        src_file = os.path.join(dst_path, file)
        dst_file = os.path.join(dst_path, "{:05d}.yuv".format(idx))
        os.rename(src_file, dst_file)
    
def extract_speed_gyro(xlsx_path):
    # 讀取 xlsx, and extract speed info and gyro info

    df = pd.read_excel(xlsx_path)

    # 檢查df 有無speed, pitch, yaw, roll欄位
    # 若沒有，則改抓 our_speed, our_pitch, our_yaw, our_roll
    
    if "speed" in df.columns:
        speed = df["speed"].values
        pitch = df["pitch"].values
        yaw = df["yaw"].values
        roll = df["roll"].values
    else:
        speed = df["our_speed"].values
        pitch = df["our_pitch"].values
        yaw = df["our_yaw"].values
        roll = df["our_roll"].values
    

    base_path = os.path.dirname(xlsx_path)
    txt_path = os.path.join(base_path, "yuv/speed_gyro.txt")
    if os.path.exists(txt_path):
        os.remove(txt_path)
    with(open(txt_path, "w")) as wf:
        for i in range(len(speed)):
            if pd.isnull(speed[i]):
                continue
            wf.write(f"{int(speed[i])} {pitch[i]} {yaw[i]} {roll[i]}\n")

def check(root_path):
    # check any miising image in all folder

    all_path = os.path.join(root_path, "all")
    num_path = os.path.join(root_path, "num.txt")
    all_num = 0
    
    with open(num_path, "r") as rf:
        lines = rf.readlines()
        for line in lines:
            infos = line.strip().split(" ")
            folder, num = infos[0], infos[1]
            all_num += int(num)
    
    for i in range(all_num):
        file_path = os.path.join(all_path, "{:05d}.yuv".format(i))
        if not os.path.exists(file_path):
            print(f"{file_path} not exists")
            pre = os.path.join(all_path, "{:05d}.yuv".format(i-1))
            post = os.path.join(all_path, "{:05d}.yuv".format(i+1))
            if os.path.exists(pre):
                shutil.copyfile(pre, file_path)
            elif os.path.exists(post):
                shutil.copyfile(post, file_path)

def yuv_generation(folder_path):
    # 根據will 拿來的log與圖片，生成filein用的yuv檔案
    input_folder = os.path.basename(folder_path)
    yuv_path = os.path.join(folder_path, "yuv")
    if os.path.exists(yuv_path):
        return
    
    xlsx_path = os.path.join(folder_path, f"{input_folder}.xlsx")
    mp4_path = os.path.join(folder_path, f"{input_folder}.mp4")
    
    print(f"Start {input_folder}")
    # 1. 根據 sliced 資料夾中的圖片，從 mp4 中選出對應的 yuv 檔案
    extract_from_sliced(folder_path, mp4_path)
    # 2. 將 yuv 檔案重新命名為 00000.yuv, 00001.yuv, ...
    reorder(os.path.join(folder_path, "yuv")) 
    # 3. 將 xlsx 中的 speed, pitch, yaw, roll 寫入到 speed_gyro.txt 中
    extract_speed_gyro(xlsx_path)
    
    print(f"Finish {input_folder}")
    
def put_images_back(root_path):
    # Based on num.txt, put all images in all back to original yuv folder, and rename the images from 00000.yuv 00001.yuv ......

    num_path = os.path.join(root_path, "num.txt")
    all_path = os.path.join(root_path, "all")
    images = os.listdir(all_path)
    images = [image for image in images if image.endswith(".yuv")]
    images.sort()
    start = 0
    
    with open(num_path, "r") as rf:
        lines = rf.readlines()
        for line in lines:
            infos = line.strip().split(" ")
            folder, num = infos[0], infos[1]
            target_folder = os.path.join(root_path, folder, "yuv")
            
            idx = 0
            for i in range(start, start + int(num)):
                src_path = os.path.join(all_path, images[i])
                dst_path = os.path.join(target_folder, "{:05d}.yuv".format(idx))
                os.rename(src_path, dst_path)
                idx += 1
            start += int(num)

def run_video(root_path):
    # Will會提供sliced資料夾，裡面有圖片，以及對應的xlsx檔案，以及mp4檔案
    all_folders = os.listdir(root_path)
    for folder in all_folders:
        folder_path = os.path.join(root_path, folder)
        sliced_path = os.path.join(folder_path, "sliced")
        mp4_path = os.path.join(folder_path, f"{folder}.mp4")
        yuv_path = os.path.join(folder_path, "yuv")
        if not os.path.exists(yuv_path):
            if os.path.exists(sliced_path):
                yuv_generation(folder_path)
            else:
                video_to_yuv(mp4_path, yuv_path, FPS=10)


if __name__ == "__main__":
    main()