//
// Created by Brian on 12/06/2025.
//

#include "SerialCommand.h"

namespace SerialCommandInterface
{
    /**
     *
     * @return Adler 32 Cyclic Redundancy Check value of the serial command
     */
    uint32_t SerialCommand::calculateCRC() const
    {
        if (!isComplete())
            return UINT32_MAX;

        static constexpr uint32_t adlerModulo{65521};

        uint32_t a{1}, b{0};
        for (size_t index = 0; index < incomingDataSize; ++index)
        {
            // ReSharper disable once CppDFANullDereference
            a = (a + dataBuffer[index]) % adlerModulo;
            b = (b + a) % adlerModulo;
        }
        return (b << 16) | a;
    }

    SerialCommand::SerialCommand(const uint8_t commandRegister,
                                 const uint8_t incomingDataSize) : commandRegister(commandRegister),
                                                                   incomingDataSize(incomingDataSize),
                                                                   totalMessageSize(
                                                                       3 * sizeof(uint8_t) + incomingDataSize + sizeof(
                                                                           uint32_t))
    {
        dataBuffer = new uint8_t[incomingDataSize];
    }

    SerialCommand::~SerialCommand()
    {
        delete dataBuffer;
    }

    bool SerialCommand::isComplete() const
    {
        return endOfMessage == 0xCF;
    }

    bool SerialCommand::isValid() const
    {
        if (!isComplete())
            return false;

        return crc == calculateCRC();
    }

    bool SerialCommand::dataComplete() const
    {
        return currentIndex == incomingDataSize;
    }

    /**
     * Sets the next byte in the data buffer. Does check to notify user of end of data buffer
     * @param next Next byte to set in the data buffer
     * @return true when the next byte won't overflow the buffer
     */
    bool SerialCommand::setNextByte(const uint8_t next) const
    {
        if (currentIndex >= incomingDataSize)
            return false;

        dataBuffer[currentIndex] = next;
        currentIndex++;
        return currentIndex < incomingDataSize;
    }

    bool SerialCommand::setNextBytes(const uint8_t* buffer, const uint8_t count) const
    {
        if (incomingDataSize - currentIndex < count)
            return false;

        memcpy(dataBuffer + currentIndex, buffer, count);
        currentIndex += count;
        return currentIndex < incomingDataSize;
    }

    /**
     * Decoded an incoming SerialCommand (if any) via a FreeRTOS task.
     * Task keeps running without timeout (but non-blocking) until a message is decoded (early exit at user's discretion)
     * @param pvParameters pointer to a SerialCommand pointer (SerialCommand**) storing the global experiment setup
     */
    [[noreturn]] void SerialCommand::commandDecodeTask(void* pvParameters)
    {
        const auto ppCommand{static_cast<SerialCommand**>(pvParameters)};
        constexpr size_t dataSizeOffset{2 * sizeof(uint8_t)};
        constexpr size_t messageStartSize{3 * sizeof(uint8_t)};
        constexpr size_t bufferSizer{4};
        static auto buffer{new uint8_t[bufferSizer]};


        constexpr size_t registerOffset{sizeof(uint8_t)};
        constexpr size_t crcSize{sizeof(uint32_t)};
        while (Serial.available() < messageStartSize)
            vTaskDelay(10);

        Serial.read(buffer, messageStartSize);

        *ppCommand = new SerialCommand(buffer[registerOffset], buffer[dataSizeOffset]);

        const auto pCommand{*ppCommand};

        while (Serial.available() < pCommand->incomingDataSize)
            vTaskDelay(10);

        Serial.read(pCommand->dataBuffer, pCommand->incomingDataSize);

        while (Serial.available() < crcSize)
            vTaskDelay(10);

        Serial.read(buffer, crcSize);
        memcpy(&pCommand->crc, &buffer, crcSize);

        while (!Serial.peek())
            vTaskDelay(10);

        Serial.read(&pCommand->endOfMessage, sizeof(uint8_t));

        for (;;)
        {
            vTaskDelay(10);
        }
    }
}
