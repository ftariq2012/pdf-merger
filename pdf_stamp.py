import os
import logging
from PyPDF2 import PdfReader, PdfWriter
from tkinter import *  # type: ignore
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import gc  # Add garbage collection for memory management

# ---------- Logging setup (scoped, non-duplicating) ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
log_file_path = os.path.join(LOG_DIR, "stamp_log.txt")

logger = logging.getLogger("pdf_stamp")
logger.setLevel(logging.INFO)
logger.propagate = False

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Add file/stream handlers only once
if not any(isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", None) == os.path.abspath(log_file_path)
           for h in logger.handlers):
    fh = logging.FileHandler(log_file_path, encoding="utf-8")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)

# ---------- Helpers ----------
def browse_folder(var: StringVar):
    path = filedialog.askdirectory()
    if path:
        var.set(path)

def browse_file(var: StringVar):
    path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if path:
        var.set(path)

class TextHandler(logging.Handler):
    """Log to the ScrolledText widget."""
    def __init__(self, text_widget: ScrolledText):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.configure(state="normal")
        self.text_widget.insert(END, msg + "\n")
        self.text_widget.configure(state="disabled")
        self.text_widget.see(END)

# ---------- UI Frame ----------
def get_stamp_frame(parent: Tk | Frame):
    frame = Frame(parent, bg="lightgrey")

    # Inputs
    input_folder = StringVar()
    output_folder = StringVar()
    stamp_pdf = StringVar()
    pages_var = StringVar(value="ALL")

    # ---- Page parser: "ALL" | "1,3,5" | "2-4,7"
    def parse_pages(pages_str: str, total_pages: int):
        if not pages_str or pages_str.strip().upper() == "ALL":
            return list(range(total_pages))

        indices = set()

        def add_1based(n1: int):
            i0 = n1 - 1
            if 0 <= i0 < total_pages:
                indices.add(i0)
            else:
                logger.warning(f"Ignored out-of-range page: {n1} (valid 1..{total_pages})")
                frame.update_idletasks()

        for token in pages_str.split(","):
            token = token.strip()
            if not token:
                continue
            if "-" in token:
                parts = token.split("-", 1)
                if len(parts) == 2:
                    a, b = parts
                    if a.strip().isdigit() and b.strip().isdigit():
                        start, end = int(a), int(b)
                        if start <= end:
                            for v in range(start, end + 1):
                                add_1based(v)
                        else:
                            logger.warning(f"Ignored descending range: {token}")
                            frame.update_idletasks()
                    else:
                        logger.warning(f"Ignored invalid range: {token}")
                        frame.update_idletasks()
                else:
                    logger.warning(f"Ignored invalid range: {token}")
                    frame.update_idletasks()
            else:
                if token.isdigit():
                    add_1based(int(token))
                else:
                    logger.warning(f"Ignored invalid page token: {token}")
                    frame.update_idletasks()

        return sorted(indices)

    # ---- Main action
    def stamp_pages():
        try:
            src_folder = input_folder.get().strip()
            out_folder = output_folder.get().strip()
            stamp_path = stamp_pdf.get().strip()
            pages_str = pages_var.get().strip()

            # Input validation
            if not src_folder or not os.path.isdir(src_folder):
                messagebox.showerror("Invalid Input", "Please select a valid Input Folder.")
                return
            if not stamp_path or not os.path.isfile(stamp_path):
                messagebox.showerror("Invalid Stamp", "Please select a valid Stamp PDF file.")
                return
            if not out_folder:
                messagebox.showerror("Invalid Output", "Please select an output folder.")
                return

            # Create output directory if it doesn't exist
            try:
                os.makedirs(out_folder, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Output Error", f"Cannot create output folder: {e}")
                return

            # Find PDF files
            pdf_files = [f for f in os.listdir(src_folder) if f.lower().endswith(".pdf")]
            if not pdf_files:
                messagebox.showinfo("No PDFs", "No PDF files found in the Input Folder.")
                return

            # Load stamp PDF once and validate
            try:
                stamp_reader = PdfReader(stamp_path)
                if len(stamp_reader.pages) == 0:
                    messagebox.showerror("Stamp Error", "Stamp PDF has no pages.")
                    return
                
                stamp_page = stamp_reader.pages[0]
                
                # Compress stamp content to reduce memory usage
                try:
                    stamp_page.compress_content_streams()
                except Exception as e:
                    logger.warning(f"Could not compress stamp content: {e}")
                    
            except Exception as e:
                messagebox.showerror("Stamp Error", f"Cannot read stamp PDF: {e}")
                return

            total_processed = 0
            total_skipped = 0
            
            logger.info(f"Starting stamp run | input={src_folder} | output={out_folder} | "
                       f"stamp={os.path.basename(stamp_path)} | pages={pages_str or 'ALL'}")
            frame.update_idletasks()

            for i, pdf_file in enumerate(pdf_files, 1):
                input_path = os.path.join(src_folder, pdf_file)
                name, ext = os.path.splitext(pdf_file)
                output_path = os.path.join(out_folder, f"{name}_stamped{ext or '.pdf'}")

                try:
                    logger.info(f"Processing {i}/{len(pdf_files)}: {pdf_file}")
                    frame.update_idletasks()

                    # Read input PDF
                    with open(input_path, 'rb') as input_file:
                        reader = PdfReader(input_file)
                        n_pages = len(reader.pages)

                        # Parse pages to stamp
                        indices = parse_pages(pages_str, n_pages)
                        if not indices:
                            total_skipped += 1
                            logger.warning(f"Skipped (no valid page indices): {pdf_file}")
                            frame.update_idletasks()
                            continue

                        # Create writer and process pages
                        writer = PdfWriter()
                        
                        for page_idx in range(n_pages):
                            try:
                                page = reader.pages[page_idx]
                                
                                # Apply stamp to specified pages
                                if page_idx in indices:
                                    original_mediabox = page.mediabox
                                    page.merge_page(stamp_page)
                                    # Restore original mediabox
                                    page.mediabox = original_mediabox
                                
                                writer.add_page(page)
                                
                            except Exception as e:
                                logger.error(f"Error processing page {page_idx + 1} of {pdf_file}: {e}")
                                # Add the page without stamping
                                writer.add_page(reader.pages[page_idx])

                    # Write output file
                    try:
                        with open(output_path, "wb") as output_file:
                            writer.write(output_file)
                        
                        total_processed += 1
                        logger.info(f"✓ Completed: {pdf_file} -> {os.path.basename(output_path)}")
                        frame.update_idletasks()
                        
                    except Exception as e:
                        total_skipped += 1
                        logger.error(f"Failed to write output for {pdf_file}: {e}")
                        frame.update_idletasks()
                        # Try to remove partial file
                        try:
                            if os.path.exists(output_path):
                                os.remove(output_path)
                        except:
                            pass

                except Exception as e:
                    total_skipped += 1
                    logger.error(f"Failed to process {pdf_file}: {e}")
                    frame.update_idletasks()
                
                # Force garbage collection after each file to manage memory
                gc.collect()

            # Final summary
            logger.info(f"COMPLETED: {total_processed} file(s) processed, {total_skipped} skipped.")
            frame.update_idletasks()
            
            if total_processed > 0:
                messagebox.showinfo("Complete", 
                    f"Successfully processed {total_processed} PDF(s).\n"
                    f"{total_skipped} file(s) skipped.\n\n"
                    f"Output saved to: {out_folder}")
            else:
                messagebox.showwarning("No Files Processed", 
                    f"No files were successfully processed.\n"
                    f"{total_skipped} file(s) had errors.")

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            frame.update_idletasks()
            messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")

    Label(frame, text="Input Folder", bg="lightgrey").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    Entry(frame, textvariable=input_folder, width=50).grid(row=0, column=1, padx=5, pady=5)
    Button(frame, text="Browse", command=lambda: browse_folder(input_folder)).grid(row=0, column=2, padx=5, pady=5)

    Label(frame, text="Output Folder", bg="lightgrey").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    Entry(frame, textvariable=output_folder, width=50).grid(row=1, column=1, padx=5, pady=5)
    Button(frame, text="Browse", command=lambda: browse_folder(output_folder)).grid(row=1, column=2, padx=5, pady=5)

    Label(frame, text="Stamp PDF (first page used)", bg="lightgrey").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    Entry(frame, textvariable=stamp_pdf, width=50).grid(row=2, column=1, padx=5, pady=5)
    Button(frame, text="Browse", command=lambda: browse_file(stamp_pdf)).grid(row=2, column=2, padx=5, pady=5)

    Label(frame, text="Pages (ALL or 1,3,5 or 2-4,7)", bg="lightgrey").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    Entry(frame, textvariable=pages_var, width=20).grid(row=3, column=1, sticky="w", padx=5, pady=5)

    Button(frame, text="Add Stamp", command=stamp_pages, bg="orange", fg="white").grid(
        row=4, column=0, columnspan=3, pady=20
    )

    log_output = ScrolledText(frame, height=12, width=85, state="disabled", 
                             bg="black", fg="white", font=("Consolas", 9))
    log_output.grid(row=6, column=0, columnspan=3, padx=10, pady=5)

    # Add UI log handler only once
    ui_handler_exists = any(isinstance(h, TextHandler) and getattr(h, "text_widget", None) is log_output
                            for h in logger.handlers)
    if not ui_handler_exists:
        text_handler = TextHandler(log_output)
        text_handler.setFormatter(formatter)
        logger.addHandler(text_handler)

    def clear_logs():
        log_output.configure(state="normal")
        log_output.delete(1.0, END)
        log_output.configure(state="disabled")

    Button(frame, text="Clear Logs", command=clear_logs).grid(
    row=10, column=0, columnspan=3, pady=5
    )

    return frame