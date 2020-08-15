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
sed -i.bak "s/#dtparam=spi=on/dtparam=spi=on/g" /boot/config.txt

echo "Setting up Slack API OAuth token"
read -p "Enter your API key here (press Enter when done): "  -r
echo    # (optional) move to a new line
echo "export SLACK_BOT_TOKEN=$REPLY" >> /etc/environment

MYIP=$(hostname -I | cut -f1 -d ' ')
echo "Print+log the IP: ${MYIP}"
echo "$MYIP" >> ip.log

echo "Create logrotate config..."
./create_logrotate_from_script_references.sh "/etc/logrotate.d/silvia-pi-logrotate"

if [ -d "ivPID" ]; then
  echo "Determined that ivPID library has already been installed. Skipping this step."
else
  echo "Installing ivPID library..."
  git clone https://github.com/ivmech/ivPID.git
  cp ivPID/PID.py .
fi

echo "Installing remaining python3 libraries..."
pip3 install --upgrade -r $BASEDIR/requirements.txt

if ! grep silvia-pi.py /etc/rc.local; then
  echo "Adding entry to /etc/rc.local"
  sed -i.bak 's|^exit 0$|'"${BASEDIR}"'/silvia-pi.py > '"${BASEDIR}"'/silvia-pi.log 2>\&1 \&\n\nexit 0|g' /etc/rc.local
  chmod 755 /etc/rc.local
else
  echo "Skipping /etc/rc.local modification since entry already found"
fi

echo "Installation complete.  Time for a reboot, so that settings will take effect.."

read -p "Is this ok? (y/n) " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "Rebooting..."
  reboot
else
  echo "Ok. Exiting"
  exit 1
fi
