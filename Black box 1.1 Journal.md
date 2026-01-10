# Project Black Box

Priority: Medium
Status: In progress

## About project

GitHub - https://github.com/syedfardin83/black-box-stm32

DevBoard used - STM32 B-L072Z-LRWAN1

### **Agenda**

A device that can sense physical motion and detects a certain kind of motion. This motion can be a gesture - like a specific movement, or as simple as a physical drop or a free fall.

If things go well, I will make a system of recording the input and storing it in a suitable format and then detecting the recorded gesture.

### Tech Stack

It is an embedded systems project written for STM32 on C. It will use MPU6050 as an IMU to detect the motion, using the custom library that I built for MPU6050 myself.

It must include the following:

- A DMA for the IMU sensor,
- Double buffering Technique to calculate data
- Writing to EEPROM, once crash detected.

---

## List of tasks

1. Mini project - Apply DMA
2. Get hands on FreeRTOS in stm32 - FreeRTOS + DMA with semaphores
3. Architect the double buffering and then crash detection. 
4. Implement EEPROM read and write functions. - END Black Box 1
5. Gesture recording and detection project - Black Box 2.0

---

## References

- https://www.youtube.com/watch?v=Eh7Szh-K-u8
- https://arm-software.github.io/CMSIS_6/latest/RTOS2/index.html

---

## Remarks/Thoughts

- Learning to talk to the MPU6050 sensor in the previous project was very helpful.

- Benchmarking an MCU
    
    This is a professional-level question. To judge how "stressed" your STM32L072CZ is, you need to look at **three core pillars**: CPU Utilization, Memory Footprint (RAM/Flash), and Power Consumption.
    
    As a systems designer, you aren't just looking for "Does it work?"—you're looking for "How much headroom is left?"
    
    ---
    
    ### 1. CPU Utilization (The "Time" Resource)
    
    This measures how much of the 32MHz clock is spent doing actual work versus sitting in the `IDLE` task.
    
    - **What matters:** **Context Switch overhead** and **Task Execution time**.
    - **How to measure it (The RTOS way):**
        - Enable **Runtime Statistics** in FreeRTOS (via CubeMX). This uses a high-speed timer to track exactly how many microseconds each task consumes.
        - **Calculation:** $Utilization = 1 - (\frac{Time\_in\_IDLE\_Task}{Total\_Time})$.
    - **Target:** For a "Black Box," you want to stay under **70-80% CPU**. If you hit 95%, your `Calculate` task will eventually "starve" the system, leading to dropped I2C samples.
    
    ---
    
    ### 2. Memory Footprint (RAM & Flash)
    
    The STM32L072CZ gives you **192KB of Flash** and **20KB of RAM**.
    
    - **Flash (Non-Volatile):** This is where your code lives.
        - **How to see it:** Look at the **Build Analyzer** in STM32CubeIDE after compiling. It will show a "Memory Usage" gauge.
    - **RAM (Volatile):** This is the most "expensive" resource on your chip.
        - **Static RAM:** Global variables and the `acc_buffer`.
        - **Dynamic RAM (Heap/Stack):** Every FreeRTOS task has its own stack. If your `Calculate` task stack is 512 bytes, that is 2.5% of your *entire* RAM gone.
    - **How to calculate:** `Stack High Water Mark`. Use `uxTaskGetStackHighWaterMark()` to see how many bytes of "safety space" are left in a task's stack. If it's close to 0, you're about to HardFault again.
    
    ---
    
    ### 3. Bus Occupancy (I2C/DMA Bandwidth)
    
    Since you are using I2C at 400kHz (Fast Mode), the bus itself is a resource.
    
    - **What matters:** **Latency**. How long does it take from the moment you request data to the moment the DMA interrupt fires?
    - **How to look at it:** Use a **Logic Analyzer** (like a Saleae) or an Oscilloscope on the SCL/SDA lines.
    - **The Design Check:** If your I2C transfer takes 2ms and you want to sample at 500Hz, you are using **100% of the bus capacity**. You have zero room for other sensors.
    
    ---
    
    ### 4. Interrupt Latency
    
    This is "Advanced Level" system design. It's the time between the hardware event (DMA Complete) and the first line of your `Calculate` task actually running.
    
    - **The Calculation:** $Latency = T_{task\_start} - T_{interrupt\_fired}$.
    - **How to measure:** "Toggle a Pin."
        1. Set a GPIO High at the very start of your `DMAcallback`.
        2. Set it Low at the very start of your `Calculate` task.
        3. Measure the pulse width on an oscilloscope. This tells you exactly how much "RTOS overhead" your system has.
    
    ### Summary of your "Tough" Project Specs:
    
    On your L072CZ, a successful "Black Box" should look like this:
    
    - **CPU:** < 40% (Most time spent waiting for I2C DMA).
    - **RAM:** < 15KB used (Leaving room for your Gesture "Circular Buffer").
    - **EEPROM:** Careful monitoring of **Write Endurance** (6KB limit).
    
    **Would you like me to help you enable the "Build Analyzer" and "Runtime Stats" in your current project so you can see these numbers for yourself?**
    

