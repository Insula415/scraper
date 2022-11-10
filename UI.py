# @name         Product Scraper
# @version      5.0
# @description  User Interface for program
# @author       Ciaran Byrne


from ast import AugAssign
from numpy import multiply, tensordot


import tkinter
import tkinter.messagebox
import customtkinter
import subprocess
import os

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):

    WIDTH = 780
    HEIGHT = 520

    def __init__(self):
        global runAgain
        runAgain = False
        global path
        global newpath
        try:
            with open("chrome.txt", "r") as f:
                newpath = f.readlines()
        except:
            print("Something went wrong fetching path")
            print("Have you ran setup.py?")
            quit()
        path = ''.join(newpath)
            
        mainText = "Select options then press start"
        super().__init__()

        self.title("Product Scraper")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        # ============ create two frames ============

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 width=180,
                                                 corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # ============ frame_left ============

        # configure grid layout (1x11)
        self.frame_left.grid_rowconfigure(0, minsize=10)   # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(5, weight=1)  # empty row as spacing
        self.frame_left.grid_rowconfigure(8, minsize=20)    # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(11, minsize=10)  # empty row with minsize as spacing

        self.label_1 = customtkinter.CTkLabel(master=self.frame_left,
                                              text="Product Scraper",
                                              text_font=("Roboto Medium", -16))  # font name and size in px
        self.label_1.grid(row=1, column=0, pady=10, padx=10)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Start",
                                                command=self.start_event)
        self.button_1.grid(row=2, column=0, pady=10, padx=20)

        self.button_3 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Run again",
                                                command=self.run_again)
        self.button_3.grid(row=4, column=0, pady=10, padx=20)

        self.button_4 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Exit",
                                                command=self.on_closing)
        self.button_4.grid(row=5, column=0, pady=10, padx=20)

        # ============ frame_right ============

        # configure grid layout (3x7)
        self.frame_right.rowconfigure((0, 1, 2, 3), weight=1)
        self.frame_right.rowconfigure(7, weight=10)
        self.frame_right.columnconfigure((0, 1), weight=1)
        self.frame_right.columnconfigure(2, weight=0)

        self.frame_info = customtkinter.CTkFrame(master=self.frame_right)
        self.frame_info.grid(row=0, column=0, columnspan=2, rowspan=4, pady=20, padx=20, sticky="nsew")

        # ============ frame_info ============

        # configure grid layout (1x1)
        self.frame_info.rowconfigure(0, weight=1)
        self.frame_info.columnconfigure(0, weight=1)
 
        self.label_info_1 = customtkinter.CTkLabel(master=self.frame_info,
                                                   text=mainText,
                                                   height=100,
                                                   corner_radius=6,  # <- custom corner radius
                                                   fg_color=("white", "gray38"),  # <- custom tuple-color
                                                   justify=tkinter.LEFT)
        self.label_info_1.grid(column=0, row=0, sticky="nwe", padx=15, pady=15)


        # ============ frame_right ============

        self.radio_var = tkinter.IntVar(value=0)

        self.label_radio_group = customtkinter.CTkLabel(master=self.frame_right,
                                                        text="Options:")
        self.label_radio_group.grid(row=0, column=2, columnspan=1, pady=20, padx=10, sticky="")

        self.combobox_4 = customtkinter.CTkComboBox(master=self.frame_right,
                                                    values=["Not signed in", "Already signed in"],
                                                    command=self.signed)
        self.combobox_4.grid(row=5, column=2, pady=10, padx=20, sticky="we")

        self.combobox_3 = customtkinter.CTkComboBox(master=self.frame_right,
                                                    values=["Manually add prices", "Multiply prices", "Add to prices"],
                                                    command=self.prices)
        self.combobox_3.grid(row=3, column=2, pady=10, padx=20, sticky="we")

        self.entry = customtkinter.CTkEntry(master=self.frame_right,
                                            width=120,
                                            placeholder_text="Amount")
        self.entry.grid(row=4, column=2, columnspan=2, pady=20, padx=20, sticky="we")


        self.combobox_2 = customtkinter.CTkComboBox(master=self.frame_right,
                                                    values=["No discount", "Discount 10%","Discount 30%", "Discount 50%"],
                                                    command=self.discounts)
        self.combobox_2.grid(row=2, column=2, pady=10, padx=20, sticky="we")
        

        self.combobox_1 = customtkinter.CTkComboBox(master=self.frame_right,
                                                    values=["Publish products","Don't publish products"],
                                                    command=self.publishProd)
        self.combobox_1.grid(row=1, column=2, pady=10, padx=20, sticky="we")

        self.button_2 = customtkinter.CTkButton(master=self.frame_right,
                                                text="Save options",
                                                command=self.save)
        self.button_2.grid(row=6, column=2, pady=10, padx=20, sticky="we")

        

        # set default values
        self.combobox_4.set("Please select")
        self.combobox_3.set("Please select")
        self.combobox_2.set("Please select")
        self.combobox_1.set("Please select")
        

    def signed(self, x):
        self.title("Product Scraper")
        self.geometry("400x400")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        global isSignedIn
        if x == "Already signed in":
            isSignedIn = "true"
        else:
            isSignedIn = "false"

    def prices(self, x):
        global price
        if x == "Manually add prices":
            price = "Manual"
        elif x == "Multiply prices":
            price = "Multiply"
        elif x == "Add to prices":
            price = "Add"

    def discounts(self, x):
        global discount
        if x == "No discount":
            discount = 0
        elif x == "Discount 10%":
            discount = 10
        elif x == "Discount 30%":
            discount = 30
        elif x == "Discount 50%":
            discount = 50

    def publishProd(self, x):
        global publish
        if x == "Publish products":
            publish = "TRUE"
        else:
            publish = "FALSE"

    def save(self):
        text = self.entry.get()
        if text:
            None
        else:
            text = "None"
        print("Saving user options")
        savedopts = path + "/saved_options.txt"
        with open(f"{savedopts}", "w") as f:
            f.writelines([str(isSignedIn),"\n", str(price),"\n", str(text),"\n", str(discount),"\n", str(publish)])
            f.close()

    def start_event(self):
        text = self.entry.get()
        if text:
            None
        else:
            text = "None"
        savedopts = path + "/saved_options.txt"
        opts = path + "/options.txt"
        if os.path.exists(f"{savedopts}"):
            print("Saved options exist")
        else:        
            try:
                with open(f"{opts}", "w") as f:
                    f.writelines([str(isSignedIn),"\n", str(price),"\n", str(text),"\n", str(discount),"\n", str(publish)])
                    f.close()
            except:
                with open(f"{opts}", "w") as f:
                    f.writelines(["true","\n", "Add","\n","10","\n","0","\n", "TRUE"])
                    f.close()
                print("Default options applied")

        mainText = "Starting..."
        self.label_info_1 = customtkinter.CTkLabel(master=self.frame_info,
                                                   text=mainText,
                                                   height=100,
                                                   corner_radius=6,  # <- custom corner radius
                                                   fg_color=("white", "gray38"),  # <- custom tuple-color
                                                   justify=tkinter.LEFT)
        self.label_info_1.grid(column=0, row=0, sticky="nwe", padx=15, pady=15)
        self.destroy()
        subprocess.run(['py','start.py'])
        quit()

    def run_again(self): 
        run = path + "/runagain.txt"
        with open(f"{run}", "w") as f:
            f.close()
        self.destroy()
        subprocess.run(['py','main.py'])
        quit()     

    def on_closing(self, event=0):
        run = path + "/runagain.txt"
        if os.path.exists(f"{run}"):
            os.remove(f"{run}")
        else:
            None
        self.destroy()


    def main():
        print("main area")

if __name__ == "__main__":
    app = App()
    app.mainloop()