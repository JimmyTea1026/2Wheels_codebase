import re 
import pandas as pd

def get_df(file_type):
    if file_type=="front60":
        df=pd.DataFrame(columns=[
                                 'frame',
                                 'time',
                                 'Scenario1_nearest object',
                                 'Scenario1 EQB',
                                 'Scenario1 object class',
                                 'Scenario1 object conf',
                                 'our_speed',
                                 'our_roll',
                                 'our_pitch',
                                 'our_yaw',
                                 'Scenario1_frame_Warning',
                                 'Scenario1_frame_Alert',
                                 'AI_STATUS_ALERT',
                                 'AI_STATUS_WARNING',
                                 'AI_STATUS_NONE',
                                 'bbox_num',
                                 
                                 ])
    elif file_type=="rear195":
        df=pd.DataFrame(columns=[
                                 'frame',
                                 'time',
                                 'Scenario2_nearest object',
                                 'Scenario2 EQB',
                                 'Scenario2 object class',
                                 'Scenario2 object conf',
                                 
                                 
                                 'Scenario4_nearest object',
                                 'Scenario4 EQB',
                                 'Scenario4 object class',
                                 'Scenario4 object conf',

                                 
                                 'Scenario5_nearest object left',
                                 'Scenario5_nearest object right',
                                 'Scenario5 EQB left',
                                 'Scenario5 EQB right',   
                                 'Scenario5 object class left',
                                 'Scenario5 object class right',
                                 'Scenario5 object conf left',
                                 'Scenario5 object conf right',
                                 'our_speed',
                                 'our_roll',
                                 'our_pitch',
                                 'our_yaw',
                                 'Scenario5_frame_left_Warning',
                                 'Scenario5_frame_left_Alert',
                                 'Scenario5_frame_right_Warning',
                                 'Scenario5_frame_right_Alert',
                                 'Scenario4_frame_Warning',
                                 'Scenario4_frame_Alert',
                                 'Scenario5_LEFT_AI_STATUS_WARNING',
                                 'Scenario5_LEFT_AI_STATUS_ALERT',
                                 'Scenario5_RIGHT_AI_STATUS_WARNING',
                                 'Scenario5_RIGHT_AI_STATUS_ALERT',
                                 'Scenario5_LEFT_AI_STATUS_NONE',
                                 'Scenario5_RIGHT_AI_STATUS_NONE',
                                 'Scenario4_object_distance',
                                 'Scenario4_AI_STATUS_ALERT',
                                 'Scenario4_AI_STATUS_WARNING',
                                 'Scenario4_AI_STATUS_NONE',
                                 'Scenario4 target obj kph',
                                 'Scenario2 target obj kph',
                                 'bbox_num',
                                 ]) 
        
    elif  file_type=="front195":
        df=pd.DataFrame(columns=[
                                 'frame',
                                 'time',
                                 'Scenario2_nearest object',
                                 'Scenario2 object class',
                                 'Scenario2 EQB',
                                 'Scenario2 object conf',
                                 
                                 'Scenario3_nearest object',
                                 'Scenario3 object class',
                                 'Scenario3 EQB',
                                 'Scenario3 object conf',
                                 
                                 'our_speed',
                                 'our_roll',
                                 'our_pitch',
                                 'our_yaw',
                                 
                                 'Scenario3_xdirection',
                                 'Scenario3_frame_left_Warning',
                                 'Scenario3_frame_left_Alert',
                                 'Scenario3_frame_right_Warning',
                                 'Scenario3_frame_right_Alert',
                                 'Scenario3_LEFT_AI_STATUS_WARNING',
                                 'Scenario3_LEFT_AI_STATUS_ALERT',
                                 'Scenario3_RIGHT_AI_STATUS_WARNING',
                                 'Scenario3_RIGHT_AI_STATUS_ALERT',
                                 'Scenario3_LEFT_AI_STATUS_NONE',
                                 'Scenario3_RIGHT_AI_STATUS_NONE',
                                 'Scenario3_DSW_judge_str',
                                 'Scenario3_area_judge_str',
                                 'Scenario3_xdirection_v_right',
                                 'Scenario3_xdirection_v_left',
                                 'Scenario2 target obj kph',
                                 'Scenario2_frame_left_Warning',
                                 'Scenario2_frame_left_Alert',
                                 'Scenario2_frame_right_Warning',
                                 'Scenario2_frame_right_Alert',
                                 'Scenario2_LEFT_AI_STATUS_WARNING',
                                 'Scenario2_LEFT_AI_STATUS_ALERT',
                                 'Scenario2_RIGHT_AI_STATUS_WARNING',
                                 'Scenario2_RIGHT_AI_STATUS_ALERT',
                                 'Scenario2_LEFT_AI_STATUS_NONE',
                                 'Scenario2_RIGHT_AI_STATUS_NONE',
                                 
                                 
            
                                 'bbox_num',
                                 ]) 
    else :
         print("please check your file_type")
         input()
    return df

