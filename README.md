# 🔐 Simple Password Manager

A clean, easy-to-use password manager with encryption and strength checking.

## Features

✅ **Secure Storage** - Military-grade encryption (AES-256)  
✅ **Add/View/Edit/Delete** - Full password management  
✅ **Strength Checker** - Real-time password strength indicator  
✅ **Master Password** - One password to secure everything  
✅ **Simple Interface** - Clean, dark-themed UI  

## Quick Start

### Installation

1. **Install Python** (3.7 or higher)
2. **Install required library:**
   ```bash
   pip install cryptography
   ```

3. **Run the app:**
   ```bash
   python password_manager_simple.py
   ```

### First Time Use

1. Create a master password (remember this - it can't be recovered!)
2. Start adding your passwords

## How to Use

### Add Password
1. Click **Add**
2. Enter website, username, and password
3. See strength indicator update in real-time
4. Click **Save**

### View Password
1. Select a password from the list
2. Click **View**
3. Click **Show** to reveal password
4. Click **Copy** to copy to clipboard

### Edit Password
1. Select a password
2. Click **Edit**
3. Update the fields
4. Click **Update**

### Delete Password
1. Select a password
2. Click **Delete**
3. Confirm deletion

## Password Strength Guide

🔴 **Weak** - Too short or simple  
🟠 **Medium** - Good but could be better  
🟢 **Strong** - Excellent security  

**Tips for strong passwords:**
- 12+ characters
- Mix uppercase and lowercase
- Include numbers
- Add special characters (!@#$%^&*)

## Files

- `password_manager_simple.py` - Main application
- `passwords.enc` - Encrypted password storage
- `master.key` - Encrypted master key

**⚠️ Backup these files regularly!**

## Security Notes

✅ All passwords encrypted  
✅ Master password never stored  
✅ Data secured with AES-256  
❌ No password recovery - keep master password safe!  

## Troubleshooting

**"No module named 'cryptography'"**
```bash
pip install cryptography
```

**"No module named 'tkinter'"** (Linux)
```bash
sudo apt-get install python3-tk
```

**Wrong master password?**
- No recovery possible (by design for security)
- Delete `master.key` and `passwords.enc` to start fresh

## Code Simplifications

This simplified version has:
- **~300 lines** (vs 500+ in full version)
- Removed timestamps and date tracking
- Simplified dialog creation
- Streamlined UI layout
- Cleaner, more readable code
- Same core features and security

Perfect for learning or personal use! 🚀
