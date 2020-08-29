

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os
import cv2
import sys
from PIL import Image, ImageTk
import numpy
import requests
import json


def change_labelcolor(count, category):
    global label1, label2, label3, label4
    
#     print (f"response is {category} and {type(category)}")
    list_labels = [label1, label2, label3, label4]
    if category['filename'] == "OK":
        list_labels[count].config(bg="green", text = f"{count+1}. is OK")
        
    elif category['filename'] == "NG":
        list_labels[count].config(bg="red", text = f"{count+1}. is NG")


def prompt_ok(event = 0):
    
    global cancel, button, button1, button2
    cancel = True

    button.place_forget()
    button1 = tk.Button(canvas2, text="Process", command=saveAndExit)
    button2 = tk.Button(canvas2, text="Try Again", command=resume)
    button1.place(anchor=tk.CENTER, relx=0.2, rely=0.9, width=150, height=50)
    button2.place(anchor=tk.CENTER, relx=0.8, rely=0.9, width=150, height=50)
    button1.focus()
    
def reset():
    global id_var, label1, label2, label3, label4, count
    list_labels = [label1, label2, label3, label4]
    id_var.set("")
    count = 4
    for i in range(4):
        list_labels[i].config(text=f'{i+1}. Hole', fg='black', bg='white',  font=("Helvetica", 16))


def saveAndExit(event = 0):
    global prevImg, count, id_num
    
    try:
        if (count > 0) and (id_num.get() != ""):
            ### Image reading and fetching data
            prevImg = numpy.array(prevImg, dtype="uint8")
            success, encoded_image = cv2.imencode('.jpg', prevImg)
            url = "http://127.0.0.1:8000/classify/"
            files = {'file':encoded_image.tobytes() }
            response = requests.post(url, files=files)
            messagebox.showinfo("Response",f"The Image is {response.text}")
            
            ###changing the label color
            change_labelcolor(4-count, json.loads(response.text)) ###using 4 - since count is 4 and list index should be 0
            count -= 1
            
        elif id_num.get() == "":
            messagebox.showwarning("Missing Info", "Enter Part Number to continue")
        else:
            messagebox.showwarning("Cant Process more", "You have taken 4 photos for this engine. Click Inpection Now")
    
    except Exception as e:
        messagebox.showinfo("Error",f"unsupported image type {prevImg.dtype} and {e}")
    
    
    #####saving the images
    folder_name = f"../{id_num.get()}_OK_{datetime.today().strftime('%m%d%Y')}"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    prevImg = prevImg.astype(numpy.uint8)
    prevImg = cv2.cvtColor(prevImg, cv2.COLOR_BGR2RGB)
    cv2.imwrite(f"{folder_name}/img_{4-count}.jpg", prevImg)


#####Done
def resume(event = 0):
    global button1, button2, button, lmain, cancel

    cancel = False

    button1.place_forget()
    button2.place_forget()

    mainWindow.bind('<Return>', prompt_ok)
    button.place(bordermode=tk.INSIDE, relx=0.5, rely=0.9, anchor=tk.CENTER, width=300, height=50)
    lmain.after(10, show_frame)
#######DOne
def changeCam(event=0, nextCam=-1):
    global camIndex, cap, fileName

    if nextCam == -1:
        camIndex += 1
    else:
        camIndex = nextCam
    del(cap)
    cap = cv2.VideoCapture(camIndex)

    #try to get a frame, if it returns nothing
    success, frame = cap.read()
    if not success:
        camIndex = 0
        del(cap)
        cap = cv2.VideoCapture(camIndex)

    f = open(fileName, 'w')
    f.write(str(camIndex))
    f.close()               

#####DOne               
def show_frame():
    global cancel, prevImg, button

    _, frame = cap.read()
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    prevImg = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=prevImg)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    if not cancel:
        lmain.after(10, show_frame)
        
def on_closing():
    global cap
    cap.release()
    cv2.destroyAllWindows()
    mainWindow.destroy()


