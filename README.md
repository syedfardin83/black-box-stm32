A device that can sense physical motion and detects a certain kind of motion. This motion can be a gesture - like a specific movement, or as simple as a physical drop or a free fall.

If things go well, I will make a system of recording the input and storing it in a suitable format and then detecting the recorded gesture.

### Tech Stack

It is an embedded systems project written for STM32 on C. It will use MPU6050 as an IMU to detect the motion, using the custom library that I built for MPU6050 myself.

It must include the following:

- A DMA for the IMU sensor,
- Double buffering Technique to calculate data
