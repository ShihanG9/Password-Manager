import string
import random
from tkinter import CENTER, Tk, Label, Button, Entry, Frame, END, Toplevel
from tkinter import ttk
from db_operations import DbOperations
from encryption_util import decrypt_password
from tkinter.simpledialog import askstring
from encryption_util import set_master_password


class root_window:

    def change_master_key(self):
        new_password = askstring("Change Master Password", "Enter your new master password:", show="*")
        if not new_password:
            self.showmessage("Error", "No new password entered")
            return
        
        # Re-encrypt all passwords using the new master key
        self.db.change_master_password(new_password)
        set_master_password(new_password)
        self.showmessage("Success", "Master password updated successfully")
        self.show_records()


    def generate_password(self):
        length = 12  # you can make this customizable
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for _ in range(length))
        self.entry_boxes[3].delete(0, END)
        self.entry_boxes[3].insert(0, password)


    def __init__(self, root, db):
        self.db = db
        self.root = root
        self.root.title("Password Manager")

        # Maximize Screen
        try:
            self.root.state('zoomed')  # Windows default
        except:
            try:
                self.root.attributes('-zoomed', True)  # Some Tcl versions
            except:
                self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0") # Maximizes the window on Windows
        
        self.is_dark_mode = True  # Theme State Tracker
        
        # Header
        head_title = Label(self.root, text = "Password Manager", width=40, bg="purple", font=("Ariel", 20), padx=10, pady=10, justify=CENTER, anchor="center").grid(columnspan=4, padx=140, pady=20)

        # CRUD FRAME
        self.crud_frame = Frame(self.root, highlightbackground="black", highlightthickness=1, padx=10, pady=30)
        self.crud_frame.grid()
        self.create_entry_labels()
        self.create_entry_boxes()
        self.create_crud_buttons()
        self.create_records_tree()

        # SEARCH LABEL
        Label(self.crud_frame, text="Search (Website / Ecrypted Password)",
            bg="#3c3f41" if self.is_dark_mode else "#ffffff",
            fg="white" if self.is_dark_mode else "black",
            font=("Ariel", 12)).grid(row=self.row_no, column=self.col_no, columnspan=2, pady=(10, 0))

        self.row_no += 1  # Move to next row for entry and button

        # SERACH BAR
        self.search_entry = Entry(self.crud_frame, width=30, font=("Ariel",12))
        self.search_entry.grid(row=self.row_no, column=self.col_no)
        self.col_no+=1
        Button(self.crud_frame, text="Search", bg="yellow", font=("Ariel",12), width=20, command=self.search_records).grid(row=self.row_no, column=self.col_no, padx=5, pady=5)
