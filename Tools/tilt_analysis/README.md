# Tilting allocation log viewer

Plots the `debug_array` published by the control allocator when `CA_TILTING_TYPE` is 1:
torque scale K\*, vertical and lateral force component per rotor, and tilt servo setpoint.

## How to run

Open the page in a browser, then drop a `.ulg` file on it. Nothing to install, and the
log is read locally.

    xdg-open tilt_review.html

Wheel zooms the time axis, drag pans, shift+drag selects a window, double-click resets.
Click a legend entry to hide a curve. *Image of all* exports the plots as a PNG, over the
window currently shown.
