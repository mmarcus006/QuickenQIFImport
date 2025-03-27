import os
import sys
from typing import Dict, List, Optional, Any, Tuple

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    class DummyTk:
        def __init__(self, *args, **kwargs):
            pass
    tk = DummyTk()

from ..models.qif_models import QIFAccountType
from ..parsers.qif_parser import QIFParser
from ..parsers.csv_parser import CSVParser
from ..converters.qif_to_csv_converter import QIFToCSVConverter
from ..converters.csv_to_qif_converter import CSVToQIFConverter
from ..models.csv_models import CSVTemplate


class GUI:
    """Graphical User Interface for the QuickenQIFImport application."""
    
    def __init__(self):
        if not TKINTER_AVAILABLE:
            raise ImportError("Tkinter is not available. GUI cannot be initialized.")
        
        self.root = tk.Tk()
        
        self.root.title("QuickenQIFImport")
        self.root.geometry("800x600")
        
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tab_control = ttk.Notebook(self.main_frame)
        
        self.qif_to_csv_tab = ttk.Frame(self.tab_control)
        self.csv_to_qif_tab = ttk.Frame(self.tab_control)
        self.template_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.qif_to_csv_tab, text="QIF to CSV")
        self.tab_control.add(self.csv_to_qif_tab, text="CSV to QIF")
        self.tab_control.add(self.template_tab, text="Templates")
        
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        self._setup_qif_to_csv_tab()
        self._setup_csv_to_qif_tab()
        self._setup_template_tab()
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def _setup_qif_to_csv_tab(self):
        """Set up the QIF to CSV conversion tab."""
        frame = ttk.LabelFrame(self.qif_to_csv_tab, text="QIF to CSV Conversion")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="QIF Input File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.qif_input_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.qif_input_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse...", command=self._browse_qif_input).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(frame, text="CSV Output File:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.csv_output_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.csv_output_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse...", command=self._browse_csv_output).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Label(frame, text="Template (Optional):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.qif_template_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.qif_template_var, width=50).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse...", command=self._browse_qif_template).grid(row=2, column=2, padx=5, pady=5)
        
        ttk.Label(frame, text="Date Format:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.qif_date_format_var = tk.StringVar(value="%Y-%m-%d")
        ttk.Entry(frame, textvariable=self.qif_date_format_var, width=20).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame, text="CSV Delimiter:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.qif_delimiter_var = tk.StringVar(value=",")
        ttk.Entry(frame, textvariable=self.qif_delimiter_var, width=5).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(frame, text="Convert", command=self._convert_qif_to_csv).grid(row=5, column=1, padx=5, pady=20)
        
    def _setup_csv_to_qif_tab(self):
        """Set up the CSV to QIF conversion tab."""
        frame = ttk.LabelFrame(self.csv_to_qif_tab, text="CSV to QIF Conversion")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="CSV Input File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.csv_input_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.csv_input_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse...", command=self._browse_csv_input).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(frame, text="QIF Output File:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.qif_output_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.qif_output_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse...", command=self._browse_qif_output).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Label(frame, text="Account Type:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.account_type_var = tk.StringVar(value="Bank")
        account_types = [t.value for t in QIFAccountType]
        ttk.Combobox(frame, textvariable=self.account_type_var, values=account_types, state="readonly").grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=5
        )
        
        ttk.Label(frame, text="Template (Optional):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.csv_template_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.csv_template_var, width=50).grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse...", command=self._browse_csv_template).grid(row=3, column=2, padx=5, pady=5)
        
        ttk.Label(frame, text="Date Format:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.csv_date_format_var = tk.StringVar(value="%Y-%m-%d")
        ttk.Entry(frame, textvariable=self.csv_date_format_var, width=20).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(frame, text="Convert", command=self._convert_csv_to_qif).grid(row=5, column=1, padx=5, pady=20)
        
    def _setup_template_tab(self):
        """Set up the template management tab."""
        frame = ttk.LabelFrame(self.template_tab, text="Template Management")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Available Templates:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        template_frame = ttk.Frame(frame)
        template_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky=tk.NSEW)
        
        self.template_listbox = tk.Listbox(template_frame, width=70, height=10)
        self.template_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(template_frame, orient=tk.VERTICAL, command=self.template_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.template_listbox.config(yscrollcommand=scrollbar.set)
        
        ttk.Label(frame, text="Template Directory:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.template_dir_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.template_dir_var, width=50).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse...", command=self._browse_template_dir).grid(row=2, column=2, padx=5, pady=5)
        
        ttk.Button(frame, text="Refresh", command=self._refresh_templates).grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        
        action_frame = ttk.Frame(frame)
        action_frame.grid(row=4, column=0, columnspan=3, padx=5, pady=5)
        
        ttk.Button(action_frame, text="Create New", command=self._create_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="View", command=self._view_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Edit", command=self._edit_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Delete", command=self._delete_template).pack(side=tk.LEFT, padx=5)
        
    def _browse_qif_input(self):
        """Browse for QIF input file."""
        filename = filedialog.askopenfilename(
            title="Select QIF File",
            filetypes=[("QIF Files", "*.qif"), ("All Files", "*.*")]
        )
        if filename:
            self.qif_input_var.set(filename)
            
    def _browse_csv_output(self):
        """Browse for CSV output file."""
        filename = filedialog.asksaveasfilename(
            title="Save CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            defaultextension=".csv"
        )
        if filename:
            self.csv_output_var.set(filename)
            
    def _browse_qif_template(self):
        """Browse for QIF template file."""
        filename = filedialog.askopenfilename(
            title="Select Template File",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if filename:
            self.qif_template_var.set(filename)
            
    def _browse_csv_input(self):
        """Browse for CSV input file."""
        filename = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if filename:
            self.csv_input_var.set(filename)
            
    def _browse_qif_output(self):
        """Browse for QIF output file."""
        filename = filedialog.asksaveasfilename(
            title="Save QIF File",
            filetypes=[("QIF Files", "*.qif"), ("All Files", "*.*")],
            defaultextension=".qif"
        )
        if filename:
            self.qif_output_var.set(filename)
            
    def _browse_csv_template(self):
        """Browse for CSV template file."""
        filename = filedialog.askopenfilename(
            title="Select Template File",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if filename:
            self.csv_template_var.set(filename)
            
    def _browse_template_dir(self):
        """Browse for template directory."""
        directory = filedialog.askdirectory(title="Select Template Directory")
        if directory:
            self.template_dir_var.set(directory)
            self._refresh_templates()
            
    def _convert_qif_to_csv(self):
        """Convert QIF to CSV."""
        qif_file = self.qif_input_var.get()
        csv_file = self.csv_output_var.get()
        template_file = self.qif_template_var.get()
        date_format = self.qif_date_format_var.get()
        delimiter = self.qif_delimiter_var.get()
        
        if not qif_file:
            messagebox.showerror("Error", "Please select a QIF input file.")
            return
            
        if not csv_file:
            messagebox.showerror("Error", "Please specify a CSV output file.")
            return
            
        if not os.path.isfile(qif_file):
            messagebox.showerror("Error", f"Input file not found: {qif_file}")
            return
            
        template = None
        if template_file:
            if not os.path.isfile(template_file):
                messagebox.showerror("Error", f"Template file not found: {template_file}")
                return
                
            
        try:
            self.status_var.set(f"Converting {qif_file} to {csv_file}...")
            self.update_idletasks()
            
            converter = QIFToCSVConverter(date_format=date_format, delimiter=delimiter)
            converter.convert_file(qif_file, csv_file, template)
            
            self.status_var.set(f"Successfully converted {qif_file} to {csv_file}")
            messagebox.showinfo("Success", f"Successfully converted {qif_file} to {csv_file}")
        except Exception as e:
            self.status_var.set("Conversion failed")
            messagebox.showerror("Error", f"Conversion failed: {e}")
            
    def _convert_csv_to_qif(self):
        """Convert CSV to QIF."""
        csv_file = self.csv_input_var.get()
        qif_file = self.qif_output_var.get()
        account_type = self.account_type_var.get()
        template_file = self.csv_template_var.get()
        date_format = self.csv_date_format_var.get()
        
        if not csv_file:
            messagebox.showerror("Error", "Please select a CSV input file.")
            return
            
        if not qif_file:
            messagebox.showerror("Error", "Please specify a QIF output file.")
            return
            
        if not os.path.isfile(csv_file):
            messagebox.showerror("Error", f"Input file not found: {csv_file}")
            return
            
        template = None
        if template_file:
            if not os.path.isfile(template_file):
                messagebox.showerror("Error", f"Template file not found: {template_file}")
                return
                
            
        try:
            self.status_var.set(f"Converting {csv_file} to {qif_file}...")
            self.update_idletasks()
            
            account_type_enum = QIFAccountType(account_type)
            converter = CSVToQIFConverter(date_format=date_format)
            converter.convert_file(csv_file, qif_file, account_type_enum, template)
            
            self.status_var.set(f"Successfully converted {csv_file} to {qif_file}")
            messagebox.showinfo("Success", f"Successfully converted {csv_file} to {qif_file}")
        except Exception as e:
            self.status_var.set("Conversion failed")
            messagebox.showerror("Error", f"Conversion failed: {e}")
            
    def _refresh_templates(self):
        """Refresh the template list."""
        template_dir = self.template_dir_var.get()
        
        if not template_dir:
            return
            
        if not os.path.isdir(template_dir):
            messagebox.showerror("Error", f"Directory not found: {template_dir}")
            return
            
        self.template_listbox.delete(0, tk.END)
        
        template_files = [f for f in os.listdir(template_dir) if f.endswith('.json')]
        
        if not template_files:
            self.template_listbox.insert(tk.END, "No templates found")
            return
            
        for template_file in template_files:
            self.template_listbox.insert(tk.END, template_file)
            
        self.status_var.set(f"Found {len(template_files)} templates in {template_dir}")
        
    def _create_template(self):
        """Create a new template."""
        messagebox.showinfo("Info", "Template creation not implemented yet")
        
    def _view_template(self):
        """View the selected template."""
        selected = self.template_listbox.curselection()
        
        if not selected:
            messagebox.showerror("Error", "No template selected")
            return
            
        template_file = self.template_listbox.get(selected[0])
        template_dir = self.template_dir_var.get()
        
        if not template_dir:
            messagebox.showerror("Error", "No template directory specified")
            return
            
        template_path = os.path.join(template_dir, template_file)
        
        if not os.path.isfile(template_path):
            messagebox.showerror("Error", f"Template file not found: {template_path}")
            return
            
        messagebox.showinfo("Info", f"Viewing template: {template_path}")
        
    def _edit_template(self):
        """Edit the selected template."""
        selected = self.template_listbox.curselection()
        
        if not selected:
            messagebox.showerror("Error", "No template selected")
            return
            
        template_file = self.template_listbox.get(selected[0])
        template_dir = self.template_dir_var.get()
        
        if not template_dir:
            messagebox.showerror("Error", "No template directory specified")
            return
            
        template_path = os.path.join(template_dir, template_file)
        
        if not os.path.isfile(template_path):
            messagebox.showerror("Error", f"Template file not found: {template_path}")
            return
            
        messagebox.showinfo("Info", f"Editing template: {template_path}")
        
    def _delete_template(self):
        """Delete the selected template."""
        selected = self.template_listbox.curselection()
        
        if not selected:
            messagebox.showerror("Error", "No template selected")
            return
            
        template_file = self.template_listbox.get(selected[0])
        template_dir = self.template_dir_var.get()
        
        if not template_dir:
            messagebox.showerror("Error", "No template directory specified")
            return
            
        template_path = os.path.join(template_dir, template_file)
        
        if not os.path.isfile(template_path):
            messagebox.showerror("Error", f"Template file not found: {template_path}")
            return
            
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete {template_file}?"):
            try:
                os.remove(template_path)
                self._refresh_templates()
                self.status_var.set(f"Deleted template: {template_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete template: {e}")


def main():
    """Main entry point for the GUI."""
    try:
        app = GUI()
        app.root.mainloop()
    except ImportError as e:
        print(f"Error: {e}")
        print("GUI requires tkinter to be installed.")
        print("Please install tkinter and try again.")


if __name__ == "__main__":
    main()
