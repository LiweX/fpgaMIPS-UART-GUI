import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import serial
import os

main_window = tk.Tk()
main_window.geometry('1000x800')

class Flags:
    habemus_file:bool
    ready_to_send:bool
    connected:bool
    ser:serial

flags = Flags()
flags.habemus_file=False
flags.ready_to_send=False
flags.connected=False

def browse_file():
    filepath = filedialog.askopenfilename()
    browse_entry.delete(0, tk.END) # borra el contenido actual del Entry
    browse_entry.insert(0, filepath) # inserta la ruta del archivo seleccionado en el Entry

def load_file(flags):
    if not browse_entry.get().endswith('.asm'):
        messagebox.showinfo("Error de formato", "El archivo no es un .asm")
        return
    file = open(file=browse_entry.get(),mode="r")
    text_area.delete(1.0,tk.END)
    text_area.insert(tk.END,file.read())
    file.close()
    flags.habemus_file=True

def connect(flags):
    if flags.connected:
        messagebox.showinfo("Aviso", "Ya se encuentra conectado")
        return
    try:
        flags.ser = serial.Serial(port_entry.get(), 9600, 8, timeout=1)
    except serial.SerialException:
        messagebox.showinfo("Error de conexion", "Hay un problema con el puerto serie")
        return
    else:
        messagebox.showinfo("Aviso", "Conexión establecida exitosamente.")
        flags.connected = True


def convert(flags):
    if not flags.habemus_file:
        messagebox.showinfo("Error", "Debe seleccionar un archivo")
        return
    os.system("python -W ignore asm-to-bin.py" + " " + browse_entry.get() + " " +"output.hex")
    flags.ready_to_send=True

def send(flags):
    if not flags.ready_to_send:
        messagebox.showinfo("Manijin", 'Primero debe seleccionar un programa y convertirlo a código máquina')
        return
    if not flags.connected:
        messagebox.showinfo("Error de conexion", 'Primero hay que conectarse al puerto serie')
    try:
        with open("output.hex", "rb") as f:
            while True:
                data = f.read(32)
                if not data:
                    break
                flags.ser.write(data)
    except serial.SerialException as e:
        # explota
        messagebox.showinfo("Error de conexion", "Hubo un problema con el puerto serie")
        return
    

select_label = tk.Label(main_window,text="Seleccione el archivo .asm")
select_label.place(x=10, y=10)

browse_entry = tk.Entry(main_window,width=45)
browse_entry.place(x=12,y=35)

browse_button = tk.Button(main_window, text="Browse", command=browse_file)
browse_button.place(x=300,y=30)

accept_button = tk.Button(main_window, text="Aceptar", command=lambda: load_file(flags))
accept_button.place(x=12,y=60)

text_area = tk.Text(main_window,width=30,height=10)
text_area.place(x=12,y=120)
scrollbar = tk.Scrollbar(main_window)
scrollbar.place(x=270,y=120,height=170)
text_area.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=text_area.yview)


port_label = tk.Label(main_window,text="Puerto serie:")
port_label.place(x=10,y=90)
port_entry = tk.Entry(main_window,width=10)
port_entry.place(x=85,y=90)
connect_button = tk.Button(main_window, text="Conectar", command=lambda: connect(flags))
connect_button.place(x=160,y=85)

convert_button = tk.Button(main_window, text="Convertir", command=lambda: convert(flags))
convert_button.place(x=12 ,y=290)
send_button = tk.Button(main_window, text="Enviar", command=lambda: send(flags))
send_button.place(x=80 ,y=290)


main_window.mainloop()