/* mbed Microcontroller Library
 * Copyright (c) 2006-2013 ARM Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <events/mbed_events.h>
#include "mbed.h"
#include "ble/BLE.h"
#include "EnvironmentalService_v2.h"
//#include "debug.h"

// Uncomment this line if you want to use the board temperature sensor instead of
// a simulated one.
#define USE_BOARD_SENSORS

#ifdef USE_BOARD_SENSORS
#include "stm32l475e_iot01_tsensor.h"
#include "stm32l475e_iot01_hsensor.h"
#include "stm32l475e_iot01_psensor.h"
#endif

#define ADVERTISING_INTERVAL 1000
#define UPDATE_VALUES_INTERVAL 1000

DigitalOut led1(LED1, 0);
DigitalOut led2(LED2, 0);

const static char     DEVICE_NAME[]        = "IoT_SENSOR";
static const uint16_t uuid16_list[]        = {GattService::UUID_ENVIRONMENTAL_SERVICE};
static EnvironmentalService *environmentServicePtr;

/* initial dummy values */
static float                     currentTemperature   = -15.0;
static float                     currentHumidity      = 0.0;
static float                     currentPressure      = 260.0 * 100; // hPa -> Pascal

static EventQueue eventQueue(/* event count */ 16 * EVENTS_EVENT_SIZE);
static int id_adv; 
static int id_conn;

void updateSensorValue(void) {
    
    static int16_t lastTemperature;
    static uint16_t lastHumidity;
    static uint32_t lastPressure;
    
    int16_t tempTemperature = 0;
    uint16_t tempHumidity = 0;
    uint32_t tempPressure = 0;

#ifdef USE_BOARD_SENSORS
    currentTemperature = BSP_TSENSOR_ReadTemp();  
    currentHumidity = BSP_HSENSOR_ReadHumidity();
    currentPressure = BSP_PSENSOR_ReadPressure();
    currentPressure = currentPressure*100; // hPa -> Pascal
#else
    /* dummy values */
    currentTemperature = (currentTemperature + 0.1f > 43.0f) ? -15.0f : currentTemperature + 0.1f;
    currentHumidity = (currentHumidity + 0.1f > 100.0f) ? 0.0f : currentHumidity + 0.1f;
    currentPressure = (currentPressure + 10 > 126000.0f) ? 26000.0f : currentPressure + 10;
#endif

#ifdef DEBUG
    pc.printf("\r\n");               
    pc.printf("T_sensor = %.2f C\r\n", ((int16_t)(currentTemperature*100))/100.0);
    pc.printf("H_sensor = %.2f %%\r\n", ((uint16_t)(currentHumidity*100))/100.0); 
    pc.printf("P_sensor = %.1f Pa\r\n", ((uint32_t)(currentPressure*10))/10.0); 
    pc.printf("\r\n");
#endif

    tempTemperature = (int16_t)(currentTemperature*100);
    tempHumidity = (uint16_t)(currentHumidity*100);
    tempPressure = (uint32_t)(currentPressure*10);
    
    /* Update char values, but only if they differ from previous */
    if(tempTemperature != lastTemperature)
    {
        environmentServicePtr->updateTemperature(tempTemperature);
        lastTemperature = tempTemperature;
    }
    if(tempHumidity != lastHumidity)
    {
        environmentServicePtr->updateHumidity(tempHumidity);
        lastHumidity = tempHumidity;
    }
     if(tempPressure != lastPressure)
    {
        environmentServicePtr->updatePressure(tempPressure);
        lastPressure = tempPressure;
    }       
}

void periodicCallback(void)
{
    /* Do blinky on LED1 while advertising */
    led1 = !led1; 
    wait(0.25);
    led1 = !led1;
}

/* On Connection event start updating sensor values */
void connectionCallback(const Gap::ConnectionCallbackParams_t *)
{
#ifdef DEBUG
    pc.printf("\r\n"); 
    pc.printf("Connection Event.\r\n");
#endif
    eventQueue.cancel(id_adv); 
    led1 = 0; 
    led2 = 1; // LED2 on when connected
    updateSensorValue();
    id_conn = eventQueue.call_every(UPDATE_VALUES_INTERVAL, updateSensorValue);
}

/* Restart Advertising on disconnection*/
void disconnectionCallback(const Gap::DisconnectionCallbackParams_t *)
{
    eventQueue.cancel(id_conn);
    led2 = 0; // LED2 off when disconnected
    BLE::Instance().gap().startAdvertising();
    id_adv = eventQueue.call_every(ADVERTISING_INTERVAL, periodicCallback);
    

#ifdef DEBUG
    pc.printf("\r\n"); 
    pc.printf("Disconnection Event - Start Advertising...\r\n");
#endif
}

void onBleInitError(BLE &ble, ble_error_t error)
{
   /* Initialization error handling should go here */
#ifdef DEBUG
     pc.printf("BLE Init Error: %u\r\n", error);
#endif

    while(1)
    {   /* Do blinky on LED2 on Error */
        led2 = !led2; 
        wait(0.25);
    }
}

void bleInitComplete(BLE::InitializationCompleteCallbackContext *params)
{
    BLE&        ble   = params->ble;
    ble_error_t error = params->error;

    if (error != BLE_ERROR_NONE) {
        onBleInitError(ble, error);
        return;
    }

    /* Ensure that it is the default instance of BLE */
    if (ble.getInstanceID() != BLE::DEFAULT_INSTANCE) {
        return;
    }
    
    /* Callback function when connected */
    ble.gap().onConnection(connectionCallback);
    /* Callback function when disconnected */
    ble.gap().onDisconnection(disconnectionCallback);

    /* Setup primary service. */
    environmentServicePtr = new EnvironmentalService(ble);

    /* setup advertising */
    ble.gap().accumulateAdvertisingPayload(GapAdvertisingData::BREDR_NOT_SUPPORTED | GapAdvertisingData::LE_GENERAL_DISCOVERABLE);
    ble.gap().accumulateAdvertisingPayload(GapAdvertisingData::COMPLETE_LIST_16BIT_SERVICE_IDS, (uint8_t *)uuid16_list, sizeof(uuid16_list));
    ble.gap().accumulateAdvertisingPayload(GapAdvertisingData::COMPLETE_LOCAL_NAME, (uint8_t *)DEVICE_NAME, sizeof(DEVICE_NAME));
    ble.gap().setAdvertisingType(GapAdvertisingParams::ADV_CONNECTABLE_UNDIRECTED);
    ble.gap().setAdvertisingInterval(ADVERTISING_INTERVAL); 
    ble.gap().startAdvertising();
}

void scheduleBleEventsProcessing(BLE::OnEventsToProcessCallbackContext* context) {
    BLE &ble = BLE::Instance();
    eventQueue.call(Callback<void()>(&ble, &BLE::processEvents));
}

int main()
{
#ifdef USE_BOARD_SENSORS
    BSP_TSENSOR_Init();
    BSP_HSENSOR_Init();
    BSP_PSENSOR_Init();
#endif
 
#ifdef DEBUG   
    pc.printf("== BLE - EnvironmentalService ==\r\n");
#endif
    
    id_adv = eventQueue.call_every(ADVERTISING_INTERVAL, periodicCallback);

    BLE &ble = BLE::Instance();
    ble.onEventsToProcess(scheduleBleEventsProcessing);

#ifdef DEBUG     
    pc.printf("Init BLE...\r\n");
#endif
  
    ble.init(bleInitComplete);
     
#ifdef DEBUG    
    pc.printf("Init complete - Advertising...\r\n");
#endif

    eventQueue.dispatch();

    return 0;
}
