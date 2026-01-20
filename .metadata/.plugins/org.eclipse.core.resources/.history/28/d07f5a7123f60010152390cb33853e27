/*
 * mpu6050.c
 *
 *  Created on: Dec 18, 2025
 *      Author: Syed Fardin
 */
#include "main.h"
#include "mpu6050.h"
#include "stdio.h"


uint8_t MPU6050_WakeUp(I2C_HandleTypeDef *i2c){
	uint8_t data = 0x0;
	if(HAL_I2C_Mem_Write(i2c,MPU6050_ADDR<<1,REG_PWR_MGMT_1,1,&data,1,2000)==HAL_OK)
		return 1;
	else
		return 0;
}

uint8_t MPU6050_Who(I2C_HandleTypeDef *i2c){
	uint8_t data = 0;
	if(HAL_I2C_Mem_Read(i2c,MPU6050_ADDR<<1,REG_WHO_AM_I,1,&data,1,2000)==HAL_OK)
		return data;
	else
		return 0;
}

float MPU6050_Read_AccX(I2C_HandleTypeDef *i2c){
	uint8_t data[2];

	if(HAL_I2C_Mem_Read(i2c,MPU6050_ADDR<<1,REG_ACCEL_XOUT_H,1,data,2,100)==HAL_OK){
//		printf("\nRead data!");
		return (((int16_t)(data[0]<<8 | data[1]))/16384.0);
//		return (int16_t)(data[1]);
	}else{
		printf("\nFailed to read!");
		return 44;
	}

}

float MPU6050_Read_AccY(I2C_HandleTypeDef *i2c){
	uint8_t data[2];

	if(HAL_I2C_Mem_Read(i2c,MPU6050_ADDR<<1,REG_ACCEL_YOUT_H,1,data,2,100)==HAL_OK){
//		printf("\nRead data!");
		return (((int16_t)(data[0]<<8 | data[1]))/16384.0);
//		return (int16_t)(data[1]);
	}else{
		printf("\nFailed to read!");
		return 44;
	}

}

float MPU6050_Read_AccZ(I2C_HandleTypeDef *i2c){
	uint8_t data[2];

	if(HAL_I2C_Mem_Read(i2c,MPU6050_ADDR<<1,REG_ACCEL_ZOUT_H,1,data,2,100)==HAL_OK){
//		printf("\nRead data!");
		return (((int16_t)(data[0]<<8 | data[1]))/16384.0);
//		return (int16_t)(data[1]);
	}else{
		printf("\nFailed to read!");
		return 44;
	}

}

float MPU6050_Read_GyroX(I2C_HandleTypeDef *i2c){
	uint8_t data[2];

		if(HAL_I2C_Mem_Read(i2c,MPU6050_ADDR<<1,REG_GYRO_XOUT_H,1,data,2,100)==HAL_OK){
	//		printf("\nRead data!");
			return (((int16_t)(data[0]<<8 | data[1]))/131.0);
	//		return (int16_t)(data[1]);
		}else{
			printf("\nFailed to read!");
			return 44;
		}
}

float MPU6050_Read_GyroY(I2C_HandleTypeDef *i2c){
	uint8_t data[2];

		if(HAL_I2C_Mem_Read(i2c,MPU6050_ADDR<<1,REG_GYRO_YOUT_H,1,data,2,100)==HAL_OK){
	//		printf("\nRead data!");
			return (((int16_t)(data[0]<<8 | data[1]))/131.0);
	//		return (int16_t)(data[1]);
		}else{
			printf("\nFailed to read!");
			return 44;
		}
}

float MPU6050_Read_GyroZ(I2C_HandleTypeDef *i2c){
	uint8_t data[2];

		if(HAL_I2C_Mem_Read(i2c,MPU6050_ADDR<<1,REG_GYRO_ZOUT_H,1,data,2,100)==HAL_OK){
	//		printf("\nRead data!");
			return (((int16_t)(data[0]<<8 | data[1]))/131.0);
	//		return (int16_t)(data[1]);
		}else{
			printf("\nFailed to read!");
			return 44;
		}
}
