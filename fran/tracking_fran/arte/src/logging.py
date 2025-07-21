import os
import glob
import datetime
import astropy.units as u
import importlib

from src import coords
importlib.reload(coords)
from src.coords import *

directory = 'tracking_logs'

def delete_logID(directory, start, end):
    for i in range(start, end+1):
        for filename in glob.glob(os.path.join(directory, f'{str(i).zfill(4)}*')):
            os.remove(filename)

def rename_files(directory, start, end):
    for i in range(start, end+1):
        for filename in glob.glob(os.path.join(directory, f'{str(i).zfill(4)}*')):
            new_filename = os.path.join(directory, '0000' + '__' + filename.split('__')[1] + filename.split('__')[2])
            print(filename, new_filename)
            os.rename(filename, new_filename)

def get_log_filenames(directory):
    list_dir = sorted(os.listdir(directory))

    if type(list_dir) != list:
        return [list_dir]

    return sorted(os.listdir(directory))

def get_log_file_name(directory):
    logNames = sorted(os.listdir(directory))
    
    #if directory of logs empty
    if logNames == []:
        timestamp = datetime.datetime.now()
        timestamp = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
        return f'0001__{timestamp}.txt'
    
    lastFile = logNames[-1]
    logID = lastFile.split('__')[0]
    
    if int(logID) == 9999:
        print('deleting logs 0001 - 9900...')
        delete_logID(directory, 1, 9900)
        rename_files(directory, 9901, 9999)
        
        timestamp = datetime.datetime.now()
        timestamp = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
        return f'0001__{timestamp}.txt'
    
    with open(os.path.join(directory,lastFile), 'r') as f:
        if len(f.readlines()) > 100000:
            timestamp = datetime.datetime.now()
            timestamp = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
            return f'{str(int(logID)+1).zfill(4)}__{timestamp}.txt'
        
        else:
            return lastFile

def load_last_line_from_log(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        last_line = lines[-1]
        last_line = last_line.strip()
        last_line = last_line.split(',')

        date, prev_ra, prev_dec, prev_alt, prev_az, abs_lap = last_line

    return date, float(prev_ra)*u.hour, float(prev_dec)*u.deg, float(prev_alt)*u.deg, float(prev_az)*u.deg, float(abs_lap)*u.deg

def get_number_of_lines(filename):

    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
        return len(lines)
    
    else:
        return -1 

def generate_tracking_log_line(ra : u.hour, dec : u.deg, alt : u.deg, az : u.deg, absolute_lap : u.deg):
    return f'{ra.to_value("hour")},{dec.to_value("deg")},{alt.to_value("deg")},{az.to_value("deg")},{absolute_lap.to_value("deg")}'
   

def write_log(directory, filename, log_line):

    if get_number_of_lines(filename) >= 100000:
        filename = get_log_file_name(directory)
    
    path = os.path.join(directory, filename)
    with open(path, 'a') as f:
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        f.write(f'{timestamp},{log_line}\n')
    
def directory_exists(directory):
    return os.path.isdir(directory)