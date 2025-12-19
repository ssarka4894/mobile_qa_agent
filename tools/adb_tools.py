"""
ADB interaction tools for Android automation
COMPLETE FILE - Copy this entire file
"""
import subprocess
import time
import re
from typing import Tuple, Optional, List
from pathlib import Path


class ADBController:
    """Handle all ADB interactions with Android device/emulator"""
    
    def __init__(self, device_id: Optional[str] = None, reference_size: Tuple[int, int] = (1440, 3120)):
        """
        Initialize ADB controller
        
        Args:
            device_id: Specific device/emulator ID (or None for auto-detect)
            reference_size: Reference screen size (default: Pixel 6 Pro 1440x3120)
        """
        self.device_id = device_id
        self.reference_size = reference_size
        self.actual_size = None
        
        # Verify ADB is available
        if not self._check_adb():
            raise RuntimeError("ADB is not available. Please install Android SDK Platform Tools.")
        
        # Detect device
        if self.device_id is None:
            self.device_id = self._detect_device()
        
        # Get actual screen size
        self.actual_size = self.get_screen_size()
        print(f"Device: {self.device_id}, Screen: {self.actual_size}")
    
    def _check_adb(self) -> bool:
        """Check if adb command is available"""
        try:
            subprocess.run(['adb', 'version'], capture_output=True, check=True, timeout=5)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _detect_device(self) -> str:
        """Auto-detect connected device/emulator"""
        result = subprocess.run(
            ['adb', 'devices'],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        
        # Parse output
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        devices = [line.split()[0] for line in lines if '\tdevice' in line]
        
        if not devices:
            raise RuntimeError("No devices/emulators found. Please start an emulator or connect a device.")
        
        if len(devices) > 1:
            print(f"Multiple devices found: {devices}")
            print(f"Using first device: {devices[0]}")
        
        return devices[0]
    
    def _run_adb(self, command: List[str], check: bool = True, timeout: int = 20, text: bool = True) -> subprocess.CompletedProcess:
        """Run adb command with device ID"""
        full_cmd = ['adb']
        if self.device_id:
            full_cmd.extend(['-s', self.device_id])
        full_cmd.extend(command)
        
        return subprocess.run(full_cmd, capture_output=True, text=text, check=check, timeout=timeout)
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get physical screen size of device"""
        try:
            result = self._run_adb(['shell', 'wm', 'size'], timeout=10)
            
            # Parse: Physical size: 1440x3120
            match = re.search(r'(\d+)x(\d+)', result.stdout)
            if match:
                return int(match.group(1)), int(match.group(2))
        except Exception as e:
            print(f"Warning: Could not detect screen size: {e}")
        
        print("Using default size (Pixel 6 Pro)")
        return self.reference_size
    
    def scale_coordinates(self, x: int, y: int) -> Tuple[int, int]:
        """
        Scale coordinates from reference size to actual device size
        
        Args:
            x, y: Coordinates based on reference_size
            
        Returns:
            (scaled_x, scaled_y) for actual device
        """
        if self.actual_size == self.reference_size:
            return x, y
        
        scale_x = self.actual_size[0] / self.reference_size[0]
        scale_y = self.actual_size[1] / self.reference_size[1]
        
        return int(x * scale_x), int(y * scale_y)
    
    def tap(self, x: int, y: int, scale: bool = False, wait_after: float = 0.5) -> bool:
        """
        Tap at coordinates
        
        Args:
            x, y: Tap coordinates
            scale: Whether to scale from reference size (default False for Pixel 6 Pro)
            wait_after: Seconds to wait after tap
            
        Returns:
            Success status
        """
        if scale:
            x, y = self.scale_coordinates(x, y)
        
        try:
            self._run_adb(['shell', 'input', 'tap', str(x), str(y)], timeout=10)
            print(f"✓ Tapped at ({x}, {y})")
            time.sleep(wait_after)
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to tap: {e}")
            return False
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, 
              duration_ms: int = 300, scale: bool = False, wait_after: float = 1.0) -> bool:
        """
        Swipe gesture
        
        Args:
            start_x, start_y: Start coordinates
            end_x, end_y: End coordinates
            duration_ms: Swipe duration in milliseconds
            scale: Whether to scale coordinates
            wait_after: Seconds to wait after swipe
        """
        if scale:
            start_x, start_y = self.scale_coordinates(start_x, start_y)
            end_x, end_y = self.scale_coordinates(end_x, end_y)
        
        try:
            self._run_adb(['shell', 'input', 'swipe', 
                          str(start_x), str(start_y), 
                          str(end_x), str(end_y), 
                          str(duration_ms)], timeout=10)
            print(f"✓ Swiped from ({start_x},{start_y}) to ({end_x},{end_y})")
            time.sleep(wait_after)
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to swipe: {e}")
            return False
    
    def type_text(self, text: str, wait_after: float = 0.5) -> bool:
        """
        Type text (spaces must be %s)
        
        Args:
            text: Text to type (use %s for spaces)
            wait_after: Seconds to wait after typing
        """
        # Spaces should already be %s in the test definitions
        # But ensure they are converted if not
        if ' ' in text and '%s' not in text:
            text = text.replace(' ', '%s')
        
        try:
            self._run_adb(['shell', 'input', 'text', text], timeout=20)
            print(f"✓ Typed: {text.replace('%s', ' ')}")
            time.sleep(wait_after)
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to type text: {e}")
            return False
    
    def press_key(self, keycode: int, wait_after: float = 0.5) -> bool:
        """
        Press a key by keycode
        
        Common keycodes:
        - BACK: 4
        - HOME: 3
        - ENTER: 66
        - BACKSPACE/DEL: 67
        - TAB: 61
        """
        try:
            self._run_adb(['shell', 'input', 'keyevent', str(keycode)], timeout=10)
            print(f"✓ Pressed key: {keycode}")
            time.sleep(wait_after)
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to press key: {e}")
            return False
    
    def press_key_combination(self, keycodes: List[int], wait_after: float = 0.5) -> bool:
        """
        Press key combination (e.g., Ctrl+A)
        
        Args:
            keycodes: List of keycodes to press simultaneously
            
        Example:
            press_key_combination([113, 29])  # Ctrl+A
        """
        try:
            self._run_adb(['shell', 'input', 'keycombination'] + list(map(str, keycodes)), timeout=10)
            print(f"✓ Pressed key combination: {keycodes}")
            time.sleep(wait_after)
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to press key combination: {e}")
            return False
    
    def select_all(self) -> bool:
        """Select all text in focused field (Ctrl+A)"""
        return self.press_key_combination([113, 29])  # Ctrl+A
    
    def delete_text(self, num_chars: int = 20) -> bool:
        """Delete text by pressing backspace multiple times"""
        for _ in range(num_chars):
            self.press_key(67, wait_after=0.05)  # BACKSPACE
        time.sleep(0.5)
        return True
    
    def take_screenshot(self, output_path: str) -> bool:
        """
        Take screenshot and save to file
        FIXED: Proper binary data handling with fallback
        
        Args:
            output_path: Where to save screenshot
            
        Returns:
            Success status
        """
        try:
            # Create directory if it doesn't exist
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Method 1: Try exec-out with binary mode
            try:
                result = self._run_adb(['exec-out', 'screencap', '-p'], check=False, timeout=30, text=False)
                
                if result.returncode == 0 and result.stdout:
                    with open(output_path, 'wb') as f:
                        f.write(result.stdout)
                    print(f"✓ Screenshot saved: {output_path}")
                    return True
            except Exception as e:
                print(f"Method 1 failed: {e}, trying fallback...")
            
            # Method 2: Fallback to file-based screenshot
            try:
                remote_path = '/sdcard/screen.png'
                
                # Take screenshot to file on device
                self._run_adb(['shell', 'screencap', '-p', remote_path], timeout=30)
                
                # Pull the file
                self._run_adb(['pull', remote_path, output_path], timeout=30)
                
                # Clean up remote file
                self._run_adb(['shell', 'rm', remote_path], check=False, timeout=10)
                
                print(f"✓ Screenshot saved: {output_path}")
                return True
                
            except Exception as e:
                print(f"Method 2 failed: {e}")
                return False
            
        except Exception as e:
            print(f"✗ Screenshot error: {e}")
            return False
    
    def install_app(self, apk_path: str) -> bool:
        """Install or reinstall APK"""
        try:
            self._run_adb(['install', '-r', apk_path], timeout=60)
            print(f"✓ Installed: {apk_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Install failed: {e}")
            return False
    
    def uninstall_app(self, package_name: str) -> bool:
        """Uninstall app by package name"""
        try:
            self._run_adb(['uninstall', package_name], timeout=30)
            print(f"✓ Uninstalled: {package_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Uninstall failed: {e}")
            return False
    
    def start_app(self, package_name: str, activity_name: str = None) -> bool:
        """
        Start an app using monkey command
        
        Args:
            package_name: App package (e.g., 'md.obsidian')
            activity_name: Specific activity to launch (optional, not used with monkey)
        """
        try:
            # Use monkey to launch app (same as your working command)
            self._run_adb(['shell', 'monkey', '-p', package_name, '-c', 
                          'android.intent.category.LAUNCHER', '1'], timeout=30)
            print(f"✓ Started app: {package_name}")
            time.sleep(2)  # Wait for app to load
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to start app: {e}")
            return False
    
    def clear_app_data(self, package_name: str) -> bool:
        """Clear app data (like uninstall/reinstall but faster)"""
        try:
            self._run_adb(['shell', 'pm', 'clear', package_name], timeout=20)
            print(f"✓ Cleared data: {package_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to clear data: {e}")
            return False
    
    def is_keyboard_visible(self) -> bool:
        """Check if keyboard is currently visible"""
        try:
            result = self._run_adb(['shell', 'dumpsys', 'input_method'], timeout=20)
            return 'mInputShown=true' in result.stdout
        except subprocess.CalledProcessError:
            return False
    
    def wait_for_idle(self, timeout: int = 10) -> bool:
        """Wait for UI to be idle"""
        try:
            self._run_adb(['shell', 'uiautomator', 'events', '--wait-for-idle', str(timeout)], timeout=timeout+5)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_current_activity(self) -> str:
        """Get currently focused activity"""
        try:
            result = self._run_adb(['shell', 'dumpsys', 'window', 'windows'], timeout=20)
            match = re.search(r'mCurrentFocus=Window{.*\s+(\S+/\S+)\}', result.stdout)
            if match:
                return match.group(1)
            return "Unknown"
        except subprocess.CalledProcessError:
            return "Unknown"


# Convenience functions
def create_adb_controller(device_id: Optional[str] = None) -> ADBController:
    """Create and return ADB controller instance"""
    return ADBController(device_id=device_id)
