import logging
import config as conf

class DummyPID:
    def __init__(self, P, I, D):
        logging.getLogger('dummy').warn("WARNING: Dummy PID is being used. No actions will be taken..")
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
        logging.getLogger('dummy').warn("WARNING: Dummy SPI is being used. No actions will be taken..")


class DummyDigitalIO:
    def __init__(self, iopin):
        logging.getLogger('dummy').warn("WARNING: Dummy DigitalIO is being used. The returned temperatures will all be 0 C.")
        self.gpiopin = iopin

class DummySensor:
    def __init__(self, spi):
        logging.getLogger('dummy').warn("WARNING: Dummy sensor is being used. The returned temperatures will all be 0 C.")
        self.temperature = 0.

    def readTempC(self):
        # do nothing
        return 0.
