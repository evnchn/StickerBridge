from flask import Flask, request, send_file
import os
import zipfile
import base64
from io import BytesIO
# from PIL import Image
from glob import glob
from wand.image import Image
from wand.color import Color

app = Flask(__name__)

from PIL import Image as PILImage

import time

PASSWORD = 'password here'

def resizeImg(sourceFile, destFile, width, height):                                                                                                                                                                                                                                       
    with Image(width=width, height=height) as outerImg:                                                                                                                                                                                                                                     
        with Image(filename=sourceFile) as img:                                                                                                                                                                                                                                               
            img.transform(resize="%dx%d>" % (width, height))                                                                                                                                                                                                                                    
            outerImg.format = img.format.lower()                                                                                                                                                                                                                                                
            outerImg.composite(img, left=(width - img.width) // 2, top=(height - img.height) // 2)                                                                                                                                                                                                
            outerImg.save(filename=destFile)

@app.route('/download')
def download():
    # check if the authentication parameter is present in the request
    auth_param = request.headers.get('evnchn-bridge-auth')
    print(request.headers.get('evnchn-bridge-auth'))
    
    if not auth_param:
        return 'Authentication required', 401

    # check the validity of the authentication parameter
    if auth_param != PASSWORD:
        return 'Invalid authentication', 401

    # create a zip file of the "output" folder
    output_folder = 'output'
    zip_filename = 'output.zip'
    try:
        os.remove(zip_filename)
    except:
        pass
    with open(zip_filename, "w") as f:
        pass
    zf = zipfile.ZipFile(zip_filename, mode='w')
                
    for root, dirs, files in os.walk(output_folder):
        for file in files:
            
            if "120_" not in str(file) and ".unknown" not in str(file):
                file_path = os.path.join(root, file)
                zf.write(file_path)
            else:
                print(file)

    zf.close()

    # serve the zip file as a response to the user
    return send_file(zip_filename, as_attachment=True)
    
    
@app.route('/convert', methods=['POST'])
def convert():
    # check if the authentication parameter is present in the request
    auth_param = request.headers.get('evnchn-bridge-auth')
    print(request.headers.get('evnchn-bridge-auth'))
    
    if not auth_param:
        return 'Authentication required', 401

    # check the validity of the authentication parameter
    if auth_param != PASSWORD:
        return 'Invalid authentication', 401

    the_data = request.get_data()
    
    with open('Output.webp', 'wb') as output_file:
        output_file.write(the_data)
    # convert the WebP image to a GIF
    '''im = Image.open('Output.webp')
    im.info.pop('background', None)
    im.save('image.gif', 'gif', save_all=True)'''
    
    ny = Image(filename='Output.webp')
    ny_convert = ny.convert('gif')
    ny_convert.save(filename ='image2.gif')

    return send_file('image2.gif')
    
@app.route('/download_stickers') 
def download_stickers():
    # check if the authentication parameter is present in the request
    auth_param = request.headers.get('evnchn-bridge-auth')
    print(request.headers.get('evnchn-bridge-auth'))
    
    if not auth_param:
        return 'Authentication required', 401

    # check the validity of the authentication parameter
    if auth_param != PASSWORD:
        return 'Invalid authentication', 401

    # create a zip file of the "output" folder
    sticker_folder = 'sticker'
    zip_filename = 'sticker.wastickers'
    
    try:
        os.remove(zip_filename)
    except:
        pass
    with open(zip_filename, "w") as f:
        pass
        
    zf = zipfile.ZipFile(zip_filename, mode='w')
                
    zf.write("author.txt")
    zf.write("title.txt")
    
    for root, dirs, files in os.walk(sticker_folder):
        for file in files:
            if not ".txt" in str(file):
                file_path = os.path.join(root, file)
                zf.write(file_path, file)

    
    zf.close()
    
    # serve the zip file as a response to the user
    return send_file(zip_filename, as_attachment=True)
    
@app.route('/upload', methods=['POST'])
def upload():


    time_str = str(int(time.time()))
    # check if the authentication parameter is present in the request
    auth_param = request.headers.get('evnchn-bridge-auth')
    print(request.headers.get('evnchn-bridge-auth'))
    
    if not auth_param:
        return 'Authentication required', 401

    # check the validity of the authentication parameter
    if auth_param != PASSWORD:
        return 'Invalid authentication', 401

    the_data = request.get_data()
    
    with open('upload.gif', 'wb') as output_file:
        output_file.write(the_data)
    try:
        ny2 = Image(filename='upload.gif')
        ny2.coalesce()

        ny2.transform(resize='512x512')
        ny2.background_color = Color("rgba(0, 0, 0, 0)")
        ny2_convert = ny2.convert('webp')
        
        ny2_convert.extent(512,512)
        ny2_convert.coalesce()
        
        ny2_convert.compression_quality = 10
        ny2_convert.save(filename =f'sticker/{time_str}.webp')
        print(os.path.getsize(f'sticker/{time_str}.webp'))

        if os.path.getsize(f'sticker/{time_str}.webp') > 500*1024:
            1/0 # raise error
        print("Using ImageMagick")
    except Exception as e:
        print(e)
        im = PILImage.open('upload.gif')
        im = im.resize((512,512))
        im.save(f'sticker/{time_str}.webp', format='WEBP', save_all=True)
        print("Using PIL")
        
    STICKER_FOLDER = 'sticker/'

    # Get a list of all WEBP files in the stickers folder
    webp_files = [f for f in os.listdir(STICKER_FOLDER) if f.endswith('.webp')]

    # Sort the list of files by modification time (oldest first)
    webp_files.sort(key=lambda f: os.path.getmtime(os.path.join(STICKER_FOLDER, f)))

    # Loop through the list of files, removing the oldest ones until there are only 3 left
    while len(webp_files) > 3:
        oldest_file = webp_files.pop(0)
        os.remove(os.path.join(STICKER_FOLDER, oldest_file))

    print(f'{len(webp_files)} webp files remaining in the stickers folder.')
    
    return "OK"

    
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=False)