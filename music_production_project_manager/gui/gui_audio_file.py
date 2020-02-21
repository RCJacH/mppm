import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


class FolderBrowser(tk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.pack()
        self.path = ""
        self.display_header()
        self.display_file_list()

    def display_header(self):
        def browse_button():
            path = tk.filedialog.askdirectory()
            if path:
                self.path = path
                self.address.delete(0, tk.END)
                self.address.insert(0, path)

        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.header_left = ttk.Frame(self.header_frame)
        self.header_left.pack(side=tk.LEFT, expand=True, fill=tk.Y)
        self.title = ttk.Label(self.header_left, text="Title")
        self.title.pack(side=tk.TOP, anchor=tk.W)
        self.address = ttk.Entry(self.header_left)
        self.address.pack(side=tk.LEFT)
        self.browse = ttk.Button(self.header_left, text="Browse", command=browse_button)
        self.browse.pack(side=tk.LEFT)
        self.header_mid = ttk.Frame(self.header_frame)
        self.header_mid.pack(side=tk.LEFT, expand=True, fill=tk.Y)
        self.header_right = ttk.Frame(self.header_frame)
        self.header_right.pack(side=tk.LEFT, expand=True, fill=tk.Y)
        self.analyze = ttk.Button(self.header_right, text="Analyze")
        self.analyze.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)


    def display_file_list(self):
        frame = ttk.Frame(self)
        tree = ttk.Treeview(frame, columns=("Channels", "Identical", "Action"))
        scroll = ttk.Scrollbar(frame, command=tree.yview)
        tree.configure(yscroll=scroll)
        tree.heading("#0", text="Filename")
        tree.column("#0", width=384, stretch=False)
        tree.heading("#1", text="Channels")
        tree.column("#1", width=64, stretch=False, anchor=tk.N)
        tree.heading("#2", text="Identical")
        tree.column("#2", width=64, stretch=False, anchor=tk.N)
        tree.heading("Action", text="Action")
        tree.column("Action", width=128, stretch=False, anchor=tk.N)
        # tree.column("Actions", stretch=False, anchor=tk.N)
        # for i in range(20):
            # self.file_tree.insert('', "end", text=str(i))
            # self.file_list.insert(tk.END, "")
            # self.property_list.insert(tk.END, "")
            # self.channels_list.insert(tk.END, "")
            # self.action_list.insert(tk.END, "")

        self.file_list_frame = frame
        self.file_list_frame.pack(side=tk.TOP)
        self.file_tree = tree
        tree.pack(side=tk.LEFT, fill=tk.Y)
        scroll.pack(side=tk.LEFT, fill=tk.Y)

    def display_actions(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    cls = FolderBrowser(root)
    root.mainloop()