---

## DMA + FreeRTOS mini project

### Double binary semaphore model

```c
void DMAcallback(){
	releaseSem(calculate);
}

void read_i2c(){
	while(1){
		if(semAquired(readsem)){
			triggerDMA();
		}
	}
}

void calculate(){
	while(1){
		if(semaphoreAquired(calSem)){
			//Calculate
			
			releaseSem(readi2c);
		}
	}
}
```

This could have been implemented with a counting semaphore as well, but:

- It would not be atomic
    - **The Scenario:** Your `read_i2c` task checks `if(osSemaphoreGetCount == 1)`.
    - **The Glitch:** Just as the CPU finishes checking that value, but *before* it executes the `triggerDMA()` line, an interrupt could fire or a higher-priority task could take over.
    - **The Result:** By the time the CPU gets back to the `read_i2c` task, the "state" of the system might have changed, but your task is already committed to the `if` block.
- osWaitForever()
    
    In the double semaphore approach, when either of a task is waiting for a semaphore with the osWaitForever, then it uses almost no CPU cycles, whereas in counting semaphore method, we could waste CPU cycles, checking for the semaphore count.
    
- "Release" adds, it doesn't "Set”
    
    In FreeRTOS/CMSIS, `osSemaphoreRelease` is an **increment** operation (Count = Count + 1).
    
    - To move from State 1 to State 2, you call `Release`.
    - To move from State 2 back to State 1, you call `Acquire`.
    - **The Problem:** If something goes wrong and the DMA interrupt fires twice (due to noise or a bug), your "State" becomes **3**. Now your `if(count == 2)` logic fails, and the whole "Black Box" engine grinds to a halt.

---

## Black Box Project architecture

The purpose of double buffering: The calculations can only be done after the whole buffer is read. If we were to use a single buffer system, then during the time that the calculations are being done, we might loose critical data.

This is where double buffering is helpful.

### Double buffering

There will be two separate buffers and once the DMA writes into one of the buffer, it will immediately switch to writing in the other buffer, while Calculations can be performed using the data in the first buffer. This way, neither does the sensor reading stop, nor does the calculation.

The catch: The calculations has to be completed before the DMA completes writing in the second buffer, otherwise it would defeat the whole purpose.

Possible fix: As  the calculation time increases, we can increase the number of buffers.

Keeping this solution in mind, I would like to design this code in such a way that it can easily be expanded to any number of buffers.

### FAQs and Fails

- Double buffering same as Single buffer?
    
    the main point of double buffering is that data reading must never stop. That means, if I make use of a model with semaphores and a separate task to fire DMAs, then that task would be paused at the cost of the calculation task at some point or the other. That alone is enough to tell me that I should not make a separate task for the readDMA, instead, I must call the dma to the other buffer in the callback of the dma itself. But with this, arises a new problem - with this model, the DMA keeps on switching buffers and firing data, regardless of which buffer the calculation task is running on, which makes it no different than a single buffer approach. Instead, I want the DMA to "wait" until the calculation is done, which beats the whole purpose of double buffering approach. You see, in both the possible cases (DMA waits after both buffers are filled and calculation is still going on in first, and DMA dsnt care about calculation and just fills buffers alternatively, blindly) are same as a single buffer.
    
    Solution - if the calculation is done before the DMA is done in the other buffer, double buffer makes sense, and it is indeed different from a single buffer, because in the same case a single buffer would have to wait to fill the data before the calculations can be performed.
    
