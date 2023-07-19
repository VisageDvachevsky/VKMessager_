import tkinter as tk
from tkinter import messagebox
import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
import clipboard
import textwrap
import threading

class VKMessenger:
    def __init__(self, token):
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()
        
        self.window = tk.Tk()
        self.window.title("VK Messenger")
        self.window.geometry("800x600")
        self.window.configure(bg="#1e3042")
        
        self.frame1 = tk.Frame(self.window, bg="#1e3042")
        self.frame1.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        self.frame2 = tk.Frame(self.window, bg="#1e3042")
        self.frame2.pack(side=tk.RIGHT, padx=10, fill=tk.BOTH, expand=True)
        
        self.chat_listbox = tk.Listbox(self.frame1, width=40, height=20)
        self.chat_listbox.pack(fill=tk.BOTH, expand=True)
        self.chat_listbox.bind("<Button-1>", self.copy_chat_id)
        
        self.chat_id_entry = tk.Entry(self.frame2)
        self.chat_id_entry.pack(pady=10)
        
        self.show_button = tk.Button(self.frame2, text="Show Messages", command=self.show_messages)
        self.show_button.pack(pady=5)
        
        self.back_button = tk.Button(self.frame2, text="Back", command=self.back_to_input)
        self.back_button.pack(pady=5)
        
        self.message_list = tk.Listbox(self.frame2, width=50, height=20)
        self.message_list.pack_forget()
        
        self.show_conversations()
    
    def copy_chat_id(self, event):
        index = self.chat_listbox.curselection()
        if index:
            chat_id = self.chat_listbox.get(index).split(" ")[-1]
            clipboard.copy(chat_id)
    
    def show_conversations(self):
        self.chat_listbox.delete(0, tk.END)
        conversations = self.vk.messages.getConversations(count=20)['items']
        for conversation in conversations:
            peer = conversation['conversation']['peer']
            chat_id = peer['id']
            chat_title = ""
            if peer.get('type') == 'chat':
                chat_settings = conversation['conversation']['chat_settings']
                chat_title = chat_settings['title']
            elif peer.get('type') == 'user':
                user_info = self.vk.users.get(user_ids=chat_id, fields='photo_100')[0]
                chat_title = "{} {}".format(user_info['first_name'], user_info['last_name'])
            self.chat_listbox.insert(tk.END, "{} - Chat ID: {}".format(chat_title, chat_id))
    
    def show_messages(self):
        chat_id = self.chat_id_entry.get()
        if chat_id.isdigit():
            chat_id = int(chat_id)
            conversation_exists = False
            conversations = self.vk.messages.getConversations(count=20)['items']
            for conversation in conversations:
                if conversation['conversation']['peer']['id'] == chat_id:
                    conversation_exists = True
                    break
            if conversation_exists:
                self.chat_id_entry.pack_forget()
                self.message_list.pack(expand=True, fill=tk.BOTH)
                threading.Thread(target=self.update_messages, args=(chat_id,), daemon=True).start()
            else:
                messagebox.showerror("Error", "Invalid chat ID")
        else:
            messagebox.showerror("Error", "Invalid chat ID")
    
    def update_messages(self, chat_id):
        messages = self.vk.messages.getHistory(peer_id=chat_id, count=50, rev=0)['items']
        self.message_list.delete(0, tk.END)
        for message in reversed(messages):
            message_text = message['text']
            message_text_wrapped = textwrap.fill(message_text, width=70)
            from_id = message['from_id']
            user_info = self.vk.users.get(user_ids=from_id, fields='first_name,last_name')
            if user_info:
                first_name = user_info[0]['first_name']
                last_name = user_info[0]['last_name']
                self.message_list.insert(tk.END, f"{first_name} {last_name}:")
            else:
                self.message_list.insert(tk.END, "Unknown User:")
            self.message_list.insert(tk.END, message_text_wrapped)
            self.message_list.insert(tk.END, "")
        self.window.after(20000, self.update_messages, chat_id)
    
    def back_to_input(self):
        self.chat_id_entry.delete(0, tk.END)
        self.chat_id_entry.pack()
        self.message_list.pack_forget()
        self.message_list.delete(0, tk.END)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    token = 'YOUR TOKEN '
    messenger = VKMessenger(token)
    messenger.run()
