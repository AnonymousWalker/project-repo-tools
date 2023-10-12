import tkinter as tk
from tkinter import filedialog
from tstudio2rc import TstudioToRC
import subprocess
import platform
import yaml

input_file = None
output_dir = None
manifest_content = None
converter = TstudioToRC()

def browse_file():
    status_label.config(text="")
    open_output_button.configure(state="disabled")
    filetypes = (("BTT Writer file", "*.tstudio"), ("All files", "*.*"))
    file_path = filedialog.askopenfilename(filetypes=filetypes)
    if file_path:
        global input_file, manifest_content
        input_file = file_path
        file_entry.delete(0, tk.END)
        file_entry.insert(tk.END, file_path)
        manifest_content = converter.previewManifest(input_file)
        text_area.insert(tk.END, manifest_content)

def browse_directory():
    status_label.config(text="")
    open_output_button.configure(state="disabled")
    directory_path = filedialog.askdirectory()
    if directory_path:
        global output_dir
        output_dir = directory_path
        directory_entry.delete(0, tk.END)
        directory_entry.insert(tk.END, directory_path)

def convert():
    if (file_entry.get() != '' and directory_entry.get() != ''):
        global input_file, output_dir, manifest_content
        input_file = file_entry.get().replace('\\', '/').replace('\"', '')
        output_dir = directory_entry.get().replace('\\', '/').replace('\"', '')
        try:
            manifest = yaml.safe_load(manifest_content)
            converter.convert(input_file, output_dir, manifest)
            open_output_button.configure(state="normal")
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

def toggle_preview_manifest():
    if preview_var.get():
        root.geometry("400x700") 
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)    
    else:
        root.geometry("400x400") 
        text_area.pack_forget()

def update_manifest(event):
    global manifest_content
    manifest_content = text_area.get(1.0, tk.END)

root = tk.Tk()
root.geometry("400x360")  # Set initial window size
preview_var = tk.BooleanVar()

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

region_frame = tk.Frame(root, height=10)
region_frame.pack()

preview_checkbox = tk.Checkbutton(root, text="Preview output manifest", variable=preview_var, command=toggle_preview_manifest)
preview_checkbox.pack()

convert_button = tk.Button(root, text="Convert", bg="blue", fg="white", command=convert, padx=10, pady=5)
convert_button.pack(pady=5)

status_label = tk.Label(root, text="")
status_label.pack(pady=2)

open_output_button = tk.Button(root, text="Show output", command=open_directory, padx=10, pady=4)
open_output_button.pack(pady=2)
open_output_button.configure(state="disabled")
open_output_button.pack()

text_area = tk.Text(root, height=10, wrap=tk.WORD, undo=True)
text_area.bind("<KeyRelease>", update_manifest)
text_area.pack_forget()

root.mainloop()
