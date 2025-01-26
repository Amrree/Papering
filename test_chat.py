import tkinter as tk
from tkinter import ttk
from frames.chat_frame import ChatFrame

def main():
    root = tk.Tk()
    root.title("Chat Frame Test")
    root.geometry('400x600')
    root.configure(bg='#1e1e1e')

    style = ttk.Style()
    style.configure('Retro.TButton', padding=6, relief='raised', background='#d4d0c8', font=('Arial', 12))

    chat_frame = ChatFrame(root)
    chat_frame.place(x=10, y=10, width=380, height=580)

    root.mainloop()

if __name__ == "__main__":
    main()