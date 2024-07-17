import os.path
import tkinter as tk
import tkinter.ttk as ttk
import re
import customtkinter
import matplotlib.pyplot as plt
import numpy as np
import cv2
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime as dt
from ComputeSunspots.detector import return_sunspots_image
from GUI.image_widgets import *
from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageFilter
from GUI.menu import Menu, ExportFrame, Menu2
from GUI.settings import *
from web_crawler.graphs import *
from pathlib import Path

class App(ctk.CTk):
    def __init__(self):
        # Setup
        super().__init__()
        self.current_email = None
        self.current_name = None
        ctk.set_appearance_mode('dark')
        self.geometry('1500x800')
        self.title('SunSpots')
        self.minsize(800, 500)
        self.init_parameters()
        # Layout
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=2, uniform = 'a')
        self.columnconfigure(1, weight= 6, uniform = 'a')
        self.a = self.a = A(self, self.handle_login_result)
        # canvas data
        self.image_width = 0
        self.image_height = 0
        self.canvas_width = 0
        self.canvas_height = 0
        #widgets
        self.image_import = ImageImport(self, self.import_image)
        self.a = A(self, self.handle_login_result)
        #run
        self.mainloop()

    def handle_login_result(self, current_email, current_name):
        # Do something with the result in the GUI
        self.current_email = current_email
        self.current_name = current_name
        print("Login result:", self.current_email, current_name)

    def set_image_import(self, image_import_widget):
        """Set the image import widget."""
        self.image_import = image_import_widget

    def init_parameters(self):
        self.pos_vars = {
            'rotate': ctk.DoubleVar(value = 0),
            'zoom': ctk.DoubleVar(value = 0),
            'flip': ctk.StringVar(value= FLIP_OPTIONS[0])
        }

        self.colour_vars = {
            'brightness': ctk.DoubleVar(value=1),
            'grayscale': ctk.BooleanVar(value=False),
            'invert': ctk.BooleanVar(value=False),
            'vibrance': ctk.DoubleVar(value=1),
        }

        self.effect_vars = {
            'blur': ctk.DoubleVar(value=0),
            'contrast': ctk.IntVar(value=0),
            'effect': ctk.StringVar(value=EFFECT_OPTIONS[0]),

        }

        combined_vars = list(self.pos_vars.values()) + list(self.colour_vars.values()) + list(self.effect_vars.values())

        for var in combined_vars:
            var.trace('w', self.manipulate_image)
    def manipulate_image(self, *args):
        self.image = self.original

        #rotate
        if self.pos_vars['rotate'].get() != 0:
            self.image = self.image.rotate(self.pos_vars['rotate'].get())

        #zoom
        if self.pos_vars['zoom'].get() != 0:
            self.image = ImageOps.crop(image = self.image, border = self.pos_vars['zoom'].get())

        #flip
        if self.pos_vars['flip'].get() != 'None':
            if self.pos_vars['flip'].get() == 'X':
                self.image = ImageOps.mirror(self.image)
            if self.pos_vars['flip'].get() == 'Y':
                self.image = ImageOps.flip(self.image)
            if self.pos_vars['flip'].get() == 'Both':
                self.image = ImageOps.mirror(self.image)
                self.image = ImageOps.flip(self.image)

        #brightness and vibrance
        if self.colour_vars['brightness'].get() != 1:
            brightness_enhancer = ImageEnhance.Brightness(self.image)
            self.image = brightness_enhancer.enhance(self.colour_vars['brightness'].get())
        if self.colour_vars['vibrance'].get() != 1:
            vibrance_enhancer = ImageEnhance.Color(self. image)
            self.image = vibrance_enhancer.enhance(self.colour_vars['vibrance'].get())

        #colours
        if self.colour_vars['grayscale'].get():
            self.image = ImageOps.grayscale(self.image)
        if self.colour_vars['invert'].get():
            self.image = ImageOps.invert(self.image)

        #blur and contrast
        if self.effect_vars['blur'].get() != False:
            self.image =self.image.filter(ImageFilter.GaussianBlur(self.effect_vars['blur'].get()))
        if self.effect_vars['contrast'].get() != False:
            self.image = self.image.filter(ImageFilter.UnsharpMask(self.effect_vars['contrast'].get()))
        match self.effect_vars['effect'].get():
            case 'Emboss': self.image = self.image.filter(ImageFilter.EMBOSS)
            case 'Find edges': self.image = self.image.filter(ImageFilter.FIND_EDGES)
            case 'Contour': self.image = self.image.filter(ImageFilter.CONTOUR)
            case 'Edge enhance': self.image = self.image.filter(ImageFilter.EDGE_ENHANCE_MORE)

        self.place_image()

    def import_image(self, path_or_image):
        if isinstance(path_or_image, str):
            # If the input is a string, assume it's a file path
            self.original = Image.open(path_or_image)
        else:
            # If the input is not a string, assume it's already an image
            self.original = path_or_image

        self.image = self.original
        self.image_ratio = self.image.size[0] / self.image.size[1]
        self.image_tk = ImageTk.PhotoImage(self.image)

        self.image_import.grid_forget()
        self.image_output = ImageOutput(self, self.resize_image)
        self.close_button = CloseOutput(self, self.close_edit)
        self.menu = Menu(self, self.pos_vars, self.colour_vars, self.effect_vars, path_or_image, self.export_image)
        self.sunspots_button = Sunspots(self, path_or_image, self.current_email)
        self.sunspots_button.grid(row=1, column=0, sticky='nwes', padx=10, pady=30)

        self.label_text = 'Hello, ' + self.current_name + ' !'
        font = ('Helvetica', 25, 'bold')
        self.name_label = ctk.CTkLabel(self, text = self.label_text, font = font )
        self.name_label.grid(row=1, column=1, sticky='e', padx=100, pady=30)
        self.logout_button = ctk.CTkButton(self, text='Log Out',command=self.log_out)
        self.logout_button.grid(row=1, column=1, sticky='w', padx=100, pady = 30)


    def close_edit(self):
        #hide the image and the button
        self.image_output.grid_forget()
        self.close_button.place_forget()
        self.sunspots_button.grid_forget()
        #recreate import button
        self.menu.grid_forget()
        self.image_import = self.image_import = ImageImport(self, self.import_image)
        self.sunspots_button.close_window()
        self.logout_button.grid_forget()

    def destroy_widgets(self):
        # Iterate through all widgets and destroy them
        for widget in self.winfo_children():
            widget.destroy()

    def resize_image(self, event):

        #curent canvas ratio
        canvas_ratio = event.width / event.height
        #update canvas attributes
        self.canvas_width = event.width
        self.canvas_height = event.height
        #resize
        if canvas_ratio > self.image_ratio:
            self.image_height = int(event.height)
            self.image_width = int(self.image_height * self.image_ratio)
        else: # taller
            self.image_width = int(event.width)
            self.image_height = int(self.image_width / self.image_ratio)

        self.place_image()

    def place_image(self):
        self.image_output.delete('all')
        resized_image = self.image.resize((self.image_width, self.image_height))
        self.image_tk = ImageTk.PhotoImage(resized_image)
        self.image_output.create_image(self.canvas_width / 2, self.canvas_height / 2, image = self.image_tk)

    def export_image(self, name, file, path):
        export_string = f'{path}/{name}.{file}'
        self.image.save(export_string)


