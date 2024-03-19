# Audio to text
import cv2 as cv
from openai import OpenAI
import speech_recognition as sr
# Text to image
import time
from kittycad.client import Client
# Image download
import requests
# Open blender
import subprocess
# ZooCAD
from kittycad.api.ai import create_text_to_cad, get_text_to_cad_model_for_user
from kittycad.client import ClientFromEnv
from kittycad.models.api_call_status import ApiCallStatus
from kittycad.models.file_export_format import FileExportFormat
from kittycad.models.text_to_cad_create_body import TextToCadCreateBody
import time
import base64
# Move files
import shutil
import os
#
from text_to_cad import text_to_cad_create, get_text_to_cad_model, decode_stl
from kittycad.client import Client
#
import runpy
from moviepy.editor import ImageClip
import subprocess




# Initialize
recognizer = sr.Recognizer()
openai_api_key = ""  # OpenAI API Key
openAI_client = OpenAI(api_key=openai_api_key)
#client = Client(api_key=api_key)


recognizer = sr.Recognizer()
#Record a audio and get text
with sr.Microphone() as source:
    print("Say something!")
    audio = recognizer.listen(source, 3, 8)

audio_transcription = recognizer.recognize_google(audio)
print(audio_transcription)

#audio_transcription = "give me a model of a bed"

model_in_text = "model"
Open_AI_prompt ="add a black background"

complete_prompt = audio_transcription + " and " + Open_AI_prompt

# def openAI_call(input_text):
#     completion = openAI_client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[
#         {"role": "system", "content": Open_AI_prompt},
#         {"role": "user", "content": input_text}
#         ]
#     )
#     descriptive_text = completion.choices[0].message.content
#     descriptive_text = descriptive_text.lower()
#     return descriptive_text

def example_create_text_to_cad(prompt):
    # Create our client.
    client = Client(token="")   # ZOOCAD API Key

    result = create_text_to_cad.sync(
        client=client,
        output_format=FileExportFormat.FBX,
        body=TextToCadCreateBody(
            prompt=prompt,
        ),
    )
    
    print(result)


def move_and_rename(src_path, dest_folder):
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        
        base_name = os.path.basename(src_path)
        
        name, ext = os.path.splitext(base_name)

        new_path = os.path.join(dest_folder, base_name)
        counter = 1
        
        # Adding subindex number to the name of the image
        while os.path.exists(new_path):
            new_path = os.path.join(dest_folder, f"{name}_{counter}{ext}")
            counter += 1
        
        shutil.move(src_path, new_path)
        
        print(f"File moved and renamed to: {new_path}")


