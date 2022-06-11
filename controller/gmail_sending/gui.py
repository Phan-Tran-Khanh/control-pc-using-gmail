from tkinter import *
from tkinter import messagebox
from gmail import Gmail

def temp_text1(e):
    global entry1
    entry1.configure(font=("Times New Roman", "20"), fg="Black")
    entry1.delete(0,"end")

def temp_text2(e):
    global entry2
    entry2.configure(font=("Times New Roman", "20"), fg="Black")
    entry2.delete(0,"end")

def temp_text3(e):
    global entry3
    entry3.configure(font=("Times New Roman", "20"), fg="Black")
    entry3.delete(0,"end")

def temp_text4(e):
    global entry4
    entry4.configure(font=("Times New Roman", "20"), fg="Black")
    entry4.delete(0,"end")

def cre_btn():
    global stt
    if stt == 0: cre_btn_shutdown(f"data/white_button/img0.png")

    if stt == 1: cre_btn_restart(f"data/white_button/img1.png")

    if stt == 2: cre_btn_filecopying(f"data/white_button/img2.png")

    if stt == 3: cre_btn_killprocess(f"data/white_button/img3.png")

    if stt == 4: cre_btn_fullcapture(f"data/white_button/img4.png")

    if stt == 5: cre_btn_camcapture(f"data/white_button/img5.png")

    if stt == 6: cre_btn_listprocess(f"data/white_button/img6.png")

    if stt == 7: cre_btn_editvalue(f"data/white_button/img7.png")

    if stt == 8: cre_btn_dect(f"data/white_button/img8.png")    

    if stt == 9: cre_btn_camrecord(f"data/white_button/img9.png")

def cre_box(sl):
    global string1
    global string2
    global string3
    global string4
    string1 = StringVar()
    string2 = StringVar()
    string3 = StringVar()
    string4 = StringVar()
    global cnt_cre_box
    cnt_cre_box = sl
    global luu
    global entry1
    global entry2
    global entry3
    global entry4
    if sl >= 1:
        entry1_img = PhotoImage(file = f"data/b_t/img_textBox0.png")
        luu.append(entry1_img)
        entry1_bg = canvas.create_image(
            801.0, 78.5,
            image = entry1_img)

        entry1 = Entry(
            bd = 0,
            bg = "#ffffff",
            highlightthickness = 0, font=("Times New Roman", "20"), textvariable=string1)

        entry1.place(
            x = 552.0, y = 53,
            width = 498.0,

            height = 50)
    if sl >= 2:
        entry2_img = PhotoImage(file = f"data/b_t/img_textBox0.png")
        luu.append(entry2_img)
        entry2_bg = canvas.create_image(
            801.0, 172.5,
            image = entry2_img)

        entry2 = Entry(
            bd = 0,
            bg = "#ffffff",
            highlightthickness = 0, font=("Times New Roman", "20"), textvariable=string2)

        entry2.place(
            x = 552.0, y = 145,
            width = 498.0,
            height = 50)
    if sl >= 3:
        entry3_img = PhotoImage(file = f"data/b_t/img_textBox0.png")
        luu.append(entry3_img)
        entry3_bg = canvas.create_image(
            801.0, 266.5,
            image = entry3_img)

        entry3 = Entry(
            bd = 0,
            bg = "#ffffff",
            highlightthickness = 0, font=("Times New Roman", "20"), textvariable=string3)

        entry3.place(
            x = 552.0, y = 240,
            width = 498.0,
            height = 50)
    if sl >= 4:
        entry4_img = PhotoImage(file = f"data/b_t/img_textBox0.png")
        luu.append(entry4_img)
        entry4_bg = canvas.create_image(
            801.0, 360.5,
            image = entry4_img)

        entry4 = Entry(
            bd = 0,
            bg = "#ffffff",
            highlightthickness = 0, font=("Times New Roman", "20"), textvariable=string4)

        entry4.place(
            x = 552.0, y = 333,
            width = 498.0,
            height = 50)

