from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import socketserver
import socket
import cgi
import argparse
from PIL import Image
from io import BytesIO
import multiprocessing
import queue

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", help="Port")
parser.add_argument("-i", "--ip", help="IP address")
args = parser.parse_args()

in_queue = multiprocessing.Queue()
out_queue = multiprocessing.Queue()


def process_image(img_data):
    try:
        img_processed = Image.open(BytesIO(img_data)).convert('L')
        output_buffer = BytesIO()
        img_processed.save(output_buffer, format="JPEG")
        return output_buffer.getvalue()
    except Exception as e:
        print(f'Error al procesar la imagen: {str(e)}')
        return b''  # Devuelve una cadena vacía si hay un error para evitar problemas adicionales


def imgProcessor(in_queue, out_queue):
    while True:
        try:
            img_data = in_queue.get()
            print(f'Servicio: Procesando imagen')
            try:
                img_processed = process_image(img_data)
            except Exception as e:
                print(f'Error de servicio: La imagen está corrupta o ocurrió un error: {str(e)}')
                continue
            print(f'Servicio: Enviando imagen')
            out_queue.put(img_processed)
        except queue.Empty:
            continue
        except Exception as e:
            print(f'Error de servicio: {str(e)}')
            continue

        if img_data == 'hasta la vista':
            print(f'Servicio: Cerrando servicio')
            break

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path.lower() == '/process_image':
            try:
                content_type, _ = cgi.parse_header(self.headers['Content-Type'])
                if content_type == 'multipart/form-data':
                    print(f'Servidor: Recibiendo imagen')
                    content_length = int(self.headers['Content-Length'])
                    img_data = self.rfile.read(content_length)

                    print(f'Servidor: Solicitando servicio de procesado de imágenes')
                    in_queue.put(img_data)

                    print(f'Servidor: Recibiendo respuesta del servicio')
                    img_processed = out_queue.get()

                    print(f'Servidor: Enviando imagen procesada')

                    self.send_response(200)
                    self.send_header('Content-type', 'image/jpeg')
                    self.end_headers()
                    self.wfile.write(img_processed)

                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'Error: Formato de solicitud incorrecto.')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f'Error: {str(e)}'.encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

if __name__ == "__main__":
    HOST = args.ip
    PORT = int(args.port)

    if ':' in HOST:
        addressFamily = socket.AF_INET6
        print("IPv6")
    else:
        addressFamily = socket.AF_INET
        print("IPv4")

    socketserver.TCPServer.allow_reuse_address = True
    socketserver.TCPServer.address_family = addressFamily
    myHandler = Handler
    httpServer = ThreadingHTTPServer((HOST, PORT), myHandler)

    print(f"Abriendo servidor HTTP en el puerto {PORT}")

    process = multiprocessing.Process(target=imgProcessor, args=(in_queue, out_queue))
    process.start()

    try:
        httpServer.serve_forever()
    except KeyboardInterrupt:
        in_queue.put('hasta la vista')  
        process.join()
        httpServer.server_close()
        print("Servidor principal: Servidor cerrado correctamente.")