def process_event(file_type,event,df,message_dicarded):
    if file_type=="front195":
        process_event_f195(event,df,message_dicarded)
    elif file_type=="rear195":
        process_event_r195(event,df,message_dicarded)
    elif file_type=="front60":
        process_event_f60(event,df,message_dicarded)
        
        
        
def process_event_r195(event,df,message_dicarded):
        obj_keywords = ['Scenario5_nearest object left', 
                        'Scenario5_nearest object right', 
                        'Scenario4_nearest object',
                        'Scenario2_nearest object']
        riding_krywords=['our_speed','our_roll','our_pitch','our_yaw']
        
        if any(keyword in event for keyword in obj_keywords):
            keyword_found = [keyword for keyword in obj_keywords if keyword in event][0]
            pattern = r"(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)"
            result = re.findall(pattern, event)
            if not result :
                print("no_match_keyword")
                print("event is ", event)
            df.at[len(df) - 1, keyword_found]=result[0]
        
        elif any(keyword in event for keyword in riding_krywords): 
            keyword_found = [keyword for keyword in riding_krywords if keyword in event][0]
            # pattern = r": -?(\d+(\.\d*)?)"
            pattern = r":\s(-?\d+(\.\d*)?)"
            result = re.findall(pattern, event)
            if result:

                df.at[len(df) - 1, keyword_found] = float(result[0][0])
            else:
                print("No matching driving_keywords  info.") 
                print("event is ", event)
                
        elif "Scenario5_frame_left_Warning" in event:
            df.at[len(df) - 1, 'Scenario5_frame_left_Warning']=1
        elif "Scenario5_frame_left_Alert" in event:
            df.at[len(df) - 1, 'Scenario5_frame_left_Alert']=1
        elif "Scenario5_frame_right_Warning" in event:
            df.at[len(df) - 1, 'Scenario5_frame_right_Warning']=1
        elif "Scenario5_frame_right_Alert" in event:
            df.at[len(df) - 1, 'Scenario5_frame_right_Alert']=1
        elif "Scenario4_frame_Warning" in event:
            df.at[len(df) - 1, 'Scenario4_frame_Warning']=1
        elif "Scenario4_frame_Alert" in event:
            df.at[len(df) - 1, 'Scenario4_frame_Alert']=1  
        elif "Scenario5_LEFT_AI_STATUS_WARNING" in event:
            df.at[len(df) - 1, 'Scenario5_LEFT_AI_STATUS_WARNING']=1
        elif "Scenario4_object_distance" in event:
            kw = re.search(r'\s\d+\.\d+', event)
            if kw:
                df.at[len(df) - 1, 'Scenario4_object_distance']=float(kw.group())
        elif "Scenario5_LEFT_AI_STATUS_ALERT" in event:
            df.at[len(df) - 1, 'Scenario5_LEFT_AI_STATUS_ALERT']=1
        elif "Scenario5_RIGHT_AI_STATUS_WARNING" in event:
            df.at[len(df) - 1, 'Scenario5_RIGHT_AI_STATUS_WARNING']=1
        elif "Scenario5_RIGHT_AI_STATUS_ALERT" in event:
            df.at[len(df) - 1, 'Scenario5_RIGHT_AI_STATUS_ALERT']=1
        elif "Scenario4 target obj kph" in event:
            kw = re.search(r':(\s-?\d+)', event)
            if kw:
                df.at[len(df) - 1, 'Scenario4 target obj kph']=int(kw.group(1))
        elif "Scenario2 target obj kph" in event:
            kw = re.search(r':(\s-?\d+)', event)
            if kw:
                df.at[len(df) - 1, 'Scenario2 target obj kph']=int(kw.group(1))      
        elif "Scenario5_LEFT_AI_STATUS_NONE" in event:
            df.at[len(df) - 1, 'Scenario5_LEFT_AI_STATUS_NONE']=1
        elif "Scenario5_RIGHT_AI_STATUS_NONE" in event:
            df.at[len(df) - 1, 'Scenario5_RIGHT_AI_STATUS_NONE']=1
        elif "Scenario4_AI_STATUS_ALERT" in event:
            df.at[len(df) - 1, 'Scenario4_AI_STATUS_ALERT']=1                    
        elif "Scenario4_AI_STATUS_NONE" in event:
            df.at[len(df) - 1, 'Scenario4_AI_STATUS_NONE']=1    
        elif "After NMS" in event:
            kw=re.search(r":\s(\d+)",event)
            if kw:
                df.at[len(df) - 1, 'bbox_num']=int(kw.group(1)) 
        elif "Scenario2 EQB" in event:
            temp=[]
            kw= re.search(r'EQB:\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)',event)
            for group in kw.groups():
                temp.append(int(group))
            df.at[len(df) - 1, 'Scenario2 EQB']=temp
       
        elif "Scenario4 EQB" in event:
            temp=[]
            kw= re.search(r'EQB:\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)',event)
            for group in kw.groups():
                temp.append(int(group))
            df.at[len(df) - 1, 'Scenario4 EQB']=temp
       
        
       
        elif "Scenario5 EQB left" in event:
            temp=[]
            kw= re.search(r'EQB left:\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)',event)
            for group in kw.groups():
                temp.append(int(group))
            df.at[len(df) - 1, 'Scenario5 EQB left']=temp
        elif "Scenario5 EQB right" in event:
            temp=[]
            kw= re.search(r'EQB right:\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)',event)
            for group in kw.groups():
                temp.append(int(group))
            df.at[len(df) - 1, 'Scenario5 EQB right']=temp
            
        elif 'Scenario2 object class' in event:
            kw=re.search(r'object class:\s(\d)',event)
            if kw:   
                df.at[len(df) - 1, 'Scenario2 object class']=int(kw.group(1))
                
        elif 'Scenario4 object class' in event :
            kw=re.search(r'object class:\s(\d)',event)
            if kw:
                df.at[len(df) - 1, 'Scenario4 object class']=int(kw.group(1))   
                
        elif 'Scenario5 object class left' in event:
            kw=re.search(r'object class left:\s(\d)',event)
            if kw:   
                df.at[len(df) - 1, 'Scenario5 object class left']=int(kw.group(1))
        elif 'Scenario5 object class right' in event:
            kw=re.search(r'object class right:\s(\d)',event)
            if kw:   
                df.at[len(df) - 1, 'Scenario5 object class right']=int(kw.group(1))

                
               
        elif 'Scenario2 object conf' in event :
            kw=re.search(r'object conf:\s(\d+\.\d+)',event)
            if kw:
                df.at[len(df) - 1, 'Scenario2 object conf']=float(kw.group(1))
        elif 'Scenario4 object conf' in event :
            kw=re.search(r'object conf:\s(\d+\.\d+)',event)
            if kw:
                df.at[len(df) - 1, 'Scenario4 object conf']=float(kw.group(1))
        elif 'Scenario5 object conf left' in event :
            kw=re.search(r'object conf left:\s(\d+\.\d+)',event)
            if kw:
                df.at[len(df) - 1, 'Scenario5 object conf left']=float(kw.group(1))
        elif 'Scenario5 object conf right' in event :
            kw=re.search(r'object conf right:\s(\d+\.\d+)',event)
            if kw:
                df.at[len(df) - 1, 'Scenario5 object conf right']=float(kw.group(1))
                                                          
            
        else:   
            message_dicarded.add(event)
            pass
        
        
        
        
        

