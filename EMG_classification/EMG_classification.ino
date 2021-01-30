//Load the right librairy depending on board's version
#if defined(ARDUINO) && ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif

#include "EMG_classification.h"

void setup()
{
  EMGSetup();
}

void loop()
{
  EMGLoop();
}
