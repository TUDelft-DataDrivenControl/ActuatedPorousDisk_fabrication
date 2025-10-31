#ifndef SERIAL_COMM_H
#define SERIAL_COMM_H

// #include <ADS1115_lite.h>

inline int16_t byte2int16(byte enc[2])
{
    return (((int16_t)(((uint8_t *)(enc))[0]) << 0) +
            ((int16_t)(((uint8_t *)(enc))[1]) << 8));
}

inline int64_t byte2int64(byte enc[8])
{
    return (((uint64_t)(((uint8_t *)(enc))[0]) << 0) +
            ((uint64_t)(((uint8_t *)(enc))[1]) << 8) +
            ((uint64_t)(((uint8_t *)(enc))[2]) << 16) +
            ((uint64_t)(((uint8_t *)(enc))[3]) << 24) +
            ((uint64_t)(((uint8_t *)(enc))[4]) << 32) +
            ((uint64_t)(((uint8_t *)(enc))[5]) << 40) +
            ((uint64_t)(((uint8_t *)(enc))[6]) << 48) +
            ((uint64_t)(((uint8_t *)(enc))[7]) << 56));
}

inline int16_t receive_int16()
{
    byte num_encoded[2];
    Serial.readBytes(num_encoded, 2);      // Read
    int16_t num = byte2int16(num_encoded); // Decode
    Serial.println(num);                   // Echo
    return num;
}

inline int64_t receive_int64()
{
    byte num_encoded[8];
    Serial.readBytes(num_encoded, 8);      // Read
    int64_t num = byte2int64(num_encoded); // Decode
    Serial.println(num);                   // Echo
    return num;
}

inline void receive_cmd(char *cmd)
{
    while (Serial.available() < 4)
    {
        led.setPixelColor(0, 0x0000FF00); // Ready for command: set green
        led.show();
        delay(100);
    }

    led.setPixelColor(0, 0x0042F5Ef); // Command received: set cyan
    led.show();
    Serial.println("COMM START");

    Serial.readBytes(cmd, 4);
}

inline void do_goto()
{
    Serial.println("GOTO RECEIVED");

    // Receive target int16_t
    byte target_encoded[2];
    int bytesRead = Serial.readBytes(target_encoded, 2);

    // Echo target
    Serial.println(*target_encoded);

    // Decode and set target
    stepper_target = byte2int16(target_encoded);

    // Step blockingly
    while (step_stepper())
    {
        ;
    }
    Serial.println("GOTO COMPLETE");
}

inline void transmit_data(int16_t SG1[], int16_t SG2[], ulong Time[], int64_t N)
{
    // Transfer data
    Serial.println("TRANSFER START");
    Serial.println("SG1");
    for (int64_t i = 0; i < N; i++)
    {
        Serial.println(SG1[i]);
    }
    Serial.println("SG2");
    for (int64_t i = 0; i < N; i++)
    {
        Serial.println(SG2[i]);
    }
    Serial.println("Time");
    for (int64_t i = 0; i < N; i++)
    {
        Serial.println(Time[i]);
    }
    Serial.println("TRANSFER OK");
    led.setPixelColor(0, 0x0000FF00);
    led.show();
}

#endif // SERIAL_COMM_H