import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import tempfile

class DCDCConverterDesigner:
    def __init__(self, root):
        self.root = root
        self.root.title("DC-DC Converter Designer")
        self.root.geometry("1200x800")
        self.setup_ui()
        self.current_design = {}
        self.create_menus()
        
    def setup_ui(self):
        # Create main frames
        self.input_frame = ttk.LabelFrame(self.root, text="Design Parameters", padding=10)
        self.input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        self.output_frame = ttk.LabelFrame(self.root, text="Calculation Results", padding=10)
        self.output_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        
        self.graph_frame = ttk.LabelFrame(self.root, text="Waveform Visualization", padding=10)
        self.graph_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        
        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Setup input controls with auto-calculation
        self.setup_input_controls()
        self.setup_output_controls()
        self.setup_graph_controls()
        
    def setup_input_controls(self):
        # Converter type selection
        ttk.Label(self.input_frame, text="Converter Type:").grid(row=0, column=0, sticky="e", pady=2)
        self.converter_type = ttk.Combobox(self.input_frame, values=["Buck", "Boost", "Buck-Boost"])
        self.converter_type.grid(row=0, column=1, pady=2, sticky="w")
        self.converter_type.current(0)
        self.converter_type.bind("<<ComboboxSelected>>", self.on_converter_change)
        
        # Input parameters with ripple specifications
        self.params = {
            "input_voltage": {"label": "Input Voltage (Vin)", "unit": "V", "default": "12", "row": 1},
            "output_voltage": {"label": "Output Voltage (Vout)", "unit": "V", "default": "5", "row": 2},
            "output_current": {"label": "Output Current (Iout)", "unit": "A", "default": "2", "row": 3},
            "switching_freq": {"label": "Switching Frequency", "unit": "kHz", "default": "500", "row": 4},
            "efficiency": {"label": "Efficiency (η)", "unit": "", "default": "0.9", "row": 5},
            "voltage_ripple": {"label": "Voltage Ripple", "unit": "%", "default": "1", "row": 6},
            "current_ripple": {"label": "Current Ripple", "unit": "%", "default": "30", "row": 7}
        }
        
        self.entries = {}
        for key, param in self.params.items():
            ttk.Label(self.input_frame, text=param["label"]+":").grid(row=param["row"], column=0, sticky="e", pady=2)
            frame = ttk.Frame(self.input_frame)
            frame.grid(row=param["row"], column=1, sticky="w")
            self.entries[key] = ttk.Entry(frame, width=10)
            self.entries[key].insert(0, param["default"])
            self.entries[key].pack(side="left")
            ttk.Label(frame, text=param["unit"]).pack(side="left", padx=5)
            
        # Calculated components display
        ttk.Label(self.input_frame, text="Calculated Components:").grid(row=8, column=0, columnspan=2, pady=(10,2), sticky="w")
        
        ttk.Label(self.input_frame, text="Inductor (L):").grid(row=9, column=0, sticky="e", pady=2)
        self.inductor_value = ttk.Label(self.input_frame, text="", width=10)
        self.inductor_value.grid(row=9, column=1, sticky="w")
        ttk.Label(self.input_frame, text="µH").grid(row=9, column=1, sticky="e")
        
        ttk.Label(self.input_frame, text="Capacitor (C):").grid(row=10, column=0, sticky="e", pady=2)
        self.capacitor_value = ttk.Label(self.input_frame, text="", width=10)
        self.capacitor_value.grid(row=10, column=1, sticky="w")
        ttk.Label(self.input_frame, text="µF").grid(row=10, column=1, sticky="e")
            
        # Buttons
        ttk.Button(self.input_frame, text="Calculate", command=self.calculate).grid(row=11, column=0, columnspan=2, pady=10)
        
    def setup_output_controls(self):
        # Results display
        self.results_text = tk.Text(self.output_frame, height=15, width=40, wrap=tk.WORD)
        self.results_text.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(self.output_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.results_text.config(yscrollcommand=scrollbar.set)
        
        # Component ratings
        self.ratings_frame = ttk.LabelFrame(self.output_frame, text="Component Ratings", padding=10)
        self.ratings_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        # Add peak and average current labels
        ratings_inner_frame = ttk.Frame(self.ratings_frame)
        ratings_inner_frame.pack(fill="x", pady=(0, 5))
        ttk.Label(ratings_inner_frame, text="Inductor Current (avg):").grid(row=0, column=0, sticky="e", padx=2)
        self.inductor_avg_label = ttk.Label(ratings_inner_frame, text="", width=10)
        self.inductor_avg_label.grid(row=0, column=1, sticky="w", padx=2)
        ttk.Label(ratings_inner_frame, text="A").grid(row=0, column=2, sticky="w")

        ttk.Label(ratings_inner_frame, text="Inductor Current (peak):").grid(row=1, column=0, sticky="e", padx=2)
        self.inductor_peak_label = ttk.Label(ratings_inner_frame, text="", width=10)
        self.inductor_peak_label.grid(row=1, column=1, sticky="w", padx=2)
        ttk.Label(ratings_inner_frame, text="A").grid(row=1, column=2, sticky="w")

        self.ratings_text = tk.Text(self.ratings_frame, height=8, width=40, wrap=tk.WORD)
        self.ratings_text.pack(fill="both", expand=True)

        # Configure grid weights
        self.output_frame.grid_rowconfigure(0, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)
        
    def setup_graph_controls(self):
        # Create figure and canvas (EXACTLY AS IN ORIGINAL CODE)
        self.figure = plt.Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add toolbar (EXACTLY AS IN ORIGINAL CODE)
        toolbar = NavigationToolbar2Tk(self.canvas, self.graph_frame)
        toolbar.update()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Graph selection (EXACTLY AS IN ORIGINAL CODE)
        self.graph_var = tk.StringVar(value="all")
        graph_frame = ttk.Frame(self.graph_frame)
        graph_frame.pack(fill="x", pady=5)
        
        ttk.Label(graph_frame, text="Display:").pack(side="left")
        ttk.Radiobutton(graph_frame, text="All", variable=self.graph_var, value="all", command=self.update_graphs).pack(side="left", padx=5)
        ttk.Radiobutton(graph_frame, text="Duty Cycle", variable=self.graph_var, value="duty", command=self.update_graphs).pack(side="left", padx=5)
        ttk.Radiobutton(graph_frame, text="Inductor Current", variable=self.graph_var, value="current", command=self.update_graphs).pack(side="left", padx=5)
        ttk.Radiobutton(graph_frame, text="Voltages", variable=self.graph_var, value="voltage", command=self.update_graphs).pack(side="left", padx=5)
        
    def create_menus(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Design", command=self.new_design)
        file_menu.add_command(label="Open Design", command=self.open_design)
        file_menu.add_command(label="Save Design", command=self.save_design)
        file_menu.add_separator()
        file_menu.add_command(label="Export Report", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="User Guide", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
    def on_converter_change(self, event=None):
        # Update UI based on converter type
        conv_type = self.converter_type.get()
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        self.ratings_text.delete(1.0, tk.END)
        
        # Update default values based on converter type
        if conv_type == "Buck":
            self.entries["output_voltage"].delete(0, tk.END)
            self.entries["output_voltage"].insert(0, "5")
        elif conv_type == "Boost":
            self.entries["output_voltage"].delete(0, tk.END)
            self.entries["output_voltage"].insert(0, "24")
        elif conv_type == "Buck-Boost":
            self.entries["output_voltage"].delete(0, tk.END)
            self.entries["output_voltage"].insert(0, "-12")
            
    def validate_inputs(self):
        try:
            # Get all values
            values = {}
            for key in self.entries:
                values[key] = float(self.entries[key].get())
                
            # Basic validation
            if values["input_voltage"] <= 0:
                raise ValueError("Input voltage must be positive")
            if values["output_voltage"] == 0:
                raise ValueError("Output voltage cannot be zero")
            if values["output_current"] <= 0:
                raise ValueError("Output current must be positive")
            if values["switching_freq"] <= 0:
                raise ValueError("Switching frequency must be positive")
            if not (0 < values["efficiency"] <= 1):
                raise ValueError("Efficiency must be between 0 and 1")
            if values["voltage_ripple"] <= 0:
                raise ValueError("Voltage ripple must be positive")
            if values["current_ripple"] <= 0:
                raise ValueError("Current ripple must be positive")
                
            # Converter-specific validation
            conv_type = self.converter_type.get()
            if conv_type == "Buck" and values["output_voltage"] >= values["input_voltage"]:
                raise ValueError("For Buck converter, output voltage must be less than input voltage")
            elif conv_type == "Boost" and values["output_voltage"] <= values["input_voltage"]:
                raise ValueError("For Boost converter, output voltage must be greater than input voltage")
                
            return True, values
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return False, None
            
    def calculate(self):
        valid, values = self.validate_inputs()
        if not valid:
            return
            
        conv_type = self.converter_type.get()
        vin = values["input_voltage"]
        vout = values["output_voltage"]
        iout = values["output_current"]
        fsw = values["switching_freq"] * 1000  # Convert to Hz
        eta = values["efficiency"]
        vripple_pct = values["voltage_ripple"] / 100  # Convert to ratio
        iripple_pct = values["current_ripple"] / 100  # Convert to ratio
        
        # Calculate duty cycle
        if conv_type == "Buck":
            d = vout / (vin * eta)
        elif conv_type == "Boost":
            d = 1 - (vin * eta / vout)
        elif conv_type == "Buck-Boost":
            d = vout / (vout - vin * eta) if vout < 0 else vout / (vin * eta + vout)
        
        # Calculate currents
        if conv_type == "Buck":
            iin = iout * vout / (vin * eta)
            il_avg = iout
        elif conv_type == "Boost":
            iin = iout * vout / (vin * eta)
            il_avg = iin
        elif conv_type == "Buck-Boost":
            iin = iout * abs(vout) / (vin * eta)
            il_avg = iin / (1 - d)
        
        # AUTO-CALCULATE INDUCTOR VALUE
        delta_il = il_avg * iripple_pct
        if conv_type == "Buck":
            l = (vin - vout) * d / (fsw * delta_il)
        elif conv_type == "Boost":
            l = vin * d / (fsw * delta_il)
        elif conv_type == "Buck-Boost":
            l = vin * d / (fsw * delta_il)
        
        # AUTO-CALCULATE CAPACITOR VALUE
        delta_vout = vout * vripple_pct
        if conv_type == "Buck":
            c = (1 - d) / (8 * l * fsw**2 * delta_vout)
        elif conv_type == "Boost":
            c = iout * d / (fsw * delta_vout)
        elif conv_type == "Buck-Boost":
            c = iout * d / (fsw * delta_vout)
        
        # Calculate actual ripples
        if conv_type == "Buck":
            delta_il_actual = (vin - vout) * d / (fsw * l)
            delta_vout_actual = (1 - d) / (8 * l * c * fsw**2)
        elif conv_type == "Boost":
            delta_il_actual = vin * d / (fsw * l)
            delta_vout_actual = iout * d / (fsw * c)
        elif conv_type == "Buck-Boost":
            delta_il_actual = vin * d / (fsw * l)
            delta_vout_actual = iout * d / (fsw * c)
        
        # Peak currents
        il_peak = il_avg + delta_il_actual / 2
        iswitch_peak = il_peak
        idiode_peak = il_peak
        
        # Store results
        self.current_design = {
            "type": conv_type,
            "parameters": {
                "vin": vin,
                "vout": vout,
                "iout": iout,
                "fsw": fsw,
                "efficiency": eta,
                "duty_cycle": d,
                "inductor": l,
                "capacitor": c,
                "voltage_ripple": delta_vout_actual,
                "current_ripple": delta_il_actual,
                "input_current": iin,
                "inductor_current_avg": il_avg,
                "inductor_current_peak": il_peak,
                "switch_current_peak": iswitch_peak,
                "diode_current_peak": idiode_peak
            }
        }
        
        # Update calculated values display
        self.inductor_value.config(text=f"{l*1e6:.2f}")
        self.capacitor_value.config(text=f"{c*1e6:.2f}")
        
        # Display results
        self.display_results()
        self.update_graphs()
        
    def display_results(self):
        design = self.current_design
        params = design["parameters"]
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        self.ratings_text.delete(1.0, tk.END)

        # Display basic results
        self.results_text.insert(tk.END, f"Converter Type: {design['type']}\n\n")
        self.results_text.insert(tk.END, "Design Parameters:\n")
        self.results_text.insert(tk.END, f"• Input Voltage: {params['vin']:.2f} V\n")
        self.results_text.insert(tk.END, f"• Output Voltage: {params['vout']:.2f} V\n")
        self.results_text.insert(tk.END, f"• Output Current: {params['iout']:.2f} A\n")
        self.results_text.insert(tk.END, f"• Switching Frequency: {params['fsw']/1000:.1f} kHz\n")
        self.results_text.insert(tk.END, f"• Efficiency: {params['efficiency']*100:.1f}%\n\n")

        self.results_text.insert(tk.END, "Calculated Values:\n")
        self.results_text.insert(tk.END, f"• Duty Cycle: {params['duty_cycle']:.3f}\n")
        self.results_text.insert(tk.END, f"• Input Current: {params['input_current']:.3f} A\n")
        self.results_text.insert(tk.END, f"• Inductor Value: {params['inductor']*1e6:.2f} µH\n")
        self.results_text.insert(tk.END, f"• Inductor Current (avg): {params['inductor_current_avg']:.2f} A\n")
        self.results_text.insert(tk.END, f"• Inductor Current (peak): {params['inductor_current_peak']:.2f} A\n")
        self.results_text.insert(tk.END, f"• Capacitor Value: {params['capacitor']*1e6:.2f} µF\n")
        self.results_text.insert(tk.END, f"• Voltage Ripple: {params['voltage_ripple']/params['vout']*100:.2f}%\n")
        self.results_text.insert(tk.END, f"• Current Ripple: {params['current_ripple']/params['inductor_current_avg']*100:.1f}%\n")

        # Update peak and average current labels in ratings frame
        self.inductor_avg_label.config(text=f"{params['inductor_current_avg']:.2f}")
        self.inductor_peak_label.config(text=f"{params['inductor_current_peak']:.2f}")

        # Display component ratings
        self.ratings_text.insert(tk.END, "Component Ratings:\n")
        self.ratings_text.insert(tk.END, f"• Inductor: {params['inductor']*1e6:.2f} µH, {params['inductor_current_peak']:.2f} A peak\n")
        self.ratings_text.insert(tk.END, f"• Capacitor: {params['capacitor']*1e6:.2f} µF, {params['vout']:.1f} V\n")
        self.ratings_text.insert(tk.END, f"• Switch: {params['vin']:.1f} V, {params['switch_current_peak']:.2f} A\n")
        self.ratings_text.insert(tk.END, f"• Diode: {max(params['vin'], abs(params['vout'])):.1f} V, {params['diode_current_peak']:.2f} A\n")
        
    def update_graphs(self):
        """ EXACTLY THE SAME GRAPHING CODE FROM ORIGINAL IMPLEMENTATION """
        if not self.current_design:
            return
            
        design = self.current_design
        params = design["parameters"]
        conv_type = design["type"]
        
        # Time parameters
        period = 1 / params["fsw"]
        t = np.linspace(0, 2*period, 1000)  # Two periods
        
        # Clear figure
        self.figure.clear()
        
        # Determine which graphs to show
        graph_mode = self.graph_var.get()
        
        if graph_mode in ["all", "duty"]:
            # Duty cycle waveform
            ax1 = self.figure.add_subplot(221) if graph_mode == "all" else self.figure.add_subplot(111)
            switch = (t % period) < (params["duty_cycle"] * period)
            ax1.plot(t*1e6, switch, 'b-')
            ax1.set_title('Switch Control Signal')
            ax1.set_ylabel('State (ON/OFF)')
            ax1.set_ylim(-0.1, 1.1)
            ax1.grid(True)
            if graph_mode == "duty":
                ax1.set_xlabel('Time (µs)')
        
        if graph_mode in ["all", "current"]:
            # Inductor current waveform
            ax2 = self.figure.add_subplot(222) if graph_mode == "all" else self.figure.add_subplot(111)
            
            # Create realistic inductor current waveform
            il_wave = np.zeros_like(t)
            for i in range(len(t)):
                phase = t[i] % period
                if phase < params["duty_cycle"] * period:  # Switch ON
                    if conv_type == "Buck":
                        slope = (params['vin'] - params['vout']) / params['inductor']
                    elif conv_type == "Boost":
                        slope = params['vin'] / params['inductor']
                    elif conv_type == "Buck-Boost":
                        slope = params['vin'] / params['inductor']
                    il_wave[i] = params['inductor_current_avg'] - params['current_ripple']/2 + slope * phase
                else:  # Switch OFF
                    if conv_type == "Buck":
                        slope = -params['vout'] / params['inductor']
                    elif conv_type == "Boost":
                        slope = (params['vin'] - params['vout']) / params['inductor']
                    elif conv_type == "Buck-Boost":
                        slope = -params['vout'] / params['inductor']
                    il_wave[i] = params['inductor_current_peak'] + slope * (phase - params['duty_cycle'] * period)
            
            ax2.plot(t*1e6, il_wave, 'r-')
            ax2.set_title('Inductor Current')
            ax2.set_ylabel('Current (A)')
            ax2.grid(True)
            if graph_mode == "current":
                ax2.set_xlabel('Time (µs)')
        
        if graph_mode in ["all", "voltage"]:
            # Input and output voltages
            ax3 = self.figure.add_subplot(223) if graph_mode == "all" else self.figure.add_subplot(111)
            
            # Input voltage (with switching noise)
            v_in = params['vin'] * np.ones_like(t)
            noise = 0.05 * params['vin'] * np.sin(2*np.pi*params['fsw']*t)
            ax3.plot(t*1e6, v_in + noise, 'g-', label='Input Voltage')
            
            # Output voltage (with ripple)
            v_out = params['vout'] * np.ones_like(t)
            ripple = params['voltage_ripple'] * np.sin(2*np.pi*params['fsw']*t)
            ax3.plot(t*1e6, v_out + ripple, 'm-', label='Output Voltage')
            
            ax3.set_title('Input/Output Voltages')
            ax3.set_ylabel('Voltage (V)')
            ax3.legend()
            ax3.grid(True)
            ax3.set_xlabel('Time (µs)')
        
        if graph_mode == "all":
            # Power and efficiency (only shown in "all" mode)
            ax4 = self.figure.add_subplot(224)
            
            # Input power (constant)
            p_in = params['vin'] * params['input_current'] * np.ones_like(t)
            
            # Output power (with ripple effect)
            p_out = (params['vout'] + params['voltage_ripple'] * np.sin(2*np.pi*params['fsw']*t)) * params['iout']
            
            ax4.plot(t*1e6, p_in, 'b-', label='Input Power')
            ax4.plot(t*1e6, p_out, 'r-', label='Output Power')
            ax4.set_title('Power Transfer')
            ax4.set_ylabel('Power (W)')
            ax4.set_xlabel('Time (µs)')
            ax4.legend()
            ax4.grid(True)
        
        self.figure.tight_layout()
        self.canvas.draw()
        
    def new_design(self):
        # Reset all fields
        self.converter_type.current(0)
        for key in self.entries:
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, self.params[key]["default"] if key in self.params else "")
            
        self.inductor_value.config(text="")
        self.capacitor_value.config(text="")
        self.results_text.delete(1.0, tk.END)
        self.ratings_text.delete(1.0, tk.END)
        self.figure.clear()
        self.canvas.draw()
        self.current_design = {}
        
    def open_design(self):
        filepath = filedialog.askopenfilename(
            title="Open Design",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    
                # Update UI with loaded data
                self.converter_type.set(data["type"])
                for key in self.entries:
                    if key in data["parameters"]:
                        self.entries[key].delete(0, tk.END)
                        value = data["parameters"][key]
                        # Convert from base units to display units
                        if key == "switching_freq":
                            value /= 1000  # Hz to kHz
                        self.entries[key].insert(0, str(value))
                        
                # Recalculate to update graphs
                self.calculate()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load design:\n{str(e)}")
                
    def save_design(self):
        if not self.current_design:
            messagebox.showwarning("Warning", "No design to save. Please calculate first.")
            return
            
        filepath = filedialog.asksaveasfilename(
            title="Save Design",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    json.dump(self.current_design, f, indent=4)
                messagebox.showinfo("Success", "Design saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save design:\n{str(e)}")
                
    def export_report(self):
        if not self.current_design:
            messagebox.showwarning("Warning", "No design to export. Please calculate first.")
            return

        # Ask user for file path
        filepath = filedialog.asksaveasfilename(
            title="Export PDF Report",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            design = self.current_design
            params = design["parameters"]
            c = canvas.Canvas(filepath, pagesize=letter)
            width, height = letter
            x = 1 * inch
            y = height - 1 * inch

            # --- PAGE 1: Graphs and Table ---
            # Prepare 2x2 grid of graphs and table at the top
            import matplotlib.pyplot as plt
            graph_titles = [
                ("Switch Control Signal", "duty"),
                ("Inductor Current", "current"),
                ("Input/Output Voltages", "voltage"),
                ("Power Transfer", "all")
            ]
            fig_width_inch = (width - 2 * x) / inch
            fig_height_inch = 7.5
            fig, axs = plt.subplots(2, 2, figsize=(fig_width_inch, fig_height_inch))
            plt.subplots_adjust(left=0.12, right=0.95, top=0.90, bottom=0.10, wspace=0.28, hspace=0.38)

            orig_fig = self.figure
            orig_graph_var = self.graph_var.get()
            for idx, (title, mode) in enumerate(graph_titles):
                self.graph_var.set(mode)
                self.update_graphs()
                src_ax = self.figure.get_axes()[0] if self.figure.get_axes() else None
                if src_ax:
                    row, col = divmod(idx, 2)
                    ax = axs[row][col]
                    for line in src_ax.get_lines():
                        ax.plot(line.get_xdata(), line.get_ydata(), color=line.get_color(), label=line.get_label())
                    for cobj in src_ax.collections:
                        ax.add_collection(cobj)
                    ax.set_title(title)
                    ax.set_xlabel(src_ax.get_xlabel())
                    ax.set_ylabel(src_ax.get_ylabel())
                    ax.set_xlim(src_ax.get_xlim())
                    ax.set_ylim(src_ax.get_ylim())
                    ax.grid(True)
                    if src_ax.get_legend():
                        ax.legend()
            self.figure = orig_fig
            self.graph_var.set(orig_graph_var)

            # Save the combined figure to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile:
                fig.savefig(tmpfile.name, bbox_inches='tight', dpi=150)
                tmpfile.flush()
                img_reader = ImageReader(tmpfile.name)

                # Draw table at the top
                y_img = height - 1 * inch
                c.setFont("Helvetica-Bold", 14)
                c.drawString(x, y_img, "Design Parameters:")
                y_img -= 0.25 * inch
                c.setFont("Helvetica", 11)
                table_data = [
                    ("Input Voltage (Vin)", f"{params['vin']:.2f} V"),
                    ("Output Voltage (Vout)", f"{params['vout']:.2f} V"),
                    ("Output Current (Iout)", f"{params['iout']:.2f} A"),
                    ("Switching Frequency", f"{params['fsw']/1000:.1f} kHz"),
                    ("Efficiency", f"{params['efficiency']*100:.1f}%"),
                    ("Duty Cycle", f"{params['duty_cycle']:.3f}"),
                    ("Inductor (L)", f"{params['inductor']*1e6:.2f} µH"),
                    ("Capacitor (C)", f"{params['capacitor']*1e6:.2f} µF"),
                    ("Voltage Ripple", f"{params['voltage_ripple']/params['vout']*100:.2f}%"),
                    ("Current Ripple", f"{params['current_ripple']/params['inductor_current_avg']*100:.1f}%")
                ]
                col1_x = x + 0.2*inch
                col2_x = x + 2.5*inch
                row_height = 0.19 * inch
                c.setFont("Helvetica-Bold", 11)
                c.drawString(col1_x, y_img, "Parameter")
                c.drawString(col2_x, y_img, "Value")
                y_img -= row_height
                c.setFont("Helvetica", 11)
                for label, value in table_data:
                    c.drawString(col1_x, y_img, label)
                    c.drawString(col2_x, y_img, value)
                    y_img -= row_height
                y_img -= 0.1 * inch
                # Draw the 2x2 grid of graphs centered
                img_width = width - 2 * x
                img_height = fig_height_inch * inch
                img_x = x
                img_y = y_img - img_height
                c.drawImage(img_reader, img_x, img_y, width=img_width, height=img_height, preserveAspectRatio=True, anchor='nw')

            c.setFont("Helvetica-Oblique", 10)
            c.drawString(x, 0.7 * inch, "Report generated by DC-DC Converter Designer")
            c.showPage()

            # --- PAGE 2: Textual Details ---
            y = height - 1 * inch
            c.setFont("Helvetica-Bold", 16)
            c.drawString(x, y, "DC-DC Converter Design Report")
            y -= 0.4 * inch

            c.setFont("Helvetica", 12)
            c.drawString(x, y, f"Converter Type: {design['type']}")
            y -= 0.3 * inch

            c.setFont("Helvetica-Bold", 12)
            c.drawString(x, y, "Design Parameters:")
            y -= 0.22 * inch
            c.setFont("Helvetica", 11)
            c.drawString(x, y, f"Input Voltage: {params['vin']:.2f} V")
            y -= 0.18 * inch
            c.drawString(x, y, f"Output Voltage: {params['vout']:.2f} V")
            y -= 0.18 * inch
            c.drawString(x, y, f"Output Current: {params['iout']:.2f} A")
            y -= 0.18 * inch
            c.drawString(x, y, f"Switching Frequency: {params['fsw']/1000:.1f} kHz")
            y -= 0.18 * inch
            c.drawString(x, y, f"Efficiency: {params['efficiency']*100:.1f}%")
            y -= 0.3 * inch

            c.setFont("Helvetica-Bold", 12)
            c.drawString(x, y, "Calculated Values:")
            y -= 0.22 * inch
            c.setFont("Helvetica", 11)
            c.drawString(x, y, f"Duty Cycle: {params['duty_cycle']:.3f}")
            y -= 0.18 * inch
            c.drawString(x, y, f"Input Current: {params['input_current']:.3f} A")
            y -= 0.18 * inch
            c.drawString(x, y, f"Inductor Value: {params['inductor']*1e6:.2f} µH")
            y -= 0.18 * inch
            c.drawString(x, y, f"Inductor Current (avg): {params['inductor_current_avg']:.2f} A")
            y -= 0.18 * inch
            c.drawString(x, y, f"Inductor Current (peak): {params['inductor_current_peak']:.2f} A")
            y -= 0.18 * inch
            c.drawString(x, y, f"Capacitor Value: {params['capacitor']*1e6:.2f} µF")
            y -= 0.18 * inch
            c.drawString(x, y, f"Voltage Ripple: {params['voltage_ripple']/params['vout']*100:.2f}%")
            y -= 0.18 * inch
            c.drawString(x, y, f"Current Ripple: {params['current_ripple']/params['inductor_current_avg']*100:.1f}%")
            y -= 0.3 * inch

            c.setFont("Helvetica-Bold", 12)
            c.drawString(x, y, "Component Ratings:")
            y -= 0.22 * inch
            c.setFont("Helvetica", 11)
            c.drawString(x, y, f"Inductor: {params['inductor']*1e6:.2f} µH, {params['inductor_current_peak']:.2f} A peak")
            y -= 0.18 * inch
            c.drawString(x, y, f"Capacitor: {params['capacitor']*1e6:.2f} µF, {params['vout']:.1f} V")
            y -= 0.18 * inch
            c.drawString(x, y, f"Switch: {params['vin']:.1f} V, {params['switch_current_peak']:.2f} A")
            y -= 0.18 * inch
            c.drawString(x, y, f"Diode: {max(params['vin'], abs(params['vout'])):.1f} V, {params['diode_current_peak']:.2f} A")
            y -= 0.3 * inch

            # Add more details to the report
            y -= 0.1 * inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(x, y, "Additional Details:")
            y -= 0.22 * inch
            c.setFont("Helvetica", 11)
            c.drawString(x, y, f"Input Power: {params['vin'] * params['input_current']:.2f} W")
            y -= 0.18 * inch
            c.drawString(x, y, f"Output Power: {params['vout'] * params['iout']:.2f} W")
            y -= 0.18 * inch
            c.drawString(x, y, f"Estimated Efficiency: {params['efficiency']*100:.2f}%")
            y -= 0.18 * inch
            c.drawString(x, y, f"Switching Frequency: {params['fsw']:.0f} Hz")
            y -= 0.18 * inch
            c.drawString(x, y, f"Inductor Ripple Current: {params['current_ripple']:.4f} A")
            y -= 0.18 * inch
            c.drawString(x, y, f"Output Voltage Ripple: {params['voltage_ripple']:.4f} V")
            y -= 0.3 * inch

            c.setFont("Helvetica-Oblique", 10)
            c.drawString(x, 0.7 * inch, "Report generated by DC-DC Converter Designer")

            c.save()
            messagebox.showinfo("Success", f"PDF report exported successfully to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF report:\n{str(e)}")
        
    def show_help(self):
        help_text = """DC-DC Converter Designer Help

1. Select converter type (Buck, Boost, Buck-Boost)
2. Enter your design parameters
3. Click Calculate to compute component values
4. View results and waveforms

For more detailed information, please refer to the user manual."""
        messagebox.showinfo("Help", help_text)
        
    def show_about(self):
        about_text = """DC-DC Converter Designer
Version 1.0

A tool for designing and analyzing DC-DC converter circuits.

© 2023 Power Electronics Toolkit"""
        messagebox.showinfo("About", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = DCDCConverterDesigner(root)
    root.mainloop()