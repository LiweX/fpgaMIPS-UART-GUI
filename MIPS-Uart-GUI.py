import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import serial
import os

main_window = tk.Tk()
main_window.geometry('665x490') #resolution de la window
main_window.title("MIPS UART GUI")
main_window.config(background="lightblue")

class Flags: #objeto flags para usar como flags valga la redundancia
    habemus_file:bool   #para saber si ya esta cargado el programa
    ready_to_send:bool  #para saber si esta todo listo para enviar
    connected:bool  #para saber si conectado el puerto serie
    ser:serial  #objeto serial para conveniencia, poq? no hay poq

flags = Flags()
flags.habemus_file=False
flags.ready_to_send=False
flags.connected=False
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
    
    def update_labels(self): #con eso se cazan los labels de los registros para cuando estan resaltados o deben de dejar de resaltarse
        self.label=self.frame.winfo_children()[self.value-1]
        self.prev_label=self.frame.winfo_children()[self.prev_val-1]
        self.update_grid()

    def update_grid(self): #se pinta de blanco el registro apuntado anterior y se pinta el nuevo de amarillo
        self.prev_label.config(bg="white")
        self.label.config(bg="yellow")
        
    def aumentar(self): # aumentar el puntero
        if (self.value < Pointer.MAX):
            self.prev_val=self.value
            self.value+=1
            self.update_labels()
        else:
            print("Puntero de %s al maximo" % (self.pointer_type))

    def disminuir(self): # disminuir el puntero
        if (self.value > Pointer.MIN):
            self.prev_val=self.value
            self.value-=1
            self.update_labels()
        else:
            print("Puntero de %s al minimo" % (self.pointer_type))
    

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

def connect(flags): #se llama al apretar el boton conectar
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

def convert(flags): #se llama al apretar convertir
    if not flags.habemus_file:
        messagebox.showinfo("Error", "Debe seleccionar un archivo")
        return
    os.system("python -W ignore asm-to-bin.py" + " " + browse_entry.get() + " " +"output.hex")
    flags.ready_to_send=True

def send(flags):    #se llama al apretar enviar
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

def run():
    print("Apretaste Run")

def step():
    print("Apretaste Step")  

def get_PC():
    print("Pediste el valor del PC")

def get_memoria():
    print("Pediste el valor de memoria apuntado") 

def get_registro():
    print("Pediste el valor de registro apuntado")

def aumentar_puntero_reg():
    register_pointer.aumentar()
    print("Apuntando a R%d" % (register_pointer.get_value()))

def aumentar_puntero_mem():
    memory_pointer.aumentar()
    print("Apuntando a R%d" % (memory_pointer.get_value()))

def disminuir_puntero_reg():
    register_pointer.disminuir()
    print("Apuntando a R%d" % (register_pointer.get_value()))

def disminuir_puntero_mem():
    memory_pointer.disminuir()
    print("Apuntando a R%d" % (memory_pointer.get_value()))

    
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
registers_label.place(x=355,y=70)
registers_frame = tk.Frame(main_window)
for i in range(32):
    label = tk.Label(registers_frame,bg="white", text=f"R{i}",relief=tk.SUNKEN,bd=2,width=10,height=1)
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
register_selector_frame.place(x=350,y=450)

memory_label = tk.Label(main_window,text="Memoria", background="lightblue")
memory_label.place(x=545,y=70)
memory_frame = tk.Frame(main_window)
for i in range(32):
    label = tk.Label(memory_frame,bg="white", text=f"R{i}",relief=tk.SUNKEN,bd=2,width=10,height=1)
    if i % 2 == 0:
        label.grid(row=32-i,column=0)
    else:
        label.grid(row=32-i+1,column=1)
memory_frame.place(x=500,y=100)

memory_selector_frame = tk.Frame(main_window)
up_memory_button = tk.Button(memory_selector_frame,text="⇧",command=aumentar_puntero_mem)
up_memory_button.grid(row=0,column=2,)
get_memory_button = tk.Button(memory_selector_frame,text="Get",command=get_memoria)
get_memory_button.grid(row=0,column=1)
down_memory_button = tk.Button(memory_selector_frame,text="⇩",command=disminuir_puntero_mem)
down_memory_button.grid(row=0,column=0)
memory_selector_frame.place(x=540,y=450)

memory_pointer= Pointer("memoria")
memory_pointer.set_frame(memory_frame)
memory_pointer.update_labels()
register_pointer= Pointer("registro")
register_pointer.set_frame(registers_frame)
register_pointer.update_labels()


main_window.mainloop()

