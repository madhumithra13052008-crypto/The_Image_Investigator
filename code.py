# IMPORTING THE NECESSARY LIBRARIES
import cv2
from tkinter import *
from tkinter import font
from tkinter import filedialog
from PIL import Image,ImageTk
import os
from datetime import datetime

#CREATING AN CONTAINER TO STROE THE IMAGE AND ITS PATH
image=None
imagepath=""

#CREATING THE VARIABLES TO STORE THE CO-ORDINATES
# VARIABLES FOR MOUSE CROP
start_x = 0
start_y = 0
end_x = 0
end_y = 0
drawing = False

# VARIABLES FOR CIRCLE
circle_center = ()
circle_radius = 0
drawing_circle = False

# VARIABLES FOR RECTANGLE
rect_start = ()
rect_end = ()
drawing_rectangle = False

# VARIABLES FOR ARROW
arrow_start = ()
arrow_end = ()
drawing_arrow = False

# FOR UNDO AND REDO
undo_stack = []
redo_stack = []

# SETTING THE WINDOW
window = Tk()
window.title("THE IMAGE INVESTIGATOR")
window.config(bg="#EAEAEA")
window.geometry("800x600")
window.resizable(width=False, height=False)

# SETTING THE FONT
title_font = font.Font(family="Times", size=25, weight="bold")
text_font = font.Font(family="Arial", size=15)


def display_image():
        rgb_image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

        #CONVERTING AN NUMPY ARRAY TO AN IMAGE
        pil_image=Image.fromarray(rgb_image)
        pil_image.thumbnail((400,300))

        #CONVERTING AN IMAGE INTO AN TKINTER IMAGE
        tk_image=ImageTk.PhotoImage(pil_image)

        #MAKING THE IMAGE TO BE OPEN IN PREVIEW SECTION
        Evidence_preview.config(image=tk_image)

        #TO MAKE IT AVAILABLE AT ALL CASES
        Evidence_preview.image=tk_image

#CREATING AN FUNCTION FOR UNDO
def undo_function(event=None):
    global image

    if len(undo_stack) == 0:
        label_statusbar.config(text="Status : Nothing to Undo ❌")
        return

    redo_stack.append(image.copy())

    image = undo_stack.pop()

    display_image()

    label_statusbar.config(text="Status : Undo Successful ↩")

#CREATING AN FUNCTION FOR REDO
def redo_function(event=None):
    global image

    if len(redo_stack) == 0:
        label_statusbar.config(text="Status : Nothing to Redo ❌")
        return

    undo_stack.append(image.copy())

    image = redo_stack.pop()

    display_image()

    label_statusbar.config(text="Status : Redo Successful ↪")

#INITIALIZING THE COLLECTING BUTTON
def collect_evidence():
    global image,imagepath
    imagepath=filedialog.askopenfilename(title="open the report")

    if imagepath == "":
        label_statusbar.config(text="Status : Failed to Load Image ❌")
        return
    
    image=cv2.imread(imagepath)

    label_statusbar.config(text="Status : Evidence Collected ✔")

    #FETCHING ONLY THE FILE NAME:
    filename=os.path.basename(imagepath)
    current=datetime.now()
    date = current.strftime("%d-%b-%Y")
    time = current.strftime("%I:%M %p")
  
    display_image()

    #CONFIGURATION OF THE CASE PREVIEW
    case_preview.config(text=f"------------CASE PREVIEW------------ \n\n 📂 EVIDENCE : {filename} \n\n 🟢 STATUS : Evidence Collected \n\n 📅 DATE : {date} \n\n 🕒 TIME : {time} \n\n 🔍ANALYSIS : Waiting......",justify=LEFT)

# CREATING FUNCTION FOR THE ARCHIVE BUTTON
def archive_evidence():
    global image

    if image is None:
        label_statusbar.config(text="Status : No Evidence to Archive ❌")
        return

    save_path = filedialog.asksaveasfilename(
        title="Save Evidence",
        defaultextension=".png",
        filetypes=[
            ("PNG Image", "*.png"),
            ("JPEG Image", "*.jpg"),
            ("All Files", "*.*")
        ]
    )

    if save_path == "":
        label_statusbar.config(text="Status : Archive Cancelled")
        return

    # Save the image
    cv2.imwrite(save_path, image)

    label_statusbar.config(text="Status : Evidence Archived Successfully 💾")

