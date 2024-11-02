import asyncio
from bleak import BleakScanner


async def main():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover(10)
    if not devices:
        print("No BLE devices found.")
        exit()
    for device in devices:
        print(
            f"📝 Name: {device.name}, 🧭 Address: {device.address} , 📡 RSSI: {device.details['props']['RSSI']} dBm")


asyncio.run(main())
