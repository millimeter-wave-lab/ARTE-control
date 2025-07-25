import yaml, subprocess

if __name__ == '__main__':
    f = open('configuration.yml', 'r')
    config = yaml.load(f, Loader=yaml.loader.SafeLoader)
    f.close()
    cmd = ['calibrate_adc5g',
            '-i', config['roach_ip'],
            #'-b', config['boffile'], #This should be commented when you run init.py for the normal operation of ARTE, 
           #only uncomment when you run this script to perform the OGP and INL calibration.
            '-g', config['cal_info']['gen_info'],
            '-gf', config['cal_info']['gen_freq'],
            '-gp', config['cal_info']['gen_power'],
            '--zdok0snap', 'adcsnap0', 'adcsnap1', #This corresponds to the ADC where the principal antennas are connected, antenna 0 and 1.
            '--zdok1snap', 'adcsnap2', 'adcsnap3', #This corresponds to the ADC where antenna 3 and reference antenna are connected, if you
           #want to calibrate only the ADC of the principal antennas, comment this line.
            '--ns', '128',
            '-bw', str(config['bandwidth']),
            '-cd', '/home/arte/Workspace/Measurements/Calibration_data/16_10_2024_ADC0'] #Path to the OGP and INL calibration files.
            #The idea is to use the previous calibrations files to calibrate the ROACH every time that it is initialized. 
    if(config['cal_info']['do_mmcm']):
        cmd.append('-dm')
    if(config['cal_info']['do_ogp']):
        cmd.append('-do')
    if(config['cal_info']['do_inl']):
        cmd.append('-di')
    if(config['cal_info']['plot_snap']):
        cmd.append('-psn')
    if(config['cal_info']['plot_spect']):
        cmd.append('-psp')

    subprocess.call(cmd)


