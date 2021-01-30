#include "EMGFilters.h"

//Sensors input pins
#define TopSensorInputPin
#define BottomSensorInputPin

//Struct use to store each previous sensor's reading.
//Use in getEMGCount function
struct VarEMGCount;

//Relaxed baseline values to remove noise.
extern unsigned long thresholdTop;
extern unsigned long thresholdBottom;
extern unsigned long calibrationStartTime;
extern unsigned long highestNoiseValueTop;
extern unsigned long highestNoiseValueBottom;

// Numbers of mouvement detected
extern unsigned long Raise_num;
extern unsigned long Lower_num;

//Initialisation of the sensor's struc to keep track of previous reading
extern VarEMGCount topSensorEMGCount;
extern VarEMGCount bottomSensorEMGCount;


extern EMGFilters myFilter;

//Can be `SAMPLE_FREQ_500HZ` or `SAMPLE_FREQ_1000HZ`
extern SAMPLE_FREQUENCY sampleRate;

//Frequency of power line of your country
//Can be `NOTCH_FREQ_50HZ`or `NOTCH_FREQ_60HZ`
extern NOTCH_FREQUENCY humFreq;

void EMGSetup();

void EMGLoop();

//Check if muscle movement happened. If yes return 1 else 0
int getEMGCount(int gforce_envelope, VarEMGCount *sensorInfo);
