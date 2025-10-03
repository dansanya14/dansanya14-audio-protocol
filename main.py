# main.py

def main():
    # Run startup checks before importing anything risky
    from startup_check import run_startup_check
    run_startup_check()

    # Delay GUI import until after dependencies are confirmed
    from gui.interface import launch_gui
    launch_gui()

if __name__ == "__main__":
    main()
