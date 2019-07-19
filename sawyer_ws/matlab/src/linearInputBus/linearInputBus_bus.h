/* Generated by S-function Builder */
/* Copyright 2013-2018 The MathWorks, Inc. */
#ifndef _LINEARINPUTBUS_BUS_H_
#define _LINEARINPUTBUS_BUS_H_
/* Read only - STARTS */
#include "tmwtypes.h"




#ifndef _DEFINED_TYPEDEF_FOR_AtmosphereBus_
#define _DEFINED_TYPEDEF_FOR_AtmosphereBus_ 
typedef struct {
  real_T air_temp;
  real_T speed_sound;
  real_T pressure;
  real_T air_density;
} AtmosphereBus;
#endif


#ifndef _DEFINED_TYPEDEF_FOR_EnvironmentBus_
#define _DEFINED_TYPEDEF_FOR_EnvironmentBus_ 
typedef struct {
  real_T Gravity_ned[3];
  AtmosphereBus AtmosphereBus;
  real_T MagneticField_ned[3];
} EnvironmentBus;
#endif

/* Read only - ENDS */


#endif
