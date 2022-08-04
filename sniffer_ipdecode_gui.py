import PySimpleGUI as sg
import os
import socket
import struct
from ctypes import *

sg.theme('BlueMono')

config_col = [
    [
        sg.Text("Host",justification='right',size=(25,1)),
        sg.In(size=(25,1), enable_events=True, key = "-HOST-"),
        sg.Button("Capture",size=(25,1)),

    ],
    [
        # sg.Listbox(
        #     values=[], enable_events=True, size=(100,5), key="-FLIST-"
        # )
        sg.Table(headings=['Protocol','Source','Destination'], values=[], expand_x = True, enable_events=True, justification='c',key="-FLIST-")
    ]

]
img_col = [
    [sg.Text("Choose an image from list.",justification='right',size=(55,1))],
    [sg.Text(size=(25,1), key="-TOUT-")],
    [sg.Image(key="-IMAGE-")],
]

# --- Full Layout ---
layout = [
    [
        sg.Column(config_col),

    ],
    # [sg.Column(result_col)],
    [sg.HSeparator(),],
    [
        sg.Column(img_col)
    ],
]

window = sg.Window("Image Viewer", layout)

while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    if event == "-CAPTURE-":
        folder = values["-CAPTURE-"]
        try:
            file_list = os.listdir(folder)
        except:
            file_list = []

        fnames = [
            f
            for f in file_list
            if os.path.isfile(os.path.join(folder,f))
            and f.lower().endswith((".png",".gif"))
        ]
        window["-FLIST-"].update(fnames)

    elif event == "-FLIST-":
        try:
            filename =os.path.join(
                values["-FOLDER-"], values["-FLIST-"][0]
            )
            window["-TOUT-"].update(filename)
            window["-IMAGE-"].update(filename=filename)
        except:
            pass

window.close()






# =====================================================================================
host ='192.168.0.7'

class IP_protocol(Structure):
        
    _fields_ = [
        ("ihl", c_ubyte, 4),
        ("version", c_ubyte, 4),
        ("tos", c_ubyte),
        ("len", c_ushort),
        ("id", c_ushort),
        ("offset", c_ushort),
        ("ttl", c_ubyte),
        ("protocol_num", c_ubyte),
        ("sum", c_ushort),
        ("src", c_uint32),
        ("dst", c_uint32)
    ]

    def __new__(cls, socket_buffer = None):
        return cls.from_buffer_copy(socket_buffer)
    
    def __init__(self, socket_buffer=None):
        self.socket_buffer = socket_buffer

        # mapeando as constantes dos protocolos aos nomes
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        # endereço IP em forma legível
        self.src_address = socket.inet_ntoa(struct.pack("@I", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("@I", self.dst))

        # obter o nome do protocolo em forma legível
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except IndexError:
            self.protocol = str(self.protcol_num)

# Criando um raw socket e associando à interface pública 
if os.name == 'nt':
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

# Criando um raw socket e associando à interface pública 
sniffer.bind((host,0))

# Incluindo os IP HEADERS na captura
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# no windows mandaremos IOCTL para habilitar o modo promíscuo
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

try:
    counter = 0
    while counter < 10:
        # Ler um pacote:
        raw_buffer = sniffer.recvfrom(65535)[0]

        #Obtendo o cabeçalho IP a partir dos primeiros 20 bytes do buffer:
        ip_header = IP_protocol(raw_buffer[:20])

        print("Protocol: %s %s -> %s" % (
            ip_header.protocol,
            ip_header.src_address,
            ip_header.dst_address)
              )
        counter += 1

except KeyboardInterrupt:
    # if we're on Windows turn off promiscuous mode
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
