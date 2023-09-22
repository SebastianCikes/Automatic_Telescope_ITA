import requests
import tkinter as tk
from tkinter import *
import serial
import time
import importlib
import ctypes
import serial.tools.list_ports

from Elementi import Gruppi
  

ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

responseMicro = b'Fatto'
altezzaPre = 0
azimuthPre = 0
invio = False
loop_flag = False
stato = False
ser = serial.Serial()

# Funzione per il loop infinito
def loop_function():
    if loop_flag:
        do_prog()
        root.after(100, loop_function)  # Chiamata ricorsiva dopo 100 ms

# Funzione per iniziare il loop
def start_loop():
    global loop_flag
    loop_flag = True
    loop_function()

# Funzione per fermare il loop
def stop_loop():
    global loop_flag
    loop_flag = False



#---------------------------  API  ----------------------------
def do_prog():
    global responseMicro
    global altezzaPre
    global azimuthPre
    global invio
    global stato
    global ser
    
    
    #selected_item_gruppo = dropdown_gruppo.get()
    #selected_item_costellazione = dropdown_costellazione.get()
    selected_item_bodies = dropdown_bodies.get()

    # Richiesta a Stellarium API
    url = f"http://localhost:8090/api/objects/info?name={selected_item_bodies}&format=json"

    if responseMicro == b'Fatto':
        responseMicro = b' '

        try:
            response = requests.get(url)
            # Controllo se la richiesta e andata a buon fine
            if response.status_code == 200:
                stato = True
            else:
                print(f"Errore nella richiesta: Codice {response.status_code}")
                stato = False
            
            if stato == True:
                print(selected_item_bodies)
    
                # Estraggo dati json
                json_data = response.json()
            
                azimuth = round(json_data["azimuth"], 5)
                altezza = round(json_data["altitude"], 5)
                print(str(azimuth) + " " + str(altezza))
            
                labelAzimuth.config(text=f"Azimuth = {azimuth}")
                labelAltezza.config(text=f"Altezza = {altezza}")
            
                if (altezza < 68 and altezza > -5):
                    altezzaPre = altezza
                    azimuthPre = azimuth
                    invio = True
                else:
                    invio = False
                
                if ser.port != None:
                    if invio:
                        a = str(azimuth) + " " + str(altezza) + "\n"
                        ser.write(bytes(a, 'utf-8'))
                    else:
                        responseMicro = b'Fatto'
                else:
                    responseMicro = b'Fatto'
            else:
                responseMicro = b'Fatto'
                    
        except:
            print("API non attivo")

    elif ser.port != None:
        if ser.in_waiting:
            responseMicro = (ser.readline()).strip()
            print(responseMicro)
            time.sleep(1)

def iniz(porta):
    # Imposta i parametri della porta seriale
    ser.port = porta
    ser.baudrate = 9600
    ser.timeout = 1
    ser.open()

    time.sleep(2)

    try:
        response = requests.get(f"http://localhost:8090/api/objects/info?name=Stella polare&format=json")
        json_data = response.json()
        azimuth = round(json_data["azimuth"], 2)
        altezza = round(json_data["altitude"], 2)
        asd = str(azimuth) + " " + str(altezza) + "\n"
        print(asd)
        ser.write(bytes(asd, 'utf-8'))
        inizializzato = b' '
        while inizializzato != b'Fatto':
            if ser.in_waiting:
                inizializzato = (ser.readline()).strip()
                print(inizializzato)
    except :
        print("API non attivo")
        

#---------------------------  GUI  ----------------------------
# Funzione per gestire la selezione nel dropdown dei gruppi
def on_select_gruppo(event):
    selection = dropdown_list_gruppo.curselection()
    if selection:
        selected_item_gruppo = dropdown_list_gruppo.get(selection)
        dropdown_gruppo.set(selected_item_gruppo)
    # Chiamare la funzione dd_bodies() con il nome del costellazione selezionato
        dd_costellazioni(selected_item_gruppo)
# Funzione per aggiornare il dropdown dei corpi celesti in base alla costellazione selezionata
def dd_costellazioni(nome_modulo):
    try:
        nome_modulo = 'Elementi.' + nome_modulo
        modulo = importlib.import_module(nome_modulo)
        # Cancella elementi precedenti dal Listbox
        dropdown_list_costellazione.delete(0, tk.END)
        # Aggiungi elementi al Listbox
        for item in modulo.bodies:
            dropdown_list_costellazione.insert(tk.END, item)
    except ImportError:
        pass

# Funzione per gestire la selezione nel dropdown delle costellazioni
def on_select_costellazione(event):
    selection = dropdown_list_costellazione.curselection()
    if selection:
        selected_item_costellazione = dropdown_list_costellazione.get(selection)
        dropdown_costellazione.set(selected_item_costellazione)
    
        # Chiamare la funzione dd_bodies() con il nome del costellazione selezionato
        dd_bodies(selected_item_costellazione)
# Funzione per aggiornare il dropdown dei corpi celesti in base alla costellazione selezionata
def dd_bodies(nome_modulo):
    try:
        nome_modulo = 'Elementi.' + nome_modulo
        modulo = importlib.import_module(nome_modulo)
        # Cancella elementi precedenti dal Listbox
        dropdown_list_bodies.delete(0, tk.END)
        # Aggiungi elementi al Listbox
        for item in modulo.bodies:
            dropdown_list_bodies.insert(tk.END, item)
    except ImportError:
        pass


