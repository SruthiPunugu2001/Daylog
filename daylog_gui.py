import os
import json
import winsound
from datetime import datetime
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
import shutil
import csv
import subprocess
import time
from tkinter.simpledialog import askinteger

JOURNAL_FILE = "journal.csv"
REMINDERS_FILE = "reminders.json"
ATTACHMENTS_DIR = "attachments"


class JournalApp:
    def __init__(self, master):
        self.master = master
        master.title("Journal App")
        self.create_menu()

    def create_menu(self):
        self.menu_label = tk.Label(self.master, text="Menu:")
        self.menu_label.pack()

        self.add_journal_entry_button = tk.Button(self.master, text="1. Add Journal Entry",
                                                  command=self.add_journal_entry)
        self.add_journal_entry_button.pack()

        self.display_journal_entries_button = tk.Button(self.master, text="2. Display Journal Entries",
                                                        command=self.display_journal_entries)
        self.display_journal_entries_button.pack()

        self.delete_journal_entry_button = tk.Button(self.master, text="3. Delete Journal Entry",
                                                     command=self.delete_journal_entry)
        self.delete_journal_entry_button.pack()

        self.add_reminder_button = tk.Button(self.master, text="4. Add Reminder", command=self.add_reminder)
        self.add_reminder_button.pack()

        self.list_reminders_button = tk.Button(self.master, text="5. List Reminders", command=self.list_reminders)
        self.list_reminders_button.pack()

        self.search_entries_button = tk.Button(self.master, text="6. Search Entries", command=self.search_entries)
        self.search_entries_button.pack()

        self.delete_all_entries_button = tk.Button(self.master, text="7. Delete All Entries",
                                                   command=self.delete_all_entries)
        self.delete_all_entries_button.pack()

        self.delete_reminder_button = tk.Button(self.master, text="8. Delete Reminder", command=self.delete_reminder)
        self.delete_reminder_button.pack()

        self.exit_button = tk.Button(self.master, text="9. Exit", command=self.exit_app)
        self.exit_button.pack()

    def add_journal_entry(self):
        self.create_add_entry_window()

    def create_add_entry_window(self):
        add_entry_window = tk.Toplevel(self.master)
        add_entry_window.title("Add Journal Entry")

        entry_text_label = tk.Label(add_entry_window, text="Entry Text:")
        entry_text_label.pack()

        entry_text_text = tk.Text(add_entry_window, height=10, width=50)
        entry_text_text.pack()

        attachments_label = tk.Label(add_entry_window, text="Attachments (comma-separated):")
        attachments_label.pack()

        attachments_var = tk.StringVar()
        attachments_entry = tk.Entry(add_entry_window, textvariable=attachments_var)
        attachments_entry.pack()

        add_entry_button = tk.Button(add_entry_window, text="Add Entry",
                                     command=lambda: self.submit_entry(add_entry_window,
                                                                       entry_text_text.get("1.0", tk.END).strip(),
                                                                       attachments_var.get()))
        add_entry_button.pack()

    def submit_entry(self, add_entry_window, entry_text, attachments):
        add_entry(entry_text, attachments.split(','))
        messagebox.showinfo("Success", "Journal entry added successfully.")
        add_entry_window.destroy()

    def display_journal_entries(self):
        display_entries()

    def delete_journal_entry(self):
        self.create_delete_entry_window()

    def create_delete_entry_window(self):
        delete_entry_window = tk.Toplevel(self.master)
        delete_entry_window.title("Delete Journal Entry")

        entry_index_label = tk.Label(delete_entry_window, text="Entry Index:")
        entry_index_label.pack()

        entry_index_var = tk.StringVar()
        entry_index_entry = tk.Entry(delete_entry_window, textvariable=entry_index_var)
        entry_index_entry.pack()

        delete_entry_button = tk.Button(delete_entry_window, text="Delete Entry",
                                        command=lambda: self.submit_delete(int(entry_index_var.get())))
        delete_entry_button.pack()

    def submit_delete(self, entry_index):
        delete_entry(entry_index)
        messagebox.showinfo("Success", "Journal entry deleted successfully.")

    def add_reminder(self):
        self.create_add_reminder_window()

    def create_add_reminder_window(self):
        add_reminder_window = tk.Toplevel(self.master)
        add_reminder_window.title("Add Reminder")

        reminder_text_label = tk.Label(add_reminder_window, text="Reminder Text:")
        reminder_text_label.pack()

        reminder_text_var = tk.StringVar()
        reminder_text_entry = tk.Entry(add_reminder_window, textvariable=reminder_text_var)
        reminder_text_entry.pack()

        remind_at_label = tk.Label(add_reminder_window, text="Remind At (YYYY-MM-DD HH:MM:SS):")
        remind_at_label.pack()

        remind_at_var = tk.StringVar()
        remind_at_entry = tk.Entry(add_reminder_window, textvariable=remind_at_var)
        remind_at_entry.pack()

        add_reminder_button = tk.Button(add_reminder_window, text="Add Reminder",
                                        command=lambda: self.submit_reminder(add_reminder_window,
                                                                             reminder_text_var.get(),
                                                                             remind_at_var.get()))
        add_reminder_button.pack()

    def submit_reminder(self, add_reminder_window, reminder_text, remind_at):
        add_reminder(reminder_text, remind_at)
        messagebox.showinfo("Success", "Reminder added successfully.")
        add_reminder_window.destroy()

    def list_reminders(self):
        reminders = load_reminders()
        if not reminders:
            messagebox.showinfo("Reminders", "No reminders found.")
        else:
            reminder_text = "\n".join(
                [f"{i + 1}. {reminder['text']} - Remind at: {reminder['remind_at']}" for i, reminder in
                 enumerate(reminders)])
            messagebox.showinfo("Reminders", reminder_text)

    def search_entries(self):
        search_window = tk.Toplevel(self.master)
        search_window.title("Search Entries")

        keyword_label = tk.Label(search_window, text="Enter the keyword to search:")
        keyword_label.pack()
        keyword_var = tk.StringVar()
        keyword_entry = tk.Entry(search_window, textvariable=keyword_var)
        keyword_entry.pack()

        date_label = tk.Label(search_window, text="Enter the date to search (format: 'YYYY-MM-DD'):")
        date_label.pack()
        date_var = tk.StringVar()
        date_entry = tk.Entry(search_window, textvariable=date_var)
        date_entry.pack()

        search_button = tk.Button(search_window, text="Search",
                                  command=lambda: self.search_results(keyword_var.get(), date_var.get()))
        search_button.pack()

    def search_results(self, keyword, date):
        if not os.path.exists(JOURNAL_FILE):
            messagebox.showinfo("Search Entries", "No journal entries found.")
            return

        matching_entries = []
        with open(JOURNAL_FILE, 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                entry_timestamp, entry_text, attachments = row
                if (keyword.lower() in entry_text.lower()) and (date in entry_timestamp):
                    matching_entries.append((entry_timestamp, entry_text, attachments))

        if not matching_entries:
            messagebox.showinfo("Search Results", "No matching entries found.")
        else:
            result_text = "\n\n".join(
                [f"Timestamp: {entry[0]}\nEntry Text: {entry[1]}\nAttachments: {entry[2]}" for entry in
                 matching_entries])
            messagebox.showinfo("Search Results", result_text)

    def delete_all_entries(self):
        confirm = messagebox.askyesno("Delete All Entries", "Are you sure you want to delete all entries?")
        if confirm:
            if os.path.exists(JOURNAL_FILE):
                os.remove(JOURNAL_FILE)
                messagebox.showinfo("Success", "All journal entries deleted.")
            if os.path.exists(ATTACHMENTS_DIR):
                shutil.rmtree(ATTACHMENTS_DIR)
                messagebox.showinfo("Success", "All attachments deleted.")
        else:
            messagebox.showinfo("Delete All Entries", "Operation canceled.")

    def delete_reminder(self):
        reminder_index = askinteger("Delete Reminder", "Enter the index of the reminder to delete:")
        if reminder_index is not None:  # Check if a valid index is provided
            delete_reminder(reminder_index)
        else:
            messagebox.showinfo("Delete Reminder", "Operation canceled.")

    def exit_app(self):
        self.master.destroy()


def add_entry(entry_text, attachments=None):
    initialize()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    attachment_folder = os.path.join(ATTACHMENTS_DIR, timestamp)
    os.makedirs(attachment_folder, exist_ok=True)
    attachments_str = ','.join(attachments) if attachments and attachments[0] != "None" else ""
    entry = f"{timestamp},{entry_text},{attachments_str}\n"
    with open(JOURNAL_FILE, 'a', newline='') as file:
        if not os.path.exists(JOURNAL_FILE):
            file.write("timestamp,entry_text,attachments\n")
        file.write(entry)
    print("Journal entry added successfully.")


def display_entries():
    if not os.path.exists(JOURNAL_FILE):
        messagebox.showinfo("Journal Entries", "No journal entries found.")
        return
    try:
        with open(JOURNAL_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            entries = list(reader)
            if not entries:
                messagebox.showinfo("Journal Entries", "No journal entries found.")
            else:
                entry_text = "\n".join([
                                           f"Timestamp: {entry.get('timestamp', '')}\nEntry Text: {entry.get('entry_text', '')}\nAttachments: {entry.get('attachments', '')}"
                                           for entry in entries])
                messagebox.showinfo("Journal Entries", entry_text)
        subprocess.run(["start", "", JOURNAL_FILE], shell=True)
    except Exception as e:
        messagebox.showerror("Error", f"Error reading journal entries: {e}")


def delete_entry(entry_index):
    if not os.path.exists(JOURNAL_FILE):
        messagebox.showinfo("Delete Entry", "No journal entries found.")
        return
    with open(JOURNAL_FILE, 'r', newline='') as file:
        reader = csv.reader(file)
        entries = list(reader)
    if 0 <= entry_index < len(entries):
        del entries[entry_index]
        with open(JOURNAL_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(entries)
        messagebox.showinfo("Success", "Journal entry deleted successfully.")
    else:
        messagebox.showinfo("Error", "Invalid entry index. No entry deleted.")


def add_reminder(reminder_text, remind_at):
    reminders = load_reminders()
    reminders.append({"text": reminder_text, "remind_at": remind_at})
    save_reminders(reminders)
    print("Reminder added successfully.")


def delete_reminder(reminder_index):
    reminders = load_reminders()
    if 0 <= reminder_index < len(reminders):
        del reminders[reminder_index]
        save_reminders(reminders)
        messagebox.showinfo("Success", "Reminder deleted successfully.")
    else:
        messagebox.showerror("Error", "Invalid index. Please enter a valid integer index.")


def remind():
    reminders = load_reminders()
    current_time = datetime.now()

    for reminder in reminders:
        remind_at = datetime.strptime(reminder["remind_at"], "%Y-%m-%d %H:%M:%S")
        if current_time >= remind_at:
            winsound.Beep(1000, 2000)
            reminder_text = f"Reminder: {reminder['text']} (Reminded at: {current_time})"
            messagebox.showinfo("Reminder", reminder_text)


    # Optionally, you can remove reminded reminders
    reminders = [reminder for reminder in reminders if
                 datetime.strptime(reminder["remind_at"], "%Y-%m-%d %H:%M:%S") > current_time]
    save_reminders(reminders)

def load_reminders():
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, 'r') as file:
            return json.load(file)
    return []


def save_reminders(reminders):
    with open(REMINDERS_FILE, 'w') as file:
        json.dump(reminders, file, indent=2)


def auto_remind():
    while True:
        remind()
        time.sleep(60)


def initialize():
    if not os.path.exists(ATTACHMENTS_DIR):
        os.makedirs(ATTACHMENTS_DIR)


def main():
    auto_remind_thread = threading.Thread(target=auto_remind)
    auto_remind_thread.daemon = True
    auto_remind_thread.start()
    initialize()
    root = tk.Tk()
    app = JournalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
