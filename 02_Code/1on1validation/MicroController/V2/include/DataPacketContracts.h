#ifndef DATA_PACKET_CONTRACTS_H
#define DATA_PACKET_CONTRACTS_H

/**
 * Measurement struct. Raw ADC output and motor rpm
 */
struct __attribute__((packed)) ExperimentMeasurement
{
	/**
	 * Constant ID for identifying different packet types over communication
	 */
	const int id{2};
	const int32_t upstreamThrust;
	const int32_t downstreamThrust;
	const int32_t noiseThrust;
	const float RPM;

	ExperimentMeasurement(const int32_t upstreamThrust, const int32_t downstreamThrust, const int32_t noiseThrust,
	                      const float RPM) : upstreamThrust(upstreamThrust), downstreamThrust(downstreamThrust),
	                                         noiseThrust(noiseThrust), RPM(RPM)
	{
	}
};

#endif //DATA_PACKET_CONTRACTS_H
