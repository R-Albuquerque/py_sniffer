import PySimpleGUI as sg
import os
import socket
import struct
from ctypes import *


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

    def __new__(cls, socket_buffer=None):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        self.socket_buffer = socket_buffer

        # mapeando as constantes dos protocolos aos nomes
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        # endereço IP em forma legível
        self.source = socket.inet_ntoa(struct.pack("@I", self.src))
        self.destination = socket.inet_ntoa(struct.pack("@I", self.dst))

        # obter o nome do protocolo em forma legível
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except IndexError:
            self.protocol = str(self.protcol_num)

hostname = socket.getfqdn()
this_host = socket.gethostbyname_ex(hostname)[2][1]

sg.theme('BrownBlue')


config_col = [
    [
        sg.Text("Host:", justification='right', size=(25, 1), ),
        sg.In(size=(25, 1), enable_events=True, key="-HOST-", default_text=this_host),
        sg.Text("# of Packets:", justification='right', size=(10, 1), ),
        sg.Combo([5,10,15], default_value=5, key='numPack'),
        sg.Button("Capture", size=(25, 1)),

    ],
    [
        sg.Table(headings=['Protocol', 'Source', 'Destination'], values=[], expand_x=True, enable_events=True, justification='c', key="-TABLE-")
    ]

]

# Layout da interface gráfica
layout = [
    [
        sg.Column(config_col),

    ]
]

window = sg.Window("Py Sniffer", layout)
valores = []
while True:
    
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    if event == "Capture":
        host = values['-HOST-']
        
        if os.name == 'nt':
         socket_protocol = socket.IPPROTO_IP
        else:
            socket_protocol = socket.IPPROTO_ICMP

        sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

        # Criando um raw socket e associando à interface pública
        sniffer.bind((host, 0))

        # Incluindo os IP HEADERS na captura
        sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        # no windows mandaremos IOCTL para habilitar o modo promíscuo
        if os.name == "nt":
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
        
        try:
            counter = 0
            while counter < values['numPack']:
                # Ler um pacote:
                raw_buffer = sniffer.recvfrom(65535)[0]

                # Obtendo o cabeçalho IP a partir dos primeiros 20 bytes do buffer:
                ip_header = IP_protocol(raw_buffer[:20])

                # Atualizando a tabela na Interface
                window['-TABLE-'].Widget.insert('', 'end', values=[ip_header.protocol,ip_header.source,ip_header.destination])
                read = True
                counter += 1

        except KeyboardInterrupt:
            # Desligar o modo promíscuo da placa de rede no Windows
            if os.name == "nt":
                sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

window.close()
