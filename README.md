
# 📤 Upload Local Project to GitHub via Git (PowerShell)

This guide helps you upload your local project (e.g., `D:\PROJECTS\legal_rag_project`) to GitHub using Git in PowerShell — without any GUI apps.

---

## 🛠 Prerequisites
- Git must be installed: [https://git-scm.com/downloads](https://git-scm.com/downloads)
- GitHub account with a repository already created
- Your project folder ready

---

## ✅ Step-by-Step Instructions

### 📁 1. Navigate to Your Project Directory
```powershell
cd "D:\PROJECTS\legal_rag_project"
```

### 📦 2. Initialize Git in the Project Folder
```powershell
git init
```

### ➕ 3. Add All Files to Staging
```powershell
git add .
```

### 💬 4. Commit the Changes
```powershell
git commit -m "Initial commit"
```

### 🌐 5. Connect to GitHub Repository
Replace the URL with your actual GitHub repo URL:
```powershell
git remote add origin https://github.com/irfansulfi11/legal_rag_project.git
```

### 🚀 6. Push Code to GitHub
```powershell
git branch -M main
git push -u origin main
```

---

## ❗ Common Errors
- **fatal: not a git repository**: You didn’t run `git init`.
- **fatal: repository '...' does not exist**: You used an invalid or placeholder repo URL.

---

## ✅ Tip
Use a **[Personal Access Token (PAT)](https://github.com/settings/tokens)** instead of your GitHub password when pushing via HTTPS.

---

## 🧠 Summary (All in One)
```powershell
cd "D:\PROJECTS\legal_rag_project"
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/irfansulfi11/legal_rag_project.git
git branch -M main
git push -u origin main
```
