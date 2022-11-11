from tkinter import *
from tkinter.scrolledtext import ScrolledText
import json
import socket
from datetime import datetime
from threading import Thread

HOST = "localhost"  # hier die IP vom Server
PORT = 8081


class Window:
    def __init__(self):
        self.root = Tk()
        self.root.geometry("1000x500")
        self.root.title("Chat")
        self.name_input = ''
        self.login_frame = Frame(self.root)  # Frame erstellen
        self.login_label = Label(self.login_frame, text="Login",
                                 font=("Arial", 30))  # Label, Entry und Button für Login erstellen
        self.username_label = Label(self.login_frame, text="Choose your name", font=("Arial", 16))
        self.username_entry = Entry(self.login_frame, font=("Arial", 14), justify=CENTER)
        self.SignIn_button = Button(self.login_frame, text="Sign in", font=("Arial", 16), command=self.main_window)
        self.right_frame = Frame(self.root)  # Frame für Chatfeld erstellen
        self.left_frame = Frame(self.root)  # Frame Links erstellen
        self.send_frame = Frame(self.right_frame)  # Frame für Senden erstellen
        self.text_area = ScrolledText(self.right_frame, font=("Arial", 10), width=60, height=20)  # Chatfeld erstellen
        self.login_window()
        self.text_area.tag_configure('joined', foreground='green', underline=True, font=('Arial', 10, 'italic'))
        self.text_area.tag_configure('whisper', foreground='purple')
        self.text_area.tag_configure('normal', foreground='black')
        self.text_area.tag_configure('error', foreground='red', underline=True)
        # name_input = self.choose_username()
        self.list_box_frame = LabelFrame(self.left_frame,
                                         text='Participant in chatroom')
        self.list_box_scrollbar = Scrollbar(self.list_box_frame)
        self.list_box = Listbox(self.list_box_frame, yscrollcommand=self.list_box_scrollbar.set,
                                height=10)  # Teilnehmerliste Fenster erstellen
        self.text_input = StringVar()
        self.text_input_entry = Entry(self.send_frame, width=80, textvariable=self.text_input)  # Text-Input erstellen
        self.send_button = Button(self.send_frame, text="SEND", width=10)  # Senden Button erstellen
        self.send_button.bind('<Button>', func=self.post)  # mit Button klicken zum Senden

    def login_window(self):
        self.username_entry.bind('<KeyPress-Return>', func=self.main_window)
        self.login_label.pack(pady=20)  # Label, Entry und Button für Login aufstellen
        self.username_label.pack(pady=10)
        self.username_entry.pack(pady=10)
        self.SignIn_button.pack(pady=10)
        self.login_frame.place(rely=0.5, relx=0.5, anchor=CENTER)  # Frame platzieren

    def post(self, *args):  # Funktion für Text-Input in Chatfeld ein
        # hier wollen wir dann user_input(my_text) aufrufen
        self.client.user_input(self.text_input_entry.get())
        self.text_input.set("")  # Leerzeichen für Entry

    def main_window(self, *args):
        self.name_input = my_Window.username_entry.get()  # Name von entry speichern
        self.client = Client(self.name_input, self)
        self.login_frame.place_forget()  # Frame von Login Fenster
        self.text_area.pack(anchor=E, fill=X)
        self.text_input_entry.pack(side=LEFT, fill=X)
        self.text_input_entry.bind('<KeyPress-Return>', func=self.post)  # mit Enter drücken zum Senden
        self.send_button.pack(side=LEFT)
        self.right_frame.pack(side=RIGHT, anchor=SE, padx=20, pady=20)  # Frame für Chatfeld platzieren
        self.send_frame.pack(fill=X)  # Frame für Senden platzieren

        def change_name():  # Funktion für Name ändern
            new_root = Tk()  # neuer Fenster erstellen
            new_root.geometry('200x100')
            new_root.title('Change name')
            new_root.focus_set()
            new_frame = Frame(new_root)  # Frame erstellen
            label = Label(new_frame, text='Change name')
            label.pack(side=TOP, anchor=N)
            entry = Entry(new_frame)
            entry.pack(side=TOP, anchor=CENTER, padx=10, pady=10)

            def save_name():  # Funktion für Name speichern
                self.name_input = entry.get()
                new_root.destroy()  # Mini-Fenster entfernen

            ok_button = Button(new_frame, text='Ok', width=7, command=save_name)  # Button für Ok
            ok_button.pack(side=LEFT)
            root_exit = new_root.destroy  # Mini-Fenster für Cancel Button entfernen
            cancel_button = Button(new_frame, text='Cancel', width=7, command=root_exit)  # Button für Cancel
            cancel_button.pack(side=RIGHT)
            new_frame.pack()  # Frame platzieren
            new_root.mainloop()

        menu = Menu(self.root)  # Menu erstellen
        settings_menu = Menu(menu, tearoff=0)
        color_menu = Menu(settings_menu, tearoff=0)
        menu.add_cascade(label='Settings', menu=settings_menu)  # Menu für Setting aufstellen
        settings_menu.add_cascade(label='Change name', command=change_name)  # Erweiterung für Setting --> Change name
        settings_menu.add_cascade(label='Change color', menu=color_menu)  # Erweiterung für Setting --> Change color
        color_menu.add_radiobutton(label='red')  # neues Menu in change color
        color_menu.add_radiobutton(label='green')
        color_menu.add_radiobutton(label='blue')
        color_menu.add_radiobutton(label='yellow')
        menu.add_command(label='Logout', command=self.logout)  # Menu für Logout aufstellen
        self.root.config(menu=menu)
        self.user_list()

    def logout(self):
        self.back_login_window()
        self.client.leave()

    def print_message(self, message, tag='normal'):
        self.text_area.configure(state='normal')  # Chatfeld Bearbeiten aktivieren
        self.text_area.insert(INSERT, f"{message} \n", tag)  # Text in Chatfeld einfügen
        self.text_area.configure(state='disabled')  # Chatfeld Bearbeiten deaktivieren

    def back_login_window(self):  # Funktion für Logout
        self.login_frame.place_forget()  # Frame leeren
        self.right_frame.pack_forget()
        self.send_frame.pack_forget()
        self.left_frame.pack_forget()
        self.login_window()  # Login Window zurückkehren
        self.text_input_entry.pack_forget()
        self.send_button.pack_forget()

    def user_list(self):  # Funktion für Teilnehmerliste
        self.list_box.pack(side=LEFT)
        self.list_box_scrollbar.config(command=self.list_box.yview)  # Funktion für Scrollbar
        self.list_box_scrollbar.pack(side=LEFT, fill=Y)
        self.list_box_frame.pack()
        self.left_frame.pack(side=LEFT, padx=20, pady=20)  # Frame platzieren

    def update_user_list(self):
        self.list_box.delete(0, END)
        for i in range(len(self.client.user_list)):
            self.list_box.insert(i, self.client.user_list[i])  # Benutzer addieren


