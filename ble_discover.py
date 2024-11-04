import argparse
import asyncio
from bleak import BleakClient, BleakScanner
parser = argparse.ArgumentParser(
    prog='BLE Service Disconver', description='Scan for BLE devices')
parser.add_argument('device_address', type=str,
                    help='Device name', )
args = parser.parse_args()


async def main():
    try:
        this_device = await BleakScanner.find_device_by_address(args.device_address, timeout=20)
        async with BleakClient(this_device) as client:
            print('\tServices:')
            for service in client.services:
                print(f'\t\tDescription: {service.description}')
                print(f'\t\tService: {service}')

                print('\t\tCharacteristics:')
                for c in service.characteristics:
                    print(f'\t\t\tUUID: {c.uuid}'),
                    print(f'\t\t\tDescription: {c.description}')
                    print(f'\t\t\tHandle: {c.handle}'),
                    print(f'\t\t\tProperties: {c.properties}')
                    # if 'read' in c.properties:
                    #     data = await client.read_gatt_char(c.uuid)
                    #     print(f'\t\t\tData: {data}')
                    print('\t\tDescriptors:')
                    for descrip in c.descriptors:
                        print(f'\t\t\t{descrip}')

    except Exception as e:
        print(f"Could not connect to device with info: {args.device_address}")
        print(f"Error: {e}")


asyncio.run(main())
