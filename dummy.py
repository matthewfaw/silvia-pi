
class DummyPID:
    def __init__(self, P, I, D):
        print("WARNING: Dummy PID is being used. No actions will be taken..")
        self.SetPoint = 0.
        self.output = 0.
        self.PTerm = 0.
        self.ITerm = 0.
        self.DTerm = 0.

    def setSampleTime(self, time):
        # do nothing
        return None

    def update(self, temp):
        # do nothing
        return None

    def clear(self):
        # do nothing
        return None


class DummySPI:
    def __init__(self, spi_port, spi_dev):
        print("WARNING: Dummy SPI is being used. No actions will be taken..")


class DummySensor:
    def __init__(self, spi):
        print("WARNING: Dummy sensor is being used. The returned temperatures will all be 0 C.")

    def readTempC(self):
        # do nothing
        return 0.