def apply_dark_theme():
    custom_style = ttk.Style()
    custom_style.theme_use('clam')
    custom_style.configure('.', background='#1e1e1e', foreground='dark', font=('Arial', 10, 'normal'))


class Sunspots(ctk.CTkFrame):
    def __init__(self, parent, path, current_user, default=None):
        super().__init__(master=parent)
        self.sunspots_button = ctk.CTkButton(self, text='Find Sunspots', command=self.display_sunspots)
        self.sunspots_button.grid(row=1, column=0, sticky='nwes', padx=10, pady=30)
        self.cursor = None
        self.conn = None
        self.path = path
        self.spots_image = default
        self.new_window = None
        self.year = None
        self.month = None
        self.image_position = (0, 0)
        self.zoom_factor = 1.0
        self.current_user = current_user
        date_match = re.search(r'(\d{4})(\d{2})(\d{2})', self.path)
        if date_match:
            year, month, day = date_match.groups()
            year = str(year)
            month = str(month)
            day = str(day)
            self.date = year + '-' + month + '-' + day
        else:
            today = dt.date.today()
            self.date = today.strftime("%Y-%m-%d")
            self.date = self.date + '-custom'

        self.current_box = None
        self.start_x = None
        self.start_y = None
        self.moved_by_click = False

    def get_button(self):
        return self.sunspots_button

    def move_image(self, direction, canvas):
        x, y = self.image_position
        if direction == "up":
            y -= 10
            self.image_position = (x, y - 10)
        elif direction == "down":
            y += 10
            self.image_position = (x, y + 10)
        elif direction == "left":
            x -= 10
            self.image_position = (x - 10, y)
        elif direction == "right":
            x += 10
            self.image_position = (x + 10, y)

        if self.moved_by_click:
            self.resize_move(canvas,self.spots_image, x, y)
        else:
            self.resize_image(canvas, self.spots_image, x, y)


    def compute_wolf_number(self):
        k_input = self.textbox.get("1.0", "end-1c")
        Wolf_number = None
        k = None
        # Check if the input is the default placeholder text
        if k_input == "Input here k parameter. k = 1 by default":
            k = 1  # Set default value
            wolf_number = k * (10 * int(self.nr_of_groups) + int(self.total))
            string_wolf_number = str(wolf_number)
            self.textbox.delete("0.0", "end")
            self.textbox.insert("0.0", "The Wolf number is: " + string_wolf_number)
            Wolf_number = string_wolf_number

        elif re.match(r'^[\d.]+$', k_input):
            try:
                k = float(k_input)  # Convert input to float
            except ValueError:
                # Handle cases where the input cannot be converted to float
                print("Invalid input for k. Using default value.")

            wolf_number = k * (10 * int(self.nr_of_groups) + int(self.total))
            string_wolf_number = str(int(wolf_number))
            self.textbox.delete("0.0", "end")
            self.textbox.insert("0.0", "The Wolf number is: "+string_wolf_number)
            Wolf_number = string_wolf_number
        else:
            self.textbox.delete("0.0", "end")
            self.textbox.insert("0.0", "Invalid input, please input a Real Number ")

        if Wolf_number:
            self.conn = sqlite3.connect('users.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute('INSERT INTO analyses (user_email, date, k_value, wolf_number) VALUES (?,?,?,?) ', [ self.current_user, k, self.date, wolf_number])
            self.conn.commit()

        self.cursor.execute('SELECT * FROM analyses')
        data = self.cursor.fetchall()
        messagebox.showinfo('All calculations', data)

    def display_analyses(self):
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('SELECT * FROM analyses')
        data = self.cursor.fetchall()
        # Format and display data
        formatted_data = ""
        for row in data:
            formatted_data += "Analysis ID: {}\n".format(row[0])
            formatted_data += "User: {}\n".format(row[1])
            formatted_data += "Date: {}\n".format(row[3])
            formatted_data += "k value: {}\n".format(row[2])
            formatted_data += "Wolf number: {}\n\n".format(row[4])

        root = tk.Tk()
        root.wm_attributes("-topmost", 1)
        root.withdraw()
        tk.messagebox.showinfo('Database Contents', formatted_data, parent=root)
        root.destroy()

    def zoom_inside(self):
        self.zoom_factor *= 1.1
        # Redraw the image with the new zoom factor
        x, y = self.image_position
        if self.moved_by_click:
            self.resize_image_click(x, y)
            self.image_position = (x, y)
        else:
            self.image_position = (x, y)
            self.resize_image(self.canvas, self.spots_image, x, y)

    def zoom_outside(self):
        if self.moved_by_click:
            if (self.zoom_factor / 1.1) > 0.1:
                self.zoom_factor /= 1.1
            x, y = self.image_position

            self.resize_image_click(x, y)
            self.image_position = (x, y)
        else:
            if (self.zoom_factor / 1.1) > 0.1:
                self.zoom_factor /= 1.1
            x, y = self.image_position

            self.image_position = (x, y)
            self.resize_image(self.canvas, self.spots_image, x, y)

    def move(self, event):
        self.canvas.create_image(event.x,event.y, anchor = tk.NW, image = self.spots_image)

    def display_sunspots(self):
        image = cv2.imread(self.path)
        self.spots_image, groups, self.total, self.nr_of_groups, self.grouped_boxes = return_sunspots_image(image)
        new_groups=''
        apply_dark_theme()
        for group in groups:
            for key, value in group.items():
                new_groups = new_groups + str(key)+ " " + str(value) + "  :  "
            new_groups = new_groups[:-3]
            new_groups = new_groups  +'\n'

        new_groups = new_groups[:-1]
        self.new_window = ctk.CTkToplevel(self.master)
        self.new_window.title("Sunspots Image")
        self.new_window.geometry("1350x1000")

        self.new_window.maxsize(1350, 1000)
        self.new_window.minsize(1350, 1000)

        self.new_window.attributes("-topmost", 1)

        self.new_window.rowconfigure(0, weight=1)
        self.new_window.columnconfigure(0, weight=2, uniform='a')
        self.new_window.columnconfigure(1, weight=6, uniform='a')


        save_button = ctk.CTkButton(self.new_window, text="Save Image", command=self.save)
        save_button.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        dropdown_year = DropDownPanel2(self.new_window, [ '2012', '2013', '2014', '2015',
                                                         '2016', '2017', '2018', '2019', '2020',
                                                         '2021', '2022', '2023', '2024',
                                                         ])
        dropdown_month = DropDownPanel2(self.new_window, ['Per Year', '1', '2', '3', '4',
                                                          '5', '6', '7', '8',
                                                          '9', '10', '11', '12',
                                                          ])
        dropdown_year.grid(row=0, column=0, padx=5, pady=170, sticky="nw")
        dropdown_month.grid(row=0, column=0, padx=5, pady=170, sticky="ne")

        textframe = customtkinter.CTkScrollableFrame(self.new_window, width=100, height = 20)
        textframe.grid(row=0, column=0, padx=30, pady=230, sticky="nwe")

        label_text = ctk.CTkLabel(textframe, text=new_groups, pady=20)
        label_text.pack()

        self.textbox = ctk.CTkTextbox(self.new_window, width=100, height = 10)
        self.textbox.grid(row=0, column=0 , padx=30, pady=450, sticky="nwe")
        self.textbox.insert("0.0", "Input here k parameter. k = 1 by default")

        wolf_number = ctk.CTkButton(self.new_window, text=" Get Wolf number", command=self.compute_wolf_number)
        wolf_number.grid(row=0, column=0, padx=30, pady=480, sticky="swe")

        move_up_button = ctk.CTkButton(self.new_window, text="Move Down", command=lambda: self.move_image("up", self.canvas))
        move_up_button.grid(row=0, column=0, padx=0, pady=400, sticky="s")

        move_down_button = ctk.CTkButton(self.new_window, text="Move Up", command=lambda: self.move_image("down", self.canvas))
        move_down_button.grid(row=0, column=0, padx=0, pady=300, sticky="s")

        move_left_button = ctk.CTkButton(self.new_window, text="Move Left", command=lambda: self.move_image("left", self.canvas))
        move_left_button.grid(row=0, column=0, padx=10, pady=350, sticky="sw")

        move_right_button = ctk.CTkButton(self.new_window, text="Move Right", command=lambda: self.move_image("right", self.canvas))
        move_right_button.grid(row=0, column=0, padx=10, pady=350, sticky="se")

        zoom_in_button = ctk.CTkButton(self.new_window, text="Zoom In", command = self.zoom_inside)
        zoom_in_button.grid(row=0, column=0, padx=10, pady=240, sticky="s")

        zoom_out_button = ctk.CTkButton(self.new_window, text="Zoom Out", command = self.zoom_outside)
        zoom_out_button.grid(row=0, column=0, padx=10, pady=200, sticky="s")

        plot_button = ctk.CTkButton(self.new_window, text="Show Plot", command=lambda: show_plot_wrapper(self))
        plot_button.grid(row=0, column=0, padx=10, pady=50, sticky="n")

        move_right_button = ctk.CTkButton(self.new_window, text="Display calculations",
                                          command=self.display_analyses)
        move_right_button.grid(row=0, column=0, padx=10, pady=150, sticky="s")

        def show_plot_wrapper(self):
            data_folder_path = (Path(__file__) / '../../web_crawler').resolve()
            csv_file = data_folder_path / 'scraped_data.csv'
            date, spots = read_data(csv_file)
            self.year = int(dropdown_year.get())

            self.month = dropdown_month.get()

            if self.month == 'Per Year':
                self.show_plot_year(date, spots, self.year)
            else:
                self.show_plot_month(date, spots, self.year, self.month)

        reverse_button = ctk.CTkButton(self.new_window, text="Exit Plot", command = self.reverse_plot)
        reverse_button.grid(row=0, column=0, padx=10, pady=90, sticky="n")

        self.canvas = tk.Canvas(self.new_window, bg='#1E1E1E')

        self.canvas.grid(row=0, column=1, sticky='nsew')

        self.new_window.image = self.spots_image

        self.canvas.bind("<Configure>", lambda event, x=0, y=0: self.resize_image(self.canvas, self.spots_image, x, y))

        self.canvas.bind("<ButtonPress-1>", self.search_group)

        self.canvas.bind("<B1-Motion>", self.move_click)

        self.canvas.bind("<MouseWheel>", self.zoom_click)

    def scale_coordinates(self, coord):
        original_width = 4096
        original_height = 4096

        target_width = 1024
        target_height = 1024

        scale_x = target_width / original_width
        scale_y = target_height / original_height

        scaled_coord = [int(coord[0] * scale_x), int(coord[1] * scale_y), int(coord[2] * scale_x),
                        int(coord[3] * scale_y)]
        return scaled_coord

    def search_group(self,event):
        x, y = event.x, event.y
        self.start_x = x
        self.start_y = y

        scaled_boxes = [self.scale_coordinates(box) for box in self.grouped_boxes]

        for i, box in enumerate(scaled_boxes):
            x1, y1, x2, y2 = box
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.current_box = i
                break

    def move_click(self, *args):
        x = args[0].x
        y = args[0].y
        self.moved_by_click = True
        self.image_position = (x, y)
        self.resize_image_click(x, y)


    def zoom_click(self, event):
        direction = event.delta

        if direction > 0:
            self.zoom_factor *= 1.1
            x, y = self.image_position
            self.resize_image_click(x, y)
            self.image_position = (x, y)
        else:
            if (self.zoom_factor / 1.1) > 0.1:
                self.zoom_factor /= 1.1
            x, y = self.image_position
            self.resize_image_click(x, y)
            self.image_position = (x, y)

    def resize_image_click(self, x, y):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        canvas_width = int(canvas_width * self.zoom_factor)
        canvas_height = int(canvas_height * self.zoom_factor)

        resized_image = cv2.resize(self.spots_image, (canvas_width, canvas_height))
        pil_image = Image.fromarray(resized_image)
        tk_image = ImageTk.PhotoImage(pil_image)

        self.canvas.delete("all")
        self.canvas.create_image(x, y, image=tk_image)
        self.canvas.image = tk_image

    def resize_image_zoom(self, x, y):
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()

        self.canvas_width = int(self.canvas_width * self.zoom_factor)
        self.canvas_height = int(self.canvas_height * self.zoom_factor)

        resized_image = cv2.resize(self.spots_image, (self.canvas_width, self.canvas_height))
        pil_image = Image.fromarray(resized_image)
        tk_image = ImageTk.PhotoImage(pil_image)

        self.canvas.delete("all")
        self.canvas.create_image(x, y, image=tk_image)
        self.canvas.image = tk_image


    def scroll_start(self, event):
        position = float(event.x) / self.hbar.winfo_width()
        self.hbar.set(position, position + 0.1)  # Set the first and last positions

    def scroll_move(self, event):
        position = float(event.x) / self.hbar.winfo_width()
        self.hbar.set(position, position + 0.1)  # Set the first and last positions


    def resize_image(self, canvas, image, x, y):
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        canvas_width = int(canvas_width * self.zoom_factor)
        canvas_height = int(canvas_height * self.zoom_factor)

        resized_image = cv2.resize(image, (canvas_width, canvas_height))
        pil_image = Image.fromarray(resized_image)
        tk_image = ImageTk.PhotoImage(pil_image)

        canvas.delete("all")
        canvas.create_image(x, y, anchor=tk.NW, image=tk_image)
        canvas.image = tk_image

    def resize_move(self, canvas, image, x, y):
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        canvas_width = int(canvas_width * self.zoom_factor)
        canvas_height = int(canvas_height * self.zoom_factor)

        resized_image = cv2.resize(image, (canvas_width, canvas_height))
        pil_image = Image.fromarray(resized_image)
        tk_image = ImageTk.PhotoImage(pil_image)

        canvas.delete("all")
        canvas.create_image(x, y, anchor=tk.CENTER, image=tk_image)
        canvas.image = tk_image

    def save(self):
        if self.spots_image.any():
            self.new_window.attributes("-topmost", False)
            self.new_window.grab_set()
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")])

            self.new_window.grab_release()

            if file_path:
                cv2.imwrite(file_path, self.spots_image)
                print("Image saved successfully.")
        else:
            print("No image to save.")

    def show_plot_year(self, date, spots, year):
        if self.new_window:
            if hasattr(self.new_window, "plot_canvas"):
                self.update_plot()
            else:
                fig = plt.figure()
                d = []
                s = []
                for dt, spot in zip(date, spots):
                    data_year, data_month, data_day = dt
                    if data_year == year:
                        if spot.strip():
                            date_obj = datetime(data_year, data_month, data_day)
                            d.append(date_obj)
                            s.append(int(spot))
                plt.plot(d, s)
                plt.xlabel("Date", color='orange', fontsize=14)
                plt.ylabel("Total Number of Spots", color='orange', fontsize=14)
                plt.title("Total Number of Spots per Year", color='orange', fontsize=14)
                plt.gcf().set_size_inches(10, 6)
                plt.gcf().set_facecolor('#1E1E1E')
                plt.gca().set_facecolor('#1E1E1E')
                plt.grid(color='purple')
                plt.tick_params(axis='both', colors='orange')
                plt.legend(['Data'], loc='upper left', facecolor='lightblue')

                canvas = self.new_window.children["!canvas"]
                canvas.delete("all")

                plot_canvas = FigureCanvasTkAgg(fig, master=canvas)
                plot_canvas.draw()
                plot_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

                self.new_window.plot_canvas = plot_canvas

                toolbar = NavigationToolbar2Tk(plot_canvas, canvas)
                toolbar.update()
                plot_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        else:
            print("Please open the Sunspots window first.")

    def show_plot_month(self, date, spots, year, month):

        if self.new_window:

            if hasattr(self.new_window, "plot_canvas"):
                self.update_plot()
            else:
                fig = plt.figure()
                d = []
                s = []
                for dt, spot in zip(date, spots):
                    data_year, data_month, data_day = dt
                    if data_year == year and data_month == int(month):
                        d.append(data_day)
                        s.append(spot)
                ss = [int(x) for x in s]
                plt.plot(np.array(d), np.array(ss))
                plt.xlabel("Date", color='orange', fontsize=14)
                plt.ylabel("Total Number of Spots", color='orange', fontsize=14)
                plt.title("Total Number of Spots per Month", color='orange', fontsize=14)
                plt.gcf().set_size_inches(10, 6)
                plt.gcf().set_facecolor('#1E1E1E')
                plt.gca().set_facecolor('#1E1E1E')
                plt.grid(color='purple')
                plt.tick_params(axis='both', colors='orange')
                plt.legend(['Data'], loc='upper left', facecolor='lightblue')

                canvas = self.new_window.children["!canvas"]
                canvas.delete("all")

                plot_canvas = FigureCanvasTkAgg(fig, master=canvas)
                plot_canvas.draw()
                plot_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

                self.new_window.plot_canvas = plot_canvas

                toolbar = NavigationToolbar2Tk(plot_canvas, canvas)
                toolbar.update()
                plot_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        else:
            print("Please open the Sunspots window first.")

    def update_plot(self):
        self.new_window.plot_canvas.draw()

    def reverse_plot(self):
        self.moved_by_click = False
        if hasattr(self.new_window, "plot_canvas"):
            self.new_window.plot_canvas.toolbar.forget()
            self.new_window.plot_canvas.get_tk_widget().forget()
            delattr(self.new_window, "plot_canvas")
            self.resize_image(self.canvas, self.spots_image, 0, 0)
        else:
            self.canvas.delete('all')
            self.image_position = (0, 0)
            self.zoom_factor = 1.0
            self.canvas_width = self.canvas.winfo_width()
            self.canvas_height = self.canvas.winfo_height()
            self.resize_image(self.canvas, self.spots_image, 0, 0)

    def close_window(self):
        if self.new_window:
            self.new_window.destroy()

