import pandas as pd
import numpy as np
import time
pd.options.mode.chained_assignment = None
HR_Data_File_Path = r'C:/Users/sanke/fitbit_1.csv'
Sensor_Data_File_Path = r'C:/Users/sanke/sensor_1.csv'
Results_File_Path = r'C:/Users/sanke/Results_'+str(time.time()).replace('.','')+'.csv'

hr_data = pd.read_csv(HR_Data_File_Path, header=0)
hr_data['TIME']=0
sensor_data = pd.read_csv(Sensor_Data_File_Path, header=0)
sensor_data['TIME']=0
proc_data = pd.DataFrame(0, index=np.arange(len(sensor_data)), columns = ['Time_Val', 'Time_sec', 'Heart_Rate', 'Sound', 'Light', 'Phone_Active'])
axl_threshold = 1.2

for i in range(0, len(hr_data)):
    #Let's get the time data to look similar to the android sensor input values
    hr_time_split= hr_data['HEART RATE DATE/TIME'][i].split(":")
    hr_time_split[0]=int(hr_time_split[0].replace(' ',''))  #removes additional space
    hr_time_split.append(hr_time_split[2].split(' ')[1]) #AM/PM information
    hr_time_split[2]=hr_time_split[2].split(' ')[0] #Seconds resolution
    #converting 12 hour to 24 hour format
    if hr_time_split[3]=='PM' and hr_time_split[0]<12:
        hr_time_split[0]+=12
    elif hr_time_split[3]=='AM' and hr_time_split[0]==12:
        hr_time_split[0]-=12
    
    #make a pretty string again
    hr_data['TIME'][i]=str(hr_time_split[0])+":"+\
                        str(hr_time_split[1])+":"+\
                        str(hr_time_split[2])

#hr_data.to_csv('C:/Users/sanke/fitbit_1_test.csv')

for i in range(0, len(sensor_data)):
    #Split Sensor Data into Hour-Minutes-Seconds
    sensor_time_split=sensor_data['YYYY-MO-DD HH-MI-SS_SSS'][i].split(":")    
    sensor_data['TIME'][i]=str(sensor_time_split[0])+":"+\
                        str(sensor_time_split[1])+":"+\
                        str(sensor_time_split[2])
    
    #Use a threshold to determine if phone is active or not after checking proximity sensor
    if sensor_data['PROXIMITY (i)'][i]==0:
        active_flag = 'No'
    else:
        if int(sensor_data['LINEAR ACCELERATION X'][i])>axl_threshold:
            active_flag = 'Yes'
        else:
            active_flag = 'No'
    
    sensor_time = sensor_data['TIME'][i]
    #lookup heart rate data based on time stamp
    found_flag = 0
    #To reduce number of iterations
    lower_bound = 1290
    for j in range(lower_bound, len(hr_data)):
        hr_time = hr_data['TIME'][j]
        if sensor_time == hr_time:
            hr_val = int(hr_data['VALUE'][i])
            found_flag = 1
            lower_bound = j
            break
    
    #if heart rate data is not found, copy previous value
    if found_flag==0:
        if i==0:
            hr_val = 70
        else:
            hr_val = proc_data['Heart_Rate'][i-1]
            
    proc_data['Time_Val'][i]=sensor_data['TIME'][i]
    proc_data['Time_sec'][i]=i+1
    proc_data['Heart_Rate'][i]=hr_val
    proc_data['Sound'][i]=sensor_data['SOUND LEVEL (dB)'][i]
    proc_data['Light'][i]=sensor_data['LIGHT (lux)'][i]
    proc_data['Phone_Active'][i]=active_flag
    
proc_data.to_csv(Results_File_Path, index=False)
    