# Funzione per gestire la selezione nel dropdown dei corpi celesti
def on_select_bodies(event):
    selectionB = dropdown_list_bodies.curselection()
    if selectionB:
        selected_item = dropdown_list_bodies.get(selectionB[0])  # Prendi il primo elemento selezionato
        dropdown_bodies.set(selected_item)

# Crea una finestra
root = tk.Tk()
root.title("Telescopio automatico")
root.geometry("300x650")

# Variabile per memorizzare la selezione del dropdown
dropdown_gruppo = tk.StringVar(root)         # Gruppo (Costellazione, Galassia, ecc)
dropdown_costellazione = tk.StringVar(root)  # costellazione (Orione, Bilancia, Drago, ecc)
dropdown_bodies = tk.StringVar(root)         # Oggetto (Luna, Giove, Vega, ecc)

dropdown_serial_ports = tk.StringVar(root)


# Crea una scrollbar per il dropdown dei gruppi
scrollbar_gruppo = tk.Scrollbar(root)
scrollbar_gruppo.pack(side=tk.RIGHT, fill=tk.Y)
# Crea un Listbox collegato alla scrollbar per il dropdown dei gruppi
dropdown_list_gruppo = tk.Listbox(root, yscrollcommand=scrollbar_gruppo.set)
dropdown_list_gruppo.pack(fill=tk.BOTH)
# Associa la scrollbar al Listbox per il dropdown dei gruppi
scrollbar_gruppo.config(command=dropdown_list_gruppo.yview)
# Aggiungi elementi al Listbox per il dropdown dei gruppi
for item in Gruppi.bodies:
    dropdown_list_gruppo.insert(tk.END, item)
# Imposta una variabile di controllo per memorizzare la selezione
dropdown_gruppo = tk.StringVar()
# Collega la funzione di gestione della selezione all'evento di selezione per il dropdown dei gruppi
dropdown_list_gruppo.bind('<<ListboxSelect>>', on_select_gruppo)


# Crea una scrollbar per il dropdown delle costellazioni
scrollbar_costellazione = tk.Scrollbar(root)
scrollbar_costellazione.pack(side=tk.RIGHT, fill=tk.Y)
# Crea un Listbox collegato alla scrollbar per il dropdown delle costellazioni
dropdown_list_costellazione = tk.Listbox(root, yscrollcommand=scrollbar_costellazione.set)
dropdown_list_costellazione.pack(fill=tk.BOTH)
# Associa la scrollbar al Listbox per il dropdown delle costellazioni
scrollbar_costellazione.config(command=dropdown_list_costellazione.yview)
# Imposta una variabile di controllo per memorizzare la selezione
dropdown_costellazione = tk.StringVar()
# Collega la funzione di gestione della selezione all'evento di selezione per il dropdown delle costellazioni
dropdown_list_costellazione.bind('<<ListboxSelect>>', on_select_costellazione)


# Crea una scrollbar per il dropdown dei corpi celesti
scrollbar_bodies = tk.Scrollbar(root)
scrollbar_bodies.pack(side=tk.RIGHT, fill=tk.Y)
# Crea un Listbox collegato alla scrollbar per il dropdown dei corpi celesti
dropdown_list_bodies = tk.Listbox(root, yscrollcommand=scrollbar_bodies.set)
dropdown_list_bodies.pack(fill=tk.BOTH)
# Associa la scrollbar al Listbox per il dropdown dei corpi celesti
scrollbar_bodies.config(command=dropdown_list_bodies.yview)
# Imposta una variabile di controllo per memorizzare la selezione
dropdown_bodies = tk.StringVar()
# Collega la funzione di gestione della selezione all'evento di selezione per il dropdown dei corpi celesti
dropdown_list_bodies.bind('<<ListboxSelect>>', on_select_bodies)

# Function to get a list of available serial ports
def get_available_serial_ports():
    available_ports = serial.tools.list_ports.comports()
    return [port.device for port in available_ports]

# Function to handle the selection in the serial port dropdown
def on_select_serial_port(*args):
    selected_port = dropdown_serial_ports.get()
    iniz(selected_port)
    
# Create a StringVar to store the selected serial port
dropdown_serial_ports = tk.StringVar(root)
dropdown_serial_ports.set("Select a serial port")  # Set a default value
# Get a list of available serial ports
available_ports = get_available_serial_ports()
try:
    # Create the serial port dropdown menu
    serial_dropdown = tk.OptionMenu(root, dropdown_serial_ports, *available_ports)
    serial_dropdown.pack()
except:
    pass
# Bind the selection handling function to the serial port dropdown
dropdown_serial_ports.trace('w', on_select_serial_port)

# Aggiungi un pulsante per avviare il loop
show_button = tk.Button(root, text="Invia", command=start_loop)
show_button.pack()

# Aggiungi un pulsante per fermare il telescopio
stop_button = tk.Button(root, text="Stop", command=stop_loop)
stop_button.pack()

# Creazione label per l'altezza
labelAltezza = tk.Label(root, text="")
labelAltezza.pack()

# Creazione label per l'azimuth
labelAzimuth = tk.Label(root, text="")
labelAzimuth.pack()

root.mainloop()