def send_e():
    global string1
    global string2
    global string3
    global string4
    global cnt_cre_send
    text1 = ""
    text2 = ""
    text3 = ""
    text4 = ""
    if cnt_cre_send >= 1: text1 = string1.get()
    if cnt_cre_send >= 2: text2 = string2.get()
    if cnt_cre_send >= 3: text3 = string3.get()
    if cnt_cre_send >= 4: text4 = string4.get()
    global txt_query
    global gmaill
    
    gmaill.setUpClass()
    gmaill.setUpRecipient(text1)
    if txt_query == "shutdown": gmaill.send_shutdown(text2)
    if txt_query == "restart": gmaill.send_restart(text2)
    if txt_query == "filecopying": gmaill.send_copy_file(text2, text3)
    if txt_query == "killprocess": gmaill.send_kill_process(text2)
    if txt_query == "fullcapture": gmaill.send_capture_screen()
    if txt_query == "camcapture": gmaill.send_capture_webcam()
    if txt_query == "listprocess": gmaill.send_list_processes()
    if txt_query == "editvalue": gmaill.send_registry_key(regis_path=text2,value=text3, value_type=text4)
    if txt_query == "dect": gmaill.send_keypress(text2)
    if txt_query == "camrecord": gmaill.send_record_webcam(text2)
    messagebox.showinfo("", "Your message has been delivered")

def cre_send(sl):
    global cnt_cre_send
    global b10
    if cnt_cre_send != 0: b10.destroy()
    cnt_cre_send = sl
    global luu
    img10 = PhotoImage(file = f"data/b_t/img10.png")
    luu.append(img10)
    b10 = Button(
        image = img10,
        borderwidth = 0,
        highlightthickness = 0,
        command = send_e,
        relief = "flat")
    if sl == 1:
        b10.place(
            x = 858, y = 159,
            width = 202,
            height = 80)
    if sl == 2:
        b10.place(
            x = 858, y = 262,
            width = 202,
            height = 80)
    if sl == 3:
        b10.place(
            x = 858, y = 351,
            width = 202,
            height = 80)
    if sl == 4:
        b10.place(
            x = 858, y = 437,
            width = 202,
            height = 80)


def shutdown_clicked():
    global txt_query
    txt_query = "shutdown"
    global canvas
    global stt
    global temp_btn
    global entry1
    global entry2
    global entry3
    global entry4
    global cnt_cre_box
    canvas.delete("all")
    temp_btn.destroy()
    cre_btn()
    cre_btn_shutdown(f"data/yl_button/img0.png")
    background_img1 = PhotoImage(file = f"data/background/bg_3/background.png")
    global luu
    luu.append(background_img1)
    background = canvas.create_image(
    550.0, 300.0,
    image=background_img1)
    if cnt_cre_box >= 1: entry1.destroy()
    if cnt_cre_box >= 2: entry2.destroy()
    if cnt_cre_box >= 3: entry3.destroy()
    if cnt_cre_box >= 4: entry4.destroy()
    cre_box(2)
    cre_send(2)
    entry1.configure(font=('Georgia 16'), fg="Gray")
    entry1.insert(1, "Enter email address")
    entry1.bind("<FocusIn>", temp_text1)
    entry2.configure(font=('Georgia 16'), fg="Gray")
    entry2.insert(1, "Enter time shut down the computer")
    entry2.bind("<FocusIn>", temp_text2)


def cre_btn_shutdown(Link):
    img0 = PhotoImage(file = Link)
    global luu
    luu.append(img0)
    b0 = Button(
        image = img0,
        borderwidth = 0,
        highlightthickness = 0,
        command = shutdown_clicked,
        relief = "flat")

    b0.place(
        x = 24, y = 12,
        width = 281,
        height = 44)
    global temp_btn
    global stt
    temp_btn = b0
    stt = 0

