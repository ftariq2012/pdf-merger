import os
from PyPDF2 import PdfMerger
import time
from datetime import datetime
import logging
from tkinter import *
from tkinter import filedialog, messagebox

# Logging
logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s - %(levelname)s - %(message)s",
  handlers=[
    logging.FileHandler("merge_log.txt"),
    logging.StreamHandler()
  ]
)

# GUI Setup
window = Tk() 
window.geometry("600x400")
window.title("PDF Merger")
window.config(background="lightgrey")

# Get proper file/folder paths
def get_valid_path(prompt, is_file=True):
    while True:
        path = input(prompt).strip().strip('"')
        if is_file and os.path.isfile(path):
            return path
        elif not is_file and os.path.isdir(path):
            return path
        else:
            print(f"Invalid {'file' if is_file else 'folder'} path. Please try again.")

# User inputs
source_folder = StringVar()
attachment1 = StringVar()
attachment2 = StringVar()
output_folder = StringVar()

def browse_folder(var):
    path = filedialog.askdirectory()
    if path:
        var.set(path)

def browse_file(var):
    path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if path:
        var.set(path)

def merge_pdfs():
  try:
      src = source_folder.get()
      att1 = attachment1.get()
      att2 = attachment2.get()
      out = output_folder.get()

      if not (os.path.isdir(src) and os.path.isfile(att1) and os.path.isfile(att2)):
          messagebox.showerror("Invalid paths", "Please make sure all paths are valid.")
          return

      os.makedirs(out, exist_ok=True)
      file_num = 1

      for filename in os.listdir(src):
          if filename.endswith(".pdf"):
              try:
                  logging.info(f"Starting merge for file number {file_num} -> Filename: {filename}...")
                  merger = PdfMerger()
                  merger.append(os.path.join(src, filename))

                  merger.append(att1)
                  logging.info(f"Appended attachment1: {att1}")
                  time.sleep(0.5)

                  merger.append(att2)
                  logging.info(f"Appended attachment2: {att2}")
                  time.sleep(0.5) 

                  merger.write(os.path.join(out, filename))
                  merger.close()

                  logging.info(f"Merged file: {filename}")
                  time.sleep(0.5)
                  file_num += 1

              except Exception as e:
                  logging.error(f"Failed merging {filename}: {e}")

      messagebox.showinfo("Done", f"Successfully merged {file_num - 1} files.")
  
  except Exception as e:
    logging.error(f"Error occured: {e}")
    messagebox.showerror("Error", str(e))

# UI layout
Label(window, text="Source Folder").grid(row=0, column=0, sticky="w", padx=10, pady=5)
Entry(window, textvariable=source_folder, width=50).grid(row=0, column=1, padx=5, pady=5)
Button(window, text="Browse", command=lambda: browse_folder(source_folder)).grid(row=0, column=2, padx=5, pady=5)

Label(window, text="Attachment 1").grid(row=1, column=0, sticky="w", padx=10, pady=5)
Entry(window, textvariable=attachment1, width=50).grid(row=1, column=1, padx=5, pady=5)
Button(window, text="Browse", command=lambda: browse_file(attachment1)).grid(row=1, column=2, padx=5, pady=5)

Label(window, text="Attachment 2").grid(row=2, column=0, sticky="w", padx=10, pady=5)
Entry(window, textvariable=attachment2, width=50).grid(row=2, column=1, padx=5, pady=5)
Button(window, text="Browse", command=lambda: browse_file(attachment2)).grid(row=2, column=2, padx=5, pady=5)

Label(window, text="Output Folder").grid(row=3, column=0, sticky="w", padx=10, pady=5)
Entry(window, textvariable=output_folder, width=50).grid(row=3, column=1, padx=5, pady=5)
Button(window, text="Browse", command=lambda: browse_folder(output_folder)).grid(row=3, column=2, padx=5, pady=5)

# Merge Button (spanning full width)
Button(window, text="Merge PDFs", command=merge_pdfs, bg="green", fg="white").grid(
    row=4, column=0, columnspan=3, pady=20
)
window.mainloop()