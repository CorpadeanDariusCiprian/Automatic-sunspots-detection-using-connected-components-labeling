import os
import re
import sqlite3
from tkinter import filedialog, Canvas, messagebox
import customtkinter as ctk
import bcrypt
from GUI.panels import DropDownPanel2

class A(ctk.CTkFrame):
    def __init__(self, parent, login_callback):
        super().__init__(master=parent)
        self.register_label = None
        self.login_callback = login_callback
        self.grid(column=0, columnspan=2, row=0, sticky='nsew')
        self.font1 = ('Helvetica', 25, 'bold')
        self.font2 = ('Arial', 17, 'bold')
        self.font3 = ('Arial', 13, 'bold')
        self.font4 = ('Arial', 13, 'bold', 'underline')
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
            )''')
        self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analyses (
                    analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT,
                    date TEXT,
                    k_value REAL,
                    wolf_number REAL,
                    FOREIGN KEY(user_email) REFERENCES users(email)
                    )''')

        self.signup_label = ctk.CTkLabel(self, font=self.font1, text='Sign In', text_color='#fff')
        self.signup_label.pack(side="top", padx=5, pady=50)
        self.username_entry = ctk.CTkEntry(self, font=self.font2, text_color='#fff',
                                                border_color='#004780', border_width=3,
                                                placeholder_text='Username', placeholder_text_color='#a3a3a3',
                                                width=200, height=50)
        self.username_entry.pack(side="top", padx=5, pady=10)
        self.email_entry = ctk.CTkEntry(self, font=self.font2, text_color='#fff',
                                              border_color='#004780', border_width=3,
                                             placeholder_text='Email', placeholder_text_color='#a3a3a3', width=200,
                                             height=50)
        self.email_entry.pack(side="top", padx=5, pady=10)
        self.password_entry = ctk.CTkEntry(self, font=self.font2, show='*', text_color='#fff',
                                                 border_color='#004780', border_width=3,
                                                placeholder_text='Password', placeholder_text_color='#a3a3a3',
                                                width=200, height=50)
        self.password_entry.pack(side="top", padx=5, pady=10)

        self.signup_button = ctk.CTkButton(self, command=self.signup, font=self.font2, text_color='#fff',
                                                 border_color='#004780',
                                                border_width=3, text='Sign In', hover_color='#006e44', cursor='hand2',
                                                corner_radius=5, width=120)
        self.signup_button.pack(side="top", padx=1, pady=10)

        self.login_label = ctk.CTkLabel(self, font=self.font3, text='Already have an account ?', text_color='#fff')
        self.login_label.pack(side="top", padx=1, pady=10)

        self.login_button = ctk.CTkButton(self, command=self.login, font=self.font4, text_color='#fff',
                                                border_color='#004780', border_width=3, text='Login',
                                               hover_color='#001220', cursor='hand2', corner_radius=5, width=40)
        self.login_button.pack(side="top", padx=1, pady=10)

    def signup(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$'

        if email != '' and password != '':
            # Check if email is in the correct format
            if not re.match(email_pattern, email):
                messagebox.showerror('Error', 'Invalid email format')
                return

            # Check if password meets criteria
            if not re.match(password_pattern, password):
                messagebox.showerror('Error',
                                     'Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one digit')
                return

        if email != '' and password != '':
            self.cursor.execute('SELECT email FROM users WHERE email = ?', [username])
            if self.cursor.fetchone() is not None:
                messagebox.showerror('Error', 'email already exists')
            else:
                encode_password = password.encode('utf-8')
                hashed_password = bcrypt.hashpw(encode_password, bcrypt.gensalt())
                self.cursor.execute('INSERT INTO users VALUES (?,?,?)', [username, email, hashed_password])
                self.conn.commit()
                messagebox.showinfo('success', 'succes')
        else:
            messagebox.showerror('Error', 'Complete all fields')

    def login_account(self):
        email = self.email_entry2.get()
        password = self.password_entry2.get()
        if email != '' and password != '':
            self.cursor.execute('SELECT email, password, username FROM users WHERE email = ?', [email])
            user = self.cursor.fetchone()
            if user:

                if bcrypt.checkpw(password.encode('utf-8'), user[1]):
                    self.login_callback(user[0], user[2])
                    self.grid_forget()
                else:
                    messagebox.showerror('Error', 'Invalid password')
            else:
                messagebox.showerror('Error', 'Invalid mail')
        else:
            messagebox.showerror('Error', 'Complete all fields')

    def login(self):
        self.username_entry.destroy()
        self.email_entry.destroy()
        self.password_entry.destroy()
        self.signup_label.destroy()
        self.signup_button.destroy()
        self.login_button.destroy()
        self.login_label.destroy()
        self.login_label = ctk.CTkLabel(self, font=self.font1, text='Login ', text_color='#fff')
        self.login_label.pack(side="top", padx=5, pady=50)

        self.email_entry2 = ctk.CTkEntry(self, font=self.font2, text_color='#fff',
                                              border_color='#004780', border_width=3, placeholder_text='Email',
                                              placeholder_text_color='#a3a3a3', width=200, height=50)
        self.email_entry2.pack(side="top", padx=5, pady=10)

        self.password_entry2 = ctk.CTkEntry(self, font=self.font2, show='*', text_color='#fff',
                                                 border_color='#004780', border_width=3,
                                                 placeholder_text='Password', placeholder_text_color='#a3a3a3',
                                                 width=200,
                                                 height=50)
        self.password_entry2.pack(side="top", padx=5, pady=10)

        self.login_button = ctk.CTkButton(self, font=self.font2,
                                               text_color='#fff',
                                               border_color='#004780', border_width=3,
                                               text='Login',
                                               hover_color='#006e44', command = self.login_account, cursor='hand2', corner_radius=5, width=120)
        self.login_button.pack(side="top", padx=5, pady=10)

        self.register_label = ctk.CTkLabel(self, font=self.font4, text='Don\'t have and account? ', text_color='#fff')
        self.register_label.pack(side="top", padx=5, pady=10)

        self.register_button = ctk.CTkButton(self, command=self.register, font=self.font4, text_color='#fff',
                                          border_color='#004780', border_width=3, text='Register',
                                          hover_color='#001220', cursor='hand2', corner_radius=5, width=40)

        self.register_button.pack(side="top", padx=5, pady=10)

    def register(self):
        self.email_entry2.destroy()
        self.password_entry2.destroy()
        self.register_label.destroy()
        self.register_button.destroy()
        self.login_button.destroy()
        self.login_label.destroy()

        self.signup_label = ctk.CTkLabel(self, font=self.font1, text='Sign In', text_color='#fff')
        self.signup_label.pack(side="top", padx=5, pady=50)
        self.username_entry = ctk.CTkEntry(self, font=self.font2, text_color='#fff',
                                           border_color='#004780', border_width=3,
                                           placeholder_text='Username', placeholder_text_color='#a3a3a3',
                                           width=200, height=50)
        self.username_entry.pack(side="top", padx=5, pady=10)
        self.email_entry = ctk.CTkEntry(self, font=self.font2, text_color='#fff',
                                        border_color='#004780', border_width=3,
                                        placeholder_text='Email', placeholder_text_color='#a3a3a3', width=200,
                                        height=50)
        self.email_entry.pack(side="top", padx=5, pady=10)
        self.password_entry = ctk.CTkEntry(self, font=self.font2, show='*', text_color='#fff',
                                           border_color='#004780', border_width=3,
                                           placeholder_text='Password', placeholder_text_color='#a3a3a3',
                                           width=200, height=50)
        self.password_entry.pack(side="top", padx=5, pady=10)

        self.signup_button = ctk.CTkButton(self, command=self.signup, font=self.font2, text_color='#fff',
                                           border_color='#004780',
                                           border_width=3, text='Sign In', hover_color='#006e44', cursor='hand2',
                                           corner_radius=5, width=120)
        self.signup_button.pack(side="top", padx=5, pady=10)

        self.login_label = ctk.CTkLabel(self, font=self.font3, text='Already have an account ?', text_color='#fff')
        self.login_label.pack(side="top", padx=5, pady=10)

        self.login_button = ctk.CTkButton(self, command=self.login, font=self.font4, text_color='#fff',
                                          border_color='#004780', border_width=3, text='Login',
                                          hover_color='#001220', cursor='hand2', corner_radius=5, width=40)
        self.login_button.pack(side="top", padx=5, pady=10)

class ImageImport(ctk.CTkFrame):
    def __init__(self,parent, import_func):
        super().__init__(master=parent)
        self.grid(column=0, columnspan=2, row=0, sticky='nsew')
        self.import_func = import_func

        ctk.CTkButton(self, text='Open Image', command=self.open_dialog).pack(side="top", padx=5, pady=120)


        self.dropdown_year = ctk.CTkOptionMenu(self, values = ['2012', '2013', '2014', '2015',
                                                   '2016', '2017', '2018', '2019', '2020',
                                                   '2021', '2022', '2023', '2024',
                                                   ])
        self.dropdown_year.pack(side="top", padx=5, pady=15)

        self.dropdown_month = ctk.CTkOptionMenu(self, values = ['1', '2', '3', '4', '5', '6', '7', '8',
                                                    '9', '10', '11', '12']
                                                    ,command = self.update_days)
        self.dropdown_month.pack(side="top", padx=5, pady=15)

        self.dropdown_day = ctk.CTkOptionMenu(self, values = ['1', '2', '3', '4', '5', '6', '7', '8',
                                                  '9', '10', '11', '12', '13', '14', '15', '16',
                                                  '17', '18', '19', '20', '21', '22', '23', '24',
                                                  '25', '26', '27', '28', '29', '30', '31'
                                                  ])
        self.dropdown_day.pack(side="top", padx=5, pady=15)

        ctk.CTkButton(self, text='Search', command=self.open_image).pack(side="top", padx=5, pady=10)

    def open_dialog(self):
        path = filedialog.askopenfile().name
        self.import_func(path)

    def open_image(self):
        selected_year = self.dropdown_year.get()
        selected_month = self.dropdown_month.get()
        selected_day = self.dropdown_day.get()

        image_path = f'C:\\Users\\dcorp\\PycharmProjects\\sunspots\\web_crawler' \
                     f'\\downloaded_images\\{selected_year}0{selected_month}0{selected_day}.jpg'
        if os.path.exists(image_path):
            self.import_func(image_path)
        else:
            messagebox.showerror("Error", "Image not available for this day.")


    def update_days(self, event):
        selected_month = self.dropdown_month.get()
        days = []

        if selected_month == '2':  # February
            year = int(self.dropdown_year.get())
            days = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                    '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                    '21', '22', '23', '24', '25', '26', '27', '28']
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                days.append('29')  # Leap year, February has 29 days

        elif selected_month in ['1', '3', '5', '7', '8', '10', '12']:  # Months with 31 days
            days = [str(i) for i in range(1, 32)]
        else:  # Months with 30 days
            days = [str(i) for i in range(1, 31)]
        self.dropdown_day.configure(values = days) # Set values directly

class ImageOutput(Canvas):
    def __init__(self, parent, resize_image):
        super().__init__(master=parent, background = '#242424', bd = 0, highlightthickness = 0, relief = 'ridge')
        self.grid(row=0, column=1, sticky='nsew', pady = 10, padx = 10)
        self.bind('<Configure>', resize_image)

class CloseOutput(ctk.CTkButton):
    def __init__(self, parent, close_func):
        super().__init__(master = parent,
                         command = close_func,
                         text = 'X',
                         text_color = '#FFF',
                         fg_color = 'transparent',
                         width=40,
                         height=40,
                         corner_radius = 0,
                         hover_color = 'red')
        self.place(relx = 0.99, rely = 0.01, anchor = 'ne')




