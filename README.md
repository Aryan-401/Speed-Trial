# Optical Flow Speed Estimation

This project uses optical flow to try to determine the speed of a vehacle in a predetermined area (as stated by user)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

```bash
$ git clone https://github.com/Aryan-401/Speed-Trial.git

$ cd Speed-Trial
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python3 speed.py
```

# How to use

1. Run the program using

```bash
$ python3 speed.py -f <path to video> -c <value of constant>
```

2. Select the Area of Interest by clicking on any 4 points to create a polygon. Preferable to make the polygon just
   larger than the vehicle being tracked.

3. To exit, press the Esc key

# Example

```bash
$ python3 speed.py -f "data/traffic_-_27260 (540p).mp4" -c 7.8
```

As a video [here](assets%2Fdemo.webm)

Note: Speed is in km/hr