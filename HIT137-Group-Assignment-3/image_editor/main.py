import tkinter as tk

from app import PictureProcessorApp


def main() -> None:
    """Main function to start the application."""
    try:
        root = tk.Tk()
        app = PictureProcessorApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Fatal error: {str(e)}")


if __name__ == "__main__":
    main()