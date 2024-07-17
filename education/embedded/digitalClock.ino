// Author: a3delta
// About: A digital clock with an alarm feature.

// includes
#include "TFT_eSPI.h"
#include "LIS3DHTR.h"

// LCD variables
TFT_eSPI tft;           // LCD variable
bool bLight = true;     // flag to track backlight state
int bLightSec = 0;      // to track time since last disturbance

// accelerometer variables
LIS3DHTR<TwoWire> lis;  // accelerometer variable
float xval, yval, zval; // for reading axii
float xT, yT, zT;       // temps for axii comparisons
float xDist, yDist, zDist;  // for checking disturbances
float xLast, xAngle;    // for checking changes in angles
float xDiff;            // for calculating the difference in angles

// variables - delay handling
unsigned long lastTick = 0;
unsigned long sDelay = 1000;
unsigned long lastLight = 0;

// variables - clock
int mode = 0;           // clock mode = 0; alarm mode = 1
int clock[3];           // active clock, hours (0-23), minutes (0-59), and seconds (0-59)
int alarm[2];           // alarm time, hours (0-23) and minutes (0-59)
bool triggered = false; // for tracking when alarm is actively beeping
bool initAlarm = true;  // flag for setting alarm on first run without setting it off

// variables - printing
bool pFlag = true;      // flag for signalling when to update display


// run-once setup code
void setup() {

  // initialize KEYS A, B, and C as inputs
  // INPUT_PULLUP sets signal default HIGH; more reliable signal reads
  pinMode(WIO_KEY_A, INPUT_PULLUP);
  pinMode(WIO_KEY_B, INPUT_PULLUP);
  pinMode(WIO_KEY_C, INPUT_PULLUP);
  
  // setup WIO_KEY_A and WIO_KEY_B as interrupts
  // interrupt calls the function (2nd param), looks for HIGH to LOW change (FALLING)
  attachInterrupt(digitalPinToInterrupt(WIO_KEY_A), fHour, FALLING);
  attachInterrupt(digitalPinToInterrupt(WIO_KEY_B), fMin, FALLING);
  attachInterrupt(digitalPinToInterrupt(WIO_KEY_C), fMode, FALLING);

  // initialize LCD - set colors and text size
  tft.begin();
  tft.setRotation(3);                         // rotation set to corner 3
  tft.fillScreen(TFT_GREEN);                  // fill the screen with green
  digitalWrite(LCD_BACKLIGHT, HIGH);          // turn on the backlight
  tft.setTextColor(TFT_BLACK);                // set screen text to black
  tft.setTextSize(6);                         // set text size to 6
  
  // initialize accelerometer
  lis.begin(Wire1);
  lis.setOutputDataRate(LIS3DHTR_DATARATE_25HZ);    // set the output data rate to 25 Hz
  lis.setFullScaleRange(LIS3DHTR_RANGE_2G);         // set the scale range to 2g
  xLast = lis.getAccelerationX();                   // initialize xLast data

  // initialize LED and BUZZER outputs
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);   // turn the LED off
  pinMode(WIO_BUZZER, OUTPUT);
  lastTick = millis();

  // initialize clock[] and alarm[]
  clock[0] = 0;
  clock[1] = 0;
  clock[2] = 0;
  alarm[0] = 0;
  alarm[1] = 60;        // initialized to 60, will be set to 0 once WIO_KEY_C is pressed once

  // initialize accelerometer temp values
  xT = lis.getAccelerationX();
  yT = lis.getAccelerationY();
  zT = lis.getAccelerationZ();

  // initialize accelerometer x angles
  xLast = xval*90;

}

