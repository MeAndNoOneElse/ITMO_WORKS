import tkinter as tk
from gui import GaussMethodGUI


def main():
    root = tk.Tk()
    app = GaussMethodGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

