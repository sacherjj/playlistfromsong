import tkinter as tk


class StatusBar(tk.Label):
    def __init__(self, master):
        self.label_variable = tk.StringVar()
        super().__init__(master, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                         textvariable=self.label_variable)

    @property
    def text(self):
        return self.label_variable.get()

    @text.setter
    def text(self, value):
        self.label_variable.set(value)
        self.update()

    def set_timed_text(self, text, milliseconds):
        self.text = text
        self.after(milliseconds, lambda: self._time_clear(text))
        self.update()

    def _time_clear(self, set_text):
        # Only change if text has not changed since call
        if self.text == set_text:
            self.text = ''
