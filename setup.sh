#!/bin/bash
set -e


SCRIPT=$(readlink -f "$0")
echo $SCRIPT
BASEDIR=$(dirname "$SCRIPT")
echo $BASEDIR

if [[ $(whoami) != 'root' ]]; then
  echo "Must run as root!"
  exit -1
fi

apt-get -y install rpi-update git build-essential python-dev python-smbus python-pip logrotate vim tmux

echo "Enable ssh"
sudo systemctl enable ssh
sudo systemctl start ssh

MYIP=$(hostname -I | cut -f1 -d ' ')
echo "Print+log the IP: ${MYIP}"
echo "$MYIP" >> ip.log

echo "Installing logrotate config..."
cp $BASEDIR/silvia-pi-logrotate /etc/logrotate.d

echo "Installing Adafruit GPIO library..."
git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
cd Adafruit_Python_GPIO
python3 setup.py install
cd ..

echo "Installing MAX31855 Thermocouple Amp library..."
git clone https://github.com/adafruit/Adafruit_Python_MAX31855.git
cd Adafruit_Python_MAX31855
python3 setup.py install
cd ..

echo "Installing ivPID library..."
git clone https://github.com/ivmech/ivPID.git
cp ivPID/PID.py .

echo "Installing remaining python3 libraries..."
pip3 install --upgrade -r $BASEDIR/requirements.txt

if ! grep silvia-pi.py /etc/rc.local; then
  echo "Adding entry to /etc/rc.local"
  cp /etc/rc.local /etc/rc.local.bak
  cat /etc/rc.local | sed 's|^exit 0$|'"${BASEDIR}"'/silvia-pi.py > '"${BASEDIR}"'/silvia-pi/silvia-pi.log 2>\&1 \&\n\nexit 0|g' > /etc/rc.local.new
  mv /etc/rc.local.new /etc/rc.local
  chmod 755 /etc/rc.local
else
  echo "Skipping /etc/rc.local modification since entry already found"
fi

echo "Installation complete.  Please reboot."
