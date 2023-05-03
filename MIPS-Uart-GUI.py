import PySimpleGUI as sg
import os
import serial

# Crear una nueva ventana con tamaño personalizadosudo apt-get install python-tk
layout = [[sg.Text('Seleccionar .asm')],
          [sg.Input(key='file_path'), sg.FileBrowse('Browse')],
          [sg.Button('Aceptar')],
          [sg.Multiline('',size=(30,10),key="textarea")],
          [sg.Button('Convertir'), sg.Button('Enviar')]]

window = sg.Window('MIPS-UART-GUI', layout, size=(1000, 600))

habemus_file = False
ready_to_send = False

# Ejecutar el bucle principal de eventos
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == 'Browse':
        # Actualizar el elemento de texto con la ruta del archivo seleccionado
        file_path = values['file_path']
        window['file_path'].update(file_path)
    elif event == 'Aceptar':
        file_path = values['file_path']
        # validación del tipo de archivo
        if not file_path.endswith('.asm'):
            sg.popup_ok('El archivo no es un .asm')
            continue
        file = open(file=file_path,mode="r")
        # printear el contentido en una textarea
        window['textarea'].update(file.read())
        habemus_file = True
    elif event == 'Convertir':
        # ver si hay algo en el text area
        if not habemus_file:
            sg.popup_ok('Debe seleccionar un archivo')
            continue
        # Llamada al programa
        os.system("python3 -W ignore asm-to-bin.py" + " " + file_path + " " +"output.hex")
        # sp.call(['python3','-W ignore','asm-to-bin.py',file_path,'output.txt'])
        ready_to_send = True
    elif event == 'Enviar':
        if not ready_to_send:
            sg.popup_ok('Primero debe seleccionar un programa y convertirlo a código máquina')
            continue
        try:
            # gilada
            ser = serial.Serial('/dev/ttyS0', 9600, 8, timeout=1)
            with open("output.hex", "rb") as f:
                while True:
                    data = f.read(32)
                    if not data:
                        break
                    ser.write(data)
            ser.close()
        except serial.SerialException as e:
            # explota
            sg.popup_ok('Hay un problema con el puerto serie')
            continue

# Cerrar la ventana y salir del programa
window.close()