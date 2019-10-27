from threading import Thread
from tkinter import Tk, StringVar, Label, Frame, Entry, Button, Scrollbar, Text, END, LabelFrame, IntVar
from tkinter.messagebox import showerror
from api import API
from execptions import InvalidLogin, InvalidURL, InvalidServerState
from time import sleep

api = None
destroy = False


def login_close():
    if not api:
        login_w.destroy()
        exit()


def main_close():
    global destroy
    destroy = True
    main_w.destroy()


def login():
    if url.get() and username.get() and password.get():
        try:
            global api
            api = API(url.get(), username.get(), password.get())
        except InvalidLogin:
            showerror("Login error", "Login invalid !")
        except InvalidURL:
            showerror("URL error", "Invalid URL !")
        except ConnectionError:
            showerror("Connexion error", "Connexion error !")
        else:
            login_w.destroy()


def start():
    try:
        api.start()
    except InvalidServerState:
        showerror("Invalid state", "The server is online !")


def stop():
    try:
        api.stop()
    except InvalidServerState:
        showerror("Invalid state", 'The server is offline !')


def restart():
    try:
        api.stop()
        while api.status():
            sleep(1)
        sleep(2)
        api.start()
    except InvalidServerState:
        showerror("Invalid state", "The server is offline !")


def kill():
    try:
        api.kill()
    except InvalidServerState:
        showerror("Invalid state", "The server is online !")


def thread_loop():
    while not destroy:
        try:
            state = api.status()
            msg = api.logs()
        except InvalidServerState:
            online.set("Offline")
            toggle_b.configure(text="Start", command=start)
            reboot_b.configure(state="disable")
            kill_b.configure(state="disable")
            players.set(0)
            latency.set(0)
            field.configure(state="disable")
            send.configure(state="disable")
            logs_text.delete("1.0", END)
            sleep(4)
        else:
            if state:
                toggle_b.configure(text="Stop", command=stop)
                reboot_b.configure(state="normal")
                kill_b.configure(state="normal")
                online.set("Online")
                players.set(state[0])
                latency.set(state[1])
                field.configure(state="normal")
                send.configure(state="normal")
            else:
                online.set("Idle...")
            update_logs(msg)
        sleep(1)


def update_logs(msg: str):
    # msg = msg.split("\n")
    # content = logs.get("1.0", END).split("\n")
    # msg = "\n".join(msg[len(content):])
    if not destroy:
        logs_text.configure(state="normal")
        logs_text.replace("1.0", END, msg)
        logs_text.configure(state="disable")
        logs_text.yview(END)


def command_send(event=None):
    try:
        api.cmd(cmd.get())
    except InvalidServerState:
        showerror("Server error", "Command not send, can't connect to the server !")
    cmd.set("")


login_w = Tk()
login_w.title("Minecraft Server Login")
login_w.resizable(0, 0)
login_w.protocol("WM_DELETE_WINDOW", login_close)
username = StringVar()
password = StringVar()
url = StringVar()
username.set("admin")
password.set("admin")
url.set("http://127.0.0.1:5000")
Label(login_w, text="Url:").pack()
login_hp = Frame(login_w)
login_hp.pack()
Entry(login_hp, textvariable=url, width=28).grid(row=0, column=0)
Label(login_w, text="Username & password:").pack()
login_up = Frame(login_w)
login_up.pack()
Entry(login_up, textvariable=username, width=14).grid(row=0, column=0)
Entry(login_up, textvariable=password, show="*", width=14).grid(row=0, column=1)
Button(login_w, text="Submit", command=login).pack()
login_w.mainloop()


main_w = Tk()
main_w.title("Minecraft Server")
main_w.resizable(0, 0)
main_w.protocol("WM_DELETE_WINDOW", main_close)

sid_bar = Frame(main_w)
sid_bar.grid(row=0, column=0)
status = LabelFrame(sid_bar, text="Status")
status.pack()
Label(status, text="State:").grid(row=0, column=0)
online = StringVar()
online.set("N/A")
Label(status, textvariable=online).grid(row=0, column=1)
Label(status, text="Players:").grid(row=1, column=0)
players = IntVar()
players.set(0)
Label(status, textvariable=players).grid(row=1, column=1)
Label(status, text="Latency:").grid(row=2, column=0)
latency = IntVar()
latency.set(0)
Label(status, textvariable=latency).grid(row=2, column=1)
actions = LabelFrame(sid_bar, text="Actions")
actions.pack()
toggle_b = Button(actions, text="Start", command=start)
toggle_b.pack()
reboot_b = Button(actions, text="Reboot", command=restart)
reboot_b.pack()
kill_b = Button(actions, text="Kill", command=kill)
kill_b.pack()

console = LabelFrame(main_w, text="Console")
console.grid(row=0, column=1)
logs = Frame(console)
logs.pack()
scrollbar = Scrollbar(logs)
scrollbar.pack(side="right", fill="y")
logs_text = Text(logs, height=30, width=100, yscrollcommand=scrollbar.set, state="disable")
logs_text.pack(side="left", fill="both")
command = Frame(console)
command.pack()
cmd = StringVar()
field = Entry(command, textvariable=cmd, width=80)
field.bind("<Return>", command_send)
field.grid(row=0, column=0)
send = Button(command, text="Send", command=command_send)
send.grid(row=0, column=1)

thread = Thread(target=thread_loop)
thread.start()
main_w.mainloop()

