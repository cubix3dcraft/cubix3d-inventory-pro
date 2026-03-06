🚀 CUBIX3D Inventory Pro
========================

**CUBIX3D Inventory Pro** is a lightweight, open-source filament management and AMS tracking system designed for 3D print farms. Optimized for Raspberry Pi and Windows, it helps you manage your inventory, track AMS slots, and maintain a detailed print history from anywhere (via Tailscale or Local Network).

_Perfect for tracking high-quality prints like the_ _**"Elegant Black Spiral Vase by CUBIX3D Craft Studio"**__._

✨ Key Features
--------------

*   **📦 Filament Rack Management:** Track full and opened spools with precise hex color visualization.
    
*   **🖨️ Printer Farm Dashboard:** Real-time visual monitoring of AMS slots across multiple printers.
    
*   **🕒 Detailed Usage History:** Automatically logs every finished print, allowing you to add custom notes and dates.
    
*   **🚨 Low Stock Alerts:** Visual indicators when a filament type is running low.
    
*   **📱 Responsive UI:** Modern dark theme optimized for both desktop and mobile browsers.
    
*   **💾 Easy Backup:** One-click database download to keep your records safe.
    

💻 Windows Installation Guide (For Local PC)
--------------------------------------------

1.  **Install Python:**
    
    *   Download Python 3.10 or newer from [python.org](https://www.python.org/).
        
    *   **Important:** During installation, make sure to check the box **"Add Python to PATH"**.
        
2.  **Download Project:**
    
    *   On this GitHub page, click the green **Code** button and select **Download ZIP**.
        
    *   Extract the ZIP file to a folder on your computer.
        
3.  **Install Dependencies:**
    
    *   pip install -r requirements.txt
        
4.  **Run the App:**
    
    *   python app.py
        
    *   Open your browser and go to: http://localhost:5000
        

🍓 Raspberry Pi Installation Guide
----------------------------------

1.  sudo apt update && sudo apt upgrade -ysudo apt install python3-pip git -y
    
2.  git clone \[https://github.com/cubix3dcraft/cubix3d-inventory-pro.git\](https://github.com/cubix3dcraft/cubix3d-inventory-pro.git)cd cubix3d-inventory-propip3 install -r requirements.txt
    
3.  **Enable Auto-Start (Run on Boot):**
    
    *   sudo nano /etc/systemd/system/cubix\_inventory.service
        
    *   \[Unit\]Description=Cubix3D Inventory ServiceAfter=network.target\[Service\]User=piWorkingDirectory=/home/pi/cubix3d-inventory-proExecStart=/usr/bin/python3 app.pyRestart=always\[Install\]WantedBy=multi-user.target
        
    *   Save and Exit (**Ctrl+O**, **Enter**, **Ctrl+X**).
        
    *   sudo systemctl enable cubix\_inventory.servicesudo systemctl start cubix\_inventory.service
        

🤝 Contributing
---------------

We welcome contributions! If you have ideas for new features or find any bugs, please open an **Issue** or submit a **Pull Request**. Let's build the best inventory system for the 3D printing community!

📄 License
----------

This project is open-source and available under the [MIT License](https://www.google.com/search?q=LICENSE).

Developed with ❤️ for **CUBIX3D Craft Studio** 🚀