def restart_clicked():
    global txt_query
    txt_query = "restart"
    global canvas
    global stt
    global temp_btn
    global entry1
    global entry2
    global entry3
    global entry4
    canvas.delete("all")
    temp_btn.destroy()
    cre_btn()
    cre_btn_restart(f"data/yl_button/img1.png")
    background_img1 = PhotoImage(file = f"data/background/bg_4/background.png")
    global luu
    luu.append(background_img1)
    background = canvas.create_image(
    550.0, 300.0,
    image=background_img1)
    if cnt_cre_box >= 1: entry1.destroy()
    if cnt_cre_box >= 2: entry2.destroy()
    if cnt_cre_box >= 3: entry3.destroy()
    if cnt_cre_box >= 4: entry4.destroy()
    cre_box(2)
    cre_send(2)
    entry1.configure(font=('Georgia 16'), fg="Gray")
    entry1.insert(1, "Enter email address")
    entry1.bind("<FocusIn>", temp_text1)
    entry2.configure(font=('Georgia 16'), fg="Gray")
    entry2.insert(1, "Enter time restart the computer")
    entry2.bind("<FocusIn>", temp_text2)

def cre_btn_restart(Link):
    img1 = PhotoImage(file = Link)
    global luu
    luu.append(img1)
    b1 = Button(
        image = img1,
        borderwidth = 0,
        highlightthickness = 0,
        command = restart_clicked,
        relief = "flat")

    b1.place(
        x = 24, y = 67,
        width = 281,
        height = 44)

    global temp_btn
    global stt
    temp_btn = b1
    stt = 1

def filecopying_clicked():
    global txt_query
    txt_query = "filecopying"
    global canvas
    global stt
    global temp_btn
    global entry1
    global entry2
    global entry3
    global entry4
    global cnt_cre_box
    canvas.delete("all")
    temp_btn.destroy()
    cre_btn()
    cre_btn_filecopying(f"data/yl_button/img2.png")
    background_img1 = PhotoImage(file = f"data/background/bg_5/background.png")
    global luu
    luu.append(background_img1)
    background = canvas.create_image(
    550.0, 300.0,
    image=background_img1)
    if cnt_cre_box >= 1: entry1.destroy()
    if cnt_cre_box >= 2: entry2.destroy()
    if cnt_cre_box >= 3: entry3.destroy()
    if cnt_cre_box >= 4: entry4.destroy()
    cre_box(3)
    cre_send(3)
    entry1.configure(font=('Georgia 16'), fg="Gray")
    entry1.insert(1, "Enter email address")
    entry1.bind("<FocusIn>", temp_text1)
    entry2.configure(font=('Georgia 16'), fg="Gray")
    entry2.insert(1, "Enter your old file path")
    entry2.bind("<FocusIn>", temp_text2)
    entry3.configure(font=('Georgia 16'), fg="Gray")
    entry3.insert(1, "Enter your new file path")
    entry3.bind("<FocusIn>", temp_text3)

def cre_btn_filecopying(Link):
    img2 = PhotoImage(file = Link)
    global luu
    luu.append(img2)
    b2 = Button(
        image = img2,
        borderwidth = 0,
        highlightthickness = 0,
        command = filecopying_clicked,
        relief = "flat")

    b2.place(
        x = 22, y = 122,
        width = 281,
        height = 44)

    global temp_btn
    global stt
    temp_btn = b2
    stt = 2

def killprocess_clicked():
    global txt_query
    txt_query = "killprocess"
    global canvas
    global stt
    global temp_btn
    global entry1
    global entry2
    global entry3
    global entry4
    global cnt_cre_box
    canvas.delete("all")
    temp_btn.destroy()
    cre_btn()
    cre_btn_killprocess(f"data/yl_button/img3.png")
    background_img1 = PhotoImage(file = f"data/background/bg_9/background.png")
    global luu
    luu.append(background_img1)
    background = canvas.create_image(
    550.0, 300.0,
    image=background_img1)
    if cnt_cre_box >= 1: entry1.destroy()
    if cnt_cre_box >= 2: entry2.destroy()
    if cnt_cre_box >= 3: entry3.destroy()
    if cnt_cre_box >= 4: entry4.destroy()
    cre_box(2)
    cre_send(2)
    entry1.configure(font=('Georgia 16'), fg="Gray")
    entry1.insert(1, "Enter email address")
    entry1.bind("<FocusIn>", temp_text1)
    entry2.configure(font=('Georgia 16'), fg="Gray")
    entry2.insert(1, "Enter process indentifier (PID)")
    entry2.bind("<FocusIn>", temp_text2)

