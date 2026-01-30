# Project Black Box: STM32 Motion Sensing & Analytics

An advanced embedded systems project designed to capture, process, and analyze physical motion in real-time. Built on the **STM32L072CZ** (Cortex-M0+), this project leverages industrial-grade data acquisition techniques to ensure zero-loss monitoring of high-speed gestures and impact events.

**GitHub Repository:** [syedfardin83/black-box-stm32](https://github.com/syedfardin83/black-box-stm32)
**Documentation:** [Notion site](https://syedfardin83.notion.site/Project-Black-Box-2dddcdc7e5e0803c9001f02b95c4b9d5)

---

## The Vision
Project Black Box aims to create a self-contained system capable of sensing physical motion and classifying it into meaningful events—such as specific user gestures, free-falls, or collision impacts. 

### Core Tech Stack
* **MCU:** STM32L072CZ (32MHz, 192KB Flash, 20KB RAM)
* **Sensor:** MPU6050 IMU (Accelerometer + Gyroscope)
* **Kernel:** FreeRTOS (CMSIS-RTOS2 API)
* **Communication:** I2C with DMA (Direct Memory Access)

---

## Black Box 1.1: High-Speed Data Engine
The 1.1 release focuses on the "Data Engine"—ensuring that the MCU can pull data from the sensor and process it without dropping a single sample, even during complex calculations.

### Technical Highlights
* **Double Buffering (Ping-Pong Architecture):** Implemented a 2-slot buffer system (`buffer[2][6]`). While the DMA fills one slot, the CPU calculates data in the other, preventing data tearing.
* **DMA Handshaking:** Utilized I2C Memory Read DMA with custom callbacks (`HAL_I2C_MemRxCpltCallback`) to reset the MPU6050 register pointer and re-trigger transfers with zero CPU intervention.
* **RTOS Synchronization:** Used **Binary Semaphores** to transition the `Calculate` task from a Blocked state to a Ready state, ensuring < 40% CPU utilization and high power efficiency.
* **Float Integration:** Configured the linker for `newlib-nano` float support to handle real-world G-force and Degrees/Second conversions.



### Known Engineering Challenges Overcome
* **The Sleep Trap:** Resolved the MPU6050 default sleep-mode issue by explicitly waking the sensor via the `PWR_MGMT_1` register.
* **The Register Pointer Reset:** Solved the I2C "junk data" issue by manually re-triggering the DMA with the start register address in the completion callback.

---

## Black Box 2.0: Gesture Intelligence (Coming Soon)
While 1.1 was about **acquisition**, 2.0 is about **intelligence**. The next evolution of the project will transform raw sensor values into actionable data.

### The Roadmap
* **Circular Buffering ($n$-buffers):** Expanding the double-buffer into a deep circular queue to store the last 2 seconds of motion data for pattern matching.
* **Dynamic Calibration:** Implementing auto-bias correction for the Gyroscope to eliminate drift during long-term recording.
* **Gesture Recognition Engine:** * **Peak Detection:** Identifying "Strike" or "Impact" gestures.
    * **Euclidean Distance Matching:** Comparing real-time motion curves against "Golden Templates" stored in Flash.
* **EEPROM Logging:** Utilizing the STM32L0's 6KB internal EEPROM to store "Crash Logs"—recording the maximum G-force and orientation during a detected impact.

---

## How to Build
1.  Open the project in **STM32CubeIDE**.
2.  Enable `-u _printf_float` in **Linker > Miscellaneous** to see sensor data.
3.  Ensure the MPU6050 is connected to **I2C1 (PB8/PB9)** with pull-up resistors.
4.  Flash to the **B-L072Z-LRWAN1** Discovery kit.

---
*Developed as part of an advanced embedded systems exploration.*