#CREATING AN FUNCTION FOR THE ANALYSIS BUTTON
def analyze_evidence():
    global image

    if image is None:
        label_statusbar.config(text="Status : No Evidence to Analyze ❌")
        return

    heigth,width,channel=image.shape

    total_pixel=heigth*width

    if channel==3:
        color="BGR"
    else:
        color="GrayScale"

    gray_scale=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    brightness=gray_scale.mean()

    if brightness<80:
        bright="Dark"
    elif brightness>180:
        bright="Light"
    else:
        bright="Normal"
  
    case_preview.config(text=f"----------ANALYSIS REPORT----------- \n\n 🖼️ Image Size : {width} × {heigth} \n\n 🎨 Color Mode : {color} \n\n 📊 Total Pixels : {total_pixel} \n\n 💡Brightness : {bright} \n\n ✅ Status : Analysis Completed ✔",justify=LEFT)

    label_statusbar.config(text="Status : Evidence Analyzed Successfully 💾")
    
#CREATING FUNCTION FOR THE ROTATE BUTTON
def rotate_function():
    global image 

    if image is None:
        label_statusbar.config(text="Status : No Evidence to Rotate ❌")
        return

    undo_stack.append(image.copy())
    redo_stack.clear()
    
    image=cv2.rotate(image,cv2.ROTATE_90_CLOCKWISE)
    display_image()

    label_statusbar.config(text="Status : Image Rotated 90° ✔")

#CREATING FUNCTION FOR THE CROP MOUSE EVENTS
def crop_mouse(event, x, y, flags, param):
    global start_x, start_y, end_x, end_y
    global drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_x = x
        start_y = y

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        temp = image.copy()

        cv2.rectangle(temp, (start_x, start_y), (x, y), (0,255,0), 2)

        cv2.imshow("Crop Image", temp)

    elif event == cv2.EVENT_LBUTTONUP:

        drawing = False

        end_x = x
        end_y = y

        cv2.destroyWindow("Crop Image")

# CREATING FUNCTION FOR THE CROP BUTTON
def crop_function():

    global image
    global start_x, start_y, end_x, end_y

    if image is None:
        label_statusbar.config(text="Status : No Evidence to Crop ❌")
        return

    cv2.imshow("Crop Image", image)

    cv2.setMouseCallback("Crop Image", crop_mouse)

    cv2.waitKey(0)

    x1 = min(start_x, end_x)
    x2 = max(start_x, end_x)

    y1 = min(start_y, end_y)
    y2 = max(start_y, end_y)

    undo_stack.append(image.copy())
    redo_stack.clear()

    image = image[y1:y2, x1:x2]

    display_image()

    label_statusbar.config(text="Status : Image Cropped Successfully ✔")

#CREATING AN FUNCTION FOR THE FLIP BUTTON
def flip_function():
    global image

    if image is None:
        label_statusbar.config(text="Status : No Evidence to Flip ❌")
        return 

    undo_stack.append(image.copy())
    redo_stack.clear()
    
    image=cv2.flip(image,0)
    display_image()

    label_statusbar.config(text="Status : Image Fliped Vertically ✔")

#CREATING AN MOUSE CALLBACK FUNCTION FOR THE CIRCLE
def circle_mouse(event, x, y, flags, param):
    global image
    global circle_center, circle_radius
    global drawing_circle

    if event == cv2.EVENT_LBUTTONDOWN:

        drawing_circle = True
        circle_center = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE and drawing_circle:

        temp = image.copy()

        radius = int(((x - circle_center[0])**2 + (y - circle_center[1])**2)**0.5)

        cv2.circle(temp, circle_center, radius, (0,255,0), 3)

        cv2.imshow("Circle Annotation", temp)

    elif event == cv2.EVENT_LBUTTONUP:

        drawing_circle = False

        circle_radius = int(((x - circle_center[0])**2 + (y - circle_center[1])**2)**0.5)

        cv2.circle(image, circle_center, circle_radius, (0,255,0), 3)

        cv2.imshow("Circle Annotation", image)