def cre_btn_killprocess(Link):
    img3 = PhotoImage(file = Link)
    global luu
    luu.append(img3)
    b3 = Button(
        image = img3,
        borderwidth = 0,
        highlightthickness = 0,
        command = killprocess_clicked,
        relief = "flat")

    b3.place(
        x = 22, y = 397,
        width = 281,
        height = 44)

    global temp_btn
    global stt
    temp_btn = b3
    stt = 3

def fullcapture_clicked():
    global txt_query
    txt_query = "fullcapture"
    global canvas
    global stt
    global temp_btn
    global entry1
    global entry2
    global entry3
    global entry4
    global cnt_cre_box
    canvas.delete("all")
    temp_btn.destroy()
    cre_btn()
    cre_btn_fullcapture(f"data/yl_button/img4.png")
    background_img1 = PhotoImage(file = f"data/background/bg_6/background.png")
    global luu
    luu.append(background_img1)
    background = canvas.create_image(
    550.0, 300.0,
    image=background_img1)
    if cnt_cre_box >= 1: entry1.destroy()
    if cnt_cre_box >= 2: entry2.destroy()
    if cnt_cre_box >= 3: entry3.destroy()
    if cnt_cre_box >= 4: entry4.destroy()
    cre_box(1)
    cre_send(1)
    entry1.configure(font=('Georgia 16'), fg="Gray")
    entry1.insert(1, "Enter email address")
    entry1.bind("<FocusIn>", temp_text1)

def cre_btn_fullcapture(Link):
    img4 = PhotoImage(file = Link)
    global luu
    luu.append(img4)
    b4 = Button(
        image = img4,
        borderwidth = 0,
        highlightthickness = 0,
        command = fullcapture_clicked,
        relief = "flat")

    b4.place(
        x = 22, y = 177,
        width = 281,
        height = 44)

    global temp_btn
    global stt
    temp_btn = b4
    stt = 4

def camcapture_clicked():
    global txt_query
    txt_query = "camcapture"
    global canvas
    global stt
    global temp_btn
    global entry1
    global entry2
    global entry3
    global entry4
    global cnt_cre_box
    canvas.delete("all")
    temp_btn.destroy()
    cre_btn()
    cre_btn_camcapture(f"data/yl_button/img5.png")
    background_img1 = PhotoImage(file = f"data/background/bg_6/background.png")
    global luu
    luu.append(background_img1)
    background = canvas.create_image(
    550.0, 300.0,
    image=background_img1)
    if cnt_cre_box >= 1: entry1.destroy()
    if cnt_cre_box >= 2: entry2.destroy()
    if cnt_cre_box >= 3: entry3.destroy()
    if cnt_cre_box >= 4: entry4.destroy()
    cre_box(1)
    cre_send(1)
    entry1.configure(font=('Georgia 16'), fg="Gray")
    entry1.insert(1, "Enter email address")
    entry1.bind("<FocusIn>", temp_text1)

def cre_btn_camcapture(Link):
    img5 = PhotoImage(file = Link)
    global luu
    luu.append(img5)
    b5 = Button(
        image = img5,
        borderwidth = 0,
        highlightthickness = 0,
        command = camcapture_clicked,
        relief = "flat")

    b5.place(
        x = 24, y = 232,
        width = 281,
        height = 44)

    global temp_btn
    global stt
    temp_btn = b5
    stt = 5

def listprocess_clicked():
    global txt_query
    txt_query = "listprocess"
    global canvas
    global stt
    global temp_btn
    global entry1
    global entry2
    global entry3
    global entry4
    global cnt_cre_box
    canvas.delete("all")
    temp_btn.destroy()
    cre_btn()
    cre_btn_listprocess(f"data/yl_button/img6.png")
    background_img1 = PhotoImage(file = f"data/background/bg_6/background.png")
    global luu
    luu.append(background_img1)
    background = canvas.create_image(
    550.0, 300.0,
    image=background_img1)
    if cnt_cre_box >= 1: entry1.destroy()
    if cnt_cre_box >= 2: entry2.destroy()
    if cnt_cre_box >= 3: entry3.destroy()
    if cnt_cre_box >= 4: entry4.destroy()
    cre_box(1)
    cre_send(1)
    entry1.configure(font=('Georgia 16'), fg="Gray")
    entry1.insert(1, "Enter email address")
    entry1.bind("<FocusIn>", temp_text1)

