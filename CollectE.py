# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""
import argparse
import os
import time
from collections import defaultdict
from StringIO import StringIO

# %%%
import pandas as pd

ERI_IPMITOOL_RNS = "echo '{0}' | sudo -S eri-ipmitool rns 0 4 5 68 69"

PROC_CPUINFO = "cat /proc/cpuinfo"

MPSTAT_CMD = 'mpstat -P ALL'

# ['time', 'temperature', 'power1', 'power2', 'total_power', 'cpu0_utilization', 'cpu0_frequency',
# 'cpu1_utilization', 'cpu1_frequency', 'cpu2_utilization', 'cpu2_frequency', 'cpu3_utilization', 'cpu3_frequency',
# 'cpu4_utilization', 'cpu4_frequency', 'cpu5_utilization', 'cpu5_frequency', 'cpu6_utilization', 'cpu6_frequency',
# 'cpu7_utilization', 'cpu7_frequency', 'cpu8_utilization', 'cpu8_frequency', 'cpu9_utilization', 'cpu9_frequency',
# 'cpu10_utilization', 'cpu10_frequency', 'cpu11_utilization', 'cpu11_frequency']
SAVING_FILE_NAME = "system.csv"


# %%
def collect_data(sudo_password='System.5'):
    """
    Collect information form the cpus of the system
    :param sudo_password: sudo password
    :return: None
    """
    cpu_usage_cmd = MPSTAT_CMD
    cpu_freq_cmd = PROC_CPUINFO
    cpu_sensor_info_cmd = ERI_IPMITOOL_RNS.format(sudo_password)
    # run the commands and get the outputs
    cpu_freq_output, cpu_sensor_info_output, cpu_usage_output = execute_command_to_get_info(cpu_freq_cmd,
                                                                                            cpu_sensor_info_cmd,
                                                                                            cpu_usage_cmd)
    cpu_util_dict, time_stamp = extract_cpu_usage(cpu_usage_output)
    # %%% read the temperature and calculate the total_power | voltage
    # remove whitespace and remove the information lines
    power1, power2, temperature, total_power = calculate_power_usage(cpu_sensor_info_output)
    # %%
    cpu_freq_dict = extract_cpu_frequency(cpu_freq_output)
    csv_line = create_csv_row_from_data(cpu_freq_dict, cpu_util_dict, power1, power2, temperature, time_stamp,
                                        total_power)
    with open(SAVING_FILE_NAME, "a") as file_:
        file_.write(csv_line + "\n")
    print(csv_line)


# %%
def create_csv_row_from_data(cpu_freq_dict, cpu_util_dict, power1, power2, temperature, time_stamp, total_power):
    """
    create a string to write down on csv file later from all collected information
    :param cpu_freq_dict: dict
    :param cpu_util_dict: dict
    :param power1:float
    :param power2:float
    :param temperature:float
    :param time_stamp:string
    :param total_power:float
    :return:
    """
    # TODO: this function's arguments are too much, refactor to reduce it
    csv_line = ",".join([time_stamp, str(temperature), str(power1), str(power2), str(total_power)])
    # there  are 12 cpus, so len(cpu_freq_dict) == len(cpu_util_dict)
    cpu_util_line = ";".join('{0},{1}'.format(cpu_util_dict[cpu_number], cpu_freq_dict[cpu_number]) for cpu_number in
                             range(len(cpu_freq_dict)))
    csv_line = csv_line + "," + cpu_util_line
    return csv_line


# %%
def extract_cpu_frequency(cpu_freq_output):
    """
    get the current frequency of each cpus in the system
    :param cpu_freq_output: output of the commands
    :return: a dictionary {cpu_id:frequency}
    """
    cpu_freq_output = cpu_freq_output.split("\n")
    # cmd = cat /proc/cpuinfo
    cpu_freq_dict = defaultdict(float)
    for i in range(0, len(cpu_freq_output), 27):
        line = cpu_freq_output[i]
        cpu_number = int(line.split(":")[-1].strip())
        cpu_freq = float(cpu_freq_output[i + 7].split(":")[-1].strip())
        cpu_freq_dict[cpu_number] = cpu_freq
    return cpu_freq_dict