# CREATING FUNCTION FOR THE CIRCLE BUTTON
def circle_function():
    global image

    if image is None:
        label_statusbar.config(text="Status : No Evidence to Annotate ❌")
        return

    undo_stack.append(image.copy())
    redo_stack.clear()

    cv2.imshow("Circle Annotation", image)

    cv2.setMouseCallback("Circle Annotation", circle_mouse)

    cv2.waitKey(0)

    cv2.destroyWindow("Circle Annotation")

    display_image()

    label_statusbar.config(text="Status : Circle Annotation Added ⭕")
#CREATING THE MOUSE CALLBACK FUNCTION FOR THE RECTANGLE
def rectangle_mouse(event, x, y, flags, param):
    global image
    global rect_start, rect_end
    global drawing_rectangle

    if event == cv2.EVENT_LBUTTONDOWN:

        drawing_rectangle = True
        rect_start = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE and drawing_rectangle:

        temp = image.copy()

        cv2.rectangle(temp, rect_start, (x, y), (0, 255, 0), 3)

        cv2.imshow("Rectangle Annotation", temp)

    elif event == cv2.EVENT_LBUTTONUP:

        drawing_rectangle = False

        rect_end = (x, y)

        cv2.rectangle(image, rect_start, rect_end, (0, 255, 0), 3)

        cv2.imshow("Rectangle Annotation", image)

# CREATING FUNCTION FOR THE RECTANGLE BUTTON
def rectangle_function():
    global image

    if image is None:
        label_statusbar.config(text="Status : No Evidence to Annotate ❌")
        return

    undo_stack.append(image.copy())
    redo_stack.clear()

    cv2.imshow("Rectangle Annotation", image)

    cv2.setMouseCallback("Rectangle Annotation", rectangle_mouse)

    cv2.waitKey(0)

    cv2.destroyWindow("Rectangle Annotation")

    display_image()

    label_statusbar.config(text="Status : Rectangle Annotation Added ⬜")

#CREATING MOUSE CALLBACK FUNCTION FOR THE ARROW
def arrow_mouse(event, x, y, flags, param):
    global image
    global arrow_start, arrow_end
    global drawing_arrow

    if event == cv2.EVENT_LBUTTONDOWN:

        drawing_arrow = True
        arrow_start = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE and drawing_arrow:

        temp = image.copy()

        cv2.arrowedLine(temp, arrow_start, (x, y), (0, 255, 0), 3)

        cv2.imshow("Arrow Annotation", temp)

    elif event == cv2.EVENT_LBUTTONUP:

        drawing_arrow = False

        arrow_end = (x, y)

        cv2.arrowedLine(image, arrow_start, arrow_end, (0, 255, 0), 3)

        cv2.imshow("Arrow Annotation", image)

# CREATING FUNCTION FOR THE ARROW BUTTON
def arrow_function():
    global image

    if image is None:
        label_statusbar.config(text="Status : No Evidence to Annotate ❌")
        return

    undo_stack.append(image.copy())
    redo_stack.clear()

    cv2.imshow("Arrow Annotation", image)

    cv2.setMouseCallback("Arrow Annotation", arrow_mouse)

    cv2.waitKey(0)

    cv2.destroyWindow("Arrow Annotation")

    display_image()

    label_statusbar.config(text="Status : Arrow Annotation Added ➡")
    
# TITLE FRAME
frame_title = Frame(window, bg="#0B1F3A")
frame_title.pack(fill=X)

# TITLE
title = Label(
    frame_title,
    text="🕵 IMAGE INVESTIGATOR",
    bg="#0B1F3A",
    fg="white",
    font=title_font,
    pady=10,
    padx=10
)
title.pack()

# SUBTITLE
sub_title = Label(
    frame_title,
    text="Every picture hides a clue...",
    bg="#0B1F3A",
    fg="lightgray",
    font=text_font,
    pady=5,
    padx=10
)
sub_title.pack()

#BUTTON FRAME
frame_button=Frame(window,background="gray")
frame_button.pack(fill=X,ipadx=5,ipady=5)

#CREATING THE BUTTON
button_open=Button(frame_button,text="📂 Collect",bg="skyblue",fg="red",activebackground="green",activeforeground="white",width=20,padx=10,pady=10,font=text_font,relief="raised",command=collect_evidence)
button_open.grid(row=0,column=0,padx=10,pady=10)
button_analyze=Button(frame_button,text="🔍 Analyze",bg="skyblue",fg="red",activebackground="green",activeforeground="white",width=20,padx=10,pady=10,font=text_font,relief="raised",command=analyze_evidence)
button_analyze.grid(row=0,column=2,padx=10,pady=10)
button_archive=Button(frame_button,text="💾 Archive",bg="skyblue",fg="red",activebackground="green",activeforeground="white",width=20,padx=10,pady=10,font=text_font,relief="raised",command=archive_evidence)
button_archive.grid(row=0,column=4,padx=10,pady=10)

