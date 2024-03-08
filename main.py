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
# Hologram
import Hologram 



# Initialize
recognizer = sr.Recognizer()
openai_api_key = ""
openAI_client = OpenAI(api_key=openai_api_key)
#client = Client(api_key=api_key)



#Record a audio and get text
#with sr.Microphone() as source:
#    print("Say something!")
#audio = recognizer.listen(source, 3, 8)

#audio_transcription = recognizer.recognize_google(audio)
#print(audio_transcription)

audio_transcription = "give me model of a watermelon"

model_in_text = "model"
Open_AI_prompt ="apply a holographic filter"

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
    client = Client(token="")

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
    
    # Changing name and moving the image to the new folder

    move_and_rename('/Users/jorgemuyo/Desktop/Challenge/IMG.jpg', '/Users/jorgemuyo/Desktop/Challenge/DALL-E_IMGS')


else:
    def handle_cad_creation(prompt):
        client = Client(token="018e1d57-8e35-7614-a24b-d68ed3c3ac7a")

        try:
            print("Attempting to create CAD model...")
            result = create_text_to_cad.sync(
                client=client,
                output_format=FileExportFormat.STL,
                body=TextToCadCreateBody(prompt=prompt),
            )
                    
            if not result:
                print("Model generation not working")
                return
            
            cad_response_body = get_text_to_cad_model_for_user.sync(client=client, id=result.id)
            
            if cad_response_body and hasattr(cad_response_body, 'outputs') and 'source.stl' in cad_response_body.outputs:
                base64_stl_string = cad_response_body.outputs['source.stl'].get_encoded()
                padding = len(base64_stl_string) % 4
                if padding > 0:
                    base64_stl_string += "=" * (4 - padding)
                
                stl_binary = base64.b64decode(base64_stl_string)
                with open('ZOOCAD.stl', 'wb') as file:
                    file.write(stl_binary)
                print("CAD model saved successfully.")
            else:
                print("Failed to retrieve or decode STL file.")
            
        except Exception as e:
            print(f"An error occurred: {e}")

    prompt = complete_prompt
    handle_cad_creation(prompt)


    # Open blender
    path_to_blender = "/Users/jorgemuyo/Desktop/Challenge/ZOO_CAD_ANIMATION.blend"
    subprocess.run(["open", path_to_blender])

    # Blender will run automaticly "blender_script.py"
    # Open the video file once blender creates it
    file_path = '/Users/jorgemuyo/Desktop/Challenge/rendered_blender_video.avi'

    def open_file(path):
        subprocess.call(['open', path])

    while True:
        if os.path.exists(file_path):
            if os.path.getsize(file_path) > 0:  
                print(f"{file_path} found and it is not empty, opening file...")
                open_file(file_path)
                break  
            else:
                print(f"{file_path} exists but is empty. Waiting for file to be populated...")
        else:
            print(f"Waiting for {file_path} to be created...")

        time.sleep(3)  
    
    move_and_rename('/Users/jorgemuyo/Desktop/Challenge/ZOOCAD.stl', '/Users/jorgemuyo/Desktop/Challenge/ZOO_CAD')
