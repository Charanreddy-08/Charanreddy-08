import gc
import torch
import subprocess
import os

def cleanup_resources():
    """
    Clears memory by running garbage collection, emptying CUDA cache,
    and attempting to drop system caches.
    """
    # Python Garbage Collection
    gc.collect()

    # PyTorch CUDA Cache
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # System Cache (requires root/sudo, handling gracefully if fails)
    try:
        # Note: This is an aggressive memory management step specific to the requirement.
        # It usually requires sudo. On the Jetson, the user running this might need nopasswd sudo for this command
        # or it might fail. We print a warning if it fails but don't crash the app.
        subprocess.run(['sudo', '/sbin/sysctl', 'vm.drop_caches=3'],
                       check=False, capture_output=True)
    except Exception as e:
        print(f"Warning: Could not drop system caches: {e}")