// main code, run as infinite loop
void loop() {

  // millis() loop to update seconds every 1000 ms
  // blink blue LED for each update of seconds (fast < 100 ms)
  if( (millis() - lastTick) >= sDelay ){
    lastTick = millis();            // update lastTick for next Tock
    clock[2] = clock[2] + 1;        // incrememnt clock seconds
    pFlag = true;                   // enable flag once incremented
    
    digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on
    delay(50);                        // wait for 50 ms
    digitalWrite(LED_BUILTIN, LOW);   // turn the LED off
    delay(50);                        // wait for 50 ms
  }

  // if seconds hit 60, reset to 0 and increment minutes
  if(clock[2] > 59){
    clock[2] = 0;
    clock[1] = clock[1] + 1;

    // if minutes hit 60, reset to 0 and increment hours
    if(clock[1] > 59){
      clock[1] = 0;
      clock[0] = clock[0] + 1;

      // if hours hit 24, reset to 0
      if(clock[0] > 23){
        clock[0] = 0;
      }
    }
  }

  // if mode = 0; print clock as HH:MM:SS, else, print alarm as HH:MM
  if(pFlag){
    pFlag = false;            // disable flag once triggered
    
    // reset screen
    tft.fillScreen(TFT_GREEN);                // clear screen; reset to solid green

    if(mode == 0){
      // center cursor and print
      tft.setCursor(20,100);
      if(clock[0] < 10){
        tft.print("0");
      }
      tft.print(clock[0]); tft.print(":");
      if(clock[1] < 10){
        tft.print("0");
      }
      tft.print(clock[1]); tft.print(":");
      if(clock[2] < 10){
        tft.print("0");
      }
      tft.print(clock[2]);
    }
    else{
      // center cursor and print
      tft.setCursor(72,100);
      if(alarm[0] < 10){
        tft.print("0");
      }
      tft.print(alarm[0]); tft.print(":");
      if(alarm[1] < 10){
        tft.print("0");
      }
      tft.print(alarm[1]);
    }
  }

  // if alarm = clock, trigger the buzzer until WIO_KEY_C is pressed
  // check if seconds = 0 to prevent retriggers for the remainder of the minute
  if(clock[2] == 0){
    if( (alarm[0] == clock[0]) && (alarm[1] == clock[1]) ){
      triggered = true;
    }
  }

  // if triggered, activate 
  // switch to millis() trigger for delay
  if(triggered){
    analogWrite(WIO_BUZZER, 128);
    delay(100);
    analogWrite(WIO_BUZZER, 0);
    delay(100);
  }

  // if the backlight is off, test x acceleration for wake up
  // else, test x acceleration for sleep
  if(!bLight){
    // read acceleration of device
    xval = lis.getAccelerationX();
    
    // convert to degrees - degrees = rads*(180/pi)
    xAngle = xval*90;             // appears to be more accurate - xval = 1 at 90 deg, 0.5 at 45 deg, etc
    if(xAngle < 0){
      xAngle = xAngle * -1;
    }

    // if tilted 50+ deg on x, turn on backlight
    xDiff = xAngle - xLast;
    //if( (xDiff > 50) || ((1 - xDiff) > 50) ){
    if(xDiff > 50){
      digitalWrite(LCD_BACKLIGHT, HIGH);      // turn on the backlight
      bLight = true;
    }
  }
  else{
    // only poll every 1000 ms/1 sec
    // 1000 was triggering at 3 s instead of 5 s, so added 300 ms
    if( (millis() - lastLight) >= 1300 ){
      // update lastLight
      lastLight = millis();

      // read acceleration of device
      xval = lis.getAccelerationX();
      yval = lis.getAccelerationY();
      zval = lis.getAccelerationZ();

      // calc disturbances
      xDist = xval - xT;
      yDist = yval - yT;
      zDist = zval - zT;

      // update axii temps
      xT = xval;
      yT = yval;
      zT = zval;

      // find absolute value of each
      if(xDist < 0){
        xDist = xDist * -1;
      }
      if(yDist < 0){
        yDist = yDist * -1;
      }
      if(zDist < 0){
        zDist = zDist * -1;
      }

      // if not disturbed more than set amount, turn off backlight
      if( (xDist >= 0) || (xDist <= 0.1) ){
        bLightSec++;
      }
      else if( (yDist >= 0) || (yDist <= 0.1) ){
        bLightSec++;
      }
      else if( (zDist >= 0) || (zDist <= 0.1) ){
        bLightSec++;
      }
      else{
        bLightSec = 0;
      }

      // if 5 sec of no disturbances, turn off backlight
      if(bLightSec > 4){
        bLightSec = 0;
        digitalWrite(LCD_BACKLIGHT, LOW);           // turn off the backlight
        bLight = false;
      }
    }
  }

}

void fHour() {
  // activate buzzer
  // switch to millis() trigger for delay?
  analogWrite(WIO_BUZZER, 128);
  delay(100);
  analogWrite(WIO_BUZZER, 0);
  delay(100);

  pFlag = true;                   // enable flag once incremented
  
  // increment hours based on mode
  if(mode == 0){
    // if not at 23, increment, else, roll over to 0
    if(clock[0] != 23){
      clock[0] = clock[0] + 1;
    }
    else{
      clock[0] = 0;
    }
    clock[2] = 0;         // reset seconds to 0
  }
  else{
    // if not at 23, increment, else, roll over to 0
    if(alarm[0] != 23){
      alarm[0] = alarm[0] + 1;
    }
    else{
      alarm[0] = 0;
    }
  }
}

void fMin() {
  // activate buzzer
  // switch to millis() trigger for delay?
  analogWrite(WIO_BUZZER, 128);
  delay(100);
  analogWrite(WIO_BUZZER, 0);
  delay(100);

  pFlag = true;                   // enable flag once incremented

  // increment minutes based on mode
  if(mode == 0){
    // if not at 59, increment, else, roll over to 0
    if(clock[1] != 59){
      clock[1] = clock[1] + 1;
    }
    else{
      clock[1] = 0;
    }
    clock[2] = 0;         // reset seconds to 0
  }
  else{
    // if not at 59, increment, else, roll over to 0
    if(alarm[1] != 59){
      alarm[1] = alarm[1] + 1;
    }
    else{
      alarm[1] = 0;
    }
  }
}

void fMode() {
  // on first run, initialize blank alarm
  if(initAlarm){
    initAlarm = false;
    alarm[1] = 0;
  }

  // if alarm has not been triggered, change between clock and alarm
  // else, disable the alarm
  if(!triggered){
    // change to the opposite mode
    if(mode == 0){
      mode = 1;
    }
    else{
      mode = 0;
    }
  }
  else{
    triggered = false;
  }
}
