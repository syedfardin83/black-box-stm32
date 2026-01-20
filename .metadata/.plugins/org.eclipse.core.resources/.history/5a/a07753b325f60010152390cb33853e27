/*
 * mpu6050.h
 *
 *  Created on: Dec 18, 2025
 *      Author: Syed Fardin
 */
#include "main.h"
#ifndef MPU6050_H_
#define MPU6050_H_


#define MPU6050_ADDR 0x68

#define REG_PWR_MGMT_1 0x6b
#define REG_WHO_AM_I 0x75
#define REG_ACCEL_XOUT_L  0x3c
#define REG_ACCEL_XOUT_H 0x3b
#define REG_ACCEL_YOUT_H 0x3d
#define REG_ACCEL_ZOUT_H 0x3f
#define REG_GYRO_XOUT_H 0x43
#define REG_GYRO_YOUT_H 0x45
#define REG_GYRO_ZOUT_H 0x47


float MPU6050_Read_AccX(I2C_HandleTypeDef *i2c);
float MPU6050_Read_AccY(I2C_HandleTypeDef *i2c);
float MPU6050_Read_AccZ(I2C_HandleTypeDef *i2c);

float MPU6050_Read_GyroX(I2C_HandleTypeDef *i2c);
float MPU6050_Read_GyroY(I2C_HandleTypeDef *i2c);
float MPU6050_Read_GyroZ(I2C_HandleTypeDef *i2c);

uint8_t MPU6050_WakeUp(I2C_HandleTypeDef *i2c);
uint8_t MPU6050_Who(I2C_HandleTypeDef *i2c);


#endif /* MPU6050_H_ */
