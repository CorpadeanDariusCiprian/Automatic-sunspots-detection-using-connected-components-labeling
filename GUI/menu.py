import customtkinter as ctk
from GUI.panels import *
from GUI.settings import *

class Menu(ctk.CTkTabview):
    def __init__(self, parent, pos_vars, colour_vars, effect_vars, path, export_image):
        super().__init__(master = parent)
        self.grid(column = 0, row = 0, sticky ='nsew', pady = 10, padx = 10)

        #tabs
        self.add('Position')
        self.add('Colour')
        self.add('Effects')
        self.add('Export')


        #widgets
        PositionFrame(self.tab('Position'), pos_vars)
        ColourFrame(self.tab('Colour'), colour_vars)
        EffectsFrame(self.tab('Effects'), effect_vars)
        ExportFrame(self.tab('Export'), export_image)


class Menu2(ctk.CTkTabview):
    def __init__(self, parent, export_image):
        super().__init__(master = parent)
        self.grid(column = 0, row = 0, sticky ='nsew', pady = 10, padx = 10)

        #tabs
        self.add('Export')
        self.add('Sunspots')
        #widgets
        SaveFrame(self.tab('Export'), export_image) #export image is a function
        SunspotsFrame(self.tab('Sunspots'))

class PositionFrame(ctk.CTkFrame):
    def __init__(self, parent, pos_vars):
        super().__init__(master=parent, fg_color= 'transparent')
        self.pack(expand=True, fill='both')

        SliderPanel(self, 'Rotation', pos_vars['rotate'], 0, 360)
        SliderPanel(self, 'Zoom', pos_vars['zoom'], 0, 1000)
        SegmentedPanel(self, 'Invert', pos_vars['flip'], FLIP_OPTIONS)
        RevertButton(self,
                     (pos_vars['rotate'], 0),
                     (pos_vars['zoom'], 0),
                     (pos_vars['flip'], 'None'),
                     )

class ColourFrame(ctk.CTkFrame):
    def __init__(self, parent, colour_vars):
        super().__init__(master=parent, fg_color= 'transparent')
        self.pack(expand=True, fill='both')

        SliderPanel(self, 'Brightness', colour_vars['brightness'], 0, 5)
        SliderPanel(self, 'Vibrance', colour_vars['vibrance'], 0, 5)

        SwitchPanel(self, (colour_vars['grayscale'], 'Black/White'), (colour_vars['invert'], 'Invert'))
        RevertButton(self,
                     (colour_vars['brightness'], 1),
                     (colour_vars['grayscale'], False),
                     (colour_vars['invert'], False),
                     (colour_vars['vibrance'], 1),
                     )

class EffectsFrame(ctk.CTkFrame):
    def __init__(self, parent, effect_vars):
        super().__init__(master=parent, fg_color= 'transparent')
        self.pack(expand=True, fill='both')

        SliderPanel(self, 'Blur', effect_vars['blur'], 0, 5)
        SliderPanel(self, 'Contrast', effect_vars['contrast'], 0, 10)

        DropDownPanel(self, effect_vars['effect'], EFFECT_OPTIONS)
        RevertButton(self,
                     (effect_vars['blur'], 0),
                     (effect_vars['contrast'], 0),
                     (effect_vars['effect'], 'None'),
                     )


class SunspotsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        #print(path)
        super().__init__(master=parent, fg_color= 'transparent')
        self.pack(expand=True, fill='both')



class ExportFrame(ctk.CTkFrame):
    def __init__(self, parent, export_image):
        super().__init__(master=parent, fg_color= 'transparent')
        self.pack(expand = True, fill = 'both')

        #data
        self.name_string = ctk.StringVar()
        self.file_string = ctk.StringVar(value = 'jpg')
        self.path_string = ctk.StringVar()
        #widgets
        FileNamePanel(self, self.name_string, self.file_string)
        FilePathPanel(self, self.path_string)
        SaveButton(self, export_image, self.name_string, self.file_string, self.path_string)


class SaveFrame(ctk.CTkFrame):
    def __init__(self, parent, export_image):
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both')

        # data
        self.name_string = ctk.StringVar()
        self.file_string = ctk.StringVar(value='jpg')
        self.path_string = ctk.StringVar()
        # widgets
        FileNamePanel(self, self.name_string, self.file_string)
        FilePathPanel(self, self.path_string)
        SaveButton(self, export_image, self.name_string, self.file_string, self.path_string)
