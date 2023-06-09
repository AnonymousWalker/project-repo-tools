import tkinter as tk
from tkinter import filedialog
import usfm.tstudio2rc as convert_script
import subprocess
import platform

input_file = None
output_dir = None

def browse_file():
    status_label.config(text="")
    open_output_button.pack_forget()
    filetypes = (("BTT Writer file", "*.tstudio"), ("All files", "*.*"))
    file_path = filedialog.askopenfilename(filetypes=filetypes)
    if file_path:
        global input_file
        input_file = file_path
        file_entry.delete(0, tk.END)
        file_entry.insert(tk.END, file_path)

def browse_directory():
    status_label.config(text="")
    open_output_button.pack_forget()
    directory_path = filedialog.askdirectory()
    if directory_path:
        global output_dir
        output_dir = directory_path
        directory_entry.delete(0, tk.END)
        directory_entry.insert(tk.END, directory_path)

def convert():
    if (file_entry.get() != '' and directory_entry.get() != ''):
        global input_file
        global output_dir
        input_file = file_entry.get().replace('\\', '/').replace('\"', '')
        output_dir = directory_entry.get().replace('\\', '/').replace('\"', '')
        try:
            convert_script.convert(input_file, output_dir)
            open_output_button.pack(pady=5)
            status_label.config(text="Conversion completed!")
            print("Done!")
        except:
            status_label.config(text="Failed!")
    else:
        status_label.config(text="Fields are required!")

def open_directory():
    global output_dir
    print(output_dir)
    if output_dir:
        if platform.system() == 'Windows':
            subprocess.Popen(str.format(r'explorer "{}"', output_dir.replace('/', '\\')))
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', output_dir])
        elif platform.system() == 'Linux':
            subprocess.Popen(['xdg-open', output_dir])

root = tk.Tk()
root.geometry("400x370")  # Set initial window size

region_frame = tk.Frame(root, height=20)
region_frame.pack()

file_label = tk.Label(root, text="Pick BTT Writer Project (.tstudio):", pady=5)
file_label.pack()

file_entry = tk.Entry(root, width=50)
file_entry.pack()

file_button = tk.Button(root, text="Browse file", command=browse_file, padx=10, pady=5)
file_button.pack()

region_frame = tk.Frame(root, height=20)
region_frame.pack()

directory_label = tk.Label(root, text="Output Directory:", pady=5)
directory_label.pack()

directory_entry = tk.Entry(root, width=50)
directory_entry.pack()

directory_button = tk.Button(root, text="Choose directory", command=browse_directory, padx=10, pady=5)
directory_button.pack()

region_frame = tk.Frame(root, height=30)
region_frame.pack()

convert_button = tk.Button(root, text="Convert", bg="blue", fg="white", command=convert, padx=10, pady=5)
convert_button.pack(pady=5)

status_label = tk.Label(root, text="")
status_label.pack(pady=5)

open_output_button = tk.Button(root, text="Show output", bg="green", fg="white", command=open_directory, padx=10, pady=4)
open_output_button.pack(pady=5)
open_output_button.pack_forget()

root.mainloop()
