from tkinter import *
import customtkinter as ctk
from tkinter import filedialog
from run import ContactConverter


# Set Theme
ctk.set_appearance_mode("light")
ctk.set_widget_scaling(1.25)
ctk.set_window_scaling(1.5)

class TextFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # Frame Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)
        
        # Header of Application
        self.header = ctk.CTkLabel(self, text="Stock & Associates - Contact Management Application", font=("Aptos", 18))
        self.header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.header.configure(state='disabled')
        
        self.text = ctk.CTkLabel(self, wraplength=500, text="Welcome to the Stock & Associates Contact Management Application.\nPlease upload the SigParser file to update the Database.", font=("Aptos", 14))
        self.text.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.text.configure(state='disabled')


class ButtonFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # Frame Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)
        
        # File upload button
        self.button = ctk.CTkButton(self, text="Upload File", command=self.file_upload)
        self.button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Exit button
        self.button = ctk.CTkButton(self, text_color='white', text="Exit", fg_color='#b22222', hover_color='darkgray', command=self.on_close)
        self.button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
                    
    def file_upload(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                converter = ContactConverter(csv_file=file_path, json_file='StockContacts.json')
                converter.run()  # Run the conversion process
                print("File processed successfully")
            except Exception as e:
                print(f'Error: {e}')
    
    def on_close(self):
        self.quit()
        self.destroy()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure Window
        self.title("Stock & Associates - Contact Management Application")
        self.geometry("500x300")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)
        
        self.text_frame = TextFrame(master=self)
        self.text_frame.grid(padx=20, pady=20, sticky="ew")
        
        self.button_frame = ButtonFrame(master=self)
        self.button_frame.grid(padx=20, pady=20, sticky="ew")
        



if __name__ == "__main__":
    app = App()
    app.mainloop()