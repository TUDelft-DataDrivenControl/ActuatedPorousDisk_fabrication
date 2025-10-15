#ifndef SIMPLE_LOGGER_H
#define SIMPLE_LOGGER_H

#include <Arduino.h>

class SimpleLogger
{
private:
    static constexpr uint32_t adlerModulo{65521};

public:
    /**
     * Calculates the Adler-32 CRC for any type to be logged
     * @tparam TLog Type to log
     * @param toLog Object to send over logger
     * @return
     */
    template <typename TLog>
    static uint32_t calculateRedundancy(const TLog toLog)
    {
        unsigned char* data{new unsigned char[sizeof(TLog)]};
        memcpy(data, &toLog, sizeof(TLog));

        uint32_t a = 1, b = 0;
        for (size_t index = 0; index < sizeof(TLog); ++index)
        {
            a = (a + data[index]) % adlerModulo;
            b = (b + a) % adlerModulo;
        }
        delete[] data;
        return (b << 16) | a;
    }

    /**
     * Logs the object over serial as raw data with the following structure:
     * [start, size, data toLog, crc, end]
     * @tparam TLog Type to log
     * @param toLog Object to send over logger
     */
    template <typename TLog>
    static void log(TLog toLog)
    {
        constexpr uint8_t startOfMessage{0xFC};
        constexpr uint8_t endOfMessage{0xCF};
        constexpr uint8_t dataSize{sizeof(TLog)};
        constexpr size_t extra{sizeof(uint32_t) + 3 * sizeof(uint8_t)};
        const size_t bufferSize{sizeof(TLog) + extra};
        unsigned char* buffer{new unsigned char[bufferSize]};
        const uint32_t redundancy{calculateRedundancy(toLog)};
        memcpy(&buffer[0], &startOfMessage, sizeof(uint8_t));
        memcpy(&buffer[1], &dataSize, sizeof(uint8_t));
        memcpy(&buffer[2], &toLog, sizeof(TLog));
        memcpy(&buffer[2 + sizeof(TLog)], &redundancy, sizeof(uint32_t));
        memcpy(&buffer[2 + sizeof(TLog) + sizeof(uint32_t)], &endOfMessage, sizeof(uint8_t));
        Serial.write(buffer, bufferSize);
        delete[] buffer;
    }
};


#endif //SIMPLE_LOGGER_H
