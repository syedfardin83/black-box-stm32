################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (13.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../mpu6050/mpu6050.c 

OBJS += \
./mpu6050/mpu6050.o 

C_DEPS += \
./mpu6050/mpu6050.d 


# Each subdirectory must supply rules for building sources it contributes
mpu6050/%.o mpu6050/%.su mpu6050/%.cyclo: ../mpu6050/%.c mpu6050/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m0plus -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32L072xx -c -I../Core/Inc -I../Drivers/STM32L0xx_HAL_Driver/Inc -I../Drivers/STM32L0xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32L0xx/Include -I../Drivers/CMSIS/Include -I"C:/Users/Syed Fardin/Desktop/Coding/mpu6050-stm32/mpu6050_i2c/mpu6050" -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfloat-abi=soft -mthumb -o "$@"

clean: clean-mpu6050

clean-mpu6050:
	-$(RM) ./mpu6050/mpu6050.cyclo ./mpu6050/mpu6050.d ./mpu6050/mpu6050.o ./mpu6050/mpu6050.su

.PHONY: clean-mpu6050

