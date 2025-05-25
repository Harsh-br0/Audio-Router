from .router import AudioRouter


def main():
    router = AudioRouter()

    print("Audio Routing System")
    print("===================")
    print("\nAvailable commands:")
    print("  list - List all audio devices")
    print("  create <input_device> <output_device> [sample_rate] - Create a new route")
    print("  stop <route_id> - Stop a specific route")
    print("  routes - List all active routes")
    print("  exit - Exit the program")

    # List devices at startup
    devices_info, input_devices, output_devices = router.list_audio_devices()
    print("\n" + devices_info)

    while True:
        try:
            command = input("\nEnter command: ").strip().split()

            if not command:
                continue

            if command[0] == "list":
                devices_info, input_devices, output_devices = router.list_audio_devices()
                print(devices_info)

            elif command[0] == "create" and len(command) >= 3:
                input_idx = int(command[1])
                output_idx = int(command[2])

                # Get the actual device indices from our categorized lists
                if 0 <= input_idx < len(input_devices) and 0 <= output_idx < len(output_devices):
                    actual_input_device = input_devices[input_idx]["index"]
                    actual_output_device = output_devices[output_idx]["index"]

                    # Optional parameters
                    sample_rate = 44100
                    if len(command) > 3:
                        sample_rate = int(command[3])

                    router.create_route(actual_input_device, actual_output_device, sample_rate)
                else:
                    print(
                        "Invalid device index. Please check available devices with 'list' command."
                    )

            elif command[0] == "stop" and len(command) >= 2:
                route_id = int(command[1])
                router.stop_route(route_id)

            elif command[0] == "routes":
                print(router.list_active_routes())

            elif command[0] == "exit":
                break

            else:
                print("Invalid command. Try again or type 'exit' to quit.")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    router.close()
    print("Program exited")
