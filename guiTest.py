import PySimpleGUI as sg
import os.path

sg.theme('BlueMono')

config_col = [
    [
        sg.Text("Host",justification='right',size=(25,1)),
        sg.In(size=(25,1), enable_events=True, key = "-FOLDER-"),
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
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
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