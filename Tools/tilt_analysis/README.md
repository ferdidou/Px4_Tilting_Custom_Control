# Tilting allocation log viewers

Plots the `debug_array` published by the control allocator when `CA_TILTING_TYPE` is 1:
torque scale K\*, vertical and lateral force component per rotor, and tilt servo setpoint.

## tilt_review.html

Open it in a browser, then drop a `.ulg` file on the page. Nothing to install, nothing
leaves the machine.

    xdg-open tilt_review.html

## tilt_review.py

Same plots as a Bokeh page.

    pip install pyulog bokeh
    ./tilt_review.py flight.ulg
    ./tilt_review.py flight.ulg -o out.html --no-browser --cdn

With no argument it takes the most recent flight under
`build/px4_sitl_default/rootfs/log`, or under `$TILT_LOG_DIR`.

## plot_tilt_debug.py

Same plots as a matplotlib window or a PNG.

    pip install pyulog matplotlib
    ./plot_tilt_debug.py flight.ulg
    ./plot_tilt_debug.py flight.ulg -o out.png --armed-only