- DMA + Double buffering vs Queues
    
    Speed is high in DMA + Double buffering approach
    
- Why circular buffering?
    
    Because with any other approach (Manually calling DMA), the DMA reading will have to wait somewhere, which beats the purpose of double buffering. Otherwise, the left over option is circular buffering.
    
- Polling approach instead of blocking
    
    ```c
    void half_DMA_Callback(){
    	osSempRelease(sem1);
    }
    void DMA_callback(){
    	osSempRelease(sem2);
    }
    
    void calculate(){
    	while(1){
    		if(osSempAquire(sem1)==osOK){
    			//calculate on buff1
    		}else if(osSempAquire(sem2)==osOK){
    			//calculate on sem2
    		}
    	}
    }
    ```
    
    That is a very insightful question. You are thinking about using a **polling** approach (checking the semaphore and moving on) rather than a **blocking** approach (`osWaitForever`).
    
    While you are technically correct that using a timeout of `0` (or a small value) prevents the task from "getting stuck" at that specific line of code, it actually makes your **System Design** weaker for three specific reasons.
    
    ---
    
    ### 1. The "Busy Waiting" Problem (CPU Starvation)
    
    If you don't use `osWaitForever`, your `while(1)` loop will run at the maximum speed of the processor (32MHz).
    
    - **With `osWaitForever`**: The task enters the **Blocked** state. The RTOS scheduler completely ignores it, giving 100% of the CPU to other things (like your background calculations or UI) until the DMA finishes.
    - **Without `osWaitForever`**: Your CPU is constantly "asking" the semaphore: "Are you ready? No? How about now? No?" This generates heat, wastes battery, and can actually slow down your math because the CPU is busy checking a flag instead of doing physics.
    
    ### 2. The Logic Race (The "Missed" Buffer)
    
    Here, the DMA processor and main MCU are racing with each other - DMA is racing to release the sem1, while MCU is racing away from the if statement of sem1. After the actual buff1 reading, it will be uncertain if the calculation will be done on it immediately on it. 
    
    Look at your `if-else if` structure again:
    
    C
    
    `if(osSempAquire(sem1, 0) == osOK){ // Check 1
        // calculate on buff1
    } else if(osSempAquire(sem2, 0) == osOK){ // Check 2
        // calculate on buff2
    }`
    
    If the **Full-Transfer** (sem2) happens while the CPU is exactly at **Check 1**, it fails Check 1, moves to Check 2, and processes `buff2`. That works fine.
    
    **However**, if both semaphores somehow become ready at the same time (which can happen if your math is slightly slow), the `if` will always take `sem1` and **skip** the `else if` for that loop. You would then need to loop all the way back around to catch `sem2`. In a high-speed "Black Box," you want the task to be **driven** by the data, not "looking" for it.
    

### **Implementation Pseudo Code**

**Key: Use a single array with circular mode DMA!!**

```c
void half_DMA_Callback(){
	osSempRelease(sem1);
}
void DMA_callback(){
	osSempRelease(sem1);
}

void calculate(){
	int next_buffer_to_process=0;
	while(1){
		if(osSemaphoreAquire(sem1)==osOK){
			//Identify which buffer to calculate on and proceed with calculation
			//...
			//Toggle next_buffer_to_process;
		}
	}
}
```

Learning - When you want to signal a task, keep it in blocked state using a semaphore, no need to release it later *(that is how it is different from a mutex)*. The function will automatically come into a blocked state until it is signaled again. 

Notice - use of a normal variable to determine which buffer to calculate instead of a semaphore.

Learning - When a choosing mechanism is required, which is not affected by external tasks, just use a normal variable instead of semaphores. Semaphores are used only when you want to notify some internal matter of a task to external matter. In this case, the DMA does not need to know which buffer the calculate task is operating on.

### N buffers approach

mostly same as double buffering.

```c
void DMA_callback(){
	osSempRelease(sem1);
}

void calculate(){
	int next_buffer_to_process=0;
	while(1){
		if(osSemaphoreAquire(sem1)==osOK){
			//Identify which buffer to calculate on and proceed with calculation
			//...
			//Toggle next_buffer_to_process;
		}
	}
}
```