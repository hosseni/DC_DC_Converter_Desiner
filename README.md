# DC-DC Converter Designer

A powerful desktop GUI application to design and analyze DC-DC converters (Buck, Boost, Buck-Boost). Built with Python and Tkinter, it allows engineers and students to input design parameters, visualize switching and inductor waveforms, and calculate optimal component values automatically.

---

## 🚀 Features

- ✅ Support for Buck, Boost, and Buck-Boost topologies
- ✅ Input/output validation with ripple specifications
- ✅ Automatic inductor and capacitor sizing
- ✅ Waveform visualizations:
  - Switch duty cycle
  - Inductor current
  - Input/output voltages
  - Power flow
- ✅ Component peak current ratings calculation
- ✅ Save/load design files (`.json`)
- ✅ Clean GUI with export/report stubs
- ✅ Desktop `.exe` packaging using PyInstaller

---

## 📦 How to Install (Windows)

### Option 1: Use Pre-built `.exe`

> Just double-click `dc_dc_converter_ui.exe`

If you face issues running it:
- Make sure your antivirus is not blocking it.
- Do **not** move the `.exe` while it's running.

---

### Option 2: Build from Source

#### 🔧 Requirements

- Python 3.10 or 3.11 (Recommended, not 3.13)
- pip packages:
  ```bash
  pip install matplotlib numpy
  pip install pyinstaller
  ```

#### 🔨 Build the `.exe`

```bash
cd "path\to\project"
pyinstaller --onefile --windowed --icon=my_icon.ico dc_dc_converter_ui.py
```

The final `.exe` will be inside the `dist/` folder.

---

## 🖥️ Running From Source (Developer Mode)

```bash
python dc_dc_converter_ui.py
```

---

## 📁 Project Structure

```
DC-DC-Converter-Designer/
│
├── dc_dc_converter_ui.py         # Main application
├── my_icon.ico                   # Optional icon file
├── README.md                     # This file
├── dist/                         # PyInstaller output (generated)
└── build/                        # PyInstaller build files (generated)
```

---

## 📄 License

This project is provided for educational and research purposes. No warranty provided.

---

## 🙋‍♂️ Author

**Your Name**  
📧 [elhossenenour@gmail.com](mailto:elhossenenour@gmail.com)  
🌍 Location: Jeddah, Saudi Arabia  
🔗 [LinkedIn Profile](https://www.linkedin.com/in/elhusseini-gamal-b6455421a/)