from flask import Flask, render_template, request
from PIL import Image
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def encode_data(image, data):
# Convert data to binary
    binary_data = ''.join(format(ord(char), '08b') for char in data)

    # Get the image pixels as a list
    pixels = list(image.getdata())

    # Get the number of color channels in the image
    num_channels = len(pixels[0])

    # Encode the binary data into the image pixels
    encoded_pixels = []
    data_index = 0
    for pixel in pixels:
        # Check if all data bits have been encoded
        if data_index >= len(binary_data):
            encoded_pixels.append(pixel)
            continue

        # Encode the binary data based on the number of color channels
        modified_pixel = list(pixel)
        for channel in range(num_channels):
            if data_index < len(binary_data):
                modified_pixel[channel] = (modified_pixel[channel] & 0xFE) | int(binary_data[data_index])
                data_index += 1

        # Update the pixel with the modified values
        encoded_pixels.append(tuple(modified_pixel))

    # Create a new image with the encoded pixels
    encoded_image = Image.new(image.mode, image.size)
    encoded_image.putdata(encoded_pixels)

    return encoded_image

def decode_data(image):
    # Get the image pixels as a list
    pixels = list(image.getdata())

    # Get the number of color channels in the image
    num_channels = len(pixels[0])

    # Extract the hidden data from the image pixels
    binary_data = ""
    for pixel in pixels:
        # Extract the binary data based on the number of color channels
        for channel in range(num_channels):
            binary_data += str(pixel[channel] & 1)

    # Convert the binary data to ASCII characters
    decoded_data = ""
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i + 8]
        decoded_data += chr(int(byte, 2))

    return decoded_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Get the uploaded image file
    image = request.files['image']

    # Open the image using PIL
    img = Image.open(image)

    # Get the data to be hidden
    data = request.form['data']

    # Encode the data into the image
    encoded_img = encode_data(img, data)

    # Save the encoded image to the server
    encoded_img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_image.png')
    encoded_img.save(encoded_img_path)

    # Return the saved filename as a response
    return f"The encoded image has been saved as: {encoded_img_path}"

@app.route('/decode', methods=['GET', 'POST'])
def decode():
    if request.method == 'POST':
        # Get the uploaded image file
        image = request.files['image']

        # Save the uploaded image to the server
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(image_path)

        # Open the image using PIL
        img = Image.open(image_path)

        # Decode the hidden data from the image
        decoded_data = decode_data(img)

        # Render the decode.html template with the image path and decoded data
        return render_template('decode.html', image=image_path, decoded_data=decoded_data)

    # Render the decode.html template for the initial GET request
    return render_template('decode.html')

if __name__ == '__main__':
    app.run(debug=True)