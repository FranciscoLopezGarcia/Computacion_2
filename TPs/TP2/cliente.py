import aiohttp
import asyncio
import argparse
import requests
from PIL import Image
from datetime import datetime

async def send_image_to_server(image_path, scale_factor, server_url):
    try:
        with open(image_path, 'rb') as file:
            image_data = file.read()
        data = aiohttp.FormData()
        data.add_field('image', image_data, filename='image.png', content_type='image/png')
        data.add_field('scale_factor', str(scale_factor))
        async with aiohttp.ClientSession() as session:
            async with session.post(server_url, data=data) as response:
                response_data = await response.read()
                if response.status == 200:
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    with open(f'received_image_{timestamp}.png', 'wb') as out_file:
                        out_file.write(response_data)
                    print('Received and saved image')
                else:
                    print('Error: Server returned status code', response.status)
    except Exception as e:
        print(f"Error sending image to server: {e}")

def prepare_image(image):
    try:
        with open(image, 'rb') as file:
            img = Image.open(file)
            img = img.convert('L')  # Convertir a escala de grises si es necesario
            img = img.convert('RGB')  # Convertir a formato RGB
            img_bytes = img.tobytes()
        return img_bytes
    except Exception as e:
        print(f"Error preparing image: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send and receive images from a server.', add_help=False)
    parser.add_argument('-i', '--image_path', type=str, default='pinguino.jpg', help='The path to the image to send.')
    parser.add_argument('-s', '--scale_factor', type=float, required=True, help='The scale factor for the image.')
    parser.add_argument('-p', '--port', help='Port for server connection.')
    parser.add_argument('-ip', '--ip', help='IP address for server connection.')
    args = parser.parse_args()

    if args.port and args.ip:
        server_url = f"http://{args.ip}:{args.port}/process_image"
        asyncio.run(send_image_to_server(args.image_path, args.scale_factor, server_url))
    else:
        print("Please provide both --ip and --port arguments.")
