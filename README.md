# Audio Router

This project provides a terminal-based user interface (TUI) for routing audio between different audio interfaces using <a href="https://people.csail.mit.edu/hubert/pyaudio/">
  PyAudio <img src="https://people.csail.mit.edu/hubert/pyaudio/images/snake-300.png" alt="Snake with Headphones" height="20">
</a>.

It is particularly useful for setups involving virtual audio cables, where routing audio from one software/device to another is needed — for example, directing microphone input to a virtual device that your streaming or recording software listens to.

## Features

- **Interactive TUI** for selecting input and output audio interfaces
- **Real-time audio routing** from input to output device
- **Minimal setup**

## Primary Use Case

Originally built to route audio through a **Virtual Audio Cable** setup, such as:

- Sending mic input to a virtual device
- Monitoring virtual input/output channels
- Bridging physical and software-based audio endpoints

## Prerequisites

- Python 3.7 or higher
- Terminal that supports basic text input

## Setup Instructions

1. **Clone the repository** (if applicable):
   ```bash
   git clone https://github.com/Harsh-br0/audio-router.git
   cd audio-router
   ```

2. (Optional) Create a virtual environment:
   ```bash
    python -m venv venv
    source venv/bin/activate    # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
    pip install -r requirements.txt
   ```

> Note: If you encounter errors installing pyaudio, you may need to install system-level dependencies:
> 
> - On Debian/Ubuntu:
>    ```bash
>      sudo apt-get install portaudio19-dev python3-pyaudio
>    ```
>
> - On macOS:
>    ```bash
>      brew install portaudio
>    ```

## Running the Application

Run the script from the project root:

```bash
   python route.py
```
