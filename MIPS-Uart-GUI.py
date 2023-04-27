import PySimpleGUI as sg

# Crear una nueva ventana con tamaño personalizado
layout = [[sg.Text('Seleccionar .asm')],
          [sg.Input(key='file_path'), sg.FileBrowse('Browse')],
          [sg.Button('Aceptar')],
          [sg.Multiline('',size=(30,10),key="shereng")]]


window = sg.Window('MIPS-UART-GUI', layout, size=(1000, 600))

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
        window['shereng'].update(file.read())
        # printear el contentido en una textarea

# Cerrar la ventana y salir del programa
window.close()