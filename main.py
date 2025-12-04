from interface import OpenBCIInterface
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = OpenBCIInterface(root)
    root.mainloop()