def process_event_f195(event,df,message_dicarded):
        # print(event)
        obj_keywords = ['Scenario3_nearest object',
                        'Scenario2_nearest object']
        riding_krywords=['our_speed','our_roll','our_pitch','our_yaw']
        if any(keyword in event for keyword in obj_keywords):
            keyword_found = [keyword for keyword in obj_keywords if keyword in event][0]
            pattern = r"(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)"
            result = re.findall(pattern, event)
            if not result :
                print("no_match_keyword")
                print("event is ", event)
            df.at[len(df) - 1, keyword_found]=result[0]
            
        
        
        elif any(keyword in event for keyword in riding_krywords): 
            keyword_found = [keyword for keyword in riding_krywords if keyword in event][0]
            # pattern = r": -?(\d+(\.\d*)?)"
            pattern = r":\s(-?\d+(\.\d*)?)"
            result = re.findall(pattern, event)
            if result:
                df.at[len(df) - 1, keyword_found] = float(result[0][0])
            else:
                print("No matching driving_keywords  info.") 
                print("event is ", event)
        
        elif "Scenario3_xdirection:" in event:
            kw = re.search(r':(\s-?\d+)', event)
            if kw:
                df.at[len(df) - 1, 'Scenario3_xdirection']=int(kw.group(1))
        elif "Scenario2 target obj kph" in event:
            kw = re.search(r':(\s-?\d+)', event)
            if kw:
                df.at[len(df) - 1, 'Scenario2 target obj kph']=int(kw.group(1))
        elif "Scenario3_frame_left_Warning" in event:
            df.at[len(df) - 1, 'Scenario3_frame_left_Warning']=1
        elif "Scenario3_frame_left_Alert" in event:
            df.at[len(df) - 1, 'Scenario3_frame_left_Alert']=1
        elif "Scenario3_frame_right_Warning" in event:
            df.at[len(df) - 1, 'Scenario3_frame_right_Warning']=1
        elif "Scenario3_frame_right_Alert" in event:
            df.at[len(df) - 1, 'Scenario3_frame_right_Alert']=1
        elif "Scenario3_LEFT_AI_STATUS_WARNING" in event:
            df.at[len(df) - 1, 'Scenario3_LEFT_AI_STATUS_WARNING']=1
        elif "Scenario3_LEFT_AI_STATUS_ALERT" in event:
            df.at[len(df) - 1, 'Scenario3_LEFT_AI_STATUS_ALERT']=1
        elif "Scenario3_RIGHT_AI_STATUS_WARNING" in event:
            df.at[len(df) - 1, 'Scenario3_RIGHT_AI_STATUS_WARNING']=1    
        elif "Scenario3_RIGHT_AI_STATUS_ALERT" in event:
            df.at[len(df) - 1, 'Scenario3_RIGHT_AI_STATUS_ALERT']=1
        elif "Scenario3_LEFT_AI_STATUS_NONE" in event:
            df.at[len(df) - 1, 'Scenario3_LEFT_AI_STATUS_NONE']=1
        elif "Scenario3_RIGHT_AI_STATUS_NONE" in event:
            df.at[len(df) - 1, 'Scenario3_RIGHT_AI_STATUS_NONE']=1
        elif "Scenario3_DSW_judge_str" in event:
            kw = re.search(r'\s\d+\.\d+', event)
            if kw:
                df.at[len(df) - 1, 'Scenario3_DSW_judge_str']=float(kw.group())
        elif "Scenario3_area_judge_str" in event:
            kw = re.search(r'\s\d+\.\d+', event)
            if kw:
                df.at[len(df) - 1, 'Scenario3_area_judge_str']=float(kw.group())
                
        elif "Scenario3_xdirection_v_right" in event:
            kw=re.search('\s-?\d+\.\d+', event)
            if kw:
                df.at[len(df) - 1, 'Scenario3_xdirection_v_right']=float(kw.group())
                
        elif "Scenario3_xdirection_v_left" in event:
            kw=re.search('\s-?\d+\.\d+', event)
            if kw:
                df.at[len(df) - 1, 'Scenario3_xdirection_v_left']=float(kw.group())
        elif "Scenario2_frame_left_Warning" in event:
            df.at[len(df) - 1, 'Scenario2_frame_left_Warning']=1
        elif "Scenario2_frame_left_Alert" in event:
            df.at[len(df) - 1, 'Scenario2_frame_left_Alert']=1        
        elif "Scenario2_frame_right_Warning" in event:
            df.at[len(df) - 1, 'Scenario2_frame_right_Warning']=1        
        elif "Scenario2_frame_right_Alert" in event:
            df.at[len(df) - 1, 'Scenario2_frame_right_Alert']=1     
        elif "Scenario2_LEFT_AI_STATUS_WARNING" in event:
            df.at[len(df) - 1, 'Scenario2_LEFT_AI_STATUS_WARNING']=1 
        elif "Scenario2_LEFT_AI_STATUS_ALERT" in event:
            df.at[len(df) - 1, 'Scenario2_LEFT_AI_STATUS_ALERT']=1  
        elif "Scenario2_RIGHT_AI_STATUS_WARNING" in event:
            df.at[len(df) - 1, 'Scenario2_RIGHT_AI_STATUS_WARNING']=1   
        elif "Scenario2_RIGHT_AI_STATUS_ALERT" in event:
            df.at[len(df) - 1, 'Scenario2_RIGHT_AI_STATUS_ALERT']=1 
        elif "Scenario2_LEFT_AI_STATUS_NONE" in event:
            df.at[len(df) - 1, 'Scenario2_LEFT_AI_STATUS_NONE']=1   
        elif "Scenario2_RIGHT_AI_STATUS_NONE" in event:
            df.at[len(df) - 1, 'Scenario2_RIGHT_AI_STATUS_NONE']=1       
        elif "After NMS" in event:
            kw=re.search(r":\s(\d+)",event)
            if kw:
                df.at[len(df) - 1, 'bbox_num']=int(kw.group(1))   
                
        elif "Scenario2 EQB" in event:
            temp=[]
            kw= re.search(r'EQB:\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)',event)
            for group in kw.groups():
                temp.append(int(group))
            df.at[len(df) - 1, 'Scenario2 EQB']=temp
        elif "Scenario3 EQB" in event:
            temp=[]
            kw= re.search(r'EQB:\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)',event)
            for group in kw.groups():
                temp.append(int(group))
            df.at[len(df) - 1, 'Scenario3 EQB']=temp
        elif 'Scenario2 object class'in event:
            kw=re.search(r'object class:\s(\d)',event)
            if kw:   
                df.at[len(df) - 1, 'Scenario2 object class']=int(kw.group(1))  
                
        elif 'Scenario3 object class':
            kw=re.search(r'object class:\s(\d)',event)
            if kw:   
                df.at[len(df) - 1, 'Scenario3 object class']=int(kw.group(1)) 
                
        elif 'Scenario2 object conf' in event :
            kw=re.search(r'object conf:\s(\d+\.\d+)',event)
            if kw:
                df.at[len(df) - 1, 'Scenario2 object conf']=float(kw.group(1))
                         
        elif 'Scenario3 object conf' in event :
            kw=re.search(r'object conf:\s(\d+\.\d+)',event)
            if kw:
                df.at[len(df) - 1, 'Scenario3 object conf']=float(kw.group(1))
                       
        else:   
            message_dicarded.add(event)
            pass