def cre_btn_listprocess(Link):
    img6 = PhotoImage(file = Link)
    global luu
    luu.append(img6)
    b6 = Button(
        image = img6,
        borderwidth = 0,
        highlightthickness = 0,
        command = listprocess_clicked,
        relief = "flat")

    b6.place(
        x = 22, y = 342,
        width = 281,
        height = 44)

    global temp_btn
    global stt
    temp_btn = b6
    stt = 6

def editvalue_clicked():
    global txt_query
    txt_query = "editvalue"
    global canvas
    global stt
    global temp_btn
    global entry1
    global entry2
    global entry3
    global entry4
    global cnt_cre_box
    canvas.delete("all")
    temp_btn.destroy()
    cre_btn()
    cre_btn_editvalue(f"data/yl_button/img7.png")
    background_img1 = PhotoImage(file = f"data/background/bg_11/background.png")
    global luu
    luu.append(background_img1)
    background = canvas.create_image(
    550.0, 300.0,
    image=background_img1)
    if cnt_cre_box >= 1: entry1.destroy()
    if cnt_cre_box >= 2: entry2.destroy()
    if cnt_cre_box >= 3: entry3.destroy()
    if cnt_cre_box >= 4: entry4.destroy()
    cre_box(4)
    cre_send(4)
    entry1.configure(font=('Georgia 16'), fg="Gray")
    entry1.insert(1, "Enter email address")
    entry1.bind("<FocusIn>", temp_text1)
    entry2.configure(font=('Georgia 16'), fg="Gray")
    entry2.insert(1, "Enter registry key's path")
    entry2.bind("<FocusIn>", temp_text2)
    entry3.configure(font=('Georgia 16'), fg="Gray")
    entry3.insert(1, "Enter registry key's new value")
    entry3.bind("<FocusIn>", temp_text3)
    entry4.configure(font=('Georgia 16'), fg="Gray")
    entry4.insert(1, "Enter the type of new value")
    entry4.bind("<FocusIn>", temp_text4)

def cre_btn_editvalue(Link):
    img7 = PhotoImage(file = Link)
    global luu
    luu.append(img7)
    b7 = Button(
        image = img7,
        borderwidth = 0,
        highlightthickness = 0,
        command = editvalue_clicked,
        relief = "flat")

    b7.place(
        x = 24, y = 507,
        width = 281,
        height = 56)

    global temp_btn
    global stt
    temp_btn = b7
    stt = 7

def dect_clicked():
    global txt_query
    txt_query = "dect"
    global canvas
    global stt
    global temp_btn
    global entry1
    global entry2
    global entry3
    global entry4
    global cnt_cre_box
    canvas.delete("all")
    temp_btn.destroy()
    cre_btn()
    cre_btn_dect(f"data/yl_button/img8.png")
    background_img1 = PhotoImage(file = f"data/background/bg_10/background.png")
    global luu
    luu.append(background_img1)
    background = canvas.create_image(
    550.0, 300.0,
    image=background_img1)
    if cnt_cre_box >= 1: entry1.destroy()
    if cnt_cre_box >= 2: entry2.destroy()
    if cnt_cre_box >= 3: entry3.destroy()
    if cnt_cre_box >= 4: entry4.destroy()
    cre_box(2)
    cre_send(2)
    entry1.configure(font=('Georgia 16'), fg="Gray")
    entry1.insert(1, "Enter email address")
    entry1.bind("<FocusIn>", temp_text1)
    entry2.configure(font=('Georgia 16'), fg="Gray")
    entry2.insert(1, "Enter number of seconds when detecting")
    entry2.bind("<FocusIn>", temp_text2)

def cre_btn_dect(Link):
    img8 = PhotoImage(file = Link)
    global luu
    luu.append(img8)
    b8 = Button(
        image = img8,
        borderwidth = 0,
        highlightthickness = 0,
        command = dect_clicked,
        relief = "flat")

    b8.place(
        x = 24, y = 452,
        width = 281,
        height = 44)

    global temp_btn
    global stt
    temp_btn = b8
    stt = 8

