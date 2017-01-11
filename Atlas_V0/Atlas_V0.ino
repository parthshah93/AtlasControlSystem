/*************************************************************************
 * Code by Troy Wang
 * Version: V0.2
 * Update Time: 01/10/2017
 * CAUTIONS:
 * 1. Any servo libray cannot be used based on my code.
 * 2. Any serial port library cannot be used based on my code.
 * IMPORTANT COMMENTS:
 * 1. Timer3, Timer4 and Timer5 are used for ESCs control and servo signal generation. 
 *    Desire freq: 50Hz (20ms)
 * 2. Timer2 COMPA is used for system status update: e.g. Motor speed refresh,
 *    servo position refresh, battery voltage and current read, etc. Desire 
 *    freq: 100Hz (10ms)
 * 3. Timer2 COMPA is also used for failsafe.
 * 4. Timer0 is still avaliable for Arduino time functions(e.g. delay()).
 * 5. Motor0 : Pin  -> PWM3A
 *    Motor1 : Pin  -> PWM3B
 *    Motor2 : Pin  -> PWM3C
 *    Motor3 : Pin  -> PWM4A
 *    Servo0 : Pin  -> PWM4B
 *    Servo1 : Pin  -> PWM4C
 *    Servo2 : Pin  -> PWM5A
 *    Servo3 : Pin  -> PWM5B
 *    Servo4 : Pin  -> PWM5C
*************************************************************************/

#include "atlasParser.h"
#include "serialISR.h"
#include "timerConfig.h"
#include "PWM.h"

extern unsigned char recvPackageComplete;
extern unsigned char recvBuffer[256];
extern unsigned char globalRefreshReady;

AtlasComm comm1;
AtlasPWM myPWM;
SysTick mySysTick;
void emergencyStop(){
  
}

void setup() {
  // put your setup code here, to run once:
  usartInit();
  comm1.setVoltage(0, 10000);
  myPWM.init();
  myPWM.start();
  mySysTick.init();
  mySysTick.start();
  interrupts();
}

void refreshMotors(){
  unsigned char i;
  for(i = 0; i < 4; i++)
    myPWM.setMotor(i, comm1.getMotor(i));
}

void refreshServos(){
  unsigned char i;
  for(i = 0; i < 5; i++)
    myPWM.setServo(i, comm1.getServo(i));
}


void loop() {
  // put your main code here, to run repeatedly:
  if(globalRefreshReady){
    if(recvPackageComplete){
  //    sendBuffer(recvBuffer, recvBuffer[0] + 1);
  //    recvPackageComplete = 0;
      comm1.parse(recvBuffer);
      comm1.handleReturnRequest();
      recvPackageComplete = 0;
      refreshMotors();
      refreshServos();
    }
    globalRefreshReady = 0;
  }
}
