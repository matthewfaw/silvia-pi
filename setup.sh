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

echo "Installing some useful packages"
apt-get -y install rpi-update git build-essential python-dev python-smbus python-pip logrotate vim tmux

echo "Enable ssh"
systemctl enable ssh
systemctl start ssh

echo "Enable SPI -- this will require system reboot to take effect"
echo "Note that, after rebooting, you should see device /dev/spidev0.0"
sed -i "s/#dtparam=spi=on/dtparam=spi=on/g" /boot/config.txt

MYIP=$(hostname -I | cut -f1 -d ' ')
echo "Print+log the IP: ${MYIP}"
echo "$MYIP" >> ip.log

echo "Installing logrotate config..."
cp $BASEDIR/silvia-pi-logrotate /etc/logrotate.d

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
