import os
from PyPDF2 import PdfMerger
import time
from datetime import datetime
import logging
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("merge_log.txt")
stream_handler = logging.StreamHandler()

# Create GUI text handler (after log_output is defined)
# You will move this after defining `log_output` so it has access

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Do not attach GUI handler until log_output is defined
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# GUI Setup
window = Tk() 
window.geometry("700x450")
window.title("PDF Merger")
window.config(background="lightgrey")

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

class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.configure(state='normal')
        self.text_widget.insert(END, msg + '\n')
        self.text_widget.configure(state='disabled')
        self.text_widget.see(END)

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
                  window.update_idletasks()
                  merger = PdfMerger()
                  merger.append(os.path.join(src, filename))

                  merger.append(att1)
                  logging.info(f"Appended attachment1: {att1}")
                  window.update_idletasks()
                  time.sleep(0.5)

                  merger.append(att2)
                  logging.info(f"Appended attachment2: {att2}")
                  window.update_idletasks()
                  time.sleep(0.5) 

                  merger.write(os.path.join(out, filename))
                  merger.close()

                  logging.info(f"Merged file: {filename}")
                  window.update_idletasks()
                  time.sleep(0.5)
                  file_num += 1

              except Exception as e:
                  logging.error(f"Failed merging {filename}: {e}")
                  window.update_idletasks()

      messagebox.showinfo("Done", f"Successfully merged {file_num - 1} files.")
  
  except Exception as e:
    logging.error(f"Error occured: {e}")
    window.update_idletasks()
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

Button(window, text="Merge PDFs", command=merge_pdfs, bg="green", fg="white").grid(
    row=4, column=0, columnspan=3, pady=20
)

Label(window, text="Merge Log", bg="lightgrey", font=("Arial", 10, "bold")).grid(
    row=5, column=0, columnspan=3, pady=(10, 0)
)

log_output = ScrolledText(window, height=10, width=80, state='disabled', bg="black", fg="white")
log_output.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

text_handler = TextHandler(log_output)
text_handler.setFormatter(formatter)
logger.addHandler(text_handler)

def clear_logs():
    log_output.configure(state='normal')
    log_output.delete(1.0, END)
    log_output.configure(state='disabled')

Button(window, text="Clear Logs", command=clear_logs).grid(
    row=6, column=0, columnspan=3, pady=5
)

window.mainloop()