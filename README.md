# 🎓 HIT137 Group Assignment 3 – Image Editor & 2D Side-Scrolling Game

Welcome to our repository for **Group Assignment 3** for the **HIT137 – Foundations of Computer Science** course at **Charles Darwin University**.

This project is divided into two distinct parts:

- 🖼️ A **Desktop Image Editing Application** using **Tkinter** and **OpenCV**
- 🎮 A **Side-Scrolling 2D Game** using **Pygame**

---

## 📝 Project Overview

This project demonstrates key programming concepts learned in HIT137, including object-oriented programming, graphical user interface design, and basic game development. It consists of two main deliverables: an image editor application that supports loading, cropping, resizing, and saving images, and a side-scrolling 2D game featuring player control, enemies, collectibles, and multiple levels.

---

## ⚙️ Prerequisites

- Python 3.8 or higher
- Tested on Windows 10 and Ubuntu 20.04
- Required Python packages listed in `requirements.txt`

---

## 📁 Repository Structure
- `github_link.txt` — Public GitHub URL for submission  
- `README.md` — Project documentation  
- `.gitignore` — Ignored files  
- `requirements.txt` — Required Python packages
- `HIT137_Assignment_3_S1_2025.pdf` — Assignment Questions 

- **HIT137-Group-Assignment-3/**  
  - **image_editor/** — Desktop application (Tkinter + OpenCV)  
    - `main.py` — Entry point  
    - `image_utils.py` — Image processing logic  
    - `gui.py` — GUI components and event handling  
    - **assets/** — Image and icon assets  
    - `README.md` — Image editor documentation  
  - **side_scrolling_game/** — Side-scrolling 2D platformer (Pygame)  
    - `main.py` — Game loop and controls  
    - `player.py` — Player class  
    - `enemy.py` — Enemy class  
    - `projectile.py` — Projectile mechanics  
    - `collectible.py` — Collectibles and bonuses  
    - `level.py` — Level design and transitions  
    - `game_utils.py` — Shared functions/utilities  
    - **assets/**  
      - **images/** — Sprites and backgrounds  
      - **sounds/** — Audio files  
    - `README.md` — Game documentation  

---

## 🖼️ Question 1: Image Editor App

### ✅ Features
- Load image from local system
- Draw rectangle using mouse to crop
- Real-time preview of selection
- Resize cropped image using slider
- Save modified image locally

### 🚀 How to Run
```bash
cd image_editor
python main.py
```
## 🎮 Question 2: Side-Scrolling Game

### ✅ Features
- Player can run, jump, shoot
- Includes enemies and collectibles
- 3 unique levels with increasing difficulty
- Boss battle on final level
- Scoring system, player health, and lives
- Game Over screen with restart option

### 🚀 How to Run
```bash
cd side_scrolling_game
python main.py
```
---
## 📦 Installation & Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/HIT137-Group-Assignment-3.git
   cd HIT137-Group-Assignment-3
    ```
2. **Create Virtual Environment (Optional but Recommended)**

    ```bash
    python -m venv env
    source env/bin/activate    # On Windows: env\Scripts\activate
    ```
3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
---
## 👥 Group Members

| Name            | Student ID | Email |
|-----------------|------------|------ |
| Anish Machamasi | S389151 | anishmachamasi2262@gmail.com |
| Xiaoyu Wang  | S391743  | ginaxu1230@gmail.com
| Veli Oz    | SS392097| veliozau@gmail.com
---

## ✅ Submission Checklist

- [x] Public GitHub repository created
- [x] All code and documentation committed to GitHub
- [x] `github_link.txt` created with correct repo URL
- [x] Code and assets zipped for Learline submission

---

## ⚠️ Known Issues / Limitations

- Image editor currently supports JPG and PNG formats only.
- Undo/redo functionality not implemented in image editor.
- Game difficulty balancing ongoing; some levels may be more challenging.
- Keyboard shortcut customization is not available.

---

## 📄 License

This project is created as part of coursework for HIT137 at Charles Darwin University. It is for educational use only.

---

## 🙏 Acknowledgments

- [OpenCV](https://opencv.org/)
- [Pygame](https://www.pygame.org/)
- Tkinter documentation and tutorials
- Course instructors and teaching assistants

---

## 💬 Contact

For questions or feedback, please contact any of the group members or raise an issue on the repository.
