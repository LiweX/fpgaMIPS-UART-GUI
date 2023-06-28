import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import serial
import os
import threading

main_window = tk.Tk()
main_window.geometry('710x490') # resolution de la window
main_window.title("MIPS UART GUI")
main_window.config(background="lightblue")
main_window.resizable(False, False)

MAX_LIMIT = 32
MIN_LIMIT = 1

class Flags: # objeto flags para usar como flags valga la redundancia
    habemus_file:bool # para saber si ya esta cargado el programa
    ready_to_send:bool # para saber si esta todo listo para enviar
    connected:bool # para saber si conectado el puerto serie
    hex_dec:bool # para saber si mostrar los datos en formato hexadecimal o decimal (False = hex)

class thread(threading.Thread):
    pressed_char:str = ""

    def __init__(self, thread_name, thread_ID):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_ID

    def run(self):
        while True:
            if ser.inWaiting():
                received = int.from_bytes(ser.readline(), byteorder='big')
                receivedHex = f'0x{received:08X}'

                print(received) # decimal
                print(receivedHex) # hexadecimal

                # si incremento o decremento el puntero de registro...
                if self.pressed_char in ['E', 'T']:
                    register_pointer.prev_val = register_pointer.value
                    register_pointer.value = received + 1
                    register_pointer.update_labels()

                # si incremento o decremento el puntero de memoria...
                if self.pressed_char in ['N', ',']:
                    memory_pointer.prev_val = memory_pointer.value
                    memory_pointer.value = int(received / 4) + 1
                    memory_pointer.update_labels()

                if self.pressed_char=='P':
                    PC_frame.config(text=received)
                elif self.pressed_char=='M':
                    memory_pointer.label.config(text="R{0}: {1}".format(memory_pointer.value - 1, received if flags.hex_dec else receivedHex))
                elif self.pressed_char=='R':
                    register_pointer.label.config(text="R{0}: {1}".format(register_pointer.value - 1, received if flags.hex_dec else receivedHex))

flags = Flags()
flags.habemus_file=False
flags.ready_to_send=False
flags.connected=False
flags.hex_dec=False
class Pointer:
    value:int
    prev_val:int
    pointer_type:str
    frame:tk.Frame
    label:tk.Label
    prev_label:tk.Label
    MIN=1
    MAX=32

    def __init__(self,pointer_type):
        self.value=1
        self.prev_val=1
        self.pointer_type = pointer_type

    def get_value(self):
        return self.value

    def get_prev(self):
        return self.prev_val

    def set_frame(self,frame:tk.Frame):
        self.frame=frame

    def update_labels(self): # con eso se cazan los labels de los registros para cuando estan resaltados o deben de dejar de resaltarse
        self.label=self.frame.winfo_children()[self.value-1]
        self.prev_label=self.frame.winfo_children()[self.prev_val-1]
        self.update_grid()

    def update_grid(self): # se pinta de blanco el registro apuntado anterior y se pinta el nuevo de amarillo
        self.prev_label.config(bg="white")
        self.label.config(bg="yellow")


def browse_file():  # se llama al apretar el boton browse
    filepath = filedialog.askopenfilename()
    browse_entry.delete(0, tk.END) # borra el contenido actual del Entry
    browse_entry.insert(0, filepath) # inserta la ruta del archivo seleccionado en el Entry

def load_file(flags): # se llama al apretar el boton aceptar
    if not browse_entry.get().endswith('.asm'):
        messagebox.showinfo("Error de formato", "El archivo no es un .asm")
        return
    file = open(file=browse_entry.get(),mode="r")
    text_area.delete(1.0,tk.END)
    text_area.insert(tk.END,file.read())
    file.close()
    flags.habemus_file=True

