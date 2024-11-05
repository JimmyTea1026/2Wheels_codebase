## preprocess

分兩種情況 -  1. 已有的影片重跑  2. 跑新的影片

程式在 D:\Compal\Projects\2_wheels\Utils\filein\code_base\[prerpocess.py](http://prerpocess.py/) 中，依照上面不同情境執行不同 function，詳情寫在註解中，包含以下功能 :

1. 生成yuv圖片檔
2. 讀取xlsx檔並抓出speed & gyro 資訊，並生成speed_gryo.txt
3. 將多部影片拼貼到一起，生成num.txt以記錄各個影片的幀數
4. 重新排序檔名
5. 檢查是否有缺少檔案，若有缺幀，則從前後複製。

**現有影片重跑執行 run_exsisting_video ( )**

**新影片執行 run_new_video( ) ，注意要有Will 整理過的sliced資料夾與xlsx**

exsisting只會跑 3~5，new會跑 1~5 

不論何種，都會生成一個all資料夾，裡面將所有待測影片接在一起以便filein程式執行

並會生成num.txt，上面記錄各個影片的總幀數，以便後續切割

p.s. 當all複製到SD卡上後，可以找時間跑 put_image_back( )，他會根據num.txt，將圖片還原到各個資料夾的yuv資料夾中。

## Inference

1. 將all資料夾搬到SD卡上
2. 開機 630，並用uart連接上

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/988e81ae-ae7e-4e6f-b32b-6392efa96cf2/398d02ba-1f6e-40da-8040-8ee29e05eb4a/image.png)

1. 使用 “ mount -t ext4 /dev/mmcblk0p1 /mnt/sd ” 來把SD掛載上，路徑會在/mnt/sd
2.  “ cd /mnt/flash/plus/kp_firmware/kp_firmware_0/kp_firmware/bin/ “ 會移動到目標資料夾
3.  “ vi /mnt/flash/plus/kp_firmware/kp_firmware_0/kp_firmware/bin/ini/filein.ini “ 會開啟編輯器，這邊要修改輸入圖片的路徑 :
改 prefix_name 為圖片的路徑 **(** **注意要到yuv資料夾並最後要有 “/”，預設應為 /mnt/sd/all/ )**
( 按i 進入編輯模式 ，編輯完按 esc 離開編輯模式再輸入 :wq 儲存並離開 )

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/988e81ae-ae7e-4e6f-b32b-6392efa96cf2/0ea403f8-c669-4eae-aa4f-6ee62b431db7/image.png)

1.  “ export LD_LIBRARY_PATH=$(pwd)/./lib; ” ← 要下這個指令才能執行程式
2. 開始執行前，確認/mnt/sd/ 要有一個資料夾為 processed ，這會放filein出來的圖片
3. 執行前清空/mnt/sd/processed，以及可能存在的 front60.txt / front195.txt / rear195.txt
4. 準備完成，下
 “ ./uart_front_filein | tee /mnt/sd/front195.txt & “
“ ./uart_widefront_filein | tee /mnt/sd/front195.txt & “
“ ./uart_widerear_filein | tee /mnt/sd/front195.txt & “
log資訊會存在 /mnt/sd/front195.txt
5. 執行完成會跳類似error的訊息，不用理他，下 " sync " 再拔掉SD卡即可
6. SD卡要到ubuntu電腦才能讀取，把資料搬到磁碟後再合成影片

p.s.

執行 11. 時可能會卡住不動，下 " ps " ，把執行的process砍掉 ( " kill -9  pid “ ) ，再重新執行一次即可，**注意要確認 /mnt/sd/processed/ 裡為空，以及/mnt/sd/front195.txt 要刪除。**

---

## Postprocess

結束後在/mnt/sd應該有processed資料夾與txt檔，將txt移到processed資料夾中，並複製到硬碟上

複製的路徑要包含 preprocess 時生成的num.txt ，如下圖

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/988e81ae-ae7e-4e6f-b32b-6392efa96cf2/e262903a-c518-4e2c-a790-6c885e9d3c6b/image.png)

程式在 D:\Compal\Projects\2_wheels\Utils\filein\code_base\[postprocess.py](http://prerpocess.py/) 

同樣分為兩種類型 -  1.  inference時跑多部影片 (需要切割)   2.  一次只跑一部

功能如下 :

1. 從 rear195.txt 抓取log生成 excel檔
2. 根據num.txt，將xlsx、圖片，切割回各影片的資料夾中
3. 合成影片

cd /mnt/flash/plus/kp_firmware/kp_firmware_0/kp_firmware/bin/

export LD_LIBRARY_PATH=$(pwd)/./lib;

mount -t ext4 /dev/mmcblk0p1 /mnt/sd

umount /mnt/sd/

./uart_widefront_speed | tee /mnt/sd/front195.txt

./uart_widerear_speed | tee /mnt/sd/rear195.txt
