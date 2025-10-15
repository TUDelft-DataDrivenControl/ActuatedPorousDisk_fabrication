#ifndef SERIAL_COMMAND_H
#define SERIAL_COMMAND_H

#include <Arduino.h>

namespace SerialCommandInterface
{
    /**
     * A class for communicating experiment setups (as well as potentially other commands and data) over serial communication.
     */
    class SerialCommand
    {
    private:
        const uint8_t commandRegister;
        const uint8_t incomingDataSize;
        uint8_t* dataBuffer{nullptr};
        uint32_t crc{0};
        uint8_t endOfMessage{0x00};
        uint32_t calculateCRC() const;
        mutable uint_fast16_t currentIndex{0};

    public:
        SerialCommand(uint8_t commandRegister, uint8_t incomingDataSize);
        ~SerialCommand();
        bool isComplete() const;
        bool isValid() const;
        bool dataComplete() const;
        bool setNextByte(uint8_t next) const;
        bool setNextBytes(const uint8_t* buffer, uint8_t count) const;
        const uint_fast16_t totalMessageSize;
        static void commandDecodeTask(void* pvParameters);

        template <typename T>
        bool convertData(T* targetBuffer) const
        {
            if (sizeof(T) != incomingDataSize)
                return false;

            memcpy(targetBuffer, dataBuffer, incomingDataSize);
            return true;
        }
    };
}

#endif //SERIAL_COMMAND_H