#        Button(self.crud_frame, text="Search", bg="yellow", font=("Ariel",12), width=20).grid(row=self.row_no, column=self.col_no, padx=5, pady=5)

        # Apply theme
        self.apply_theme()

        # Toggle Theme Button
        self.row_no += 1  # Move to the next row below search
        self.col_no = 0

        Button(self.crud_frame, text="Toggle Theme", bg="gray", fg="white",
            font=("Segoe UI", 10, "bold"), command=self.toggle_theme).grid(
            row=self.row_no, column=self.col_no, padx=5, pady=10, columnspan=4)



    def create_entry_labels(self):
        self.col_no,  self.row_no = 0, 0
        labels_info = ('ID', 'Website', 'Username', 'Password')
        for label_info in labels_info:
            Label(self.crud_frame, text=label_info, bg="grey", fg="white", font=("Ariel", 12), padx=5, pady=2).grid(row=self.row_no, column=self.col_no, padx=5, pady=2)
            self.col_no+=1

    def create_crud_buttons(self):
        self.row_no+=1
        self.col_no = 0
        buttons_info = (('Save', 'green', self.save_record), 
                ('Update', 'blue', self.update_record), 
                ('Delete', 'red', self.delete_record), 
                ('Copy Password', 'violet', self.copy_password), 
                ('Generate Password', 'orange', self.generate_password),
                ('Change Master Password', 'black', self.change_master_key),
                ('Show All Records', 'purple', self.show_records))
        
        for btn_info in buttons_info:
            if btn_info[0]=='Show All Records':
                self.row_no+=1
                self.col_no=0
            Button(self.crud_frame, text=btn_info[0], bg=btn_info[1], fg="white", font=("Ariel", 12), padx=2, pady=1, width=20,command=btn_info[2]).grid(row=self.row_no, column=self.col_no, padx=5, pady=10)
            self.col_no+=1

    def create_entry_boxes(self):
        self.row_no+=1
        self.entry_boxes = []
        self.col_no = 0
        for i in range(4):
            show=""
            if i == 3:
                show = "*"
            entry_box = Entry(self.crud_frame, width=20, background="lightgrey",font=("Ariel", 12), show=show)
            entry_box.grid(row=self.row_no, column=self.col_no, padx=5, pady=2)
            self.col_no+=1
            self.entry_boxes.append(entry_box)

    
    # CRUD Functions

    def save_record(self):
        website = self.entry_boxes[1].get()
        username = self.entry_boxes[2].get()
        password = self.entry_boxes[3].get()
        data = { 'website': website, 'username': username, 'password': password}        
        self.db.create_record(data)
        self.show_records()

    def update_record(self):
        ID = self.entry_boxes[0].get()
        website = self.entry_boxes[1].get()
        username = self.entry_boxes[2].get()
        password = self.entry_boxes[3].get()
        data = { 'ID': ID, 'website': website, 'username': username, 'password': password}        
        self.db.update_record(data)
        self.show_records()

    def delete_record(self):
        ID = self.entry_boxes[0].get()     
        self.db.delete_record(ID)
        self.show_records()

    def search_records(self):
        keyword = self.search_entry.get().strip().lower()
        if not keyword:
            self.showmessage("Error", "Enter keyword to search")
            return
        
        # Clear previous results
        for item in self.records_tree.get_children():
           self.records_tree.delete(item)
            
        records_list = self.db.show_records()
        matches_found = False


        # First: check if input is an encrypted password
#        decrypted_done = False

#        for record in records_list:
#            encrypted_pwd = record[5]
#            if keyword == encrypted_pwd and not decrypted_done:
#                try:
#                    decrypted_password = decrypt_password(encrypted_pwd)
                    # Show decrypted password in popup
#                    self.showmessage("Decrypted Password", f"The password is: {decrypted_password}")
#                    return  # Exit after showing decrypted password
#                except:
#                    self.showmessage("Error", "Decryption failed.")
#                    decrypted_done = True
            
        # Else: continue normal website/username search
        keyword = keyword.lower()
        matches = []


        for record in records_list:
            website = record[3].lower()
            username = record[4].lower()

            try:
                decrypted_password = decrypt_password(record[5])
            except:
                decrypted_password = "[Decryption Failed]"

            
            if keyword in website or keyword in username:               
                self.records_tree.insert('', END, values=(record[0], record[3], record[4], decrypted_password))
                matches.append((record[3], record[4], decrypted_password))
                matches_found = True

        if len(matches) == 1:
            self.entry_boxes[1].delete(0, END)
            self.entry_boxes[1].insert(0, matches[0][0])  # Website

            self.entry_boxes[2].delete(0, END)
            self.entry_boxes[2].insert(0, matches[0][1])  # Username

            self.entry_boxes[3].delete(0, END)
            self.entry_boxes[3].insert(0, matches[0][2])  # Password

        if not matches_found:
            self.showmessage("Info", "No matching records found")     


    def show_records(self):
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)
        records_list = self.db.show_records()
        for record in records_list:
            self.records_tree.insert('', END, values=(record[0], record[3], [record[4]], record[5]))
    
    def create_records_tree(self):
        columns = ('ID', 'Website', 'Username', 'Password')
        self.records_tree = ttk.Treeview(self.root, columns=columns, show='headings')
        self.records_tree.heading('ID', text="ID")
        self.records_tree.heading('Website', text="Website Name")
        self.records_tree.heading('Username', text="Username")
        self.records_tree.heading('Password', text="Password")
        self.records_tree['displaycolumns'] = ('Website', 'Username')


        def item_selected(event):
           for selected_item in self.records_tree.selection():
                item = self.records_tree.item(selected_item)
                record = item['values']
                for entry_box, item in zip(self.entry_boxes, record):
                    entry_box.delete(0, END)
                    entry_box.insert(0, item)

        self.records_tree.bind('<<TreeviewSelect>>', item_selected)

        self.records_tree.grid()

