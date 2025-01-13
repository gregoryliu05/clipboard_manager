import sys
from PySide6 import QtCore, QtWidgets, QtGui
import os
import json
from pynput import keyboard
import time
from threading import Thread
import copykitten

class MyWidget(QtWidgets.QWidget):
    PERSISTENCE_FILE = "clipboard_history.json"

    def __init__(self):
        super().__init__()

        self.clipboard = set()
        self.text = QtWidgets.QLabel("Clipboard", alignment = QtCore.Qt.AlignCenter)
        self.list_widget = QtWidgets.QListWidget()
        self.layout = QtWidgets.QVBoxLayout(self)
        #self.layout.addWidget(self.text)
        self.layout.addWidget(self.list_widget)
        self.load_clipboard_data()

    def save_clipboard_data(self):
        """Save clipboard data to a file."""
        try:
            with open(self.PERSISTENCE_FILE, "w") as file:
                json.dump(list(self.clipboard), file)
            print(f"Clipboard data saved to {self.PERSISTENCE_FILE}")
        except Exception as e:
            print(f"Error saving clipboard data: {e}")

    def load_clipboard_data(self):
        """Load clipboard data from a file."""
        if os.path.exists(self.PERSISTENCE_FILE):
            try:
                with open(self.PERSISTENCE_FILE, "r") as file:
                    data = json.load(file)
                    for item in data:
                        self.add_to_clipboard(item)
                print(f"Clipboard data loaded from {self.PERSISTENCE_FILE}")
            except Exception as e:
                print(f"Error loading clipboard data: {e}")

    def closeEvent(self, event):
        """Override closeEvent to save data before exiting."""
        self.save_clipboard_data()
        event.accept()

    @QtCore.Slot()
    def bring_to_front(self):
        """Bring the window to the front."""
        self.show()
        self.raise_()
        self.activateWindow()

    def add_to_clipboard(self,info):
        if info not in self.clipboard:
            stripped_info = info.strip()
            self.clipboard.add(stripped_info)
            self.list_widget.addItem(stripped_info)

    def keyPressEvent(self, event):
        print(f"Key pressed: {event.key()}")
        selected_item = self.list_widget.currentItem()
        if event.key() == QtCore.Qt.Key_Return:
            if selected_item:
                text_to_copy = selected_item.text()
                print(f"textCopied: {text_to_copy}")
                copykitten.copy(text_to_copy)
        if event.key() == QtCore.Qt.Key_Backspace:
            selected_item = self.list_widget.currentItem()
            if selected_item:
                row = self.list_widget.currentRow()
                item_text = selected_item.text()
                self.list_widget.takeItem(row)
                print(f"deleted item {item_text}")
        else:
            super().keyPressEvent(event)

    def eventFilter(self, source, event):
        """Handle Delete key press specifically for the list widget."""
        if source == self.list_widget and event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Delete:
                selected_item = self.list_widget.currentItem()
                if selected_item:
                    row = self.list_widget.currentRow()
                    self.list_widget.takeItem(row) 
                    self.clipboard.remove(item_text)  
                    print(f"Deleted: {item_text}")
                return True 
        return super().eventFilter(source, event)
        
    
    def remove_from_clipboard(self, info):
        if info in self.clipboard:
            stripped_info = info.strip()
            self.clipboard.remove(stripped_info)
    


def listen_for_hotkey(app):
    copykitten.clear()
    def activate_copy():
        print("copy activated!")
        
        time.sleep(0.1)

        try:
            keyboard_content = copykitten.paste()  

            if keyboard_content and keyboard_content.strip(): 
                app.add_to_clipboard(keyboard_content)
                print(f"Copied content: {keyboard_content}")  
            else:
                print("Clipboard is empty or invalid!")
        except Exception as e:
            print(f"Error accessing clipboard: {e}")


    def activate_clipboard():
        print("clipboard activated!")
        
        QtCore.QMetaObject.invokeMethod(widget,"bring_to_front", QtCore.Qt.QueuedConnection)  # Safely show the widget
     
        

    def hide_app():
        print("hiding app")
        QtCore.QMetaObject.invokeMethod(widget, "hide", QtCore.Qt.QueuedConnection)  # Safely hide the widget

    with keyboard.GlobalHotKeys({'<cmd>+c': activate_copy, 
                                 '<shift>+v': activate_clipboard,
                                 '<esc>': hide_app
                                
                                 }) as hotkeys: hotkeys.join()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(500,300)
    widget.show()

    #Run hotkey listener in a separate thread
    listener_thread = Thread(target=listen_for_hotkey, args=(widget,), daemon=True)
    listener_thread.start()

    sys.exit(app.exec())