def connect(flags): # se llama al apretar el boton conectar
    if flags.connected:
        messagebox.showinfo("Aviso", "Ya se encuentra conectado")
        return
    try:
        global ser
        ser = serial.Serial(port_entry.get(), 9600, 8, timeout=1)
    except serial.SerialException:
        messagebox.showinfo("Error de conexion", "Hay un problema con el puerto serie")
        return
    else:
        messagebox.showinfo("Aviso", "Conexión establecida exitosamente.")
        flags.connected = True
        global serial_thread
        serial_thread = thread("SERIAL_THREAD", "666")
        serial_thread.start()
        # fixeo pointers
        aumentar_puntero_reg()

def convert(flags): # se llama al apretar convertir
    if not flags.habemus_file:
        messagebox.showinfo("Error", "Debe seleccionar un archivo")
        return
    os.system("python -W ignore asm-to-bin.py " + browse_entry.get() + " output.hex")
    flags.ready_to_send=True

def send(flags): # se llama al apretar enviar
    if not flags.ready_to_send:
        messagebox.showinfo("Manijin", 'Primero debe seleccionar un programa y convertirlo a código máquina')
        return
    if not flags.connected:
        messagebox.showinfo("Error de conexion", 'Primero hay que conectarse al puerto serie')
    try:
        ser.write(b'B')
        with open("output.hex", "rb") as f:
            while True:
                data = f.read(32)
                if not data:
                    break
                ser.write(data)

    except serial.SerialException:
        messagebox.showinfo("Error de conexion", "Hubo un problema con el puerto serie")
        return

def run():
    ser.write(b'G')
    serial_thread.pressed_char = 'G'
    print("Apretaste Run")

def step():
    print("Apretaste Step")
    ser.write(b'S')

def get_PC():
    print("Pediste el valor del PC")
    serial_thread.pressed_char = 'P'
    ser.write(b'P')

def get_memoria():
    ser.write(b'M')
    serial_thread.pressed_char = 'M'
    print("Pediste el valor de memoria apuntado")

def get_registro():
    ser.write(b'R')
    serial_thread.pressed_char = 'R'
    print("Pediste el valor de registro apuntado")

def aumentar_puntero_reg():
    if register_pointer.value < MAX_LIMIT:
        ser.write(b'T')
        serial_thread.pressed_char = 'T'
        print("Apuntando a R%d" % register_pointer.get_value())

def aumentar_puntero_mem():
    if memory_pointer.value < MAX_LIMIT / 4:
        ser.write(b',')
        serial_thread.pressed_char = ','
        print("Apuntando a R%d" % memory_pointer.get_value())

def disminuir_puntero_reg():
    if register_pointer.value > MIN_LIMIT:
        ser.write(b'E')
        serial_thread.pressed_char = 'E'
        print("Apuntando a R%d" % register_pointer.get_value())

def disminuir_puntero_mem():
    if memory_pointer.value > MIN_LIMIT:
        ser.write(b'N')
        serial_thread.pressed_char = 'N'
        print("Apuntando a R%d" % memory_pointer.get_value())

def erase_program(flags:Flags):
    ser.write(b'F')
    print("Borraste el programa")
    os.remove("./output.hex")
    flags.habemus_file = False
    flags.ready_to_send = False
    text_area.delete(1.0, tk.END)

def Simpletoggle():
    flags.hex_dec = not flags.hex_dec
    if toggle_button.config('text')[-1] == 'DEC':
        toggle_button.config(text='HEX')
    else:
        toggle_button.config(text='DEC')


toggle_button = tk.Button(text="HEX", width=10, command=Simpletoggle)
toggle_button.place(x=587,y=350)

select_label = tk.Label(main_window,text="Seleccione el archivo .asm",background="lightblue")
select_label.place(x=10, y=10)

browse_entry = tk.Entry(main_window,width=35)
browse_entry.place(x=12,y=35)

browse_button = tk.Button(main_window, text="Browse", command=browse_file)
browse_button.place(x=240,y=30)

open_button = tk.Button(main_window, text="Abrir", command=lambda: load_file(flags))
open_button.place(x=12,y=60)

