import shutil
import pandas as pd
import os 
import cv2
from tqdm import tqdm
from add_bounding_box import video_synthesis

def video_processing(folder_path, xlsx_path, save_path, infos):
    # folder_path 為 yuv 檔案所在資料夾
    # 會在save_path中根據folder_path中的資料夾名稱建立資料夾，並將影片存放在該資料夾中
    # infos 包含了影片的相關資訊，包括fps, fourcc, resize_width, resize_height, 
    # yuv_width, yuv_height, camera_type, version
    
    df = pd.read_excel(xlsx_path)
    folder = os.path.basename(folder_path)
    video_folder_path = os.path.join(save_path, folder)
    if not os.path.exists(video_folder_path):
        os.makedirs(video_folder_path)
    video_path = os.path.join(video_folder_path, f"{folder}.mp4")
    if os.path.exists(video_path):
        os.remove(video_path)
    video = cv2.VideoWriter(video_path, infos["fourcc"], infos["fps"], (infos["resize_width"], infos["resize_height"])) 
    
    yuv_images = os.listdir(folder_path)
    yuv_images = [yuv_image for yuv_image in yuv_images if yuv_image.endswith('.yuv')]
    yuv_images.sort()    
    vs = video_synthesis(infos["yuv_width"], infos["yuv_height"], df, infos["camera_type"])

    for yuv_image in tqdm(yuv_images, desc=f"{folder}"):
        yuv_path = os.path.join(folder_path, yuv_image)
        jpg_image = vs.draw_log(yuv_path)
        # 在右上角加上文字
        cv2.putText(jpg_image, infos["version"], (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 1)
        
        resize_image = cv2.resize(jpg_image, (infos["resize_width"], infos["resize_height"]), interpolation=cv2.INTER_LINEAR)
        # cv2.imshow('image', resize_image)
        # cv2.waitKey(1)
        video.write(resize_image)
                    
    video.release()  
    cv2.destroyAllWindows()
    
    print(f"影片已成功保存至：{video_path}")
    
    # 將xlsx也搬到save_path
    xlsx_save_path = os.path.join(save_path, folder)
    xlsx_save_path = os.path.join(xlsx_save_path, f"{folder}.xlsx")
    shutil.copyfile(xlsx_path, xlsx_save_path)
    print(f"xlsx已成功保存至：{xlsx_save_path}")
