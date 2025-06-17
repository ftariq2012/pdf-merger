import os
import logging
from PyPDF2 import PdfReader, PdfWriter
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

# Logging setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("swap_log.txt")
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# GUI setup
window = Tk()
window.geometry("700x450")
window.title("Batch PDF Page Swapper (Swap Page 2 & 3)")
window.config(background="lightgrey")

input_folder = StringVar()
output_folder = StringVar()

def browse_folder(var):
    path = filedialog.askdirectory()
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

def batch_swap_pages():
    try:
        src_folder = input_folder.get()
        out_folder = output_folder.get()

        if not os.path.isdir(src_folder) or not os.path.isdir(out_folder):
            messagebox.showerror("Invalid Input", "Please select valid input and output folders.")
            return

        pdf_files = [f for f in os.listdir(src_folder) if f.lower().endswith(".pdf")]
        if not pdf_files:
            messagebox.showinfo("No PDFs", "No PDF files found in the input folder.")
            return

        total = 0
        skipped = 0
        for pdf_file in pdf_files:
            input_path = os.path.join(src_folder, pdf_file)
            output_path = os.path.join(out_folder, f"swapped_{pdf_file}")

            try:
                reader = PdfReader(input_path)
                writer = PdfWriter()
                total_pages = len(reader.pages)

                if total_pages < 3:
                    skipped += 1
                    logger.warning(f"Skipped {pdf_file} (only {total_pages} pages)")
                    continue

                for i in range(total_pages):
                    if i == 1:
                        continue  # Skip page 2
                    elif i == 2:
                        writer.add_page(reader.pages[2])  # Page 3
                        writer.add_page(reader.pages[1])  # Then page 2
                    else:
                        writer.add_page(reader.pages[i])  # All others

                with open(output_path, "wb") as f:
                    writer.write(f)

                total += 1
                logger.info(f"Swapped pages in: {pdf_file}")

            except Exception as e:
                skipped += 1
                logger.error(f"Failed {pdf_file}: {e}")

        logger.info(f"\nDone. {total} file(s) processed, {skipped} skipped.")
        messagebox.showinfo("Complete", f"{total} PDFs processed.\n{skipped} skipped.")

    except Exception as e:
        logger.error(f"Error: {e}")
        messagebox.showerror("Error", str(e))

# UI Layout


Label(window, text="Input Folder").grid(row=0, column=0, sticky="w", padx=10, pady=5)
Entry(window, textvariable=input_folder, width=50).grid(row=0, column=1, padx=5, pady=5)
Button(window, text="Browse", command=lambda: browse_folder(input_folder)).grid(row=0, column=2, padx=5, pady=5)

Label(window, text="Output Folder").grid(row=1, column=0, sticky="w", padx=10, pady=5)
Entry(window, textvariable=output_folder, width=50).grid(row=1, column=1, padx=5, pady=5)
Button(window, text="Browse", command=lambda: browse_folder(output_folder)).grid(row=1, column=2, padx=5, pady=5)

Button(window, text="Batch Swap Pages 2 & 3", command=batch_swap_pages, bg="blue", fg="white").grid(
    row=4, column=0, columnspan=3, pady=20
)

Label(window, text="Swap Log", bg="lightgrey", font=("Arial", 10, "bold")).grid(
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
