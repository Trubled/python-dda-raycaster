# Python DDA Raycaster Engine

A custom 3D retro rendering engine built completely from scratch in python using 'pygame-ce', demonstrating low level graphics programming and spatial mathematics without relying on heavy game engines or external rendering frameworks.

## Core Features & mathematics
** DDA (Digital Differential Analysis) Algorithm: Implemented for efficient ray grid traversal to accurately detect and calculate wall collisions.
* Trigonometric Rotation Matrices: Powers smooth player camera movement, direction vectors, and field-of-view calculations.
* Fish-Eye correction: Applies perpendicular distance calculations to eliminate geometric distortion across screen columns.
*  Pixel-Buffering & Surface Rendering : Dynamically projects column slices onto the display window in real-time.

## Tech Stack
* Language: Python 3.x 
* Library: 'pygame-ce' (SDL2 wrapper)

## How To running 1. Ensure you have Python installed along with 'pygame-ce' and 'numpy':
   '''bash
   pip install pygame-ce numpy
   2. Run the script: python raycaster.py