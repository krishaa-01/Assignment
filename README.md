**VAULT - GUI-based Secure Password Manager**
-> VAULT is a desktop password manager built using Python and Tkinter. It allows users to securely store and manage credentials locally using encryption.

**Features**
- Master password authentication
- Encrypted storage using Fernet (cryptography library)
- Add, edit, view, and delete credentials
- Password strength indicator (Weak / Medium / Strong)
- Random strong password generator
- Search functionality
- Dark themed user interface

**How It Works**
-> When the application is launched for the first time, the user creates a master password.The master password is hashed using SHA-256 and used to generate an encryption key. All credentials are encrypted before being stored in a local file. When logging in, the entered master password is verified and used to decrypt the stored data.

**How to Run**
1. Install the required dependency:
-> pip install cryptography

2. Run the application:
-> python assignment.py

**Project Files**
- assignment.py — Main application file  
- README.md — Project documentation  

**Purpose of This Project**
-> This project was created to practice:

- GUI development with Tkinter  
- Encryption and hashing concepts  
- File handling in Python  
- Basic UI/UX design  

All data is stored locally on the user's machine.
