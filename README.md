# diskbrake

## About this project

diskbrake is a program that stops a hard disk if it has not been used for a while, it was made because the OS tools, hd-idle and smartctl did not work

## Prequisites

- python3
- hdparm
- root or sudo user

## How it works

Each time this program is executed it will be validated if the configured disks were read or written since the last execution, in case its status has not changed its cycle counter will be increased, if the number of cycles of a disk reaches its setting the disk will stop (spin down)

## Installation

Download this project, you can use the following script to do this:

```bash
git clone https://github.com/jp10z/diskbrake
```

Copy the config.ini file from the default folder to the root of the project and then edit it according to your needs, you can use the following script to do this:

```bash
cp ./default/config.ini ./config.ini
```

Add execute permissions to run.sh, you can use the following script to do this:

```
chmod +x run.sh
```

## Usage

Manual execution as sudo

```bash
sudo sh ./run.sh
```

Execution every 5 minutes using crontab (sudo)

```bash
sudo crontab -e
```

Add this line at the end (change the installation path)

```
*/5 * * * * /full_installation_path/run.sh
```

## About the Config file

### **[APP]**
|||
|-|-|
|STATES_FILE_PATH|Path where the states of the disks will be saved|

### **[LOGS]**
|||
|-|-|
|PATH|Path of the folder that will contain the logs|
|LEVEL|Log level (0 No, 1 Critical, 2 Error, 3 Warning, 4 Info, 5 Debug, 6 Data)|

### **[DEVICE_NAME]**
This section should be repeated for all the devices you want to include
|||
|-|-|
|UUID|UUID of any partition on the disk (you can list uuids with `ls -l /dev/disk/by-uuid/`)|
|CYCLES|Number of cycles required for the unit to stop|