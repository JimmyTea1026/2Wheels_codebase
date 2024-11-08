import re 
import pandas as pd
import os
import cv2
import re
import numpy as np

class video_synthesis:
    object_class = {0:"human", 
                    1:"bike",
                    2:"car",
                    3:"motor",
                    4:"bus",
                    5:"truck",
                    6:"long_truck",
                    7:"other",}
    status = {}
    width = 1920
    height = 1280
    df = None
    i = 0
    file_type = None
    
    def __init__(self, width, height, df, file_type):
        self.width = width
        self.height = height
        self.df = df
        self.file_type = file_type
        if file_type == "rear195":
            self.status = {"scenario5_left":"None", "scenario5_right":"None", "scenario4":"None"}
        elif file_type == "front195":
            self.status = {"scenario2_left":"None", "scenario3_left":"None", "scenario2_right":"None", "scenario3_right":"None"}
        elif file_type == "front60":
            self.status = {"scenario1":"None"}

    def yuv_to_rgb(self, yuv_path):
        width = self.width
        height = self.height
        # 計算 YUV 影像的大小
        frame_size = width * height
        yuv_size = frame_size + (frame_size // 2)  # YUV 4:2:0 的格式

        # 讀取 YUV 影像
        with open(yuv_path, 'rb') as f:
            yuv_data = np.frombuffer(f.read(), dtype=np.uint8)

        # 檢查 YUV 資料大小是否正確
        assert len(yuv_data) == yuv_size, f"YUV data size mismatch. Expected {yuv_size}, got {len(yuv_data)}."

        # 提取 Y, U, V 平面
        y_plane = yuv_data[0:frame_size].reshape((height, width))
        u_plane = yuv_data[frame_size:frame_size + (frame_size // 4)].reshape((height // 2, width // 2))
        v_plane = yuv_data[frame_size + (frame_size // 4):].reshape((height // 2, width // 2))

        # 將 U 和 V 平面擴展到與 Y 平面相同的大小
        u_plane = cv2.resize(u_plane, (width, height), interpolation=cv2.INTER_LINEAR)
        v_plane = cv2.resize(v_plane, (width, height), interpolation=cv2.INTER_LINEAR)

        # 合併 Y, U, V 到單個 3 通道的 YUV420 影像
        yuv_image = cv2.merge([y_plane, u_plane, v_plane])

        # 將 YUV420 轉換為 RGB
        rgb_image = cv2.cvtColor(yuv_image, cv2.COLOR_YUV2BGR)
        
        return rgb_image

    def draw_log(self, yuv_path):
        
        rgb_image = self.yuv_to_rgb(yuv_path)
        
        bgr_image = self.add_bounding_box(rgb_image)
        
        self.i += 1

        return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        
    def add_bounding_box(self, image):
        if self.i >= len(self.df):
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            return image_bgr
        
        if self.file_type=="rear195":
            self.process_rear195(image)  
            image=self.r195_plot(image)
        elif self.file_type=="front195":
            self.process_front195(image) 
            image=self.f195_plot(image)
        elif self.file_type=="front60":
            self.processing_front60(image)
            image=self.f60_plot(image)
        else:
            print("please check processing   >> file.xlsx")
            input()

        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return image_bgr

    def add_speed_gyro(self, image, df, i):
        speed, pitch, yaw, roll = 0, 0, 0, 0
        if not pd.isnull(df.at[i, 'our_speed']):
            speed = df.at[i, 'our_speed']
        if not pd.isnull(df.at[i, 'our_pitch']):
            pitch = df.at[i, 'our_pitch']
        if not pd.isnull(df.at[i, 'our_yaw']):
            yaw = df.at[i, 'our_yaw']
        if not pd.isnull(df.at[i, 'our_roll']):
            roll = df.at[i, 'our_roll']
        
        self.set_label(image, f"speed: {speed}", 10, 150, 1.5, (0, 165, 255), thickness=3)
        self.set_label(image, f"pitch: {pitch}", 10, 250, 1.5, (0, 165, 255), thickness=3)
        self.set_label(image, f"yaw: {yaw}", 10, 350, 1.5, (0, 165, 255), thickness=3)
        self.set_label(image, f"roll: {roll}", 10, 450, 1.5, (0, 165, 255), thickness=3)

    def r195_plot(self, image):
        df = self.df
        i = self.i
        if pd.isnull(df.at[i,'Scenario2_nearest object']): 
            s2x1,s2y1,s2x2,s2y2=0, 0, 0, 0
        else:
            match=re.findall(r"\d+\.\d+",df.at[i,'Scenario2_nearest object'])#---------S2
            if match:
                b_box = [int(float(num)) for num in match]
                s2x1,s2y1,s2x2,s2y2=b_box[0],b_box[1],b_box[2],b_box[3]
            
        if pd.isnull(df.at[i,'Scenario4_nearest object']):
            s4x1,s4y1,s4x2,s4y2=0, 0, 0, 0
        else:
            match=re.findall(r"\d+\.\d+",df.at[i,'Scenario4_nearest object'])#---------S4
            if match:
                b_box = [int(float(num)) for num in match]
                s4x1,s4y1,s4x2,s4y2=b_box[0],b_box[1],b_box[2],b_box[3]
            
        
        if pd.isnull(df.at[i,'Scenario5_nearest object left']):
            s5lx1,s5ly1,s5lx2,s5ly2=0, 0, 0, 0
        else:
            match=re.findall(r"\d+\.\d+",df.at[i,'Scenario5_nearest object left'])#---------S5L
            if match:
                b_box = [int(float(num)) for num in match]
                s5lx1,s5ly1,s5lx2,s5ly2=b_box[0],b_box[1],b_box[2],b_box[3]
            
            
        if pd.isnull(df.at[i,'Scenario5_nearest object right']):
            s5rx1,s5ry1,s5rx2,s5ry2=0, 0, 0, 0
        else:
            match=re.findall(r"\d+\.\d+",df.at[i,'Scenario5_nearest object right'])#---------S5R
            if match:
                b_box = [int(float(num)) for num in match]
                s5rx1,s5ry1,s5rx2,s5ry2=b_box[0],b_box[1],b_box[2],b_box[3]
        
        if pd.isnull(df.at[i, 'Scenario2 target obj kph']):
            s2_target_obj_kph = -1
        else:
            s2_target_obj_kph = df.at[i, 'Scenario2 target obj kph']
        
        if pd.isnull(df.at[i, 'Scenario4 target obj kph']):
            s4_target_obj_kph = -1
        else:
            s4_target_obj_kph = df.at[i, 'Scenario4 target obj kph']
        
        cv2.rectangle(image, (int(s2x1*1920/480), int(s2y1*1280/480)), (int(s2x2*1920/480),int(s2y2*1280/480)), (255, 0, 0), 2)
        cv2.rectangle(image, (int(s4x1*1920/480), int(s4y1*1280/480)), (int(s4x2*1920/480), int(s4y2*1280/480)), (255, 0, 0), 2)
        cv2.rectangle(image, (int(s5lx1*1920/480), int(s5ly1*1280/480)), (int(s5lx2*1920/480), int(s5ly2*1280/480)), (255, 0, 0), 2)
        cv2.rectangle(image, (int(s5rx1*1920/480), int(s5ry1*1280/480)), (int(s5rx2*1920/480), int(s5ry2*1280/480)), (255, 0, 0), 2)

        
        if s2_target_obj_kph != -1:
            self.set_label(image, f"S2_target_obj_kph: {s2_target_obj_kph}", 300, 150, 1.5, (0, 165, 255), thickness=3)
        if s4_target_obj_kph != -1:
            self.set_label(image, f"S4_target_obj_kph: {s4_target_obj_kph}", 300, 250, 1.5, (0, 165, 255), thickness=3)
            
        if self.status["scenario5_left"] != "None":
            self.set_label(image, f"Scenario5_left: {self.status['scenario5_left']}", 900, 50, 1.5, (0, 0, 255), thickness=3)
        if self.status["scenario5_right"] != "None":
            self.set_label(image, f"Scenario5_right: {self.status['scenario5_right']}", 900, 100, 1.5, (0, 0, 255), thickness=3)
        if self.status["scenario4"] != "None":
            self.set_label(image, f"Scenario4: {self.status['scenario4']}", 900, 150, 1.5, (0, 0, 255), thickness=3)
        
        # object class
        if pd.isnull(df.at[i, 'Scenario5 object class left']):
            s5_obj_class_left = -1
        else:
            s5_obj_class_left = df.at[i, 'Scenario5 object class left']
            s5_obj_class_left = self.object_class[s5_obj_class_left]
        if pd.isnull(df.at[i, 'Scenario5 object conf left']):
            s5_obj_conf_left = -1
        else:
            s5_obj_conf_left = df.at[i, 'Scenario5 object conf left']
            
        if pd.isnull(df.at[i, 'Scenario5 object class right']):
            s5_obj_class_right = -1
        else:
            s5_obj_class_right = df.at[i, 'Scenario5 object class right']
            s5_obj_class_right = self.object_class[s5_obj_class_right]
        if pd.isnull(df.at[i, 'Scenario5 object conf right']):
            s5_obj_conf_right = -1
        else:
            s5_obj_conf_right = df.at[i, 'Scenario5 object conf right']
            
        if pd.isnull(df.at[i, 'Scenario2 object class']):
            s2_obj_class = -1
        else:
            s2_obj_class = df.at[i, 'Scenario2 object class']
            s2_obj_class = self.object_class[s2_obj_class]
        if pd.isnull(df.at[i, 'Scenario2 object conf']):
            s2_obj_conf = -1
        else:
            s2_obj_conf = df.at[i, 'Scenario2 object conf']
            
        if pd.isnull(df.at[i, 'Scenario4 object class']):
            s4_obj_class = -1
        else:
            s4_obj_class = df.at[i, 'Scenario4 object class']
            s4_obj_class = self.object_class[s4_obj_class]
        if pd.isnull(df.at[i, 'Scenario4 object conf']):
            s4_obj_conf = -1
        else:
            s4_obj_conf = df.at[i, 'Scenario4 object conf']
        
        if s2x1 != 0 or s2y1 != 0:
            if s2_obj_class != -1:
                self.set_label(image, f"S2_obj_class: {s2_obj_class}", int(s2x1*1920/480),int(s2y1*1280/480))
            if s2_obj_conf != -1:
                self.set_label(image, f"S2_obj_conf: {s2_obj_conf}", int(s2x1*1920/480),int(s2y1*1280/480)+20)
        if s4x1 != 0 or s4y1 != 0:
            if s4_obj_class != -1:
                self.set_label(image, f"S4_obj_class: {s4_obj_class}", int(s4x1*1920/480),int(s4y1*1280/480+40))
            if s4_obj_conf != -1:
                self.set_label(image, f"S4_obj_conf: {s4_obj_conf}", int(s4x1*1920/480),int(s4y1*1280/480)+60)
        if s5lx1 != 0 or s5ly1 != 0:
            if s5_obj_class_left != -1:
                self.set_label(image, f"S5_obj_class_left: {s5_obj_class_left}", int(s5lx1*1920/480),int(s5ly1*1280/480)+80)    
            if s5_obj_conf_left != -1:
                self.set_label(image, f"S5_obj_conf_left: {s5_obj_conf_left}", int(s5lx1*1920/480),int(s5ly1*1280/480)+100)
        if s5rx1 != 0 or s5ry1 != 0:
            if s5_obj_class_right != -1:
                self.set_label(image, f"S5_obj_class_right: {s5_obj_class_right}", int(s5rx1*1920/480),int(s5ry1*1280/480)+120)
            if s5_obj_conf_right != -1:
                self.set_label(image, f"S5_obj_conf_right: {s5_obj_conf_right}", int(s5rx1*1920/480),int(s5ry1*1280/480)+140)
            
        #  ---------------- EQB ----------------  #
        if pd.isnull(df.at[i, 'Scenario5 EQB left']):
            s5_eqb_left = -1
        else:
            s5_eqb_left = df.at[i, 'Scenario5 EQB left']
            s5_eqb_left = s5_eqb_left.replace("[", "")
            s5_eqb_left = s5_eqb_left.replace("]", "")
            s5_eqb_left = s5_eqb_left.replace(" ", "")
            # 共有四組xy，要x1,y1,x2,y2,x3,y3,x4,y4
            s5_eqb_left_x1, s5_eqb_left_y1, s5_eqb_left_x2, s5_eqb_left_y2, \
            s5_eqb_left_x3, s5_eqb_left_y3, s5_eqb_left_x4, s5_eqb_left_y4 = map(int, s5_eqb_left.split(","))
            
        if pd.isnull(df.at[i, 'Scenario5 EQB right']):
            s5_eqb_right = -1
        else:
            s5_eqb_right = df.at[i, 'Scenario5 EQB right']
            s5_eqb_right = s5_eqb_right.replace("[", "")
            s5_eqb_right = s5_eqb_right.replace("]", "")
            s5_eqb_right = s5_eqb_right.replace(" ", "")
            # 共有四組xy，要x1,y1,x2,y2,x3,y3,x4,y4
            s5_eqb_right_x1, s5_eqb_right_y1, s5_eqb_right_x2, s5_eqb_right_y2, \
            s5_eqb_right_x3, s5_eqb_right_y3, s5_eqb_right_x4, s5_eqb_right_y4 = map(int, s5_eqb_right.split(","))
        
        if pd.isnull(df.at[i, 'Scenario2 EQB']):
            s2_eqb = -1
        else:
            s2_eqb = df.at[i, 'Scenario2 EQB']
            # 去掉前後的 [ ]
            s2_eqb = s2_eqb.replace("[", "")
            s2_eqb = s2_eqb.replace("]", "")
            s2_eqb = s2_eqb.replace(" ", "")
            # 共有四組xy，要x1,y1,x2,y2,x3,y3,x4,y4
            s2_eqb_x1, s2_eqb_y1, s2_eqb_x2, s2_eqb_y2, \
            s2_eqb_x3, s2_eqb_y3, s2_eqb_x4, s2_eqb_y4 = map(int, s2_eqb.split(","))
            
        if pd.isnull(df.at[i, 'Scenario4 EQB']):
            s4_eqb = -1
        else:
            s4_eqb = df.at[i, 'Scenario4 EQB']
            # 去掉前後的 [ ]
            s4_eqb = s4_eqb.replace("[", "")
            s4_eqb = s4_eqb.replace("]", "")
            s4_eqb = s4_eqb.replace(" ", "")
            # 共有四組xy，要x1,y1,x2,y2,x3,y3,x4,y4
            s4_eqb_x1, s4_eqb_y1, s4_eqb_x2, s4_eqb_y2, \
            s4_eqb_x3, s4_eqb_y3, s4_eqb_x4, s4_eqb_y4 = map(int, s4_eqb.split(","))

        # 從eqb的四組xy畫出四邊形
        if s5_eqb_left != -1:
            cv2.line(image, (s5_eqb_left_x1, s5_eqb_left_y1), (s5_eqb_left_x2, s5_eqb_left_y2), (0, 0, 0), 3)
            cv2.line(image, (s5_eqb_left_x2, s5_eqb_left_y2), (s5_eqb_left_x3, s5_eqb_left_y3), (0, 0, 0), 3)
            cv2.line(image, (s5_eqb_left_x3, s5_eqb_left_y3), (s5_eqb_left_x4, s5_eqb_left_y4), (0, 0, 0), 3)
            cv2.line(image, (s5_eqb_left_x4, s5_eqb_left_y4), (s5_eqb_left_x1, s5_eqb_left_y1), (0, 0, 0), 3)
            
        if s5_eqb_right != -1:
            cv2.line(image, (s5_eqb_right_x1, s5_eqb_right_y1), (s5_eqb_right_x2, s5_eqb_right_y2), (0, 0, 0), 3)
            cv2.line(image, (s5_eqb_right_x2, s5_eqb_right_y2), (s5_eqb_right_x3, s5_eqb_right_y3), (0, 0, 0), 3)
            cv2.line(image, (s5_eqb_right_x3, s5_eqb_right_y3), (s5_eqb_right_x4, s5_eqb_right_y4), (0, 0, 0), 3)
            cv2.line(image, (s5_eqb_right_x4, s5_eqb_right_y4), (s5_eqb_right_x1, s5_eqb_right_y1), (0, 0, 0), 3)
    
        if s2_eqb != -1:
            cv2.line(image, (s2_eqb_x1, s2_eqb_y1), (s2_eqb_x2, s2_eqb_y2), (0, 0, 0), 3)
            cv2.line(image, (s2_eqb_x2, s2_eqb_y2), (s2_eqb_x3, s2_eqb_y3), (0, 0, 0), 3)
            cv2.line(image, (s2_eqb_x3, s2_eqb_y3), (s2_eqb_x4, s2_eqb_y4), (0, 0, 0), 3)
            cv2.line(image, (s2_eqb_x4, s2_eqb_y4), (s2_eqb_x1, s2_eqb_y1), (0, 0, 0), 3)
        
        if s4_eqb != -1:
            cv2.line(image, (s4_eqb_x1, s4_eqb_y1), (s4_eqb_x2, s4_eqb_y2), (0, 0, 0), 3)
            cv2.line(image, (s4_eqb_x2, s4_eqb_y2), (s4_eqb_x3, s4_eqb_y3), (0, 0, 0), 3)
            cv2.line(image, (s4_eqb_x3, s4_eqb_y3), (s4_eqb_x4, s4_eqb_y4), (0, 0, 0), 3)
            cv2.line(image, (s4_eqb_x4, s4_eqb_y4), (s4_eqb_x1, s4_eqb_y1), (0, 0, 0), 3)
        
        self.add_speed_gyro(image, df, i)
        
        return image

    def f195_plot(self, image):
        df = self.df
        i = self.i
        if pd.isnull(df.at[i,'Scenario2_nearest object']):
            s2x1,s2y1,s2x2,s2y2=0, 0, 0, 0
        else:
            match=re.findall(r"\d+\.\d+",df.at[i,'Scenario2_nearest object'])#---------S2
            if match:
                b_box = [int(float(num)) for num in match]
                s2x1,s2y1,s2x2,s2y2=b_box[0],b_box[1],b_box[2],b_box[3]

        if pd.isnull(df.at[i,'Scenario3_nearest object']):
            s3x1,s3y1,s3x2,s3y2=0, 0, 0, 0
        else:
            match=re.findall(r"\d+\.\d+",df.at[i,'Scenario3_nearest object'])#---------S3
            if match:
                b_box = [int(float(num)) for num in match]
                s3x1,s3y1,s3x2,s3y2=b_box[0],b_box[1],b_box[2],b_box[3]
                
        if pd.isnull(df.at[i, 'Scenario3_xdirection_v_left']):
            s3xv_left = -1
        else:
            s3xv_left = df.at[i, 'Scenario3_xdirection_v_left']
        
        if pd.isnull(df.at[i, 'Scenario3_xdirection_v_right']):
            s3xv_right = -1
        else:
            s3xv_right = df.at[i, 'Scenario3_xdirection_v_right']
        
        if pd.isnull(df.at[i, 'Scenario2 target obj kph']):
            s2_target_obj_kph = -1
        else:
            s2_target_obj_kph = df.at[i, 'Scenario2 target obj kph']
                
        cv2.rectangle(image, (int(s2x1*1920/480), int(s2y1*1280/480)), (int(s2x2*1920/480),int(s2y2*1280/480)), (255, 0, 0), 2)
        cv2.rectangle(image, (int(s3x1*1920/480), int(s3y1*1280/480)), (int(s3x2*1920/480), int(s3y2*1280/480)), (255, 0, 0), 2)
        # set_label(image,"S2_object",int(s2x1*1920/480),int(s2y1*1920/480))
        # set_label(image,"S3_object",int(s3x1*1920/480),int(s3y1*1280/480)+40)
        if s2_target_obj_kph != -1:
            self.set_label(image, f"S2_target_obj_kph: {s2_target_obj_kph}", 300, 150, 1.5, (0, 165, 255), thickness=3)
        if s3xv_left != -1:
            self.set_label(image, f"S3_xdirection_v_left: {s3xv_left}", 300, 250, 1.5, (0, 165, 255), thickness=3)
        if s3xv_right != -1:
            self.set_label(image, f"S3_xdirection_v_right: {s3xv_right}", 300, 350, 1.5, (0, 165, 255), thickness=3)
            
        if self.status["scenario2_left"] != "None":
            self.set_label(image, f"Scenario2_left: {self.status['scenario2_left']}", 900, 50, 1.5, (0, 0, 255), thickness=3)
        if self.status["scenario2_right"] != "None":
            self.set_label(image, f"Scenario2_right: {self.status['scenario2_right']}", 900, 100, 1.5, (0, 0, 255), thickness=3)
        if self.status["scenario3_left"] != "None":
            self.set_label(image, f"Scenario3_left: {self.status['scenario3_left']}", 900, 150, 1.5, (0, 0, 255), thickness=3)
        if self.status["scenario3_right"] != "None":
            self.set_label(image, f"Scenario3_right: {self.status['scenario3_right']}", 900, 200, 1.5, (0, 0, 255), thickness=3)
        
        # object class
        if pd.isnull(df.at[i, 'Scenario2 object class']):
            s2_obj_class = -1
        else:
            s2_obj_class = df.at[i, 'Scenario2 object class']
            s2_obj_class = self.object_class[s2_obj_class]
        if pd.isnull(df.at[i, 'Scenario2 object conf']):
            s2_obj_conf = -1
        else:
            s2_obj_conf = df.at[i, 'Scenario2 object conf']
            
        if pd.isnull(df.at[i, 'Scenario3 object class']):
            s3_obj_class = -1
        else:
            s3_obj_class = df.at[i, 'Scenario3 object class']
            s3_obj_class = self.object_class[s3_obj_class]
        if pd.isnull(df.at[i, 'Scenario3 object conf']):
            s3_obj_conf = -1
        else:
            s3_obj_conf = df.at[i, 'Scenario3 object conf']
            
        if s2x1 != 0 or s2y1 != 0:
            if s2_obj_class != -1:
                self.set_label(image, f"S2_obj_class: {s2_obj_class}", int(s2x1*1920/480),int(s2y1*1920/480))
            if s2_obj_conf != -1:
                self.set_label(image, f"S2_obj_conf: {s2_obj_conf}", int(s2x1*1920/480),int(s2y1*1920/480)+20)
        if s3x1 != 0 or s3y1 != 0:
            if s3_obj_class != -1:
                self.set_label(image, f"S3_obj_class: {s3_obj_class}", int(s3x1*1920/480),int(s3y1*1280/480)+40)
            if s3_obj_conf != -1:
                self.set_label(image, f"S3_obj_conf: {s3_obj_conf}", int(s3x1*1920/480),int(s3y1*1280/480)+60)
        
        # EQB
        if pd.isnull(df.at[i, 'Scenario2 EQB']):
            s2_eqb = -1
        else:
            s2_eqb = df.at[i, 'Scenario2 EQB']
            # 去掉前後的 [ ]
            s2_eqb = s2_eqb.replace("[", "")
            s2_eqb = s2_eqb.replace("]", "")
            s2_eqb = s2_eqb.replace(" ", "")
            # 共有四組xy，要x1,y1,x2,y2,x3,y3,x4,y4
            s2_eqb_x1, s2_eqb_y1, s2_eqb_x2, s2_eqb_y2, \
            s2_eqb_x3, s2_eqb_y3, s2_eqb_x4, s2_eqb_y4 = map(int, s2_eqb.split(","))
        
        if pd.isnull(df.at[i, 'Scenario3 EQB']):
            s3_eqb = -1
        else:
            s3_eqb = df.at[i, 'Scenario3 EQB']
            # 去掉前後的 [ ]
            s3_eqb = s3_eqb.replace("[", "")
            s3_eqb = s3_eqb.replace("]", "")
            s3_eqb = s3_eqb.replace(" ", "")
            # 共有四組xy，要x1,y1,x2,y2,x3,y3,x4,y4
            s3_eqb_x1, s3_eqb_y1, s3_eqb_x2, s3_eqb_y2, \
            s3_eqb_x3, s3_eqb_y3, s3_eqb_x4, s3_eqb_y4 = map(int, s3_eqb.split(","))
        
        # 從eqb的四組xy畫出四邊形
        if s2_eqb != -1:
            cv2.line(image, (s2_eqb_x1, s2_eqb_y1), (s2_eqb_x2, s2_eqb_y2), (0, 0, 0), 3)
            cv2.line(image, (s2_eqb_x2, s2_eqb_y2), (s2_eqb_x3, s2_eqb_y3), (0, 0, 0), 3)
            cv2.line(image, (s2_eqb_x3, s2_eqb_y3), (s2_eqb_x4, s2_eqb_y4), (0, 0, 0), 3)
            cv2.line(image, (s2_eqb_x4, s2_eqb_y4), (s2_eqb_x1, s2_eqb_y1), (0, 0, 0), 3)
        
        if s3_eqb != -1:
            cv2.line(image, (s3_eqb_x1, s3_eqb_y1), (s3_eqb_x2, s3_eqb_y2), (0, 0, 0), 3)
            cv2.line(image, (s3_eqb_x2, s3_eqb_y2), (s3_eqb_x3, s3_eqb_y3), (0, 0, 0), 3)
            cv2.line(image, (s3_eqb_x3, s3_eqb_y3), (s3_eqb_x4, s3_eqb_y4), (0, 0, 0), 3)
            cv2.line(image, (s3_eqb_x4, s3_eqb_y4), (s3_eqb_x1, s3_eqb_y1), (0, 0, 0), 3)
            
        self.add_speed_gyro(image, df, i)
        
        if not pd.isnull(df.at[i, 'Scenario3_area_judge_str']):
            s3_area = df.at[i, 'Scenario3_area_judge_str']
            s3_area = float(s3_area)
            self.set_label(image, f"S3_area: {s3_area}", int(s3x1*1920/480),int(s3y1*1280/480)+80)
        
        if not pd.isnull(df.at[i, 'Scenario3_DSW_left_too_big']):
            self.set_label(image, f"S3_left_too_big", int(s3x1*1920/480),int(s3y1*1280/480)+100, color=(0,0,255))
            
        if not pd.isnull(df.at[i, 'Scenario3_DSW_right_too_big']):
            self.set_label(image, f"S3_right_too_big", int(s3x1*1920/480),int(s3y1*1280/480)+100, color=(0,0,255))
        
        return image

    def f60_plot(self, image):  
        df = self.df
        i = self.i
        if pd.isnull(df.at[i,'Scenario1_nearest object']):
            s1x1,s1y1,s1x2,s1y2=0, 0, 0, 0
        else:
            match=re.findall(r"\d+\.\d+",df.at[i,'Scenario1_nearest object']) #---------S1
            if match:
                b_box = [int(float(num)) for num in match]
                s1x1,s1y1,s1x2,s1y2=b_box[0],b_box[1],b_box[2],b_box[3]
            
        cv2.rectangle(image, (int(s1x1*1920/480), int(s1y1*1280/480)), (int(s1x2*1920/480),int(s1y2*1280/480)), (255, 0, 0), 2)
        self.set_label(image,"S1_object",int(s1x1*1920/480),int(s1y1*1280/480))  
            
        if pd.isnull(df.at[i, 'Scenario1 object class']):
            s1_obj_class = -1
        else:
            s1_obj_class = df.at[i, 'Scenario1 object class']
            s1_obj_class = self.object_class[s1_obj_class]
            
        if pd.isnull(df.at[i, 'Scenario1 object conf']):  
            s1_obj_conf = -1
        else:
            s1_obj_conf = df.at[i, 'Scenario1 object conf']
        
        if s1x1 != 0 or s1y1 != 0:
            if s1_obj_class != -1:
                self.set_label(image, f"S1_obj_class: {s1_obj_class}", int(s1x1*1920/480),int(s1y1*1280/480)+20)
            if s1_obj_conf != -1:
                self.set_label(image, f"S1_obj_conf: {s1_obj_conf}", int(s1x1*1920/480),int(s1y1*1280/480)+40)
            
        if self.status["scenario1"] != "None":
            self.set_label(image, f"Scenario1: {self.status['scenario1']}", 900, 100, 1.5, (0, 0, 255), thickness=3)
            
        self.add_speed_gyro(image, df, i)
        
        return image

    def processing_front60(self, image):
        df = self.df
        i = self.i
        if df.at[i,'Scenario1_frame_Warning']==1:
            self.set_label(image,'Scenario1_frame_Warning',1000,300,1.5,(255,255,0),thickness = 3)
        if df.at[i,'Scenario1_frame_Alert']==1:
            self.set_label(image,'Scenario1_frame_Alert',1000,300,1.5,thickness = 3)
        if df.at[i,'AI_STATUS_WARNING']==1:
            self.status["scenario1"] = "Warning"
        if df.at[i,'AI_STATUS_ALERT']==1:
            self.status["scenario1"] = "Alert"
        if df.at[i,'AI_STATUS_NONE']==1:
            self.status["scenario1"] = "None" 
        
    def process_rear195(self, image):      
        df = self.df
        i = self.i
        if df.at[i,'Scenario5_frame_left_Warning']==1:
            self.set_label(image,'Scenario5_frame_left_Warning',1000,300,1.5,(255,255,0),thickness = 3)
        if df.at[i,'Scenario5_frame_left_Alert']==1:
            self.set_label(image,'Scenario5_frame_left_Alert',1000,330,1.5,thickness = 3)
        if df.at[i,'Scenario5_frame_right_Warning']==1:
            self.set_label(image,'Scenario5_frame_right_Warning',1000,360,1.5,(255,255,0),thickness = 3)
        if df.at[i,'Scenario5_frame_right_Alert']==1:
            self.set_label(image,'Scenario5_frame_right_Alert',1000,390,1.5,thickness = 3)
        if df.at[i,'Scenario4_frame_Warning']==1:
            self.set_label(image,'Scenario4_frame_Warning',1000,420,1.5,(255,255,0),thickness = 3)
        if df.at[i,'Scenario4_frame_Alert']==1:
            self.set_label(image,'Scenario4_frame_Alert',1000,450,1.5,thickness = 3)
        if df.at[i,'Scenario5_LEFT_AI_STATUS_WARNING']==1:
            self.status["scenario5_left"] = "Warning"
        if df.at[i,'Scenario5_LEFT_AI_STATUS_ALERT']==1:
            self.status["scenario5_left"] = "Alert"
        if df.at[i,'Scenario5_RIGHT_AI_STATUS_WARNING']==1:
            self.status["scenario5_right"] = "Warning"
        if df.at[i,'Scenario5_RIGHT_AI_STATUS_ALERT']==1:
            self.status["scenario5_right"] = "Alert"
        if df.at[i,'Scenario5_LEFT_AI_STATUS_NONE']==1:
            self.status["scenario5_left"] = "None"
        if df.at[i,'Scenario5_RIGHT_AI_STATUS_NONE']==1:
            self.status["scenario5_right"] = "None"
        if df.at[i,'Scenario4_AI_STATUS_WARNING']==1:
            self.status["scenario4"] = "Warning"
        if df.at[i,'Scenario4_AI_STATUS_ALERT']==1:
            self.status["scenario4"] = "Alert"
        if df.at[i,'Scenario4_AI_STATUS_NONE']==1:
            self.status["scenario4"] = "None"
            
    def process_front195(self, image):
        df = self.df
        i = self.i
        if df.at[i,'Scenario3_frame_left_Warning']==1:
            self.set_label(image,'Scenario3_frame_left_Warning',1000,300,1.5,(255,255,0),thickness = 3)
        if df.at[i,'Scenario3_frame_left_Alert']==1:
            self.set_label(image,'Scenario3_frame_left_Alert',1000,360,1.5,thickness = 3)
        if df.at[i,'Scenario3_frame_right_Warning']==1:
            self.set_label(image,'Scenario3_frame_right_Warning',1000,390,1.5,(255,255,0),thickness = 3)
        if df.at[i,'Scenario3_frame_right_Alert']==1:
            self.set_label(image,'Scenario3_frame_right_Alert',1000,420,1.5,thickness = 3)
        if df.at[i,'Scenario3_LEFT_AI_STATUS_WARNING']==1:
            self.status["scenario3_left"] = "Warning"
        if df.at[i,'Scenario3_LEFT_AI_STATUS_ALERT']==1:
            self.status["scenario3_left"] = "Alert"
        if df.at[i,'Scenario3_RIGHT_AI_STATUS_WARNING']==1:
            self.status["scenario3_right"] = "Warning"
        if df.at[i,'Scenario3_RIGHT_AI_STATUS_ALERT']==1:
            self.status["scenario3_right"] = "Alert"
        if df.at[i,'Scenario3_LEFT_AI_STATUS_NONE']==1:
            self.status["scenario3_left"] = "None"
        if df.at[i,'Scenario3_RIGHT_AI_STATUS_NONE']==1:
            self.status["scenario3_right"] = "None"
        if df.at[i,'Scenario2_LEFT_AI_STATUS_WARNING']==1:
            self.status["scenario2_left"] = "Warning"
        if df.at[i,'Scenario2_LEFT_AI_STATUS_ALERT']==1:
            self.status["scenario2_left"] = "Alert"
        if df.at[i,'Scenario2_RIGHT_AI_STATUS_WARNING']==1:
            self.status["scenario2_right"] = "Warning"
        if df.at[i,'Scenario2_RIGHT_AI_STATUS_ALERT']==1:
            self.status["scenario2_right"] = "Alert"
        if df.at[i,'Scenario2_LEFT_AI_STATUS_NONE']==1:
            self.status["scenario2_left"] = "None"
        if df.at[i,'Scenario2_RIGHT_AI_STATUS_NONE']==1:
            self.status["scenario2_right"] = "None"
                    
    def set_label(self, image,text,x,y,font_scale=0.6,font_color = (255, 0, 0),thickness = 2):
        label = text  # 你可以修改這裡的標籤文字
        font = cv2.FONT_HERSHEY_SIMPLEX  # 字體
        text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]  # 取得文字大小
        
        # 計算文字顯示位置，放在 bounding box 上方
        text_x = x
        text_y = y - 7  # 上方偏移 10 個像素，避免文字貼在框線上   
        cv2.putText(image, label, (text_x, text_y), font, font_scale, font_color, thickness)
        