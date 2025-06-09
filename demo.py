import subprocess
import time
import threading

def run_sender():
    """Run the sender script"""
    print("Starting sender process...")
    subprocess.run(["python", "sender.py"])
    time.sleep(2)

def run_receiver():
    """Run the receiver script with a delay"""
    # Wait a bit for the sender to start up
    time.sleep(2)
    print("Starting receiver process...")
    subprocess.run(["python", "receiver.py"])

if __name__ == "__main__":
    # Create a thread for the reciever
    receiver_thread = threading.Thread(target=run_receiver)
    
    # Start the sender
    receiver_thread.start()
    
    # Run the receiver
    run_sender()
    
    # Wait for sender to finish
    receiver_thread.join()
    
    print("Demo completed!")