# %%
def calculate_power_usage(cpu_sensor_info_output):
    """
    calculate power usage of the system
    :param cpu_sensor_info_output: outputs of the command to get cpu data
    :return: float:power1, power2, temperature and total_power
    """
    cpu_sensor_info_df = pd.read_csv(cpu_sensor_info_output, sep='|', skiprows=1, header=0, skipinitialspace=True)
    cpu_sensor_info_df = cpu_sensor_info_df.iloc[1:]  # remove the -----
    # %%
    # remove the spaces in header names
    cpu_sensor_info_df.columns = cpu_sensor_info_df.columns.str.strip()
    temperature = float(cpu_sensor_info_df[cpu_sensor_info_df.Name == "Tempera  0 "]['Value'])
    voltage1 = float(cpu_sensor_info_df[cpu_sensor_info_df.Name == 'Voltage  1 ']['Value'])
    voltage2 = float(cpu_sensor_info_df[cpu_sensor_info_df.Name == 'Voltage  2 ']['Value'])
    current1 = float(cpu_sensor_info_df[cpu_sensor_info_df.Name == 'Current  1 ']['Value'])
    current2 = float(cpu_sensor_info_df[cpu_sensor_info_df.Name == 'Current  2 ']['Value'])
    # %%
    power1 = voltage1 * current1
    power2 = voltage2 * current2
    total_power = power1 + power2
    return power1, power2, temperature, total_power


# %%
def extract_cpu_usage(cpu_usage_output):
    """
    extract cpu usage/utilization from the out of terminal commands
    :param cpu_usage_output: output from command to get cpu usage
    :return: ({cpu_id: utlization_percentage}, time_stamp)
    """
    cpu_usage_df = pd.read_csv(cpu_usage_output, delimiter=r"\s+", skiprows=2, engine='python', header=0)
    # get the utilization of each cpu
    # %%
    number_of_cpu = cpu_usage_df.shape[0] - 1  # the number of cpu
    time_stamp = cpu_usage_df.columns[0] + ' ' + cpu_usage_df.columns[1]
    cpu_util_dict = defaultdict(float)
    for i in range(0, number_of_cpu):
        idle_percent = cpu_usage_df[cpu_usage_df.CPU == str(i)]['%idle']  # return the series
        idle_percent = idle_percent.iloc[0]  # get the first and only value
        cpu_util_dict[i] = round(100 - idle_percent, 2)  # due to wrong float calculation of python
    return cpu_util_dict, time_stamp


# %%
def execute_command_to_get_info(cpu_freq_cmd, cpu_sensor_info_cmd, cpu_usage_cmd):
    """
    run terminal commands to get information about cpu frequencies, cpu utilization and thermol/voltage info
    :param cpu_freq_cmd: command to get the cpu frequencies
    :param cpu_sensor_info_cmd: command to get the cpu power, voltalge and temperature
    :param cpu_usage_cmd: command to get the cpu utilization percentages
    :return: the 3 outputs of those command, in string
    """
    cpu_usage_output = os.popen(cpu_usage_cmd).read()
    cpu_freq_output = os.popen(cpu_freq_cmd).read().strip()
    cpu_sensor_info_output = os.popen(cpu_sensor_info_cmd).read()
    # convert the output StringIO object to use it for pandas
    cpu_usage_output = StringIO(cpu_usage_output)
    # cpu_freq_output = StringIO(cpu_freq_output)
    cpu_sensor_info_output = StringIO(cpu_sensor_info_output)
    # %%
    return cpu_freq_output, cpu_sensor_info_output, cpu_usage_output


# %%
def activate_12_cpu(sudo_password='System.5'):
    """
    By default, only 2 cpus are activated. This function ensures that all cpus are enable
    :return:
    """
    command = 'echo "System.5" | sudo -S sh -c "echo -n 1 > /sys/devices/system/cpu/cpu{0}/online"'
    print("activate cpus:")
    for i in range(1, 12):  # cpu0 always activated, never disable it
        cmd = command.format(i)
        os.system(cmd)
        print(cmd)


# %%
if __name__ == "__main__":
    print(
        "MUST ACTIVATE 12 CPUs before running this command file. The password for this system is System.5 and hard-coded.")
    print(
        "Usage: python untitle0.py --sudo_pass password_of_sudo IF need a new sudo password. Default password is System.5")
    parser = argparse.ArgumentParser(
        description="Collect cpu data every second",
        epilog="Input is the password, otherwise, default password is System.5",
        fromfile_prefix_chars='@')
    parser.add_argument(
        "--sudo_password",
        help="sudo password of the system",
        metavar="password", default='System.5')
    args = parser.parse_args()

    activate_12_cpu()
    try:
        while True:
            collect_data(args.sudo_password)
            time.sleep(1)
    except KeyboardInterrupt as e:
        print(e)