def camrecord_clicked():
    global txt_query
    txt_query = "camrecord"
    global canvas
    global stt
    global temp_btn
    global entry1
    global entry2
    global entry3
    global entry4
    global cnt_cre_box
    canvas.delete("all")
    temp_btn.destroy()
    cre_btn()
    cre_btn_camrecord(f"data/yl_button/img9.png")
    background_img1 = PhotoImage(file = f"data/background/bg_10/background.png")
    global luu
    luu.append(background_img1)
    background = canvas.create_image(
    550.0, 300.0,
    image=background_img1)
    if cnt_cre_box >= 1: entry1.destroy()
    if cnt_cre_box >= 2: entry2.destroy()
    if cnt_cre_box >= 3: entry3.destroy()
    if cnt_cre_box >= 4: entry4.destroy()
    cre_box(2)
    cre_send(2)
    entry1.configure(font=('Georgia 16'), fg="Gray")
    entry1.insert(1, "Enter email address")
    entry1.bind("<FocusIn>", temp_text1)
    entry2.configure(font=('Georgia 16'), fg="Gray")
    entry2.insert(1, "Enter number of seconds to record")
    entry2.bind("<FocusIn>", temp_text2)

def cre_btn_camrecord(Link):
    img9 = PhotoImage(file = Link)
    global luu
    luu.append(img9)
    b9 = Button(
        image = img9,
        borderwidth = 0,
        highlightthickness = 0,
        command = camrecord_clicked,
        relief = "flat")

    b9.place(
        x = 24, y = 287,
        width = 281,
        height = 44)

    global temp_btn
    global stt
    temp_btn = b9
    stt = 9

def main_ui():

    global stt
    global temp_btn
    global canvas
    global luu
    global cnt_cre_box
    global cnt_cre_send
    global b10

    canvas.delete("all")
    
    cnt_cre_send = 0
    cnt_cre_box = 0
    stt = -1
    temp_btn = None
    luu = []

    canvas = Canvas(
    window,
    bg = "#ffffff",
    height = 600,
    width = 1100,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge")
    canvas.place(x = 0, y = 0)

    background_img = PhotoImage(file = f"data/background/bg_2/background.png")
    luu.append(background_img)
    background = canvas.create_image(
    550.0, 300.0,
    image=background_img)

    cre_btn_shutdown(f"data/white_button/img0.png")

    cre_btn_restart(f"data/white_button/img1.png")

    cre_btn_filecopying(f"data/white_button/img2.png")

    cre_btn_killprocess(f"data/white_button/img3.png")

    cre_btn_fullcapture(f"data/white_button/img4.png")

    cre_btn_camcapture(f"data/white_button/img5.png")

    cre_btn_listprocess(f"data/white_button/img6.png")

    cre_btn_editvalue(f"data/white_button/img7.png")

    cre_btn_dect(f"data/white_button/img8.png")    

    cre_btn_camrecord(f"data/white_button/img9.png")    

def sign_in():
    global gmaill
    gmaill = Gmail()
    gmaill.setUpClass()
    messagebox.showinfo("", "You have logged in successfully!")
    main_ui()

def Start():
    global window
    global string1
    global string2
    global string3
    global string4
    global txt_query
    txt_query = ""
    window = Tk()
    window.geometry("1100x600+150+50")
    window.title("Remote")
    window.configure(bg = "#ffffff")
    global canvas
    canvas = Canvas(
        window,
        bg = "#ffffff",
        height = 600,
        width = 1100,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge")
    canvas.place(x = 0, y = 0)

    background_img = PhotoImage(file = f"data/background/bg_1/background.png")
    background = canvas.create_image(
        797.5, 350.5,
        image=background_img)

    img0 = PhotoImage(file = f"data/b_t/signin.png")
    b0 = Button(
        image = img0,
        borderwidth = 0,
        highlightthickness = 0,
        command = sign_in,
        relief = "flat")

    b0.place(
        x = 357, y = 466,
        width = 420,
        height = 100)

    window.resizable(False, False)
    window.mainloop()


Start()
