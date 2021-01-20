//Load the right librairy depending on board's version
#if defined(ARDUINO) && ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif

#include "EMGFilters.h"

//Sensors input pins
#define TopSensorInputPin A1
#define BottomSensorInputPin A2

//Struct use to store each previous sensor's reading.
//Use in getEMGCount function
struct VarEMGCount
{
  long integralData;
  long integralDatap;
  long integralDataEve;
  bool remainFlag;
  unsigned long timeMillis;
  unsigned long timeBeginzero;
  long fistNum;
  int  TimeStandard;
};

//Relaxed baseline values to remove noise.
unsigned long threshold = 0;
unsigned long calibrationStartTime = 0;
unsigned long highestNoiseValue = 0;

// Numbers of mouvement detected
unsigned long Raise_num = 0;
unsigned long Lower_num = 0;

//Initialisation of the sensor's struc to keep track of previous reading
VarEMGCount topSensorEMGCount = {0, 0, 0, false, 0, 0, 0, 200};
VarEMGCount bottomSensorEMGCount = {0, 0, 0, false, 0, 0, 0, 200};


EMGFilters myFilter;

//Can be `SAMPLE_FREQ_500HZ` or `SAMPLE_FREQ_1000HZ`
SAMPLE_FREQUENCY sampleRate = SAMPLE_FREQ_500HZ;

//Frequency of power line of your country
//Can be `NOTCH_FREQ_50HZ`or `NOTCH_FREQ_60HZ`
NOTCH_FREQUENCY humFreq = NOTCH_FREQ_50HZ;

void setup()
{
  //Initialisation of the filter
  //Params: SAMPLE_FREQUENCY, NOTCH_FREQUENCY, enableNotchFilter, enableLowpassFilter, enableHighpassFilter
  myFilter.init(sampleRate, humFreq, true, true, true);
  
  Serial.begin(115200);
}

void loop()
{
  //Reads sensor's values
  int topData = analogRead(TopSensorInputPin);
  int bottomData = analogRead(BottomSensorInputPin);

  //Filter the values following myFiliter.init params
  int topDataAfterFilter = myFilter.update(topData);
  int bottomDataAfterFilter = myFilter.update(bottomData);

  //Get envelope by squaring the filtered input. Help to reduce noise by outlining the extremes
  int topEnvelope = sq(topDataAfterFilter);
  int bottomEnvelope = sq(bottomDataAfterFilter);

  //The data set below the threshold value is set to 0
  topEnvelope = (topEnvelope > threshold) ? topEnvelope : 0;
  bottomEnvelope = (bottomEnvelope > threshold) ? bottomEnvelope : 0;

  //Set the starting calibration time
  if (calibrationStartTime == 0) { calibrationStartTime = millis(); };
  
  //If calibration has been done, can start detecting mouvment
  if (threshold > 0)
  {
    if (getEMGCount(bottomEnvelope, &bottomSensorEMGCount))
    {
      Lower_num++;
      Serial.print("Lower_num: ");
      Serial.println(Lower_num);
    }
    if (getEMGCount(topEnvelope, &topSensorEMGCount))
    {
      Raise_num++;
      Serial.print("Raise_num: ");
      Serial.println(Raise_num);
    }
  }
  //If calibration has not been done, calibrate the sensor
  else if ( !((millis() - calibrationStartTime) > 5000) )
  {
    //Save the highest value while ralaxing the muscles
    highestNoiseValue = ( topEnvelope > highestNoiseValue ) ? topEnvelope : highestNoiseValue;
    highestNoiseValue = ( bottomEnvelope > highestNoiseValue ) ? bottomEnvelope : highestNoiseValue;
  }
  else
  {
    //Add majoration of 10% to the threshold for safety
    threshold = ( unsigned long ) (highestNoiseValue * 1.10) ;
    Serial.println(threshold);
  }
  delayMicroseconds(500);
}

//Check if muscle movement happened. If yes return 1 else 0
int getEMGCount(int gforce_envelope, VarEMGCount *sensorInfo)
{
  //The integral is processed to continuously add the signal value
  //and compare the integral value of the previous sampling to determine whether the signal is continuous
  sensorInfo->integralDataEve = sensorInfo->integralData;
  //Add the read value to the total value
  sensorInfo->integralData += gforce_envelope;
  
  //If the integral is constant, and it doesn't equal 0, then the time is recorded;
  //If the value of the integral starts to change again, the remainflag is true, and the time record will be re-entered next time
  if ((sensorInfo->integralDataEve == sensorInfo->integralData) && (sensorInfo->integralDataEve != 0))
  {
    sensorInfo->timeMillis = millis();
    if (sensorInfo->remainFlag)
    {
      sensorInfo->timeBeginzero = sensorInfo->timeMillis;
      sensorInfo->remainFlag = false;
      return 0;
    }
    //If the integral value exceeds 200 ms, the integral value is clear 0,return that get EMG signal
    if ((sensorInfo->timeMillis - sensorInfo->timeBeginzero) > sensorInfo->TimeStandard)
    {
      sensorInfo->integralDataEve = sensorInfo->integralData = 0;
      return 1;
    }
    return 0;
  }
  else {
    sensorInfo->remainFlag = true;
    return 0;
   }
}