#PREVIEW FRAME
frame_evidence=Frame(window,background="#0B1F3A")
frame_evidence.pack(fill=X)

#PREVIEW AND REPORT LABEL
# ---------- IMAGE PREVIEW ----------
preview_frame = Frame(
    frame_evidence,
    width=400,
    height=230,
    bg="black",
    bd=2,
    relief="groove"
)
preview_frame.grid(row=0, column=0, padx=5, pady=5)

# Keep the frame size fixed
preview_frame.grid_propagate(False)

Evidence_preview = Label(
    preview_frame,
    bg="black"
)

Evidence_preview.place(relx=0.5, rely=0.5, anchor="center")
case_preview = Label(frame_evidence,text="------------CASE PREVIEW------------ \n\n 📂 EVIDENCE : {filename} \n\n 🟢 STATUS : Evidence Collected \n\n 📅 DATE : {date} \n\n 🕒 TIME : {time} \n\n 🔍 ANALYSIS : Waiting......",justify="center",width=62,height=15,relief="groove",bd=2,bg="#0B1F3A",fg="white")
case_preview.grid(row=0,column=1)

#FRAME FOR MANIPULATION
frame_manipulation=Frame(window,background="skyblue")
frame_manipulation.pack(fill=X)

#SETTING THE MANIPULATION BUTTONS
crop_button=Button(frame_manipulation,text="✂ CROP",width=20,bg="gray",fg="yellow",activebackground="green",activeforeground="white",padx=10,pady=10,relief="sunken",command=crop_function)
crop_button.grid(row=0,column=0,padx=50,pady=10)

rotate_button=Button(frame_manipulation,text="🔄 ROTATE",width=20,bg="gray",fg="yellow",activebackground="green",activeforeground="white",padx=10,pady=10,relief="sunken",command=rotate_function)
rotate_button.grid(row=0,column=1,padx=50,pady=10)

flip_button=Button(frame_manipulation,text="🔁 FLIP",width=20,bg="gray",fg="yellow",activebackground="green",activeforeground="white",padx=10,pady=10,relief="sunken",command=flip_function)
flip_button.grid(row=0,column=2,padx=50,pady=10)

#FRAME FOR ANNOTATION
frame_annotation=Frame(window,background="skyblue");
frame_annotation.pack(fill=X)

#SETTING THE ANNOTATAION BUTTONS
circle_button=Button(frame_annotation,text="⭕ CIRCLE",width=20,bg="gray",fg="yellow",activebackground="green",activeforeground="white",padx=10,pady=10,relief="sunken",command=circle_function)
circle_button.grid(row=0,column=0,padx=50,pady=10)

rectangle_button=Button(frame_annotation,text="⬜ RECTANGLE",width=20,bg="gray",fg="yellow",activebackground="green",activeforeground="white",padx=10,pady=10,relief="sunken",command=rectangle_function)
rectangle_button.grid(row=0,column=1,padx=50,pady=10)

arrow_button=Button(frame_annotation,text="➡ ARROW",width=20,bg="gray",fg="yellow",activebackground="green",activeforeground="white",padx=10,pady=10,relief="sunken",command=arrow_function)
arrow_button.grid(row=0,column=2,padx=50,pady=10)

#FRAME FOR STATUS BAR
frame_status_bar=Frame(window,background="#0B1F3A")
frame_status_bar.pack(fill=BOTH)

#SETTING THE LABEL OF STATUS BAR
label_statusbar=Label(frame_status_bar,text="Status : Waiting for Evidence...",padx=10,pady=10,bg="#0B1F3A",fg="lightgreen",font=text_font)
label_statusbar.grid(row=0,column=0,columnspan=3)

#CREATING THE BIND FOR UNDO AND REDO FUNCTION
window.bind("u", undo_function)
window.bind("U", undo_function)

window.bind("r", redo_function)
window.bind("R", redo_function)

#RUNNING THE WINDOW
window.mainloop()
