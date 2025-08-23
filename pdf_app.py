from tkinter import * # type: ignore
from pdf_merge import get_merger_frame
from pdf_swap import get_swap_frame
from pdf_add import get_add_frame
from pdf_stamp import get_stamp_frame

root = Tk()
root.title("Bulk PDF Tool")
root.geometry("750x500")

merge_frame = get_merger_frame(root)
swap_frame = get_swap_frame(root)
add_frame = get_add_frame(root)
stamp_frame = get_stamp_frame(root)
nav_frame = Frame(root, bg="lightgrey")
nav_frame.pack(fill="x")

def show_merge():
    swap_frame.pack_forget()
    add_frame.pack_forget()
    stamp_frame.pack_forget()
    merge_frame.pack(fill="both", expand=True)

def show_swap():
    merge_frame.pack_forget()
    add_frame.pack_forget()
    stamp_frame.pack_forget()
    swap_frame.pack(fill="both", expand=True)

def show_add():
    merge_frame.pack_forget()
    swap_frame.pack_forget()
    stamp_frame.pack_forget()
    add_frame.pack(fill="both", expand=True)

def show_stamp():
    merge_frame.pack_forget()
    swap_frame.pack_forget()
    add_frame.pack_forget()
    stamp_frame.pack(fill="both", expand=True)

Button(nav_frame, text="Merge", command=show_merge).pack(
        side="left", padx=10, pady=10
    )
Button(nav_frame, text="Swap", command=show_swap).pack(
        side="left", padx=10, pady=10
    )

Button(nav_frame, text="Add", command=show_add).pack(
        side="left", padx=10, pady=10
    )

Button(nav_frame, text="Stamp", command=show_stamp).pack(
        side="left", padx=10, pady=10
    )

root.mainloop()
