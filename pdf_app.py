from tkinter import *
from pdf_reader import get_merger_frame
from pdf_reorder import get_swap_frame

root = Tk()
root.title("PDF Tool")
root.geometry("750x500")

merge_frame = get_merger_frame(root)
swap_frame = get_swap_frame(root)
nav_frame = Frame(root, bg="lightgrey")
nav_frame.pack(fill="x")

def show_merge():
    swap_frame.pack_forget()
    merge_frame.pack(fill="both", expand=True)

def show_swap():
    merge_frame.pack_forget()
    swap_frame.pack(fill="both", expand=True)

Button(nav_frame, text="Merge", command=show_merge).pack(
        side="left", padx=10, pady=10
    )
Button(nav_frame, text="Swap", command=show_swap).pack(
        side="left", padx=10, pady=10
    )

root.mainloop()
