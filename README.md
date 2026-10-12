# Px4_Tilting_Custom_Control
 Customization of PX4 firmware to introduce a custom flight control stack


# Px4_Tilting_Custom_Control — Mini-Tilt hexarotor

PX4 v1.14 firmware for a **tilting-arm hexarotor** (6 arms, 1 rotor + 1 tilt servo per arm),
flown in position mode with OptiTrack motion capture.

This repository is a fork of
[**prisma-lab/Px4_Tilting_Custom_Control**](https://github.com/prisma-lab/Px4_Tilting_Custom_Control)
(PRISMA Lab, University of Naples Federico II), which provides the custom control stack and the
tilting-rotor control allocation this work is built on. The original framework is described in
the article cited [below](#original-work). All credit for the base architecture goes to its authors;
this fork adds the hexarotor platform, its simulation model and several fixes.

---

## Video

Mini-Tilt hexarotor in the OptiTrack room, position mode.



https://github.com/user-attachments/assets/2e5ec70d-94ec-4505-82ac-0492043b8518



## How to use

### Setup (Ubuntu 20.04 / 22.04)

1. Clone the repository **with submodules** (pulls the custom Gazebo models too):
```
   git clone --recurse-submodules https://github.com/ferdidou/Px4_Tilting_Custom_Control.git
   cd Px4_Tilting_Custom_Control
```
   Already cloned without submodules? `git submodule update --init --recursive`
2. Install the PX4 toolchain (once, then reboot):
```
   bash ./Tools/setup/ubuntu.sh
```

### Run the simulation

Mini-Tilt hexarotor (this fork):
```
make px4_sitl gazebo_mini_tilt_hexa
```

Generic tilting hexarotor:
```
make px4_sitl gazebo_hexa_tilting
```

Platforms from the original repository:
```
make px4_sitl gazebo_NDT_tilting          # omnidirectional tilting drone
make px4_sitl gazebo_NDT_tilting_interaction
make px4_sitl gazebo_baby_k               # one-tilt drone
make px4_sitl gazebo_baby_k_interaction
```

Custom flight modes (from the original stack):
```
commander mode prisma:man       # commands through RC
commander mode prisma:prisma1   # commands through the ROS 2 network
```

### Command a body attitude during flight

In position mode, set the desired pitch and roll (in degrees) from the PX4 shell
(MAVLink console in QGroundControl, or the `pxh>` prompt in SITL):
```
param set MC_DES_PITCH 5     # hold +5° of pitch
param set MC_DES_ROLL 0
param set MC_DES_PITCH 0     # back to level
```
The parameters can also be changed from the QGroundControl *Parameters* page.
The vehicle keeps its position while holding the commanded attitude.
They are ignored as soon as a message arrives on `tilting_mc_desired_angles` (ROS 2 interface).

### Companion repositories (PRISMA Lab)

- ROS 2 planner: <https://github.com/prisma-lab/px4_ros_com> (branch 1.14)
- Custom PX4 messages: <https://github.com/prisma-lab/px4_msgs> (same branch as the planner)
- Custom QGroundControl: <https://github.com/prisma-lab/qgroundcontrol>

---

## Original work

This fork builds on the firmware customization presented in:

> S. D'Angelo, F. Pagano, F. Longobardi, F. Ruggiero, V. Lippiello,
> **"Efficient Development of Model-Based Controllers in PX4 Firmware: A Template-Based Customization Approach,"**
> *2024 International Conference on Unmanned Aircraft Systems (ICUAS)*, Chania, Greece, 2024, pp. 1155–1162.
> DOI: [10.1109/ICUAS60882.2024.10556938](https://doi.org/10.1109/ICUAS60882.2024.10556938)

Original repository: <https://github.com/prisma-lab/Px4_Tilting_Custom_Control>

If you use this code, please cite the original article:

```bibtex
@inproceedings{dangelo2024efficient,
  author    = {D'Angelo, Simone and Pagano, Francesca and Longobardi, Francesco and Ruggiero, Fabio and Lippiello, Vincenzo},
  title     = {Efficient Development of Model-Based Controllers in {PX4} Firmware: A Template-Based Customization Approach},
  booktitle = {2024 International Conference on Unmanned Aircraft Systems (ICUAS)},
  pages     = {1155--1162},
  year      = {2024},
  doi       = {10.1109/ICUAS60882.2024.10556938}
}
```

## License

BSD-3-Clause, as the original repository and PX4. The original copyright notices are kept.