if __name__ == "__main__":
    
    fileName = os.environ['ALLUSERSPROFILE'] + "\WebcamCap.txt"
    cancel = False
    
    try:
        f = open(fileName, 'r')
        camIndex = int(f.readline())
    except:
        camIndex = 0

    cap = cv2.VideoCapture(camIndex)
    capWidth = cap.get(3)
    capHeight = cap.get(4)

    success, frame = cap.read()
    if not success:
        if camIndex == 0:
            print("Error, No webcam found!")
            sys.exit(1)
        else:
            changeCam(nextCam=0)
            success, frame = cap.read()
            if not success:
                print("Error, No webcam found!")
                sys.exit(1)
                
    ####variable
    count = 4
    
    
    ####main window title and inspection
    mainWindow = tk.Tk(screenName="Camera Capture")
    mainWindow.title("Auto Engine Inspection")
    width, height = 900,600
    mainWindow.geometry(f"{width}x{height}")
    mainWindow.resizable(width=True, height=True)
    mainWindow.bind('<Escape>', lambda e: mainWindow.quit()) ##binding operation here
    
    canvas1 = tk.Canvas(mainWindow )
    canvas2 = tk.Canvas(mainWindow )
    canvas3 = tk.Canvas(mainWindow, bg = "white" )
    canvas4 = tk.Canvas(mainWindow )
    canvas5 = tk.Canvas(mainWindow )
    canvas6 = tk.Canvas(mainWindow )
    
    canvas1.grid(row=0, column = 0)
    canvas2.grid(row=0, column = 1)
    canvas3.grid(row=0, column = 2)
    canvas4.grid(row=1, column = 0)
    canvas5.grid(row=1, column = 1)
    canvas6.grid(row=1, column = 2)

    ##############################################################################################Canvas 1  
    
    label = tk.Label(canvas1, text= "Part Number Input",font=("Helvetica", 26),relief=tk.RAISED)
    label.pack()
    id_var = tk.StringVar()
    id_num = tk.Entry(canvas1, textvariable = id_var, font=('calibre',26,'normal'))
    
    ###############################################################################################canvas 2
    lmain = tk.Label(canvas2, compound=tk.CENTER, anchor=tk.CENTER, relief=tk.RAISED)
    button = tk.Button(canvas2, text="Capture", command=prompt_ok)
    button_changeCam = tk.Button(canvas2, text="Switch Camera", command=changeCam)

    lmain.pack()
    id_num.pack( side = tk.LEFT )
    button.place(bordermode=tk.INSIDE, relx=0.5, rely=0.9, anchor=tk.CENTER, width=height//2, height=50)
    button.focus()
    button_changeCam.place(bordermode=tk.INSIDE, relx=0.85, rely=0.1, anchor=tk.CENTER, width=150, height=50)
    
    ##################################################################################################canvas 3
    label1 = tk.Label(canvas3, text='1. Hole', fg='black', bg='white',  font=("Helvetica", 16),relief=tk.RAISED)
    label2 = tk.Label(canvas3, text='2. Hole', fg='black', bg='white', font=("Helvetica", 16),relief=tk.RAISED)
    label3 = tk.Label(canvas3, text='3. Hole', fg='black', bg='white', font=("Helvetica", 16),relief=tk.RAISED)
    label4 = tk.Label(canvas3, text='4. Hole', fg='black', bg='white', font=("Helvetica", 16),relief=tk.RAISED)
    label1.pack(padx=6, pady=6)
    label2.pack(padx=6, pady=6)
    label3.pack(padx=6, pady=6)
    label4.pack(padx=6, pady=6)
    
    #################################################################################################canvas 4
    
    # Put the image into a canvas compatible class, and stick in an
    # arbitrary variable to the garbage collector doesn't destroy it

    ok_label = tk.Label(canvas4, text='OK', fg='black', bg='white',  font=("Helvetica", 16), relief=tk.RAISED)
    img1= Image.open("11;2;20_0048.JPG")
    img1 = img1.resize((200,100))
    img1 = ImageTk.PhotoImage(img1)
    panel = tk.Label(canvas4, image = img1)
    panel.pack(side = "bottom", fill = "both", expand = "yes")

    ok_label.pack()
    
    #################################################################################################canvas 6
    ng_label = tk.Label(canvas6, text='NG', fg='black', bg='white',  font=("Helvetica", 16), relief=tk.RAISED)
    
    img2= Image.open("02,01,20_0128 - Copy.JPG")
    img2 = img2.resize((200,100))
    img2 = ImageTk.PhotoImage(img2)
    panel = tk.Label(canvas6, image = img2)
    panel.pack(side = "bottom", fill = "both", expand = "yes")

    ng_label.pack()
    
    ###################################################################################################canvas 5
    inspection = tk.Button(canvas5, text="Inspection Complete",bg="#32b0d5", command = reset)
    inspection.place(bordermode=tk.INSIDE, relx=0.5, rely=0.2, anchor=tk.CENTER, width=height//2, height=50)
    inspection.focus()
    show_frame()
    

    mainWindow.protocol("WM_DELETE_WINDOW", on_closing)
    mainWindow.mainloop()
