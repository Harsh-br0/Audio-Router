import threading
import time

import pyaudio


class AudioRouter:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.routes = {}
        self.running = True
        self.next_route_id = 1

    def list_audio_devices(self):
        """List all available audio devices separated by input and output"""
        input_devices = []
        output_devices = []

        # Collect input and output devices separately
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            if device_info["hostApi"] == 0:  # Default host API
                if device_info["maxInputChannels"] > 0:
                    input_devices.append(
                        {
                            "index": i,
                            "name": device_info["name"],
                            "channels": device_info["maxInputChannels"],
                            "sample_rate": device_info["defaultSampleRate"],
                        }
                    )

                if device_info["maxOutputChannels"] > 0:
                    output_devices.append(
                        {
                            "index": i,
                            "name": device_info["name"],
                            "channels": device_info["maxOutputChannels"],
                            "sample_rate": device_info["defaultSampleRate"],
                        }
                    )

        # Format device information
        result = []

        # Add input devices
        result.append("Available Input Devices:")
        if input_devices:
            for idx, device in enumerate(input_devices):
                result.append(f"[{idx}] Device {device['index']}: {device['name']}")
                result.append(
                    f"    Channels: {device['channels']}, Sample Rate: {device['sample_rate']}"
                )
        else:
            result.append("  None found")

        result.append("")

        # Add output devices
        result.append("Available Output Devices:")
        if output_devices:
            for idx, device in enumerate(output_devices):
                result.append(f"[{idx}] Device {device['index']}: {device['name']}")
                result.append(
                    f"    Channels: {device['channels']}, Sample Rate: {device['sample_rate']}"
                )
        else:
            result.append("  None found")

        return "\n".join(result), input_devices, output_devices

    def create_route(
        self, input_device_index, output_device_index, sample_rate=44100, chunk_size=1024
    ):
        """Create a new audio route with auto-generated ID"""
        try:
            # Get device info for both input and output devices
            input_info = self.p.get_device_info_by_index(input_device_index)
            output_info = self.p.get_device_info_by_index(output_device_index)

            # Get the channel counts
            input_channels = int(input_info["maxInputChannels"])
            output_channels = int(output_info["maxOutputChannels"])

            # Generate a new route ID
            route_id = self.next_route_id
            self.next_route_id += 1

            # Create a new thread for this route
            route_thread = threading.Thread(
                target=self._route_audio,
                args=(
                    route_id,
                    input_device_index,
                    output_device_index,
                    input_channels,
                    output_channels,
                    sample_rate,
                    chunk_size,
                ),
                daemon=True,
            )

            self.routes[route_id] = {
                "thread": route_thread,
                "active": True,
                "input_device": input_device_index,
                "output_device": output_device_index,
                "input_channels": input_channels,
                "output_channels": output_channels,
                "sample_rate": sample_rate,
            }

            route_thread.start()
            print(
                f"Route {route_id} created: Device {input_device_index} ({input_channels} ch) → "
                f"Device {output_device_index} ({output_channels} ch)"
            )
            return route_id

        except Exception as e:
            print(f"Error creating route: {e}")
            return None

    def _route_audio(
        self,
        route_id,
        input_device_index,
        output_device_index,
        input_channels,
        output_channels,
        sample_rate,
        chunk_size,
    ):
        """Route audio from input device to output device"""
        try:
            # Create input stream with its native channel count
            input_stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=input_channels,
                rate=sample_rate,
                input=True,
                input_device_index=input_device_index,
                frames_per_buffer=chunk_size,
            )

            # Create output stream with its native channel count
            output_stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=output_channels,
                rate=sample_rate,
                output=True,
                output_device_index=output_device_index,
                frames_per_buffer=chunk_size,
            )

            # For mono to stereo conversion, we'll create a simple adapter function
            # that duplicates the mono channel to both stereo channels
            if input_channels == 1 and output_channels == 2:

                def adapter(data, length):
                    # Each float32 is 4 bytes, so the number of samples is length/4
                    count = int(length / 4)

                    # Duplicate each sample across both channels
                    stereo_data = bytearray(length * 2)
                    for i in range(count):
                        # Copy the same sample value to both channels
                        stereo_data[i * 8 : i * 8 + 4] = stereo_data[i * 8 + 4 : i * 8 + 8] = data[
                            i * 4 : i * 4 + 4
                        ]

                    return bytes(stereo_data)
            else:
                # No conversion needed or handled by PyAudio
                adapter = None

            # Continue routing until this specific route is deactivated
            while self.routes[route_id]["active"] and self.running:
                try:
                    # Read audio data with the format of the input device
                    data = input_stream.read(chunk_size, exception_on_overflow=False)

                    # Apply channel conversion if needed
                    if adapter:
                        data = adapter(data, len(data))

                    # Write to output device
                    output_stream.write(data)

                except IOError as e:
                    print(f"Warning in route {route_id}: {e}")
                    time.sleep(0.1)  # Prevent CPU overload on errors

            # Clean up streams when route is stopped
            input_stream.stop_stream()
            input_stream.close()
            output_stream.stop_stream()
            output_stream.close()

        except Exception as e:
            print(f"Error in route {route_id}: {e}")

        finally:
            if route_id in self.routes:
                self.routes[route_id]["active"] = False

            print(f"Route {route_id} stopped")

    def stop_route(self, route_id):
        """Stop a specific audio route"""
        if route_id not in self.routes:
            print(f"Route {route_id} doesn't exist")
            return False

        self.routes[route_id]["active"] = False

        # Wait for thread to complete
        self.routes[route_id]["thread"].join(timeout=2.0)
        del self.routes[route_id]

        print(f"Route {route_id} removed")
        return True

    def list_active_routes(self):
        """List all active audio routes"""
        if not self.routes:
            return "No active routes"

        info = ["Active Routes:"]
        for route_id, route_info in self.routes.items():
            info.append(
                f"Route {route_id}: Device {route_info['input_device']} "
                f"({route_info['input_channels']} ch) → "
                f"Device {route_info['output_device']} ({route_info['output_channels']} ch)"
            )

        return "\n".join(info)

    def close(self):
        """Close the router and terminate all routes"""

        self.running = False

        # Stop all routes
        route_ids = list(self.routes.keys())
        for route_id in route_ids:
            self.stop_route(route_id)

        # Terminate PyAudio
        self.p.terminate()
        print("Audio router closed")