port_label = tk.Label(main_window,text="Puerto serie:", background="lightblue")
port_label.place(x=10,y=90)
port_entry = tk.Entry(main_window,width=10)
port_entry.place(x=85,y=90)
port_entry.insert(tk.END,"COM6")
connect_button = tk.Button(main_window, text="Conectar", command=lambda: connect(flags))
connect_button.place(x=160,y=85)

text_area = tk.Text(main_window,width=30,height=19)
text_area.place(x=12,y=120)
scrollbar = tk.Scrollbar(main_window)
scrollbar.place(x=270,y=120,height=310)
text_area.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=text_area.yview)

convert_button = tk.Button(main_window, text="Convertir", command=lambda: convert(flags))
convert_button.place(x=12 ,y=440)
send_button = tk.Button(main_window, text="Enviar", command=lambda: send(flags))
send_button.place(x=80 ,y=440)

PC_label = tk.Label(main_window,text="PC:", background="lightblue")
PC_label.place(x=320,y=30)
PC_frame = tk.Label(width=5,height=1,bg="white",fg="black",relief=tk.SUNKEN,bd=3,justify="center",text="1")
PC_frame.place(x=350,y=30)
PC_button = tk.Button(main_window,text="Get", command=get_PC)
PC_button.place(x=400,y=27)

run_button = tk.Button(main_window,text="Run",width=10, command=run, background="lightgreen")
run_button.place(x=470,y=27)
step_button = tk.Button(main_window,text="Step",width=10, command=step, background="orange")
step_button.place(x=560,y=27)

registers_label = tk.Label(main_window,text="Registros", background="lightblue")
registers_label.place(x=390,y=70)
registers_frame = tk.Frame(main_window)
for i in range(32):
    label = tk.Label(registers_frame,bg="white", text=f"R{i}",relief=tk.SUNKEN,bd=2,width=15,height=1)
    if i % 2 == 0:
        label.grid(row=32-i,column=0)
    else:
        label.grid(row=32-i+1,column=1)
registers_frame.place(x=310,y=100)

register_selector_frame = tk.Frame(main_window)
up_register_button = tk.Button(register_selector_frame,text="⇧",command=aumentar_puntero_reg)
up_register_button.grid(row=0,column=2,)
get_register_button = tk.Button(register_selector_frame,text="Get",command=get_registro)
get_register_button.grid(row=0,column=1)
down_register_button = tk.Button(register_selector_frame,text="⇩",command=disminuir_puntero_reg)
down_register_button.grid(row=0,column=0)
register_selector_frame.place(x=387,y=450)

memory_label = tk.Label(main_window,text="Memoria", background="lightblue")
memory_label.place(x=595,y=70)
memory_frame = tk.Frame(main_window)
for i in range(8):
    label = tk.Label(memory_frame,bg="white", text=f"R{i}",relief=tk.SUNKEN,bd=2,width=20,height=1)
    label.grid(row=8-i,column=0)

memory_frame.place(x=550,y=100)

memory_selector_frame = tk.Frame(main_window)
up_memory_button = tk.Button(memory_selector_frame,text="⇧",command=aumentar_puntero_mem)
up_memory_button.grid(row=0,column=2,)
get_memory_button = tk.Button(memory_selector_frame,text="Get",command=get_memoria)
get_memory_button.grid(row=0,column=1)
down_memory_button = tk.Button(memory_selector_frame,text="⇩",command=disminuir_puntero_mem)
down_memory_button.grid(row=0,column=0)
memory_selector_frame.place(x=587,y=280)

erase_button = tk.Button(main_window,text="Borrar",background="red",fg="white",command=lambda: erase_program(flags))
erase_button.place(x=210 ,y=440)

memory_pointer= Pointer("memoria")
memory_pointer.set_frame(memory_frame)
memory_pointer.update_labels()
register_pointer= Pointer("registro")
register_pointer.set_frame(registers_frame)
register_pointer.update_labels()

main_window.mainloop()