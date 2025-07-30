import time
import os
import glob
import keyboard
import sys
from datetime import datetime

# Import main functions from both scripts
from S1 import main as s1_main
from S2 import main as s2_main

# Global flag to control the loop
running = True

def get_resume_file_count(resume_dir="./resumes"):
    """Get the current number of .pdf and .docx files in the resume directory"""
    os.makedirs(resume_dir, exist_ok=True)  # Ensure directory exists
    pdf_files = glob.glob(os.path.join(resume_dir, "*.pdf"))
    docx_files = glob.glob(os.path.join(resume_dir, "*.docx"))
    return len(pdf_files + docx_files)

def run_sequential():
    """Run S1.py main() followed by S2.py main()"""
    try:
        print(f"[{datetime.now()}] Starting S1.py main()")
        s1_main()
        print(f"[{datetime.now()}] S1.py main() completed")

        print(f"[{datetime.now()}] Starting S2.py main()")
        s2_main()
        print(f"[{datetime.now()}] S2.py main() completed")
    except Exception as e:
        print(f"[{datetime.now()}] Error in sequential execution: {e}")

def main():
    global running
    print("Monitoring ./resumes directory for changes...")
    print("Press 'q' to exit.")
    
    resume_dir = "./resumes"
    last_file_count = get_resume_file_count(resume_dir)
    print(f"[{datetime.now()}] Initial file count in {resume_dir}: {last_file_count}")

    while running:
        try:
            # Get current file count
            current_file_count = get_resume_file_count(resume_dir)
            
            # Check if file count has changed
            if current_file_count != last_file_count:
                print(f"[{datetime.now()}] Detected change in {resume_dir}: {last_file_count} -> {current_file_count} files")
                run_sequential()
                last_file_count = current_file_count
                print(f"[{datetime.now()}] Processing complete, waiting for next change...")
            elif current_file_count == 0:
                print(f"[{datetime.now()}] No files in {resume_dir}, waiting for files to be added...")

            # Check for 'q' keypress
            if keyboard.is_pressed('q'):
                print(f"[{datetime.now()}] 'q' pressed, initiating shutdown...")
                running = False
                break

            # Sleep to avoid high CPU usage
            time.sleep(1)  # Check every 1 second
        except KeyboardInterrupt:
            print(f"[{datetime.now()}] Interrupted by Ctrl+C, shutting down...")
            running = False
            break
        except Exception as e:
            print(f"[{datetime.now()}] Error in main loop: {e}")
            time.sleep(5)  # Wait before retrying on error

    print(f"[{datetime.now()}] Shutdown complete.")
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[{datetime.now()}] Fatal error in wrapper: {e}")
        running = False
        sys.exit(1)