#        self.records_tree.bind("<ButtonRelease-1>", self.on_row_select)
#        self.records_tree.grid()

#    def on_row_select(self, event):
#        selected_item = self.records_tree.selection()
#        if selected_item:
#            record = self.records_tree.item(selected_item[0])['values']
#            if len(record) >= 4:
#                self.entry_boxes[1].delete(0, END)
#                self.entry_boxes[1].insert(0, record[1])  # Website

#                self.entry_boxes[2].delete(0, END)
#                self.entry_boxes[2].insert(0, record[2])  # Username

#                self.entry_boxes[3].delete(0, END)
#                self.entry_boxes[3].insert(0, record[3])  # Decrypted Password



    
    # Theming
    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def apply_theme(self):
        if self.is_dark_mode:
            self.root.configure(bg="#1e1e1e")
            self.crud_frame.configure(bg="#2d2d2d")
        else:
            self.root.configure(bg="#f0f0f0")
            self.crud_frame.configure(bg="#ffffff")

        dark_colors = {
            "Save": "#227733",
            "Update": "#2255aa",
            "Delete": "#aa2222",
            "Copy Password": "#4444aa",
            "Generate Password": "#cc7722",
            "Change Master Password": "#555",
            "Show All Records": "#4b0082",
            "Search": "#997700",
            "Toggle Theme": "#333"                
        }

        light_colors = {
            "Save": "green",
            "Update": "blue",
            "Delete": "red",
            "Copy Password": "violet",
            "Generate Password": "orange",
            "Change Master Password": "black",
            "Show All Records": "purple",
            "Search": "yellow",
            "Toggle Theme": "gray"                
        }

        for child in self.crud_frame.winfo_children():
            if isinstance(child, Label):
                child.configure(bg="#3c3f41" if self.is_dark_mode else "#ffffff",
                            fg="white" if self.is_dark_mode else "black")
            elif isinstance(child, Entry):
                child.configure(bg="#1e1e1e" if self.is_dark_mode else "white",
                            fg="white" if self.is_dark_mode else "black",
                            insertbackground="white" if self.is_dark_mode else "black")
            elif isinstance(child, Button):
                original_text = child.cget("text")
                
                if self.is_dark_mode:
                    child.configure(bg=dark_colors.get(original_text, "#444"), fg="white")
                else:
                    fg_color = "white" if original_text != "Search" else "black"
                    child.configure(bg=light_colors.get(original_text, "#d9d9d9"), fg=fg_color)



    # Copy to Clipboard
    def copy_password(self):
        password_value = self.entry_boxes[3].get()
        # Try decrypting in case the password is encrypted
        try:
            decrypted = decrypt_password(password_value)
        except:
            decrypted = password_value  # fallback if already decrypted or not formatted correctly
        self.root.clipboard_clear()
        self.root.clipboard_append(decrypted)
        message = "Password Copied"
        title = "Copy"
        if self.entry_boxes[3].get()=="":
            message="Box is Empty"
            title = "Error"
        self.showmessage(title, message)

    def showmessage(self, title_box:str=None, message:str=None):
        TIME_TO_WAIT = 900 # in milliseconds
        root = Toplevel(self.root)
        background = 'green'
        if title_box == "Error":
            background = "red"
        root.geometry('350x40+600+200')
        root.title(title_box)
        Label(root, text=message, background=background, font=("Ariel", 15), fg='white').pack(padx=4, pady=2)
        try:
            root.after(TIME_TO_WAIT, root.destroy)
        except Exception as e:
            print("Error occured", e)


if __name__ == "__main__":
    from tkinter import messagebox

    # Ask master password before showing the main window
    temp_root = Tk()
    temp_root.withdraw()  # Hide temp window

    db_class = DbOperations()

    while True:
        password = askstring("Master Password", "Enter your master password:", show="*")
        if not password:
            exit()  # User cancelled

        set_master_password(password)

        db_class.create_master_check()  # Create master_check table and initial encrypted token

        if db_class.validate_master_password():
            break
        else:
            messagebox.showerror("Invalid", "Incorrect master password. Try again.")

    temp_root.destroy()  # Close temporary window after validation

    # Create DB and launch main window
    db_class.create_table()
    root = Tk()
    root_class = root_window(root, db_class)
    root.mainloop()