if audio_transcription.find(model_in_text) == -1:
    print("no model")
    #descriptive_text = openAI_call(audio_transcription)

    # print(dall_e_prompt)
    response = openAI_client.images.generate(
        model="dall-e-3",
        prompt=complete_prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    print (image_url)

    #Image download
    img_data = requests.get(image_url).content
    with open('IMG.jpg', 'wb') as handler:
        handler.write(img_data)

    # Animate image
    input_image_path = '/Users/jorgemuyo/Desktop/Challenge/IMG.jpg'
    output_image_video_path = '/Users/jorgemuyo/Desktop/Challenge/rendered_blender_video.mp4'

    video_duration = 20

    clip = ImageClip(input_image_path).set_duration(video_duration)

    clip.write_videofile(output_image_video_path, fps=24)



    def file_modification_stable(file_path, stability_duration=60, check_interval=40, timeout=3600):
        """
        Waits for a file's modification time to be stable for a given duration.
        Args:
            file_path: The path to the file to monitor.
            stability_duration: The duration (in seconds) for which the file's modification time should be stable.
            check_interval: How often (in seconds) to check the file's modification time.
            timeout: The maximum time to wait in seconds.
        """
        start_time = time.time()
        last_mod_time = None
        stable_start_time = None

        while True:
            if not os.path.exists(file_path):
                print(f"{file_path} does not exist yet.")
                last_mod_time = None  
            else:
                current_mod_time = os.path.getmtime(file_path)
                if last_mod_time is None or current_mod_time != last_mod_time:
                    last_mod_time = current_mod_time
                    stable_start_time = time.time()  
                elif time.time() - stable_start_time >= stability_duration:
                    print(f"File {file_path} has been stable for {stability_duration} seconds.")
                    break

            if time.time() - start_time > timeout:
                print("Timed out waiting for file to become stable.")
                break

            time.sleep(check_interval)

    def run_python_script(script_path):
        """
        Executes a Python script.
        Args:
            script_path: The path to the Python script to run.
        """
        print(f"Running script {script_path}...")
        subprocess.run(["python", script_path], check=True)



    file_path = '/Users/jorgemuyo/Desktop/Challenge/rendered_blender_video.mp4'
    script_path = '/Users/jorgemuyo/Desktop/Challenge/Hologram_Video_Layout.py'
    # Wait for the file to finish rendering and for the file modification time to be stable
    file_modification_stable(file_path)

    # Once the file is stable, run another script
    run_python_script(script_path)

    
    # Changing name and moving the image to the new folder

    # move_and_rename('/Users/jorgemuyo/Desktop/Challenge/IMG.jpg', '/Users/jorgemuyo/Desktop/Challenge/DALL-E_IMGS')


else:
    # If mistake "An error occurred: argument of type 'NoneType' is not iterable" create a file called ZOOCAD.stl
    def handle_cad_creation(prompt):
        client = Client(token="018e3c3a-6c19-788c-a05d-4c5a37bb128e")

        try:
            print("Attempting to create CAD model...")
            result = create_text_to_cad.sync(
                client=client,
                output_format=FileExportFormat.STL,
                body=TextToCadCreateBody(prompt=prompt),
            )
                    
            # Check if result is None before proceeding
            if result is None:
                print("No result from create_text_to_cad.sync, exiting...")
                return
            
            cad_response_body = get_text_to_cad_model_for_user.sync(client=client, id=result.id)
            
            # Check if cad_response_body or cad_response_body.outputs is None
            if cad_response_body is None or not hasattr(cad_response_body, 'outputs') or 'source.stl' not in cad_response_body.outputs:
                print("Failed to retrieve or decode STL file. Exiting...")
                return
            
            base64_stl_string = cad_response_body.outputs['source.stl'].get_encoded()
            padding = len(base64_stl_string) % 4
            if padding > 0:
                base64_stl_string += "=" * (4 - padding)
            
            stl_binary = base64.b64decode(base64_stl_string)
            with open('ZOOCAD.stl', 'wb') as file:
                file.write(stl_binary)
            print("CAD model saved successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")


    prompt = complete_prompt
    handle_cad_creation(prompt)

    
    # Open blender
    path_to_blender = "/Users/jorgemuyo/Desktop/Challenge/Blender_CAD.blend"
    subprocess.run(["open", path_to_blender])

    # Blender will run automaticly "blender_script.py"
    # Open the video file once blender creates it
    
    def open_file(path):
        subprocess.call(['open', path])
        while True:
            if os.path.exists(file_path):
                if os.path.getsize(file_path) > 0:  
                    print(f"{file_path} found and not empty, opening file...")
                    open_file(file_path)
                    break  
                else:
                    print(f"{file_path} exists but is empty. Waiting for file to be populated...")
            else:
                print(f"Waiting for {file_path} creation.")
                time.sleep(40)  
    


    file_path = '/Users/jorgemuyo/Desktop/Challenge/rendered_blender_video.mp4'
    script_path = '/Users/jorgemuyo/Desktop/Challenge/Hologram_Video_Layout.py'


    def file_modification_stable(file_path, stability_duration=60, check_interval=40, timeout=3600):
        """
        Waits for a file's modification time to be stable for a given duration.
        Args:
            file_path: The path to the file to monitor.
            stability_duration: The duration (in seconds) for which the file's modification time should be stable.
            check_interval: How often (in seconds) to check the file's modification time.
            timeout: The maximum time to wait in seconds.
        """
        start_time = time.time()
        last_mod_time = None
        stable_start_time = None

        while True:
            if not os.path.exists(file_path):
                print(f"{file_path} does not exist yet.")
                last_mod_time = None  
            else:
                current_mod_time = os.path.getmtime(file_path)
                if last_mod_time is None or current_mod_time != last_mod_time:
                    last_mod_time = current_mod_time
                    stable_start_time = time.time()  
                elif time.time() - stable_start_time >= stability_duration:
                    print(f"File {file_path} has been stable for {stability_duration} seconds.")
                    break

            if time.time() - start_time > timeout:
                print("Timed out waiting for file to become stable.")
                break

            time.sleep(check_interval)

    def run_python_script(script_path):
        """
        Executes a Python script.
        Args:
            script_path: The path to the Python script to run.
        """
        print(f"Running script {script_path}...")
        subprocess.run(["python", script_path], check=True)


    # Wait for the file to finish rendering and for the file modification time to be stable
    file_modification_stable(file_path)

    # Once the file is stable, run another script
    run_python_script(script_path)


    '''
    def run_python_script(script_path):
    # Replace 'python' with 'python3' if necessary on your system
        subprocess.call(['python3', script_path])

    def check_and_run_script(file_path, script_path):
        while True:
            if os.path.exists(file_path):
                if os.path.getsize(file_path) > 0:
                    print(f"{file_path} found and not empty, running script...")
                    run_python_script(script_path)
                    break
                else:
                    print(f"{file_path} exists but is empty. Waiting for file to be populated...")
            else:
                print(f"Waiting for {file_path} creation.")
            time.sleep(20)

    # Example usage

    check_and_run_script(file_path, script_path)
    
'''
    




path_to_video = "/Users/jorgemuyo/Desktop/Challenge/VIDEO/DEFINITIVE_HOLOGRAM.mp4"
time.sleep(360) 
#open_file(path_to_video)