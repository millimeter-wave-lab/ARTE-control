def get_image_data_temperature(filenames,cal_time=1,spect_time=1e-2,file_time=5 ,decimation=1,
        win_size=32,tails=32, temperature=True):
    """
    filenames   :   list with the names of the plots
    cal_time    :   calibration time at the begining of each file
    spect_time  :   time between two spectra
    file_time   :   complete time of each file in minutes
    tails       :
    temperature :   Return the data in temperature relative to the hot source
    """
    sample = read_10gbe_data(filenames[0])
    sample_spect, header = sample.get_complete()

    sample.close_file()

    P = np.median(sample_spect,axis = 1)
    gradiente = np.abs(np.gradient(P))
    maxim = np.max(gradiente)
    index  = np.where(gradiente== maxim)
    index  =  index[0][0]

    hot_index = index-30
    P_hot = (np.mean(sample_spect[hot_index:hot_index+5,:],axis=0))
    P_hot = savgol_filter(P_hot, 9, 3)

    load_index = index+ 30
    P_load = (np.mean(sample_spect[load_index:load_index+5,:],axis=0))
    P_load = savgol_filter(P_load, 9, 3)

    flags, baseline_load = get_baseline(P_load)
    spect_size = int(file_time*60/spect_time-tails)
    data = np.zeros([len(filenames)*spect_size//decimation, int(flags.shape[0])])
    data_new = np.zeros([len(filenames)*spect_size//decimation, int(flags.shape[0])])
    bases = np.zeros((len(filenames), 2048))
    clip = np.zeros(len(filenames)*spect_size//decimation, dtype=bool)

    for i in range(0, len(filenames)):
        sample = read_10gbe_data(filenames[i])
        sample_spect, header = sample.get_complete()
        sample.close_file()

        P = np.median(sample_spect,axis = 1)
        gradiente = np.abs(np.gradient(P))
        maxim = np.max(gradiente)
        index  = np.where(gradiente== maxim)
        index  =  index[0][0]

        hot_index = index-30
        P_hot = (np.mean(sample_spect[hot_index:hot_index+5,:],axis=0))
        P_hot = savgol_filter(P_hot, 9, 3)

        load_index = index+ 30
        P_load = (np.mean(sample_spect[load_index:load_index+5,:],axis=0))
        P_load = savgol_filter(P_load, 9, 3)

        flags, baseline_load = get_baseline(P_load)
        bases[i,:] = baseline_load

        t_load = 290 #temp amb
        ENR_ns = (14.85+14.74)/2. #dB
        t_hot = 10**((ENR_ns-7.8/2)/10.)*t_load+t_load # revisar descuento de perdidas  #temp ns on

        t_rx = (t_hot*P_load -t_load*P_hot)/(P_hot-P_load)

        aux = sample_spect[:spect_size,:]
        aux = (aux/P_load)*(t_rx+t_load)-t_rx

        dec_size = aux.shape[0]//decimation
        aux = aux[:dec_size*decimation,:].reshape([-1, decimation, aux.shape[1]])
        aux = np.mean(aux.astype(float), axis=1)

        data[i*(spect_size//decimation):(i+1)*(spect_size//decimation),flags] = aux[:,flags]

        data = data[100:,:]
        mediana = (np.nanmedian(data[:,:],axis=0))
        data_new = np.subtract(data,mediana)


       #now we look at the clipping
        sat = np.bitwise_and(header[:spect_size,1],2**4-1) #just take the cliping values
        sat = sat[:dec_size*decimation].reshape([-1, decimation])
        sat = np.sum(sat, axis=1)
        sat = np.invert(sat==0)

    avg_pow = np.mean(data[:,flags], axis=1)
    avg_pow = moving_average(avg_pow, win_size=win_size)

    data_new/= np.std(data_new[100:,:],axis=0)

    snr = np.mean(data_new[:,flags], axis=1)
    snr = moving_average(snr, win_size=win_size)

    clip = moving_average(clip, win_size=win_size)
    clip = np.invert(clip==0)

    t = np.arange(len(avg_pow))*spect_time/60.*decimation #time in minutes
    return data, avg_pow, clip, t, bases,flags, data_new,snr
