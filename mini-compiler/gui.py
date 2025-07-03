import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
from main import compile_c
import tempfile
import os
from tkinter.font import Font
import re

# Modern color scheme
THEME = {
    'bg_primary': '#FFFFFF',    # White background
    'bg_secondary': '#F5F5F5',  # Light gray background
    'text_primary': '#2C2C2C',  # Dark gray text
    'text_secondary': '#666666', # Medium gray text
    'accent': '#007ACC',        # Blue accent
    'accent_dark': '#005A9E',   # Darker blue
    'success': '#28A745',       # Green
    'warning': '#FFC107',       # Yellow
    'error': '#DC3545',         # Red
    'error_bg': '#FFF0F0',      # Light red background
    'highlight': '#E8F2FF'      # Light blue highlight
}

class GradientFrame(tk.Canvas):
    def __init__(self, parent, color1="#E6F3FF", color2="#FFE6F0", **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self._color1 = color1
        self._color2 = color2
        self.bind("<Configure>", self._draw_gradient)

    def _draw_gradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        limit = width
        (r1, g1, b1) = self.winfo_rgb(self._color1)
        (r2, g2, b2) = self.winfo_rgb(self._color2)
        r_ratio = float(r2-r1) / limit
        g_ratio = float(g2-g1) / limit
        b_ratio = float(b2-b1) / limit

        for i in range(limit):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = "#%4.4x%4.4x%4.4x" % (nr,ng,nb)
            self.create_line(i,height,i,0, tags=("gradient",), fill=color)
        self.lower("gradient")

class ModernButton(ttk.Button):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, style='Modern.TButton', **kwargs)

class LineNumberedText(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg=THEME['bg_primary'])
        
        # Create custom fonts
        self.text_font = Font(family="Consolas", size=11)
        self.line_num_font = Font(family="Consolas", size=10)
        
        # Create the line numbers text widget
        self.line_numbers = tk.Text(self, width=4, padx=5, pady=5, takefocus=0, border=0,
                                  background=THEME['bg_secondary'],
                                  foreground=THEME['text_secondary'],
                                  font=self.line_num_font,
                                  state='disabled',
                                  wrap='none')
        self.line_numbers.pack(side='left', fill='y')

        # Create the main text widget with syntax highlighting colors
        self.text = tk.Text(self, wrap='none', font=self.text_font,
                           background=THEME['bg_primary'],
                           foreground=THEME['text_primary'],
                           insertbackground=THEME['text_primary'],
                           selectbackground=THEME['highlight'],
                           selectforeground=THEME['text_primary'],
                           pady=5, padx=5,
                           *args, **kwargs)
        self.text.pack(side='left', fill='both', expand=True)

        # Create a modern scrollbar
        self.scrollbar = ttk.Scrollbar(self, style='Modern.Vertical.TScrollbar')
        self.scrollbar.pack(side='right', fill='y')

        # Link scrollbar to text widget
        self.scrollbar.config(command=self.on_scroll)
        self.text.config(yscrollcommand=self.scrollbar.set)

        # Configure error highlighting
        self.text.tag_configure('error_line', background=THEME['error_bg'])
        self.text.tag_configure('error_highlight', background=THEME['error'], underline=1)

        # Configure syntax highlighting with colors suitable for light theme
        self.text.tag_configure('keywords', foreground='#0000CC')   # Dark blue
        self.text.tag_configure('strings', foreground='#008000')    # Green
        self.text.tag_configure('comments', foreground='#808080')   # Gray
        self.text.tag_configure('numbers', foreground='#800080')    # Purple
        self.text.tag_configure('operators', foreground='#FF0000')  # Red

        # Bind events
        self.text.bind('<KeyPress>', self.on_key_press)
        self.text.bind('<KeyRelease>', self.on_key_release)
        self.text.bind('<MouseWheel>', self.on_mouse_wheel)
        
        # Initialize line numbers
        self.update_line_numbers()

    def on_scroll(self, *args):
        # Sync text and line numbers on scroll
        self.text.yview(*args)
        self.line_numbers.yview(*args)

    def on_mouse_wheel(self, event):
        # Handle mouse wheel scrolling
        self.text.yview_scroll(int(-1 * (event.delta / 120)), 'units')
        self.line_numbers.yview_scroll(int(-1 * (event.delta / 120)), 'units')
        return 'break'

    def on_key_press(self, event):
        # Handle special key combinations
        if event.keysym == 'Tab':
            self.text.insert(tk.INSERT, ' ' * 4)
            return 'break'

    def on_key_release(self, event):
        self.update_line_numbers()
        self.highlight_syntax()

    def update_line_numbers(self):
        # Update the line numbers
        line_count = self.text.get('1.0', tk.END).count('\n')
        line_numbers_text = '\n'.join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_numbers_text)
        self.line_numbers.config(state='disabled')

    def highlight_syntax(self):
        # Remove existing tags
        for tag in self.text.tag_names():
            self.text.tag_remove(tag, "1.0", tk.END)

        # Define syntax patterns
        patterns = {
            'keywords': r'\b(void|int|float|if|else|while|for|return|printf)\b',
            'strings': r'"[^"]*"',
            'comments': r'//.*$',
            'numbers': r'\b\d+(\.\d+)?\b',
            'operators': r'[+\-*/=<>!&|]'
        }

        # Apply highlighting
        content = self.text.get("1.0", tk.END)
        for pattern_name, pattern in patterns.items():
            for match in re.finditer(pattern, content, re.MULTILINE):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text.tag_add(pattern_name, start, end)

    def highlight_error(self, line_number, start_col=None, end_col=None):
        # Remove previous error highlights
        self.text.tag_remove('error_line', '1.0', tk.END)
        self.text.tag_remove('error_highlight', '1.0', tk.END)
        
        if line_number:
            # Highlight the entire line
            self.text.tag_add('error_line', f'{line_number}.0', f'{line_number}.end')
            
            # Highlight specific portion if columns are provided
            if start_col is not None and end_col is not None:
                self.text.tag_add('error_highlight', f'{line_number}.{start_col}', f'{line_number}.{end_col}')
            
            # Ensure the error line is visible
            self.text.see(f'{line_number}.0')

    def clear_error_highlights(self):
        self.text.tag_remove('error_line', '1.0', tk.END)
        self.text.tag_remove('error_highlight', '1.0', tk.END)

class CompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Compiler")
        
        # Configure root window
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        self.root.configure(bg=THEME['bg_primary'])
        
        # Configure modern styles
        self.configure_styles()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main container
        self.main_container = ttk.PanedWindow(root, orient=tk.HORIZONTAL, style='Modern.TPanedwindow')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # Create left panel (C code)
        self.left_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
        self.main_container.add(self.left_frame, weight=1)
        
        # Create right panel (Python code)
        self.right_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
        self.main_container.add(self.right_frame, weight=1)
        
        # Create error panel
        self.create_error_panel()
        
        # Create status bar
        self.create_status_bar()
        
        # Add components to left panel
        self.create_left_panel()
        
        # Add components to right panel
        self.create_right_panel()
        
        # Initialize with sample code
        self.load_sample_code()

    def configure_styles(self):
        style = ttk.Style()
        
        # Configure modern theme elements
        style.configure('Modern.TFrame',
                       background=THEME['bg_primary'])
        
        style.configure('Modern.TLabelframe',
                       background=THEME['bg_primary'])
        
        style.configure('Modern.TLabelframe.Label',
                       background=THEME['bg_primary'],
                       foreground=THEME['text_primary'],
                       font=('Segoe UI', 10, 'bold'))
        
        # Configure button style
        style.configure('Modern.TButton',
                       background=THEME['accent'],
                       foreground=THEME['text_primary'],
                       font=('Segoe UI', 9),
                       padding=(10, 5))
        
        style.map('Modern.TButton',
                  background=[('active', THEME['accent_dark']),
                            ('pressed', THEME['accent_dark'])],
                  foreground=[('active', THEME['bg_primary']),
                            ('pressed', THEME['bg_primary'])])
        
        # Configure scrollbar style
        style.configure('Modern.Vertical.TScrollbar',
                       background=THEME['bg_secondary'],
                       troughcolor=THEME['bg_primary'],
                       arrowcolor=THEME['text_primary'],
                       bordercolor=THEME['bg_secondary'],
                       width=12)
        
        style.configure('Modern.Horizontal.TScrollbar',
                       background=THEME['bg_secondary'],
                       troughcolor=THEME['bg_primary'],
                       arrowcolor=THEME['text_primary'],
                       bordercolor=THEME['bg_secondary'],
                       height=12)
        
        style.configure('Modern.TPanedwindow',
                       background=THEME['bg_primary'],
                       sashrelief='flat')
        
        style.configure('Modern.TLabel',
                       background=THEME['bg_primary'],
                       foreground=THEME['text_primary'])

    def create_toolbar(self):
        toolbar = ttk.Frame(self.root, style='Modern.TFrame')
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        # Create modern buttons with icons and better styling
        buttons = [
            ("New File", self.new_file),
            ("Open", self.open_file),
            ("Save", self.save_file),
            (None, None),  # Separator
            ("Compile", self.compile_code),
            ("Run", self.run_code),
            (None, None),  # Separator
            ("Load Sample", self.load_sample_code)
        ]
        
        for btn_text, btn_command in buttons:
            if btn_text is None:
                # Add separator
                ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, padx=10, fill='y', pady=2)
            else:
                btn = ModernButton(toolbar, text=btn_text, command=btn_command)
                btn.pack(side=tk.LEFT, padx=2)

    def create_left_panel(self):
        frame = ttk.LabelFrame(self.left_frame, text="C Code Editor", style='Modern.TLabelframe')
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.c_code_editor = LineNumberedText(frame)
        self.c_code_editor.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    def create_right_panel(self):
        # Python code panel
        python_frame = ttk.LabelFrame(self.right_frame, text="Generated Python Code", style='Modern.TLabelframe')
        python_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.python_code_display = LineNumberedText(python_frame)
        self.python_code_display.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.python_code_display.text.config(state='disabled')
        
        # Output panel
        output_frame = ttk.LabelFrame(self.right_frame, text="Output", style='Modern.TLabelframe')
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.output_display = tk.Text(output_frame, height=10, wrap=tk.WORD,
                                    background=THEME['bg_secondary'],
                                    foreground=THEME['text_primary'],
                                    font=('Consolas', 10))
        self.output_display.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.output_display.config(state='disabled')

    def create_error_panel(self):
        self.error_frame = ttk.LabelFrame(self.root, text="Compiler Messages", 
                                        style='Modern.TLabelframe')
        self.error_frame.pack(fill=tk.X, padx=10, pady=(5, 0))
        
        self.error_display = tk.Text(self.error_frame, height=3, wrap=tk.WORD,
                                   background=THEME['bg_secondary'],
                                   foreground=THEME['text_primary'],
                                   insertbackground=THEME['text_primary'],
                                   selectbackground=THEME['highlight'],
                                   selectforeground=THEME['text_primary'],
                                   font=('Consolas', 10))
        self.error_display.pack(fill=tk.X, padx=2, pady=2)
        self.error_display.config(state='disabled')
        
        # Configure error text tags with improved colors
        self.error_display.tag_configure('error', foreground=THEME['error'])
        self.error_display.tag_configure('warning', foreground=THEME['warning'])
        self.error_display.tag_configure('success', foreground=THEME['success'])

    def create_status_bar(self):
        self.status_bar = ttk.Label(self.root, text="Ready",
                                   style='Modern.TLabel',
                                   relief=tk.SUNKEN,
                                   anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

    def create_menu_bar(self):
        menubar = tk.Menu(self.root, 
                         bg=THEME['bg_primary'],
                         fg=THEME['text_primary'],
                         activebackground=THEME['highlight'],
                         activeforeground=THEME['text_primary'])
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0,
                           bg=THEME['bg_primary'],
                           fg=THEME['text_primary'],
                           activebackground=THEME['highlight'],
                           activeforeground=THEME['text_primary'])
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0,
                           bg=THEME['bg_primary'],
                           fg=THEME['text_primary'],
                           activebackground=THEME['highlight'],
                           activeforeground=THEME['text_primary'])
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=lambda: self.c_code_editor.text.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.c_code_editor.text.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.c_code_editor.text.event_generate("<<Paste>>"))
        
        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0,
                          bg=THEME['bg_primary'],
                          fg=THEME['text_primary'],
                          activebackground=THEME['highlight'],
                          activeforeground=THEME['text_primary'])
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Compile", command=self.compile_code)
        run_menu.add_command(label="Run", command=self.run_code)

    def new_file(self):
        if messagebox.askyesno("New File", "Do you want to clear the current code?"):
            self.c_code_editor.text.delete('1.0', tk.END)
            self.python_code_display.text.config(state='normal')
            self.python_code_display.text.delete('1.0', tk.END)
            self.python_code_display.text.config(state='disabled')
            self.output_display.config(state='normal')
            self.output_display.delete('1.0', tk.END)
            self.output_display.config(state='disabled')

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("C files", "*.c"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    self.c_code_editor.text.delete('1.0', tk.END)
                    self.c_code_editor.text.insert('1.0', content)
                    self.status_bar.config(text=f"Opened: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")

    def save_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".c",
            filetypes=[("C files", "*.c"), ("All files", "*.*")]
        )
        if file_path:
            try:
                content = self.c_code_editor.text.get('1.0', tk.END)
                with open(file_path, 'w') as file:
                    file.write(content)
                self.status_bar.config(text=f"Saved: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def load_sample_code(self):
        sample_code = '''void main() {
    // Variable declarations
    int x;
    int y;
    float result;

    // Assignments and arithmetic
    x = 10;
    y = 5;
    result = x + y * 2;
    printf("Initial result: %f\\n", result);

    // If-else statement
    if (result > 20) {
        result = result - 10;
        printf("Result was > 20, subtracted 10: %f\\n", result);
    } else {
        result = result + 5;
        printf("Result was <= 20, added 5: %f\\n", result);
    }

    // While loop
    while (x > 0) {
        x = x - 1;
        result = result + 1;
        printf("In while loop, x = %d, result = %f\\n", x, result);
    }
}'''
        self.c_code_editor.text.delete('1.0', tk.END)
        self.c_code_editor.text.insert('1.0', sample_code)
        self.c_code_editor.highlight_syntax()
        self.status_bar.config(text="Loaded sample code")

    def show_error(self, error_msg, line_number=None, start_col=None, end_col=None, level='error'):
        # Update error display with modern styling
        self.error_display.config(state='normal')
        self.error_display.delete('1.0', tk.END)
        
        if line_number:
            error_text = f"⚠ Line {line_number}: {error_msg}"
        else:
            error_text = f"⚠ {error_msg}"
            
        self.error_display.insert('1.0', error_text, level)
        self.error_display.config(state='disabled')
        
        # Highlight error in code editor if line number is provided
        if line_number:
            self.c_code_editor.highlight_error(line_number, start_col, end_col)
        
        # Update status bar with error icon
        self.status_bar.config(text=f"❌ Error: {error_msg}")

    def show_success(self, message):
        self.error_display.config(state='normal')
        self.error_display.delete('1.0', tk.END)
        self.error_display.insert('1.0', f"✓ {message}", 'success')
        self.error_display.config(state='disabled')
        self.status_bar.config(text=f"✓ {message}")

    def compile_code(self):
        try:
            self.clear_error()
            self.status_bar.config(text="Compiling...")
            
            # Get the C code from the editor
            c_code = self.c_code_editor.text.get('1.0', tk.END)
            
            try:
                # Compile the code
                python_code = compile_c(c_code)
                
                # Display the generated Python code
                self.python_code_display.text.config(state='normal')
                self.python_code_display.text.delete('1.0', tk.END)
                self.python_code_display.text.insert('1.0', python_code)
                self.python_code_display.text.config(state='disabled')
                
                # Save Python code to a temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_py_file:
                    temp_py_file.write(python_code)
                    self.current_py_file = temp_py_file.name
                
                self.status_bar.config(text="Compilation successful")
                self.show_success("Code compiled successfully!")
                
            except Exception as e:
                error_msg = str(e)
                line_number = None
                start_col = None
                end_col = None
                
                # Try to extract line number from error message
                import re
                line_match = re.search(r'line (\d+)', error_msg, re.IGNORECASE)
                if line_match:
                    line_number = int(line_match.group(1))
                
                # Try to extract column information
                col_match = re.search(r'column (\d+)-(\d+)', error_msg)
                if col_match:
                    start_col = int(col_match.group(1))
                    end_col = int(col_match.group(2))
                
                self.show_error(error_msg, line_number, start_col, end_col)
                
        except Exception as e:
            self.show_error(str(e))

    def run_code(self):
        if not hasattr(self, 'current_py_file'):
            self.show_error("Please compile the code first!")
            return
        
        try:
            self.clear_error()
            self.status_bar.config(text="Running code...")
            
            # Redirect stdout to capture output
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                try:
                    # Execute the Python code
                    with open(self.current_py_file, 'r') as file:
                        exec(file.read())
                except Exception as e:
                    error_msg = str(e)
                    line_number = None
                    
                    # Try to extract line number from traceback
                    import traceback
                    tb = traceback.extract_tb(sys.exc_info()[2])
                    if tb:
                        line_number = tb[-1].lineno
                    
                    self.show_error(f"Runtime Error: {error_msg}", line_number)
                    return
            
            # Get the output and display it
            output = f.getvalue()
            self.output_display.config(state='normal')
            self.output_display.delete('1.0', tk.END)
            self.output_display.insert('1.0', output)
            self.output_display.config(state='disabled')
            
            self.status_bar.config(text="Code execution completed")
            
        except Exception as e:
            self.show_error(f"Runtime Error: {str(e)}")
        finally:
            # Clean up the temporary Python file
            if hasattr(self, 'current_py_file'):
                try:
                    os.unlink(self.current_py_file)
                except:
                    pass

    def clear_error(self):
        # Clear error display
        self.error_display.config(state='normal')
        self.error_display.delete('1.0', tk.END)
        self.error_display.config(state='disabled')
        
        # Clear error highlights
        self.c_code_editor.clear_error_highlights()
        
        # Reset status bar
        self.status_bar.config(text="Ready")

def main():
    root = tk.Tk()
    app = CompilerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 