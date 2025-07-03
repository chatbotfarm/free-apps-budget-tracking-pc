import json
from pathlib import Path
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

DATA_FILE = Path('transactions.json')

class BudgetTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('ChatbotFarm Budget Tracker')
        self.geometry('800x600')
        self.resizable(False, False)
        self.transactions = []
        self._create_widgets()
        self._load_transactions()
        self._refresh_tree()
        self._update_summary()

    def _create_widgets(self):
        # Entry frame
        entry_frame = ttk.LabelFrame(self, text='New Transaction')
        entry_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(entry_frame, text='Amount:').grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.amount_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.amount_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(entry_frame, text='Type:').grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.type_var = tk.StringVar(value='Income')
        ttk.Combobox(entry_frame, textvariable=self.type_var, values=['Income', 'Expense'], state='readonly', width=10).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(entry_frame, text='Category:').grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.category_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.category_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(entry_frame, text='Description:').grid(row=1, column=2, padx=5, pady=5, sticky='e')
        self.desc_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.desc_var).grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(entry_frame, text='Date:').grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.date_var = tk.StringVar(value=date.today().isoformat())
        ttk.Entry(entry_frame, textvariable=self.date_var).grid(row=2, column=1, padx=5, pady=5)

        add_btn = ttk.Button(entry_frame, text='Add Entry', command=self._add_entry)
        add_btn.grid(row=2, column=2, padx=5, pady=5)

        clear_btn = ttk.Button(entry_frame, text='Clear Fields', command=self._clear_fields)
        clear_btn.grid(row=2, column=3, padx=5, pady=5)

        # Treeview for transactions
        table_frame = ttk.Frame(self)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('date', 'type', 'category', 'description', 'amount')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=100, anchor='center')
        self.tree.column('description', width=200, anchor='w')

        vsb = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side='right', fill='y')
        self.tree.pack(fill='both', expand=True)

        del_btn = ttk.Button(self, text='Delete Selected', command=self._delete_selected)
        del_btn.pack(pady=(0, 10))

        # Summary frame
        summary = ttk.LabelFrame(self, text='Summary')
        summary.pack(fill='x', padx=10, pady=10)

        self.income_var = tk.StringVar(value='0.00')
        self.expense_var = tk.StringVar(value='0.00')
        self.balance_var = tk.StringVar(value='0.00')

        ttk.Label(summary, text='Total Income:').grid(row=0, column=0, padx=5, pady=5, sticky='e')
        ttk.Label(summary, textvariable=self.income_var).grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(summary, text='Total Expenses:').grid(row=0, column=2, padx=5, pady=5, sticky='e')
        ttk.Label(summary, textvariable=self.expense_var).grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(summary, text='Balance:').grid(row=0, column=4, padx=5, pady=5, sticky='e')
        ttk.Label(summary, textvariable=self.balance_var).grid(row=0, column=5, padx=5, pady=5, sticky='w')

        export_btn = ttk.Button(summary, text='Export CSV', command=self._export_csv)
        export_btn.grid(row=0, column=6, padx=5, pady=5)

        # Footer
        footer = ttk.Label(self, text='Connecting Business To The Grid')
        footer.pack(side='bottom', pady=5)

    def _load_transactions(self):
        if DATA_FILE.exists():
            try:
                self.transactions = json.loads(DATA_FILE.read_text())
            except json.JSONDecodeError:
                messagebox.showerror('Error', 'Failed to load transactions file.')
                self.transactions = []
        else:
            self.transactions = []

    def _save_transactions(self):
        DATA_FILE.write_text(json.dumps(self.transactions, indent=2))

    def _add_entry(self):
        try:
            amount = float(self.amount_var.get())
        except ValueError:
            messagebox.showerror('Invalid Input', 'Amount must be a number.')
            return

        entry = {
            'date': self.date_var.get(),
            'type': self.type_var.get(),
            'category': self.category_var.get(),
            'description': self.desc_var.get(),
            'amount': amount
        }
        self.transactions.append(entry)
        self._save_transactions()
        self._refresh_tree()
        self._update_summary()
        self._clear_fields()

    def _clear_fields(self):
        self.amount_var.set('')
        self.category_var.set('')
        self.desc_var.set('')
        self.date_var.set(date.today().isoformat())
        self.type_var.set('Income')

    def _refresh_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for tx in self.transactions:
            self.tree.insert('', 'end', values=(tx['date'], tx['type'], tx['category'], tx['description'], f"{tx['amount']:.2f}"))

    def _update_summary(self):
        income = sum(tx['amount'] for tx in self.transactions if tx['type'] == 'Income')
        expense = sum(tx['amount'] for tx in self.transactions if tx['type'] == 'Expense')
        balance = income - expense
        self.income_var.set(f"{income:.2f}")
        self.expense_var.set(f"{expense:.2f}")
        self.balance_var.set(f"{balance:.2f}")

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        if messagebox.askyesno('Delete', 'Delete selected transaction?'):
            self.transactions.pop(index)
            self._save_transactions()
            self._refresh_tree()
            self._update_summary()

    def _export_csv(self):
        if not self.transactions:
            messagebox.showinfo('No Data', 'No transactions to export.')
            return
        file = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files','*.csv')])
        if not file:
            return
        try:
            import csv
            with open(file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['date','type','category','description','amount'])
                writer.writeheader()
                writer.writerows(self.transactions)
            messagebox.showinfo('Exported', f'Transactions exported to {file}')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to export: {e}')

if __name__ == '__main__':
    app = BudgetTracker()
    app.mainloop()