class Client:

    def __init__(self, name, window):
        self.window = window
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))
        self.new_client(name)
        self.receive_thread = Thread(target=self.receive, args=())
        self.receive_thread.start()
        self.name_input = name
        self.user_list = []

    def normal_message(self, msg):
        header = json.dumps(
            {'datetime': str(datetime.now().strftime('%d.%m.%y %H:%M')),
             'name': self.name_input, 'length': len(msg)})
        header_length_raw = int.to_bytes(len(header), 2, 'big')
        self.send_message(b's', header_length_raw, bytes(header, 'utf-8'), bytes(msg, 'utf-8'))

    def new_client(self, name):
        self.send_message(b'n', int.to_bytes(len(name), 2, 'big'), bytes(name, 'utf-8'))

    def get_user_list(self, length):
        # convert into string and split at seperator
        return str(self.s.recv(length), 'utf-8').split(', ')

    def leave(self):
        self.s.sendall(b'l')
        self.receive_thread.join()

    def client_left(self):
        msg_length_raw = self.s.recv(2)
        msg_length = int.from_bytes(msg_length_raw, 'big')
        name_raw = self.s.recv(msg_length)
        name = str(name_raw, 'utf-8')
        # Der Client soll auch eine User-Liste haben, wo er den Namen den er hier bekommt dann rauslöscht

    def whisper(self, msg):
        parts = msg.split(' ')
        receiver = parts[0]
        msg = ' '.join(parts[1:])
        print(f'{receiver!r}: {msg}')
        header = json.dumps(
            {'datetime': str(datetime.now().strftime('%d.%m.%y %H:%M')),
             'receiver': receiver, 'name': self.name_input, 'length': len(msg)})
        header_raw = bytes(header, 'utf-8')
        header_length = int.to_bytes(len(header_raw), 2, 'big')
        msg_raw = bytes(msg, 'utf-8')
        self.send_message(b'w', header_length, header_raw, msg_raw)

    def config_name(self, new_name):
        name_length = int.to_bytes(len(new_name), 2, 'big')
        name_raw = bytes(new_name, 'utf-8')
        self.send_message(b'c', name_length, name_raw)

    def send_message(self, *args):
        for msg_part in args:
            self.s.sendall(msg_part)

    def receive(self):
        while True:
            try:
                message_type = str(self.s.recv(1), 'utf-8')
                length = int.from_bytes(self.s.recv(2), 'big')
                print(message_type)
                match message_type:
                    # Hier alles mit print_message() ändern
                    case 's':
                        header = json.loads(str(self.s.recv(length), 'utf-8'))
                        message = str(self.s.recv(header['length']), 'utf-8')
                        self.window.print_message(f"[{header['datetime']}] {header['name']}: {message}")
                    case 'w':
                        header = json.loads(str(self.s.recv(length), 'utf-8'))
                        message = str(self.s.recv(header['length']), 'utf-8')
                        self.window.print_message(f"[{header['datetime']}] {header['name']} "
                                                  f"whispered {header['receiver']}: {message}", 'whisper')
                    case 'n':
                        name = str(self.s.recv(length), 'utf-8')
                        self.user_list.append(name)
                        self.window.update_user_list()
                        self.window.print_message(f"{name} joined the room", 'joined')
                    case 'l':
                        name = str(self.s.recv(length), 'utf-8')
                        self.user_list.remove(name)
                        self.window.update_user_list()
                        self.window.print_message(f"{name} left the room", 'error')
                    case 'e':
                        error_text = str(self.s.recv(length), 'utf-8')
                        self.window.print_message(error_text, 'error')
                    case 'u':
                        self.user_list = self.get_user_list(length)
                        self.window.update_user_list()
                        # self.window.print_message(self.user_list)
                    case _:
                        break
            except ConnectionError:
                break

    def user_input(self, message_input):
        if message_input[:3] == '/w ':
            self.whisper(message_input[3:].strip())
        elif message_input[:3] == '/s ':
            self.normal_message(message_input[3:].strip())
        elif message_input[:7] in ['/logoff', '/l']:
            self.leave()
            self.window.back_login_window()
        else:
            self.normal_message(message_input)


if __name__ == '__main__':
    my_Window = Window()
    my_Window.root.mainloop()
