import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
import PIL
from PIL import Image
from tkinter import filedialog as fd
import socket
import threading
import base64

window = tk.Tk()
window.title("Client")
username = " "

# Top frame consisting of the "Connect" button and the text box to put your username into
topFrame = tk.Frame(window)
lblName = tk.Label(topFrame, text="Name:").pack(side=tk.LEFT)
entName = tk.Entry(topFrame)
entName.pack(side=tk.LEFT)
btnConnect = tk.Button(topFrame, text="Connect", command=lambda: connect())
btnConnect.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP)

# Display frame consisting of the divider between the Top frame and this frame, the scroll bar. and the display for chat messages
displayFrame = tk.Frame(window)
lblLine = tk.Label(displayFrame,
                   text="============================================").pack()
scrollBar = tk.Scrollbar(displayFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(displayFrame, height=20, width=55)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
tkDisplay.tag_config("tag_your_message", foreground="blue")
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set,
                 background="#F4F6F7",
                 highlightbackground="grey",
                 state="disabled")
displayFrame.pack(side=tk.TOP)

# Bottom frame consisting only of the text box to type messages in
bottomFrame = tk.Frame(window)
tkMessage = tk.Text(bottomFrame, height=2, width=60)
tkMessage.pack(side=tk.LEFT, padx=(5, 13), pady=(5, 10))
# TO BE DONE: Image support
#tkImage = tk.Button(
  #bottomFrame,
  #text="Image",
  #command=lambda: send_img_to_server(tkMessage.get("1.0", tk.END)))
#tkImage.pack(side=tk.RIGHT, padx=(0, 13), pady=(5, 10))
#
tkMessage.config(highlightbackground="grey", state="disabled")
tkMessage.bind(
  "<Return>",
  (lambda event: send_mssage_to_server(tkMessage.get("1.0", tk.END))))
bottomFrame.pack(side=tk.BOTTOM)


def connect():
  global username, client
  if len(entName.get()) < 1:
    tk.messagebox.showerror(
      title="ERROR!!!", message="You MUST enter your first name <e.g. John>")
  else:
    username = entName.get()
    connect_to_server(username)


client = None
HOST_ADDR = "0.0.0.0"
HOST_PORT = 8080


def connect_to_server(name):
  global client, HOST_PORT, HOST_ADDR
  try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST_ADDR, HOST_PORT))
    client.send(name.encode())  # Send name to server after connecting

    entName.config(state=tk.DISABLED)
    btnConnect.config(state=tk.DISABLED)
    tkMessage.config(state=tk.NORMAL)

    threading._start_new_thread(receive_message_from_server, (client, "m"))
  except Exception as e:
    tk.messagebox.showerror(title="ERROR!!!",
                            message="Cannot connect to host: " + HOST_ADDR +
                            " on port: " + str(HOST_PORT) +
                            " Server may be Unavailable. Try again later")


def receive_message_from_server(sck, m):
  while True:
    from_server = sck.recv(4096).decode()
    if (str(sck).startswith("data:image/png;base64,")
        or str(sck).startswith("data:image/jpg;base64,")
        or str(sck).startswith("data:image/jpeg;base64,") or
        str(sck).startswith("data:image/gif;base64,")) and (" "
                                                            not in str(sck)):
      imgmsg = sck[sck.index(",") + 1:]
      from_server = tk.PhotoImage(data=imgmsg)

    if not from_server: break

    # display message from server on the chat window

    texts = tkDisplay.get("1.0", tk.END).strip()
    tkDisplay.config(state=tk.NORMAL)
    if len(texts) < 1:
      tkDisplay.insert(tk.END, from_server)
    else:
      tkDisplay.insert(tk.END, "\n\n" + from_server)

    tkDisplay.config(state=tk.DISABLED)
    tkDisplay.see(tk.END)

  sck.close()
  window.destroy()


def getChatMessage(msg):
  if (str(msg).startswith("data:image/png;base64,")
      or str(msg).startswith("data:image/jpg;base64,")
      or str(msg).startswith("data:image/jpeg;base64,") or
      str(msg).startswith("data:image/gif;base64,")) and (" " not in str(msg)):
    imgmsg = msg[msg.index(",") + 1:]
    msg = tk.PhotoImage(data=imgmsg)
  texts = tkDisplay.get("1.0", tk.END).strip()

  tkDisplay.config(state=tk.NORMAL)
  if len(texts) < 1:
    tkDisplay.insert(tk.END, "You->" + msg, "tag_your_message")
  else:
    tkDisplay.insert(tk.END, "\n\n" + "You->" + msg, "tag_your_message")

  tkDisplay.config(state=tk.DISABLED)

  tkDisplay.see(tk.END)
  tkMessage.delete('1.0', tk.END)


def send_mssage_to_server(msg):
  msg = msg.replace('\n', '')
  client_msg = str(msg)
  if len(msg) == 0:
    tk.messagebox.showerror(title="ERROR!!!", message="Please enter a message")
  client.send(client_msg.encode())
  getChatMessage(msg)
  if msg == "text.red":
    tkDisplay.tag_config("tag_your_message", foreground="red")
  elif msg == "text.blue":
    tkDisplay.tag_config("tag_your_message", foreground="blue")
  elif msg == "text.green":
    tkDisplay.tag_config("tag_your_message", foreground="green")
  elif msg == "text.black":
    tkDisplay.tag_config("tag_your_message", foreground="black")
  elif msg == "text.purple":
    tkDisplay.tag_config("tag_your_message", foreground="purple")
  elif msg == "text.yellow":
    tkDisplay.tag_config("tag_your_message", foreground="yellow")
  elif msg == "text.orange":
    tkDisplay.tag_config("tag_your_message", foreground="orange")
  elif msg == "text.white":
    tkDisplay.tag_config("tag_your_message", foreground="white")
  elif msg == "text.gray":
    tkDisplay.tag_config("tag_your_message", foreground="gray")
  if msg == "exit":
    client.close()
    window.destroy()
  print("Sending message")


def send_img_to_server(img):
  file = fd.askopenfilename()
  with open(file, "rb") as f:
    b64_image = base64.b64encode(f.read())
    ext = "data:image/" + file.split(".")[-1] + ";base64," + str(b64_image)
    getChatMessage(ext)
    client.send(ext.encode())


window.mainloop()
