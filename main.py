import sys
from PySide6 import QtCore, QtWidgets, QtGui
import os
import json
from pynput import keyboard
import time
from threading import Thread
import copykitten
import sqlite3
from sqlite import init_db

class MyWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.con, self.cur = init_db()

        self.clipboard = set()
        self.text = QtWidgets.QLabel("Clipboard", alignment = QtCore.Qt.AlignCenter)
        self.list_widget = QtWidgets.QListWidget()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.list_widget)
        self.load_clipboard_data()
         
    def load_clipboard_data(self):
        res = self.cur.execute("SELECT info from data")
        items = res.fetchall()
        items_list = [item[0] for item in items]
        print(items_list)
        self.clipboard = set(items_list)
        for item in items_list:
            stripped_item = item.strip()
            self.list_widget.addItem(stripped_item)

    def closeEvent(self, event):
        event.accept()

    @QtCore.Slot()
    def bring_to_front(self):
        self.show()
        self.raise_()
        self.activateWindow()

    @QtCore.Slot(str)
    def add_to_clipboard(self,info):
        if info not in self.clipboard and info != None:
            self.clipboard.add(info)
            self.cur.execute(f"INSERT INTO data VALUES ('{info}')")
            self.con.commit()
            self.list_widget.addItem(info)
        elif info == None:
            print("error: adding blank info")
        else: 
            print("error: info already in database!")

    def keyPressEvent(self, event):
        print(f"Key pressed: {event.key()}")
        selected_item = self.list_widget.currentItem()
        if event.key() == QtCore.Qt.Key_Return:
            if selected_item:
                text_to_copy = selected_item.text()
                copykitten.copy(text_to_copy)
        if event.key() == QtCore.Qt.Key_Backspace:
            selected_item = self.list_widget.currentItem()
            if selected_item:
                row = self.list_widget.currentRow()
                item_text = selected_item.text()
                self.list_widget.takeItem(row)
                self.clipboard.remove(item_text)
                self.cur.execute(f"DELETE FROM data WHERE info = '{item_text}'")
                self.con.commit()
        else:
            super().keyPressEvent(event)
        


def listen_for_hotkey(app):
    copykitten.clear()

    con = sqlite3.connect("history.db")
    cur = con.cursor()

    def activate_copy():
        print("copy activated!")
        
        time.sleep(0.1)

        try:
            keyboard_content = copykitten.paste()  

            if keyboard_content and keyboard_content.strip(): 
                keyboard_content_strip = keyboard_content.strip()
                QtCore.QMetaObject.invokeMethod(
                    widget, "add_to_clipboard", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, keyboard_content_strip)
                )
                print(f"Copied content: {keyboard_content}")  
            else:
                print("Clipboard is empty or invalid!")
        except Exception as e:
            print(f"Error accessing clipboard: {e}")


    def activate_clipboard():
        print("clipboard activated!")
        QtCore.QMetaObject.invokeMethod(widget,"bring_to_front", QtCore.Qt.QueuedConnection) 
     
        

    def hide_app():
        print("hiding app")
        QtCore.QMetaObject.invokeMethod(widget, "hide", QtCore.Qt.QueuedConnection)  

    with keyboard.GlobalHotKeys({'<cmd>+c': activate_copy, 
                                 '<ctrl>+<shift>': activate_clipboard,
                                 '<esc>': hide_app
                                
                                 }) as hotkeys: hotkeys.join()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(500,300)
    widget.show()

    listener_thread = Thread(target=listen_for_hotkey, args=(widget,), daemon=True)
    listener_thread.start()

    sys.exit(app.exec())