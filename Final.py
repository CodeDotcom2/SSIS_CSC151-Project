from tkinter import *
from tkinter import ttk,font,messagebox
import os,csv,re
from tkinter import messagebox

def populate_form(student_data):
    id_no.delete(0, END)
    id_no.insert(0, student_data[0])

    last_name.delete(0, END)
    last_name.insert(0, student_data[1])

    first_name.delete(0, END)
    first_name.insert(0, student_data[2])

    gender_dropdown.set(student_data[3])
    year_dropdown.set(student_data[4])
    college_dropdown.set(student_data[5])

    program_info.delete(0, END)
    program_info.insert(0, student_data[6])

def find_student_in_csv(student_id):

    try:
        with open("students.csv", mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0] == student_id:
                    return row 
    except FileNotFoundError:
        messagebox.showerror("Error", "CSV file not found.")
    return None

def capitalize_program_name(program_name):
    words = program_name.split()
    return " ".join([word.capitalize() if len(word) > 3 else word.lower() for word in words])

def save_to_csv():
    global saved_label

    file_path = "students.csv"
    headers = ["ID No.", "Last Name", "First Name", "Gender", "Year Level", "College", "Program"]

    student_id = id_no.get()
    student_data = [
        student_id,
        last_name.get().title(),
        first_name.get().title(),
        gender_dropdown.get(),
        year_dropdown.get(),
        college_dropdown.get(),
        program_info.get()
    ]

    errors = []

    id_pattern = r"^\d{4}-\d{4}$"
    if not re.match(id_pattern, student_id) or any(char.isalpha() for char in student_id):
        errors.append("• ID No. must be in the format XXXX-XXXX (e.g., 2024-1234) and contain only numbers.")

    if any(char.isdigit() for char in last_name.get()):
        errors.append("• Last Name must not contain numbers.")

    if any(char.isdigit() for char in first_name.get()):
        errors.append("• First Name must not contain numbers.")

    program_pattern = r"^([A-Za-z]+(?:\s[A-Za-z]+){0,3})\s*-\s*([A-Za-z\s]+)$"
    match = re.match(program_pattern, program_info.get())

    if not match:
        errors.append("• Program Info must be in the format 'CODE - Program Name' (e.g., BSCS - Bachelor of Science in Computer Science).")
    else:
        program_code = match.group(1).upper()
        program_name = match.group(2).strip()

        if len(program_code.split()) > 3:
            errors.append("• Program Code must have at most 3 spaces (e.g., 'BS CS AI').")

        if any(char.isdigit() for char in program_code):
            errors.append("• Program Code must not contain numbers.")

        if len(program_name) < 6:
            errors.append("• Program Name must be at least 6 characters long.")

        if any(char.isdigit() for char in program_name):
            errors.append("• Program Name must not contain numbers.")

        program_name = capitalize_program_name(program_name)

        student_data[6] = f"{program_code} - {program_name}"

    if "" in student_data[:3]:
        errors.append("• All fields (ID No., Last Name, First Name) must be filled out.")

    if gender_dropdown.get() == "Select":
        errors.append("• Please select a Gender.")

    if year_dropdown.get() == "Select":
        errors.append("• Please select a Year Level.")

    if college_dropdown.get() == "Select":
        errors.append("• Please select a College.")

    if program_info.get() == "Ex: BSCS - Bachelor of Science in Computer Science" or program_info.get() == "":
        errors.append("• Program information is required.")

    if errors:
        messagebox.showerror("Form Error", "There are errors in your form:\n\n" + "\n".join(errors))
        return

    file_exists = os.path.exists(file_path)
    existing_student = find_student_in_csv(student_id)
    if existing_student:
        confirm = messagebox.askyesno("ID Already Exists", f"A student with ID No. {student_id} already exists.\n\nDo you want to override their information?")
        if not confirm:
            return  
        updated_rows = []
        with open(file_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader)
            for row in reader:
                if row and row[0] != student_id:
                    updated_rows.append(row)

        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(updated_rows)

    with open(file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(student_data)

    id_no.delete(0, "end")
    id_no.insert(0, "Ex: 1234-5678")
    id_no.config(fg="gray", justify="center")

    last_name.delete(0, "end")
    first_name.delete(0, "end")

    gender_dropdown.set("Select")
    year_dropdown.set("Select")
    college_dropdown.set("Select")

    program_info.delete(0, "end")
    program_info.insert(0, "Ex: BSCS AI - Bachelor of Science in Computer Science")
    program_info.config(fg="gray")
    
    display_students()

    saved_label = Label(root, bg="lightgray", width=30, text="Saved Successfully!", fg="green", font=("Arial", 10, "bold"))
    frame.create_window(145, 365, window=saved_label)

    bind_reset_events()

def remove_saved_label(event=None):
    global saved_label
    if saved_label is not None:
        saved_label.destroy()
        saved_label = None

def bind_reset_events():
    for widget in [id_no, last_name, first_name, program_info]:
        widget.bind("<Key>", remove_saved_label)
    for dropdown in [gender_dropdown, year_dropdown, college_dropdown]:
        dropdown.bind("<<ComboboxSelected>>", remove_saved_label)

def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=10, **kwargs):
    points = [
        x1 + radius, y1, x2 - radius, y1,
        x2, y1, x2, y1 + radius, x2, y2 - radius,
        x2, y2, x2 - radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius, x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

def on_resize(event):
    global x1,y1
    search_frame.delete("all")
    margin = 6
    radius = 20
    canvas_width = search_frame.winfo_width()
    canvas_height = search_frame.winfo_height()

    x1 = margin
    y1 = margin
    x2 = canvas_width - margin
    y2 = canvas_height - margin

    create_rounded_rectangle(search_frame, x1, y1, x2, y2, radius=radius, fill='#F1F3F8', outline="#E4EBF5")
    
    search_frame.create_window(x1 + 5, y1 + 3, anchor="nw", window=search_bar, width=x2 - x1 - 10, height=y2 - y1 - 4)

    icon_label.place(x=x1 + -7, y=y1 + -3)
    text_label.place(x=x1 + 15, y=y1 + 1)
    search_var.set("")
    cancel_butt.pack_forget()

def on_add_button_click(event):
    item = side_bar_canvas.find_closest(event.x, event.y)[0]
    if item in [add_button, add_text]:  
        side_bar_canvas.itemconfig(add_button, fill='#2E4D8C')
        side_bar_canvas.itemconfig(add_text, fill='#FFFFFF')
    elif item in [edit_button, edit_text, edit_icon]:  
        side_bar_canvas.itemconfig(edit_button, fill='#153E83')
        side_bar_canvas.itemconfig(edit_text, fill='#FFFFFF')
    elif item in [delete_button, delete_text, delete_icon]:  
        side_bar_canvas.itemconfig(delete_button, fill='#153E83')
        side_bar_canvas.itemconfig(delete_text, fill='#FFFFFF')

def button_release(event):
    side_bar_canvas.itemconfig(add_button, fill='#D7E3F5')  
    side_bar_canvas.itemconfig(add_text, fill='#154BA6')

    global frame, is_form_visible
    
    if not is_form_visible: 
        
        side_bar_canvas.configure(bg="lightgray")

        frame = Canvas(content_frame, bg="white", width=287, height=430, bd=0, highlightthickness=0)
        frame.grid(row=0, column=0, rowspan=2, columnspan=2, sticky="nw")

        toggle_form()
        frame.grid()
    else:
        restore_content()
    
def on_hover(event):
    side_bar_canvas.itemconfig(add_button, fill='#A5CAEC')  
    side_bar_canvas.itemconfig(add_text, fill='#154BA6') 
    side_bar_canvas.config(cursor="hand2")
def on_leave(event):
    side_bar_canvas.itemconfig(add_button, fill='white')
    side_bar_canvas.itemconfig(add_text, fill='#2363C6')
    side_bar_canvas.config(cursor="")

def on_hover_delete(event):
    side_bar_canvas.itemconfig(delete_button, fill='#A5CAEC')  
    side_bar_canvas.itemconfig(delete_text, fill='#154BA6') 
    side_bar_canvas.config(cursor="hand2")
def on_leave_delete(event):
    side_bar_canvas.itemconfig(delete_button, fill='#2363C6')
    side_bar_canvas.itemconfig(delete_text, fill='white')
    side_bar_canvas.config(cursor="")

def on_hover_edit(event):
    side_bar_canvas.itemconfig(edit_button, fill='#A5CAEC')  
    side_bar_canvas.itemconfig(edit_text, fill='#154BA6') 
    side_bar_canvas.config(cursor="hand2")
def on_leave_edit(event):
    side_bar_canvas.itemconfig(edit_button, fill='#2363C6')
    side_bar_canvas.itemconfig(edit_text, fill='white')
    side_bar_canvas.config(cursor="")

def delete_stud(event):
    def trigger_once(event):
        on_leave_delete(event)
        root.unbind("<Motion>")

    root.bind("<Motion>", trigger_once)
    selected_item = tree.selection() 
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a student to delete.")
        return

    student_data = tree.item(selected_item, "values") 
    student_id = student_data[0] 

    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete student ID {student_id}?")
    if not confirm:
        return  
    
    tree.delete(selected_item)

 
    updated_rows = []
    with open("students.csv", "r", newline="") as file:
        reader = csv.reader(file)
        header = next(reader) 
        for row in reader:
            if row and row[0] != student_id:  
                updated_rows.append(row)


    with open("students.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header) 
        writer.writerows(updated_rows) 

    

    display_students()
    restore_content()
    messagebox.showinfo("Success", f"Student ID {student_id} has been deleted!")

def edit_stud(event):
    global frame, is_form_visible,sorting

    def trigger_once(event):
        on_leave_edit(event)
        root.unbind("<Motion>")
    root.bind("<Motion>",trigger_once)

    selected_item = tree.selection()
    if not selected_item:  
        messagebox.showwarning("Warning", "Please select a student to edit!")
        return

    student_id = tree.item(selected_item, "values")[0]  
    student_data = find_student_in_csv(student_id)

    if student_data:
        if not is_form_visible:
            side_bar_canvas.configure(bg="lightgray")
            frame = Canvas(content_frame, bg="white", width=287, height=430, bd=0, highlightthickness=0)
            frame.grid(row=0, column=0, rowspan=2, columnspan=2, sticky="nw")

            toggle_form()


        populate_form(student_data)

        style = ttk.Style()
        style.configure("Custom.TCombobox", foreground="") 
        style.configure("Custom.TCombobox", foreground="black")

        year_dropdown = ttk.Combobox(style="Custom.TCombobox")
        id_no.config(fg="black",justify="left")
        last_name.config(fg="black")
        first_name.config(fg="black")
        program_info.config(fg="black")
        text.configure(text="Edit Form")


        submit_canvas.bind("<ButtonRelease-1>", lambda event: update_student(student_id))

    else:
        messagebox.showerror("Error", "Student not found in the CSV file.")

def update_student(old_id):
    file_path = "students.csv"

    new_data = [
        id_no.get(),
        last_name.get().title(),
        first_name.get().title(),
        gender_dropdown.get(),
        year_dropdown.get(),
        college_dropdown.get(),
        program_info.get()
    ]

    errors = []  

    id_pattern = r"^\d{4}-\d{4}$"
    if not re.match(id_pattern, id_no.get()) or any(char.isalpha() for char in id_no.get()):
        errors.append("• ID No. must be in the format XXXX-XXXX (e.g., 2024-1234) and contain only numbers.")

    if any(char.isdigit() for char in last_name.get()):
        errors.append("• Last Name must not contain numbers.")
    
    if any(char.isdigit() for char in first_name.get()):
        errors.append("• First Name must not contain numbers.")

    program_pattern = r"^([A-Za-z]+(?:\s[A-Za-z]+){0,3})\s*-\s*([A-Za-z\s]+)$"
    match = re.match(program_pattern, program_info.get())

    if not match:
        errors.append("• Program Info must be in the format 'CODE - Program Name' (e.g., BSCS - Bachelor of Science in Computer Science).")
    else:
        program_code = match.group(1).upper()  
        program_name = match.group(2).strip()

        if len(program_code.split()) > 3:
            errors.append("• Program Code must have at most 3 spaces (e.g., 'BS CS AI').")

        if any(char.isdigit() for char in program_code):
            errors.append("• Program Code must not contain numbers.")

        if len(program_name) < 6:
            errors.append("• Program Name must be at least 6 characters long.")

        if any(char.isdigit() for char in program_name):
            errors.append("• Program Name must not contain numbers.")

        program_name = capitalize_program_name(program_name)

        new_data[6] = f"{program_code} - {program_name}" 

    if "" in new_data[:3]: 
        errors.append("• All fields (ID No., Last Name, First Name) must be filled out.")

    if gender_dropdown.get() == "Select":
        errors.append("• Please select a Gender.")

    if year_dropdown.get() == "Select":
        errors.append("• Please select a Year Level.")

    if college_dropdown.get() == "Select":
        errors.append("• Please select a College.")

    if program_info.get() == "Ex: BSCS - Bachelor of Science in Computer Science" or program_info.get() == "":
        errors.append("• Program information is required.")

    try:
        with open(file_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  
            for row in reader:
                if row and row[0] == new_data[0] and row[0] != old_id:
                    errors.append(f"• Student ID {new_data[0]} already exists. Please use a different ID.")
                    break
    except FileNotFoundError:
        errors.append("• Student database (CSV file) not found.")

    if errors:
        messagebox.showerror("Form Error", "There are errors in your form:\n\n" + "\n".join(errors))
        return

    confirm = messagebox.askyesno("Confirm Update", f"Replace data for student ID {old_id}?")
    if not confirm:
        return

    updated_rows = []
    try:
        with open(file_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            headers = next(reader)
            for row in reader:
                if row and row[0] != old_id: 
                    updated_rows.append(row)

        updated_rows.append(new_data)

        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(updated_rows)

        messagebox.showinfo("Success", "Student information updated!")

        display_students()
        restore_content()

    except FileNotFoundError:
        messagebox.showerror("Error", "The student database file could not be found.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred while updating the student record:\n\n{str(e)}")

def on_sidebar_resize(event):
    global add_button, add_text, edit_button, edit_text, delete_button, delete_text, edit_icon_img, delete_icon_img,delete_icon,edit_icon,delete_icon_img
    side_bar_canvas.delete("all")
    canvas_width = side_bar_canvas.winfo_width()
    canvas_height = side_bar_canvas.winfo_height()

    side_frame = create_rounded_rectangle(side_bar_canvas, -200, 0, canvas_width, canvas_height + 50, radius=130, fill="#2363C6")
    side_bar_canvas.tag_bind(side_frame,"<ButtonRelease-1>",remove)
    add_width, add_height = 160, 35
    edit_width, edit_height = 160, 25
    delete_width, delete_height = 160, 25


    add_to_edit_spacing = 15
    edit_to_delete_spacing = 2

    offset_x = 0  
    icon_text_spacing = 5  

    add_x1 = (canvas_width - add_width) // 2
    add_y1 = 35
    add_x2 = add_x1 + add_width
    add_y2 = add_y1 + add_height

    add_button = create_rounded_rectangle(side_bar_canvas, add_x1, add_y1, add_x2, add_y2, radius=20, fill="white")
    add_text = side_bar_canvas.create_text((add_x1 + add_x2) // 2, (add_y1 + add_y2) // 2,
                                           text="Add Student", fill="#2363C6", font=('Albert Sans', 13, 'bold'))

    delete_x1 = ((canvas_width - delete_width) // 2) + offset_x
    delete_y1 = add_y2 + add_to_edit_spacing 
    delete_x2 = delete_x1 + delete_width
    delete_y2 = delete_y1 + delete_height

    delete_button = create_rounded_rectangle(side_bar_canvas, delete_x1, delete_y1, delete_x2, delete_y2, radius=20, fill="#2363C6")


    delete_icon_img = PhotoImage(file="Images/Trash.png")
    delete_icon_x = delete_x1 + 8  
    delete_icon_y = (delete_y1 + delete_y2) // 2
    delete_icon = side_bar_canvas.create_image(delete_icon_x, delete_icon_y, anchor="w", image=delete_icon_img)

    delete_text_x = delete_icon_x + delete_icon_img.width() + icon_text_spacing
    delete_text = side_bar_canvas.create_text(delete_text_x, delete_icon_y, text="Delete Student", fill="white",
                                              font=('Albert Sans', 11, 'normal'), anchor="w")


    edit_x1 = ((canvas_width - edit_width) // 2) + offset_x
    edit_y1 = delete_y2 + edit_to_delete_spacing  
    edit_x2 = edit_x1 + edit_width
    edit_y2 = edit_y1 + edit_height

    edit_button = create_rounded_rectangle(side_bar_canvas, edit_x1, edit_y1, edit_x2, edit_y2, radius=20, fill="#2363C6")

    global edit_icon_img
    edit_icon_img = PhotoImage(file="Images/edit.png")
    icon_x = edit_x1 + 10  # Left inside button
    icon_y = (edit_y1 + edit_y2) // 2
    edit_icon = side_bar_canvas.create_image(icon_x, icon_y, anchor="w", image=edit_icon_img)

    text_x = icon_x + edit_icon_img.width() + icon_text_spacing
    edit_text = side_bar_canvas.create_text(text_x, icon_y, text="Edit Student", fill="white",
                                            font=('Albert Sans', 11, 'normal'), anchor="w")

    #add button
    side_bar_canvas.tag_bind(add_button, "<Enter>", on_hover)
    side_bar_canvas.tag_bind(add_button, "<Leave>", on_leave)
    side_bar_canvas.tag_bind(add_button, "<Button-1>", on_add_button_click)
    side_bar_canvas.tag_bind(add_button, "<ButtonRelease-1>", button_release)

    side_bar_canvas.tag_bind(add_text, "<Enter>", on_hover)
    side_bar_canvas.tag_bind(add_text, "<Leave>", on_leave)
    side_bar_canvas.tag_bind(add_text, "<Button-1>", on_add_button_click)
    side_bar_canvas.tag_bind(add_text, "<ButtonRelease-1>", button_release)

    #edit button
    side_bar_canvas.tag_bind(edit_button, "<Leave>", on_leave_edit)
    side_bar_canvas.tag_bind(edit_button, "<Button-1>", on_add_button_click)
    side_bar_canvas.tag_bind(edit_button, "<ButtonRelease-1>", edit_stud)

    side_bar_canvas.tag_bind(edit_icon, "<Enter>", on_leave_edit)
    side_bar_canvas.tag_bind(edit_icon, "<ButtonRelease-1>", edit_stud)

    side_bar_canvas.tag_bind(edit_text, "<Enter>", on_hover_edit)
    side_bar_canvas.tag_bind(edit_text, "<Button-1>", on_add_button_click)
    side_bar_canvas.tag_bind(edit_text, "<ButtonRelease-1>", edit_stud)

    #delete button
    side_bar_canvas.tag_bind(delete_button, "<Leave>", on_leave_delete)
    side_bar_canvas.tag_bind(delete_button, "<Button-1>", on_add_button_click)
    side_bar_canvas.tag_bind(delete_button, "<ButtonRelease-1>", delete_stud)

    side_bar_canvas.tag_bind(delete_icon, "<Enter>", on_hover_delete)
    side_bar_canvas.tag_bind(delete_icon, "<ButtonRelease-1>", delete_stud)

    side_bar_canvas.tag_bind(delete_text, "<Enter>", on_hover_delete)
    side_bar_canvas.tag_bind(delete_text, "<Button-1>", on_add_button_click)
    side_bar_canvas.tag_bind(delete_text, "<ButtonRelease-1>", delete_stud)
    

def delete_entry():
    search_var.set("")
    search_bar.focus_set()
    cancel_butt.pack_forget()

def on_input_change(*args):
    if search_var.get():
        cancel_butt.lift()
        cancel_butt.pack(side="right",padx=2)

def clear_placeholder(event=None):
    if search_var.get() == "":
        icon_label.place_forget()
        text_label.place_forget()
    search_bar.focus_set()

def restore_placeholder(event=None):
    if search_var.get() == "":
        icon_label.place(x=x1 + -7, y=y1 + -3)
        text_label.place(x=x1 + 15, y=y1 + 1)

def remove_focus(event):
    global sorting
    widget = event.widget

    if isinstance(widget, (Entry, Button, ttk.Combobox, ttk.Treeview, Label, Canvas)):
        return

    tree.selection_remove(tree.selection())
    cancel_butt.pack_forget()
    search_var.set("")
    root.focus_set()
    

def toggle_selection(event):
    clicked_item = tree.identify_row(event.y)
    selected_item = tree.selection()

    if clicked_item in selected_item:
        tree.selection_remove(clicked_item)
    else:
        tree.selection_set(clicked_item)


def on_root_resize(event):
    total_width = root.winfo_width()

    sidebar_width = max(220, min(270, int(total_width * 0.25)))

    root.columnconfigure(0, minsize=sidebar_width)

    side.config(width=sidebar_width)

root = Tk()
root.geometry("1100x605")
root.minsize(510, 200)
root.title(" ")
root.configure(bg="white")
root.rowconfigure(1, weight=1)
root.columnconfigure(0,minsize=220)
root.columnconfigure(1,weight=1)



#header
header = Frame(root, bg="white",height=50)
header.grid(row=0, column=0, sticky="nsew",columnspan=2)
header.rowconfigure(0, weight=0)
header.columnconfigure(0, weight=0)
header.columnconfigure(1, weight=1)
header.grid_propagate(False)

text_stud = Label(header, text="Student Information", font=('Albert Sans', 15, 'bold'), bg='white')
text_stud.grid(row=0, column=0, padx=20)

def filter_students():
    global students 

    query = search_var.get().strip().lower().replace(",", "").replace("  ", " ")

    tree.delete(*tree.get_children())

    for student in students:

        student_values = [str(value).lower().replace(",", "").strip() for value in student]

        original_name = student[1].lower().replace(",", "").strip()
        reversed_name = " ".join(reversed(student[1].split(","))).strip().lower()

        if any(query in value for value in student_values) or query in original_name or query in reversed_name:
            tree.insert("", "end", values=student)


def on_input_change(*args):
    if search_var.get():
        cancel_butt.lift()
        cancel_butt.pack(side="right", padx=2)
    else:
        cancel_butt.pack_forget()
    filter_students()


search_var = StringVar()
search_var.trace_add("write", on_input_change)
search_frame = Canvas(header, bg="white", height=40, bd=0, highlightthickness=0)
search_frame.grid(row=0, column=1, sticky="nsew", padx=(50, 120), pady=5)

search_bar = Entry(header, textvariable=search_var, bg="#F1F3F8", font=('Albert Sans', 10, 'normal'), fg="gray", borderwidth=0, highlightthickness=0)
search_bar.grid(row=0,column=0,padx=0)

icon1 = PhotoImage(file="Images/SearchIcon.png")
icon_label = Label(search_bar, image=icon1, bg="#F1F3F8", bd=0)
text_image = PhotoImage(file="Images/Search In Here.png")
text_label = Label(search_bar, image=text_image, bg="#F1F3F8", bd=0)

cancel = PhotoImage(file='Images/cancel.png')
cancel_butt = Button(search_bar,image=cancel,bg="#F1F3F8", bd=0,cursor="hand2",command=delete_entry)

search_frame.bind("<Configure>", on_resize)
search_bar.bind("<FocusIn>", clear_placeholder)
search_bar.bind("<FocusOut>", restore_placeholder)
icon_label.bind("<Button-1>",clear_placeholder)
text_label.bind("<Button-1>",clear_placeholder)

root.bind("<Button-1>", remove_focus)


# side frame
side = Frame(root,bg="white")
side.grid(row=1,column=0,sticky="nsew")
side.columnconfigure(0, weight=1)
side.rowconfigure(0,weight=1)
# Side Bar
side_bar_canvas = Canvas(side, bg="white", width=180, height=105, bd=0, highlightthickness=0)
side_bar_canvas.grid(row=0, column=0, sticky="nsew")
side_bar_canvas.bind("<Configure>", on_sidebar_resize)


# content
content_frame = Frame(root,bg="white")
content_frame.grid(row=1,column=1,sticky="nsew")
content_frame.grid_rowconfigure(0, weight=1)
content_frame.grid_columnconfigure(0, weight=1)

student_text = Label(content_frame, background="white", text="STUDENTS", font=("AlbertSans", 20, "bold"))
student_text.grid(row=0, column=0, sticky="nw", pady=15, padx=20)

is_form_visible = False  
rounded_rectangle_id = None
form_widgets = []

#form

def on_select(event):
    event.widget.configure(foreground="black")
def toggle_form():
    global sorting,is_form_visible,text, round, form_widgets,last_name,first_name,gender_dropdown,id_no,year_dropdown,college_dropdown,program_info,submit_canvas

    if is_form_visible:
        restore_content()
    else:
        is_form_visible = True

        if sorting:
            sorting.destroy()
            sorting=None
            sort_canvas.itemconfig(sort_frame, fill="white")

        style = ttk.Style()
        style.configure("Custom.TCombobox", foreground="") 
        style.configure("Custom.TCombobox",relief="flat",foreground="gray")

        form_frame = round = create_rounded_rectangle(frame, -300, 0, 287, 430, radius=130,fill='lightgray')
        form_widgets.append(round)
        frame.tag_bind(form_frame,"<Button-1>",remove)

        text = Label(root,text="Student Form", font=("Arial", 20, "bold"), bg="lightgray",fg="#2363C6")
        frame.create_window(130,30,window=text)
        form_widgets.append(text)

        text2 = Label(root, text="Student's Full Name ", bg="lightgray", font=("Arial", 12, "bold"))
        frame.create_window(90,70,window=text2)
        form_widgets.append(text2)
        
        last_name = Entry(root, font=("Albert Sans", 10, "normal"),width=14)
        frame.create_window(65,90,window=last_name)
        form_widgets.append(last_name)

        last_text = Label(root, text="Last Name ", bg="lightgray", fg="gray", font=("Arial", 8))
        frame.create_window(65,110,window=last_text)
        form_widgets.append(last_text)

        first_name = Entry(root, font=("Albert Sans", 10, "normal"),width=20)
        frame.create_window(200,90,window=first_name)
        form_widgets.append(first_name)

        first_text = Label(root, text="First Name ", bg="lightgray", fg="gray", font=("Arial", 8))
        frame.create_window(200,110,window=first_text)
        form_widgets.append(first_text)


        gender = Label(root, text="Gender", font=('Arial', 12, 'bold'), bg='light gray')
        frame.create_window(42,130,window=gender)
        form_widgets.append(gender)

        gender_dropdown = ttk.Combobox(root,style="Custom.TCombobox",values=["Male", "Female", "Other"], state="readonly", width=13)
        frame.create_window(65,150,window=gender_dropdown)
        form_widgets.append(gender_dropdown)
        gender_dropdown.set("Select") 
        gender_dropdown.bind("<<ComboboxSelected>>",on_select)

        id = Label(root, text="ID No.", font=('Arial', 12, 'bold'), bg='light gray')
        frame.create_window(39,175,window=id)
        form_widgets.append(id)

        id_no = Entry(root, font=('Albert Sans', 10, 'normal'),width=14, fg="gray",justify="center")
        frame.create_window(66,195,window=id_no)
        form_widgets.append(id_no)
        id_no.insert(0, "Ex: 1234-5678")
        id_no.bind("<FocusIn>", lambda event: id_no.get() == "Ex: 1234-5678" and (id_no.delete(0, END), id_no.config(fg="black",justify="left")))
        id_no.bind("<FocusOut>", lambda event: id_no.get() == "" and (id_no.insert(0, "Ex: 1234-5678"), id_no.config(fg="gray",justify="center")))


        year_dropdown = ttk.Combobox(root,style="Custom.TCombobox",values=["1st", "2nd", "3rd", "4th"], state="readonly", width=13)
        frame.create_window(180,195,window=year_dropdown)
        form_widgets.append(year_dropdown)

        year = Label(root, text="Year Level", font=('Arial', 12, 'bold'), bg='light gray')
        frame.create_window(170,170,window=year)
        form_widgets.append(year)
        year_dropdown.set("Select") 
        year_dropdown.bind("<<ComboboxSelected>>",on_select)


        college_names = [
            "CCS - College of Computer Studies",
            "COET - College of Engineering and Technology", 
            "CSM - College of Science and Mathematics", 
            "CED - College of Education", 
            "CASS - College of Arts and Social Sciences", 
            "CEBA - College of Economics Business and Accountancy", 
            "CHS - College of Health Sciences" ]
        college = Label(root, text="College", font=('Arial', 12, 'bold'), bg='light gray')
        frame.create_window(45,218,window=college)
        form_widgets.append(college)

        college_dropdown = ttk.Combobox(root,style="Custom.TCombobox",values=college_names, state="readonly", width=38)
        frame.create_window(140,238,window=college_dropdown)
        form_widgets.append(college_dropdown)
        college_dropdown.set("Select") 
        college_dropdown.bind("<<ComboboxSelected>>",on_select)

        program = Label(root,text="Program",font=('Arial', 12, 'bold'),bg="light gray")
        frame.create_window(50,262,window=program)
        form_widgets.append(program)

        program_info = Entry(root, font=('Albert Sans', 10, 'normal'),width=35, fg="gray")
        frame.create_window(140,282,window=program_info)
        form_widgets.append(program_info)

        program_code = Label(root, text="Program Code ", bg="lightgray", fg="gray", font=("Arial", 8))
        frame.create_window(65,305,window=program_code)
        form_widgets.append(program_code)

        program_name = Label(root, text="Program Name ", bg="lightgray", fg="gray", font=("Arial", 8))
        frame.create_window(200,305,window=program_name)
        form_widgets.append(program_name)
        program_info.insert(0, "Ex: BSCS - Bachelor of Science in Computer Science")
        program_info.bind("<FocusIn>", lambda event: program_info.get() == "Ex: BSCS - Bachelor of Science in Computer Science" and (program_info.delete(0, END), program_info.config(fg="black")))
        program_info.bind("<FocusOut>", lambda event: program_info.get()  == "" and (program_info.insert(0, "Ex: BSCS - Bachelor of Science in Computer Science"), program_info.config(fg="gray")))


        def submit_click(event):
            submit_canvas.itemconfig(submit, fill='#153E83')
        def submit_release(event):
            submit_canvas.itemconfig(submit, fill='#2363C6')
            save_to_csv()
            
        def submit_hover(event):
            submit_canvas.itemconfig(submit, fill='#154BA6') 
            submit_canvas.config(cursor="hand2")
        def on_submit_leave(event):
            submit_canvas.itemconfig(submit, fill='#2363C6')
            submit_canvas.config(cursor="")


        def close_click(event):
            close_canvas.itemconfig(close, fill='#872D2D')

        def close_release(event):
            close_canvas.itemconfig(close, fill='#AA4141') 
            if 'saved_label' in globals() and saved_label is not None:
                remove_saved_label()
            restore_content()

        def close_hover(event):
            close_canvas.itemconfig(close, fill='#9B3535') 
            close_canvas.config(cursor="hand2")

        def close_leave(event):
            close_canvas.itemconfig(close, fill='#AA4141')
            close_canvas.config(cursor="")


        submit_canvas = Canvas(root, width=85, height=40, bg="light gray", highlightthickness=0)
        frame.create_window(100,335,window=submit_canvas)
        form_widgets.append(submit_canvas)
        submit = create_rounded_rectangle(submit_canvas, 5, 5, 85, 35, radius=20,fill='#2363C6')
        form_widgets.append(submit)
        submit_canvas.create_text(44, 20, text="Submit", fill="white", font=("Arial", 12, "bold"))
        submit_canvas.bind("<Button-1>", submit_click)
        submit_canvas.bind("<ButtonRelease-1>", submit_release)
        submit_canvas.bind("<Enter>", submit_hover)
        submit_canvas.bind("<Leave>", on_submit_leave)
                

        close_canvas = Canvas(root, width=85, height=40, bg="lightgray", highlightthickness=0)
        frame.create_window(190,335,window=close_canvas)
        form_widgets.append(close_canvas)
        close = create_rounded_rectangle(close_canvas, 5, 5, 85, 35, radius=20, fill='#AA4141')
        form_widgets.append(close)

        close_canvas.create_text(44, 20, text="Close", fill="white", font=("Arial", 12, "bold"))
        close_canvas.bind("<Button-1>", close_click)
        close_canvas.bind("<ButtonRelease-1>", close_release)
        close_canvas.bind("<Enter>", close_hover)
        close_canvas.bind("<Leave>", close_leave)

def restore_content(event=None):
    global is_form_visible, form_widgets
    if is_form_visible:
        for widget in form_widgets:
            if isinstance(widget, int):  
                if frame.type(widget) != "text" and frame.type(widget) != "rectangle":  
                    frame.delete(widget)  
            else: 
                widget.destroy()  
        frame.grid_forget()
        form_widgets.clear()
        is_form_visible = False  

    side_bar_canvas.config(bg="white")

def load_students():
    students = []
    if os.path.exists("students.csv"):
        with open("students.csv", "r") as file:
            reader = csv.reader(file)
            next(reader) 
            for row in reader:
                if len(row) >= 7: 
                    full_name = f"{row[1]}, {row[2]}" 
                    gender = row[3]
                    year_level = row[4]
                    college = row[5].split(" - ")[0] 
                    program = row[6].split(" - ")[0] 
                    students.append([row[0], full_name, gender, year_level, college, program])
    return students





def display_students():
    global tree,students
    students = load_students()
    
    columns = ("ID No.", "Name", "Gender", "Year Level", "College", "Program")

    if not hasattr(display_students, "initialized"):
        tree = ttk.Treeview(content_frame, columns=columns, show="headings", height=20,selectmode="browse")
        
            
        for col in columns:
            tree.heading(col, text=col, anchor="w")
            
            if col == "ID No.":
                tree.column(col, anchor="w", width=100)
            elif col == "Name":
                tree.column(col, anchor="w", width=250)
            elif col == "Gender":
                tree.column(col, anchor="w", width=80)
            elif col == "Year Level":
                tree.column(col, anchor="w", width=100)
            elif col == "College":
                tree.column(col, anchor="w", width=80)
            elif col == "Program":
                tree.column(col, anchor="w", width=150)
            
        
        
        tree.grid(row=0, column=0, sticky="nsew", pady=(70, 0), padx=(20, 0))
        
        style = ttk.Style()
        style.configure("Treeview", font=('Albert Sans', 12), rowheight=40, padding=(5, 5), highlightthickness=0, borderwidth=0)
        style.configure("Treeview.Heading", font=('Albert Sans', 15, 'bold'), anchor="w", padding=(1, 8), foreground="#9F9EA1", relief="flat", borderwidth=0)
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        style.map("Treeview", background=[('selected', '#2363C6')])
        
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.place(relx=1.0, rely=0.14, relheight=0.85, anchor="ne")


        def disable_column_drag(event):
            region = tree.identify_region(event.x, event.y)
            if region == "separator" or region == "heading": 
                return "break"

        tree.bind('<Button-1>', disable_column_drag, add='+')
        tree.bind('<B1-Motion>', disable_column_drag, add='+')

        display_students.initialized = True  


    for row in tree.get_children():
        tree.delete(row)
    for student in students:
        tree.insert("", "end", values=student)
 

    tree.delete(*tree.get_children())

    for student in students:
        tree.insert("", "end", values=student)
        
    def resize_columns(event=None):
        total_width = tree.winfo_width()
        
        name_column_index = columns.index("Name")
        tree_font = font.Font(font=('Albert Sans', 12))
        
        max_width = max([tree_font.measure(tree.set(item, "Name")) for item in tree.get_children()], default=200)
        tree.column("Name", width=max_width + 20)  

    tree.bind("<Configure>", resize_columns)
    search_var.trace_add("write", lambda *args: filter_students())

    def toggle_selection(event):
        clicked_item = tree.identify_row(event.y)
        selected_item = tree.selection() 

        if clicked_item: 
            if clicked_item in selected_item:  
                tree.after(1, lambda: tree.selection_remove(clicked_item))
            else:
                tree.after(1, lambda: tree.selection_set(clicked_item)) 
    tree.bind("<Button-1>", toggle_selection)


def remove(event):
    root.focus_set()

def sort_click(event):
    sort_canvas.itemconfig(sort_frame, fill="light gray")



sort_order = True

def sort_id():
    global tree, sort_order

    sort_order = not sort_order  
    id_reverse = not sort_order  

    def parse_id(id_str):

        try:
            year, number = map(int, id_str.split("-")) 
            return (year, number)
        except ValueError:
            return (float('inf'), float('inf')) 
    displayed_students = []
    for item in tree.get_children():
        displayed_students.append(tree.item(item, "values")) 
    displayed_students.sort(key=lambda x: parse_id(x[0]), reverse=id_reverse)


    for item in tree.get_children():
        tree.delete(item)

    for student in displayed_students:
        tree.insert("", "end", values=student)

    if id_reverse:
        id_text.configure(text="Descending")
    else:
        id_text.configure(text="Ascending")


def sort_name(event=None):
    global tree, sort_order

    sort_order = not sort_order  
    name_reverse = not sort_order  

    displayed_students = []
    for item in tree.get_children():
        displayed_students.append(tree.item(item, "values"))
    displayed_students.sort(key=lambda x: x[1].strip().lower(), reverse=name_reverse)


    for item in tree.get_children():
        tree.delete(item)

    for student in displayed_students:
        tree.insert("", "end", values=student)

    if name_reverse:
        sort_text.configure(text="Descending")
    else:
        sort_text.configure(text="Ascending")



def sort_click_release(event):
    global sorting,sort_text,id_text

    if sorting:
        sorting.destroy() 
        sorting = None


        sort_canvas.itemconfig(sort_frame, fill="white") 
    else:
        if is_form_visible:
            restore_content()
        style = ttk.Style()
        style.configure("Custom.TCombobox", foreground="") 
        style.configure("Custom.TCombobox",relief="flat",foreground="gray")

        def on_click(event):
            widget = event.widget  # Get the widget that was clicked

            if widget in [sort_text, name_sort_bg]:  
                name_sort_bg.itemconfig(sort_butt, fill='#153E83')
                sort_text.configure(bg="#153E83", fg="white")

            elif widget in [id_text, id_sort_bg]:  
                id_sort_bg.itemconfig(id_butt, fill='#153E83')
                id_text.configure(bg="#153E83", fg="white")
        
        def id_release(event):
            sort_id()
        def name_release(event):
            sort_name()

        def name_sort_hover(event):
            name_sort_bg.itemconfig(sort_butt, fill='#A5CAEC')
            sort_text.config(bg='#A5CAEC', fg='#154BA6')  
            name_sort_bg.config(cursor="hand2")
            sort_text.configure(cursor="hand2")

        def name_sort_leave(event):
            name_sort_bg.itemconfig(sort_butt, fill='#2363C6') 
            sort_text.config(bg='#2363C6', fg='white') 
            name_sort_bg.config(cursor="")

        def id_sort_hover(event):
            id_sort_bg.itemconfig(id_butt, fill='#A5CAEC')
            id_text.config(bg='#A5CAEC', fg='#154BA6')  
            id_sort_bg.config(cursor="hand2")
            id_text.configure(cursor="hand2")

        def id_sort_leave(event):
            id_sort_bg.itemconfig(id_butt, fill='#2363C6') 
            id_text.config(bg='#2363C6', fg='white') 
            name_sort_bg.config(cursor="")

        sorting = Canvas(content_frame, width=100, height=150, bg="white", highlightthickness=0)
        sorting_frame = create_rounded_rectangle(sorting, 0, 0, 100, 150, radius=20, fill="light gray") 
        sorting.grid(row=0, column=0, sticky="ne", padx=(0, 70))

        sorting.tag_bind(sorting_frame, "<Button-1>", remove)


        sort_by = Label(root,text="Sort By:", font=("Arial", 10, "bold"), bg="light gray",fg="#2363C6")
        sorting.create_window(30,15,window=sort_by)




        name_sort = Label(root,text="Name", font=("Arial", 10, "bold"), bg="light gray",fg="black")
        sorting.create_window(25,40,window=name_sort)

        name_sort_bg = Canvas(root,bg="lightgray",width=80,height=22,bd=0,highlightthickness=0)
        sorting.create_window(45,65,window=name_sort_bg)

        sort_butt = create_rounded_rectangle(name_sort_bg, 0, 0, 80, 22, radius=20, fill="#2363C6") 
        sort_text = Label(root,text="Ascending", font=("Albert Sans", 8, "bold"), bg="#2363C6",fg="white")
        sorting.create_window(45,65,window=sort_text)


        name_sort_bg.bind("<Button-1>",on_click)
        name_sort_bg.bind("<ButtonRelease-1>",name_release)
        sort_text.bind("<Button-1>",on_click)
        sort_text.bind("<ButtonRelease-1>",name_release)

        name_sort_bg.bind("<Enter>",name_sort_hover)
        name_sort_bg.bind("<Leave>",name_sort_leave)
        sort_text.bind("<Enter>",name_sort_hover)
        sort_text.bind("<Leave>",name_sort_leave)

        id_sort = Label(root,text="ID No.", font=("Arial", 10, "bold"), bg="light gray",fg="black")
        sorting.create_window(25,90,window=id_sort)

        id_sort_bg = Canvas(root,bg="lightgray",width=80,height=22,bd=0,highlightthickness=0)
        sorting.create_window(45,115,window=id_sort_bg)

        id_butt = create_rounded_rectangle(id_sort_bg, 0, 0, 80, 22, radius=20, fill="#2363C6") 
        id_text = Label(root,text="Ascending", font=("Albert Sans", 8, "bold"), bg="#2363C6",fg="white")
        sorting.create_window(45,115,window=id_text)

        id_sort_bg.bind("<Button-1>",on_click)
        id_sort_bg.bind("<ButtonRelease-1>",id_release)
        id_text.bind("<Button-1>",on_click)
        id_text.bind("<ButtonRelease-1>",id_release)

        id_sort_bg.bind("<Enter>",id_sort_hover)
        id_sort_bg.bind("<Leave>",id_sort_leave)
        id_text.bind("<Enter>",id_sort_hover)
        id_text.bind("<Leave>",id_sort_leave)



sorting = None
sort_canvas = Canvas(header,width=40,height=40,highlightthickness=0,bd=0,bg="white")
sort_canvas.grid(row=0,column=1,padx=(0,70),pady=0,sticky="e")
sort_frame = create_rounded_rectangle(sort_canvas, 4, 7, 35, 35, radius=20, fill="white") 
sort = PhotoImage(file="Images/sort.png")
sort_canvas.create_image(20, 20, image=sort, anchor="center") 

sort_canvas.bind("<Button-1>",sort_click)
sort_canvas.bind("<ButtonRelease-1>",sort_click_release)






display_students()
root.bind("<Configure>",on_root_resize)
root.mainloop()
