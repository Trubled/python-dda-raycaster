import asyncio
from bleak import BleakScanner

async def main():
    print("STARTING SCRIPT")
    print("Scanning for Bluetooth Low Energy devices...")
    devices = await BleakScanner.discover(timeout=5.0)

    found = False
    for d in devices:
        # Handle devices where d.name might be None
        name = d.name if d.name else "Unknown Device"
        print(f"Found Device: Name={name}")
        
        if d.name and "buzz" in d.name.lower():  # Using .lower() makes it case-insensitive
            print(f" ---> MATCH FOUND: {d.name} at {d.address}")
            found = True

    # This check now runs AFTER the loop finishes checking all devices
    if not found:
        print("\nRobot not found by name. Make sure Buzz is powered on and in pairing mode!")

if __name__ == "__main__":
    asyncio.run(main())