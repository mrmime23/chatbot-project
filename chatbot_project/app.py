from tkinter import *
import pandas as pd
import sqlite3
from chat import chat
from functions import split_words, check_for_url
from hyperlink import HyperlinkManager
import webbrowser
from functools import partial
from functions import make_predictions


background_gray = '#ABB2B9'
background_color = '#17202A'
text_color = '#EAECEE'

font = "Helvetica 14"
font_bold = "Helvetica 13 bold"


class ChatApp:
    index = 0

    def __init__(self):
        self.create_index()
        self.window = Tk()
        self._setup_main_window()
        self.start_model()

    def create_index(self):
        connection = sqlite3.connect("database_x.db")
        cur = connection.cursor()
        cur.execute("INSERT INTO chats (content) VALUES(Null)")
        db_get_id = pd.read_sql('select id from chats order by id desc limit 1', connection)
        ChatApp.index = db_get_id["id"][0]
        connection.commit()
        connection.close()

    def run(self):
        self.window.mainloop()

    def _setup_main_window(self):
        f = open('files/' + str(ChatApp.index) + ".txt", "w+")
        self.window.title("Chat")
        self.window.resizable(width=False, height=False)
        self.window.configure(width=500, height=600, bg=background_color)

        head_label = Label(self.window, bg=background_color,
                           fg=text_color, text="#"+str(ChatApp.index), font="font_bold", pady=10)
        head_label.place(relwidth=1)

        line = Label(self.window, width=480, bg=background_gray)
        line.place(relwidth=1, rely=0.07, relheight=0.012)

        self.text_widget = Text(self.window, width=20, height=2, bg=background_color, fg=text_color,
                                font=font, padx=5, pady=5)
        self.text_widget.place(relheight=0.745, relwidth=1, rely=0.08)
        self.text_widget.configure(cursor="arrow", state=DISABLED)

        bottom_label = Label(self.window, bg=background_gray, height=80)
        bottom_label.place(relwidth=1, rely=0.825)

        self.msg_entry = Entry(bottom_label, bg='#2C3E50', fg=text_color, font=font)
        self.msg_entry.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", self._on_enter_pressed)
        send_button = Button(bottom_label, text="Send", font=font_bold, width=20, bg=background_gray,
                             command=lambda: self._on_enter_pressed(None))
        send_button.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)

    def start_model(self):
        make_predictions(["testing..."])

    def _on_enter_pressed(self, event):
        msg = self.msg_entry.get()
        self._insert_message_(msg, "You")
        self.window.after(250, self._insert_message_, msg, "Bot")

    def _insert_message_(self, msg, sender):
        if not msg:
            return
        if sender == "You":
            self.msg_entry.delete(0, END)
            msg1 = f"{sender}: {msg}\n\n"
            self.text_widget.configure(state=NORMAL)
            self.text_widget.insert(END, msg1)
            self.text_widget.configure(state=DISABLED)
            self.text_widget.see(END)
        else:
            msg2 = f"{sender}: {chat(msg, ChatApp.index)}\n"
            arr = split_words(msg2)
            index_of_urls = check_for_url(arr)

            self.msg_entry.delete(0, END)
            for i in range(len(arr)):
                if i in index_of_urls:
                    self.text_widget.configure(state=NORMAL)
                    hyperlink = HyperlinkManager(self.text_widget)
                    self.text_widget.insert(END, arr[i] + "\n", hyperlink.add(partial(webbrowser.open, arr[i])))
                    self.text_widget.configure(state=DISABLED)
                else:
                    self.text_widget.configure(state=NORMAL)
                    self.text_widget.insert(END, arr[i] + "\n")
                    self.text_widget.configure(state=DISABLED)

            self.text_widget.see(END)


if __name__ == "__main__":
    app = ChatApp()
    app.run()


