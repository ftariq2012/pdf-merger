# Bulk PDF Tool

Bulk PDF Tool is a desktop application built with **Python** and **Tkinter** that provides a simple interface for performing bulk operations on PDF files.  
It supports **merging, swapping, adding, and stamping** PDFs, with built-in logging and error handling for a smooth user experience.

---

## ✨ Features

- **Bulk Merge**
  - Merge all PDFs from a source folder.
  - Optionally append up to **two attachments** to every merged PDF.
  - Logs detailed progress (e.g., which files were merged, skipped, or failed).

- **Bulk Swap**
  - Swap two user-specified pages in all PDFs from an input folder.
  - Skips files with insufficient pages and records logs for clarity.

- **Bulk Add**
  - Insert an attachment PDF at a specific page number across all PDFs in a folder.

- **Bulk Stamp**
  - Apply a stamp (from the first page of another PDF) onto selected pages (e.g., ALL, 1,3,5, or ranges like 2-4,7).

- **Live Logging**
  - Console panel shows real-time logs inside the app.
  - Logs are also saved in a dedicated `logs/` folder for debugging or review.

- **User-Friendly GUI**
  - Built with **Tkinter** for a simple tabbed interface.
  - Separate tabs for each operation (Merge, Swap, Add, Stamp).
  - “Clear Logs” button to reset the console view.

---

## 🛠️ Tools & Libraries Used

- **[Tkinter](https://docs.python.org/3/library/tkinter.html)** – GUI framework for the desktop interface.
- **[PyPDF2](https://pypi.org/project/pypdf2/)** – PDF manipulation library used for reading, writing, and editing PDF pages.
- **Logging (Python standard library)** – For tracking progress, warnings, and errors in both console and log files.
- **OS (Python standard library)** – File and folder handling.

---

## 🚀 How It Works

Each function (Merge, Swap, Add, Stamp) is separated into its own module (`pdf_merge.py`, `pdf_swap.py`, `pdf_add.py`, `pdf_stamp.py`).  
The **main app (`pdf_app.py`)** provides a tabbed interface where you can switch between features.

1. **Browse Input & Output Folders**  
   - Select an input folder containing PDFs.  
   - Select an output folder (or a new one will be created if missing).

2. **Perform Operations**  
   - Depending on the tab:
     - **Merge:** Attach additional PDFs (Attachment 1 merges first).  
     - **Swap:** Enter two page numbers to swap (page numbers are 1-based).  
     - **Add:** Insert an attachment at a specific page number.  
     - **Stamp:** Choose which pages to apply a stamp on.

3. **View Logs**  
   - Logs display in the console window at the bottom.  
   - Detailed logs are also saved in the `logs/` folder (e.g., `swap_log.txt`).  

4. **Completion Notice**  
   - On success, a message box shows the number of files processed and skipped.

---

## ⚡ Usage

1. Clone the repo:
   ```bash
   git clone https://github.com/ftariq2012/pdf-merger.git
   cd pdf-merger
2. Run the app:
   ```bash
   python pdf_app.py

