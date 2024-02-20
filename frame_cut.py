import os
import cv2
import subprocess

def extract_frames(video_path, frames_temp_folder, output_video_folder):
    # 获取视频文件名（不包含路径和后缀）
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    
    # 创建临时输出帧文件夹
    os.makedirs(frames_temp_folder, exist_ok=True)
    
    # 打开视频文件
    video_capture = cv2.VideoCapture(video_path)
    
    # 确保视频文件被成功打开
    if not video_capture.isOpened():
        print("Error: Unable to open video file")
        return
    
    # 获取视频的帧率
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    print(f"Video FPS: {fps}")
    
    # 设置间隔帧数
    if fps <= 30:
        frames_to_skip = 20
    else:
        frames_to_skip = 30
    
    # 初始化保存的帧计数器
    saved_frame_count = 0
    
    # 视频帧计数器
    frame_count = 0
    
    # 逐帧抽取并保存
    while True:
        # 读取下一帧
        ret, frame = video_capture.read()
        
        # 检查是否成功读取帧
        if not ret:
            break
        
        # 判断是否跳过该帧
        if frame_count % frames_to_skip != 0:
            # 保存帧到临时输出文件夹中
            frame_path = os.path.join(frames_temp_folder, f"{video_name}_frame_{saved_frame_count}.jpg")
            cv2.imwrite(frame_path, frame)
            
            # 更新保存的帧计数器
            saved_frame_count += 1
        
        # 更新帧计数器
        frame_count += 1

    # 关闭视频文件
    video_capture.release()
    
    # 使用ffmpeg从源视频中提取声音并保存到临时输出文件夹中
    audio_path = os.path.join(frames_temp_folder, f"{video_name}_temp_audio.aac")
    subprocess.run(["ffmpeg", "-y", "-i", video_path, "-vn", "-acodec", "aac", "-strict", "experimental", audio_path])
    
    # 使用ffmpeg将图片合成为视频，并添加提取的声音
    output_video_path = os.path.join(output_video_folder, f"{video_name}_output.mp4")
    subprocess.run(["ffmpeg", "-y", "-framerate", str(fps), "-i", os.path.join(frames_temp_folder, f"{video_name}_frame_%d.jpg"), "-i", audio_path, "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-c:a", "copy", "-shortest", output_video_path])
    print(f"Output video saved at: {output_video_path}")
    
    print(f"Total frames extracted: {saved_frame_count}")  # 打印总共抽取了多少帧

    # 清空临时输出帧文件夹中的所有文件
    for file in os.listdir(frames_temp_folder):
        file_path = os.path.join(frames_temp_folder, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

# 指定输入视频文件夹路径
input_video_folder = "input_video"

# 指定帧临时输出文件夹路径
frames_temp_folder = "frames_temp"

# 指定输出视频文件夹路径
output_video_folder = "output_video"

# 遍历输入视频文件夹中的视频文件，并逐个执行抽帧并生成视频
for video_file in sorted(os.listdir(input_video_folder)):
    video_path = os.path.join(input_video_folder, video_file)
    extract_frames(video_path, frames_temp_folder, output_video_folder)
