# Px4_Tilting_Custom_Control
 Customization of PX4 firmware to introduce a custom flight control stack

## Efficient Development of Model-Based Controllers in PX4 Firmware: A Template-Based Customization Approach
__abstract__ This paper introduces a refined iteration of the PX4 autopilot firmware tailored to support developers in integrating bespoke control algorithms alongside the existing control framework. The proposed methodology employs a template-driven approach and introduces two novel control modules, thereby enabling users to harness all firmware functionalities within their custom modalities, including the QGroundControl interface, while retaining all the standard modules and compatibility with the QGroundControl interface. With its transparent and adaptable structure, the software framework presented herein lays a robust groundwork for implementing tailored and specialized solutions across diverse aerospace domains. As a practical demonstration, we apply the developed firmware to the domain of inspection and maintenance, wherein it incorporates an admittance controller and a model-based control algorithm for a tiltable drone equipped with a sensorized tool. The efficacy and versatility of the proposed approach are validated through simulations and empirical trials conducted across multiple aerial platforms. The produced code is released to the community.
## Article
The description of the firmware architecture, the integration with the standard PX4 control stack, as well as its integration with a PixHawk autopilot, are described in the following article:

Simone D'Angelo, Francesca Pagano, Francesco Longobardi, Fabio Ruggiero, Vincenzo Lippiello, "Efficient Development of Model-Based Controllers in PX4 Firmware: A Template-Based Customization Approach", submitted to the 2024 International Conference on Unmanned Aircraft System (ICUAS ’24)  June 4-7, Chania, Crete, Greece

This work is currently under review

## Video


# How to use

## Setup (Ubuntu 20.04 / 22.04)
1. Clone the repository **with submodules** (pulls the custom Gazebo models too): <br />
`git clone --recurse-submodules https://github.com/ferdidou/Px4_Tilting_Custom_Control.git` <br />
`cd Px4_Tilting_Custom_Control`
2. Install the PX4 toolchain and dependencies (one time only, then reboot): <br />
`bash ./Tools/setup/ubuntu.sh` <br />
3. Build & run a SITL simulation with one of the commands below.

> Already cloned without submodules? Run `git submodule update --init --recursive`.

## Run the simulation
For the tilting hexarotor (6 arms, 1 rotor + 1 tilt servo per arm) <br />
`make px4_sitl gazebo_hexa_tilting`

For omnidirectional tilting drone <br />
`make px4_sitl gazebo_NDT_tilting`
 or <br />
`make px4_sitl gazebo_NDT_tilting_interaction`

For one-tilt tilting drone <br />
`make px4_sitl gazebo_baby_k`
or  <br />
`make px4_sitl gazebo_baby_k_interaction`

### Custom tilting hexarotor model
Our contribution: a 6-arm tilting hexarotor (1 rotor + 1 tilt servo per arm), added to the standard PX4 tilting stack. <br />
- Airframe: `ROMFS/.../airframes/25005_gazebo-classic_hexa_tilting` (omnidirectional tilting, `CA_AIRFRAME 13`, `CA_TILTING_TYPE 1`). <br />
- Gazebo model: `Tools/simulation/gazebo-classic/sitl_gazebo-classic/models/hexa_tilting`. <br />
- The control allocator was extended from 4 to 6 tilt servos to support this platform. <br />

Trigger the custom flight modes:<br />
`commander mode prisma:man` to send command through RC<br />
or<br />
`commander mode prisma:prisma1` to send command through ROS2 network

### The ros2 planner is available here <br />
https://github.com/prisma-lab/px4_ros_com <br />
select the default branch for stable custom release 1.13, or switch to branch 1.14 for the latest custom stable release <br />

### The custom PX4 msgs definition is available here <br />
https://github.com/prisma-lab/px4_msgs <br />
Select the same branch of the planner to match with the right message definition <br />

### The custom QGC interface is available here <br />
https://github.com/prisma-lab/qgroundcontrol.git
