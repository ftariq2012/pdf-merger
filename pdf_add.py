import os
import logging
from PyPDF2 import PdfReader, PdfWriter
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

# Logging setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("add_log.txt")
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

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

def get_add_frame(parent):
    frame = Frame(parent, bg="lightgrey")
    input_folder = StringVar()
    output_folder = StringVar()
    attachment1 = StringVar()
    page1 = IntVar()
    def add_pages():
        try:
            src_folder = input_folder.get()
            out_folder = output_folder.get()
            att1 = attachment1.get()
            first_pg = page1.get() - 1

            if not os.path.isdir(src_folder) or not os.path.isdir(out_folder):
                messagebox.showerror("Invalid Input", "Please select valid input and output folders.")
                return

            pdf_files = [f for f in os.listdir(src_folder) if f.lower().endswith(".pdf")]
            if not pdf_files:
                messagebox.showinfo("No PDFs", "No PDF files found in the input folder.")
                return
            
            if not page1.get():
                messagebox.showinfo("Error", "Check page number")
                return

            total = 0
            skipped = 0
            for pdf_file in pdf_files:
                input_path = os.path.join(src_folder, pdf_file)
                output_path = os.path.join(out_folder, f"{pdf_file}")

                try:
                    reader = PdfReader(input_path)
                    writer = PdfWriter()
                    total_pages = len(reader.pages)
                    pages = list(reader.pages)

                    if first_pg >= total_pages:
                        skipped += 1
                        logger.warning(f"Skipped {pdf_file} (only {total_pages} pages)")
                        frame.update_idletasks()
                        continue
                    
                    attachment_reader = PdfReader(att1)
                    attachments = list(attachment_reader.pages)

                    for i, attachment_page in enumerate(attachments):
                        pages.insert(first_pg + i, attachment_page)

                    for page in pages:
                        writer.add_page(page)

                    with open(output_path, "wb") as f:
                        writer.write(f)

                    total += 1
                    logger.info(f"Added page in: {pdf_file}")
                    frame.update_idletasks()

                except Exception as e:
                    skipped += 1
                    logger.error(f"Failed {pdf_file}: {e}")
                    frame.update_idletasks()

            logger.info(f"\nDone. {total} file(s) processed, {skipped} skipped.")
            frame.update_idletasks()
            messagebox.showinfo("Complete", f"{total} PDFs processed.\n{skipped} skipped.")

        except Exception as e:
            logger.error(f"Error: {e}")
            messagebox.showerror("Error", str(e))

# UI Layout


    Label(frame, text="Input Folder").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    Entry(frame, textvariable=input_folder, width=50).grid(row=0, column=1, padx=5, pady=5)
    Button(frame, text="Browse", command=lambda: browse_folder(input_folder)).grid(row=0, column=2, padx=5, pady=5)

    Label(frame, text="Output Folder").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    Entry(frame, textvariable=output_folder, width=50).grid(row=1, column=1, padx=5, pady=5)
    Button(frame, text="Browse", command=lambda: browse_folder(output_folder)).grid(row=1, column=2, padx=5, pady=5)

    Label(frame, text="Input Page to Add attachment at").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    Entry(frame, textvariable=page1, width=5).grid(row=2, column=1, padx=5, pady=5)
    Button(frame, text="Add Page", command=add_pages, bg="red", fg="white").grid(
        row=4, column=0, columnspan=3, pady=20
    )
    
    Label(frame, text="Attachment").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    Entry(frame, textvariable=attachment1, width=50).grid(row=3, column=1, padx=5, pady=5)
    Button(frame, text="Browse", command=lambda: browse_file(attachment1)).grid(row=3, column=2, padx=5, pady=5)

    Label(frame, text="Add Log", bg="lightgrey", font=("Arial", 10, "bold")).grid(
        row=5, column=0, columnspan=3, pady=(10, 0)
    )

    log_output = ScrolledText(frame, height=10, width=80, state='disabled', bg="black", fg="white")
    log_output.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

    text_handler = TextHandler(log_output)
    text_handler.setFormatter(formatter)
    logger.addHandler(text_handler)

    def clear_logs():
        log_output.configure(state='normal')
        log_output.delete(1.0, END)
        log_output.configure(state='disabled')

    Button(frame, text="Clear Logs", command=clear_logs).grid(
        row=6, column=0, columnspan=3, pady=5
    )

    return frame