def process_event_f60(event,df,message_dicarded):
        obj_keywords = ['Scenario1_nearest object']
        riding_krywords=['our_speed','our_roll','our_pitch','our_yaw']
        if any(keyword in event for keyword in obj_keywords):
            keyword_found = [keyword for keyword in obj_keywords if keyword in event][0]
            pattern = r"(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)"
            result = re.findall(pattern, event)
            if not result :
                print("no_match_keyword")
                print("event is ", event)
            df.at[len(df) - 1, keyword_found]=result[0]
            
        elif any(keyword in event for keyword in riding_krywords): 
            keyword_found = [keyword for keyword in riding_krywords if keyword in event][0]
            # pattern = r": -?(\d+(\.\d*)?)"
            # pattern = r":\s(-?\d+(\.\d*)?)"
            pattern = r':\s-?\d+(\.\d+)?'
            mat=re.search(pattern,event)
            if mat:
                temp=mat.group(0)
                temp=temp[2:]
                df.at[len(df) - 1, keyword_found] = float(temp)
            else:
                print("No matching driving_keywords  info.") 
                print("event is ", event)
            
        elif "Scenario1_frame_Warning" in event:
            df.at[len(df) - 1, 'Scenario1_frame_Warning']=1
        elif "AI_STATUS_ALERT" in event:
            df.at[len(df) - 1, 'AI_STATUS_ALERT']=1
        elif "AI_STATUS_WARNING" in event:
            df.at[len(df) - 1, 'AI_STATUS_WARNING']=1
        elif "AI_STATUS_NONE" in event:
            df.at[len(df) - 1, 'AI_STATUS_NONE']=1
        elif "Scenario1_frame_Alert" in event:
            df.at[len(df) - 1, 'Scenario1_frame_Alert']=1
        elif "After NMS" in event:
            kw=re.search(r":\s(\d+)",event)
            if kw:
                df.at[len(df) - 1, 'bbox_num']=int(kw.group(1))    
                
                
        elif "Scenario1 EQB" in event:
            temp=[]
            kw= re.search(r'EQB:\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)\s(\d+)',event)
            for group in kw.groups():
                temp.append(int(group))
            df.at[len(df) - 1, 'Scenario1 EQB']=temp        
                
        elif 'Scenario1 object class' in event:
            kw=re.search(r'object class:\s(\d)',event)
            if kw:   
                df.at[len(df) - 1, 'Scenario1 object class']=int(kw.group(1)) 
                
        elif 'Scenario1 object conf' in event :
            kw=re.search(r'object conf:\s(\d+\.\d+)',event)
            if kw:
                df.at[len(df) - 1, 'Scenario1 object conf']=float(kw.group(1))
                       
                
            
        else:   
            message_dicarded.add(event)
            pass
        return 