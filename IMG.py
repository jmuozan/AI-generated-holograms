from moviepy.editor import ImageClip

input_image_path = '/Users/jorgemuyo/Desktop/Challenge/IMG.jpg'
output_image_video_path = '/Users/jorgemuyo/Desktop/Challenge/IMG_video.mp4'

video_duration = 30

clip = ImageClip(input_image_path).set_duration(video_duration)

clip.write_videofile(output_image_video_path, fps=24)