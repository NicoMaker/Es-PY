import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import threading
import queue

class UserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestione Utenti CRUD")
        
        # Inizializza la coda per la comunicazione tra thread
        self.queue = queue.Queue()

        # Usa un percorso assoluto per il database
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(script_dir, "Database.db")
        self.create_db_and_table()

        # Configurazione dello stile
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10), padding=5)
        style.configure("TLabel", font=("Arial", 10))

        # Creazione dei frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.form_frame = ttk.LabelFrame(self.main_frame, text="Dati Utente", padding="10")
        self.form_frame.pack(padx=10, pady=10, fill="x")

        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.pack(padx=10, pady=5, fill="x")

        self.table_frame = ttk.LabelFrame(self.main_frame, text="Lista Utenti", padding="10")
        self.table_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Campi di input
        self.create_form_fields()

        # Pulsanti
        self.create_buttons()

        # Tabella (Treeview)
        self.create_table()

        # Carica i dati all'avvio
        self.load_users()

        # Avvia il check periodico della coda
        self.root.after(100, self.process_queue)

    def create_db_and_table(self):
        """Crea il database e la tabella users se non esistono."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
        """)
        conn.commit()
        conn.close()

    def create_form_fields(self):
        """Crea le etichette e i campi di input nel form."""
        labels = ["Username", "Email", "Password"]
        self.entries = {}
        for i, label_text in enumerate(labels):
            label = ttk.Label(self.form_frame, text=f"{label_text}:")
            label.grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)
            entry = ttk.Entry(self.form_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[label_text.lower()] = entry

    def create_buttons(self):
        """Crea i pulsanti per le operazioni CRUD."""
        self.add_btn = ttk.Button(self.buttons_frame, text="Aggiungi Utente", command=self.add_user)
        self.add_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.update_btn = ttk.Button(self.buttons_frame, text="Aggiorna Utente", command=self.update_user)
        self.update_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.update_btn["state"] = "disabled"

        self.delete_btn = ttk.Button(self.buttons_frame, text="Elimina Utente", command=self.delete_user)
        self.delete_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.delete_btn["state"] = "disabled"
        
        self.clear_btn = ttk.Button(self.buttons_frame, text="Cancella Campi", command=self.clear_fields)
        self.clear_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    def create_table(self):
        """Crea la Treeview per visualizzare gli utenti."""
        columns = ("id", "username", "email", "password")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.heading("id", text="ID")
        self.tree.heading("username", text="Username")
        self.tree.heading("email", text="Email")
        self.tree.heading("password", text="Password")

        self.tree.column("id", width=50, stretch=tk.NO)
        self.tree.column("username", width=150)
        self.tree.column("email", width=200)
        self.tree.column("password", width=150)

        self.tree.bind("<<TreeviewSelect>>", self.on_select_user)

    def get_connection(self):
        """Ottiene una connessione al database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def load_users(self):
        """Avvia il caricamento degli utenti in un thread separato."""
        thread = threading.Thread(target=self._load_users_thread)
        thread.start()

    def _load_users_thread(self):
        """Carica gli utenti dal database (eseguito nel thread)."""
        try:
            conn = self.get_connection()
            users = conn.execute("SELECT * FROM users").fetchall()
            conn.close()
            self.queue.put(("load_users", users))
        except sqlite3.Error as e:
            self.queue.put(("error", f"Si è verificato un errore durante il caricamento: {e}"))

    def add_user(self):
        """Avvia l'aggiunta di un utente in un thread separato."""
        username = self.entries["username"].get().strip()
        email = self.entries["email"].get().strip()
        password = self.entries["password"].get().strip()
        if not username or not email or not password:
            messagebox.showerror("Errore", "Tutti i campi sono obbligatori!")
            return
        
        thread = threading.Thread(target=self._add_user_thread, args=(username, email, password))
        thread.start()

    def _add_user_thread(self, username, email, password):
        """Aggiunge un utente al database (eseguito nel thread)."""
        try:
            conn = self.get_connection()
            conn.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            conn.commit()
            conn.close()
            self.queue.put(("add_user_success", "Utente aggiunto con successo!"))
        except sqlite3.Error as e:
            self.queue.put(("error", f"Si è verificato un errore: {e}"))

    def update_user(self):
        """Avvia l'aggiornamento di un utente in un thread separato."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Errore", "Seleziona un utente da aggiornare.")
            return
        
        user_id = self.tree.item(selected_item, "values")[0]
        username = self.entries["username"].get().strip()
        email = self.entries["email"].get().strip()
        password = self.entries["password"].get().strip()
        if not username or not email or not password:
            messagebox.showerror("Errore", "Tutti i campi sono obbligatori!")
            return

        thread = threading.Thread(target=self._update_user_thread, args=(username, email, password, user_id))
        thread.start()

    def _update_user_thread(self, username, email, password, user_id):
        """Aggiorna un utente nel database (eseguito nel thread)."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET username = ?, email = ?, password = ?
                WHERE id = ?
            """, (username, email, password, user_id))
            conn.commit()
            conn.close()
            if cursor.rowcount > 0:
                self.queue.put(("update_user_success", "Utente aggiornato con successo!"))
            else:
                self.queue.put(("error", "Utente non trovato."))
        except sqlite3.Error as e:
            self.queue.put(("error", f"Si è verificato un errore: {e}"))

    def delete_user(self):
        """Avvia l'eliminazione di un utente in un thread separato."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Errore", "Seleziona un utente da eliminare.")
            return

        user_id = self.tree.item(selected_item, "values")[0]
        
        if messagebox.askyesno("Conferma Eliminazione", f"Sei sicuro di voler eliminare l'utente con ID {user_id}?"):
            thread = threading.Thread(target=self._delete_user_thread, args=(user_id,))
            thread.start()

    def _delete_user_thread(self, user_id):
        """Elimina un utente dal database (eseguito nel thread)."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            if cursor.rowcount > 0:
                self.queue.put(("delete_user_success", "Utente eliminato con successo!"))
            else:
                self.queue.put(("error", "Utente non trovato."))
        except sqlite3.Error as e:
            self.queue.put(("error", f"Si è verificato un errore: {e}"))

    def process_queue(self):
        """Processa i messaggi dalla coda, aggiornando la GUI."""
        try:
            while True:
                task, data = self.queue.get_nowait()
                if task == "load_users":
                    self.tree.delete(*self.tree.get_children())
                    for user in data:
                        self.tree.insert("", tk.END, values=tuple(user))
                elif task in ["add_user_success", "update_user_success", "delete_user_success"]:
                    messagebox.showinfo("Successo", data)
                    self.clear_fields()
                    self.load_users()
                elif task == "error":
                    messagebox.showerror("Errore", data)
                
                self.queue.task_done()
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)

    def on_select_user(self, event):
        """Popola i campi di input quando si seleziona un utente nella tabella e abilita i pulsanti."""
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            self.entries["username"].delete(0, tk.END)
            self.entries["username"].insert(0, values[1])
            self.entries["email"].delete(0, tk.END)
            self.entries["email"].insert(0, values[2])
            self.entries["password"].delete(0, tk.END)
            self.entries["password"].insert(0, values[3])

            self.add_btn["state"] = "disabled"
            self.update_btn["state"] = "normal"
            self.delete_btn["state"] = "normal"
        else:
            self.clear_fields()
            self.add_btn["state"] = "normal"
            self.update_btn["state"] = "disabled"
            self.delete_btn["state"] = "disabled"

    def clear_fields(self):
        """Pulisce tutti i campi di input e resetta i pulsanti."""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        
        self.tree.selection_remove(self.tree.focus())
        
        self.add_btn["state"] = "normal"
        self.update_btn["state"] = "disabled"
        self.delete_btn["state"] = "disabled"

if __name__ == "__main__":
    root = tk.Tk()
    app = UserApp(root)
    root.mainloop()