 🐍 art-bio : A Real-Time BIOsignal feature extraction tool 🦆 
    https://github.com/vatte/rt-bio

    sources:
        ecg (electrocardiogram) sends /ecg/ibi
        recg (same as above + /ecg/raw)
        eeg (electroencephalogram sends /eeg/alpha, /eeg/beta /eeg/gamma, /eeg/theta)
        reeg (same as above + /eeg/raw)
        emg (electromyogram) sends /emg/power
        remg (same as above + /emg/raw)
        eda (electrodermal activity) sends /eda/edr([length, amplitude])
        reda (same as above + /eda/raw)

        example usage:
            art-bio -c ecg osc -c reeg file

    command line arguments:
    -d, --device [device_type (default: bitalino)]
        choose biosignal acquisition device
        [device_type] - bitalino, (openbci soon i promise...)
    -f, --freq [sampling_frequency (default: 100)]
        set sampling frequency for biosignal data acquisition
    -l, --list
        lists available devices
    -i, --index [device_index (default: 0)]
        set the correct device from available devices, see --list
    -c, --connect [sourcetype] [destinationtype] 
        makes connections for biosignal sources to data destinations
        [source]: ecg, eda, eeg, emg
        [destination]: osc, file, digital
    --osc-address [destination_address]
        [destination_address (default: 127.0.0.1:4810)] IP_ADDRESS:PORT
    --osc-prefix [prefix]
        [prefix (default: /rtbio)]
    --filename [filename]
        [filename (default: temp.txt)]
        
 ### LICENSE : GNU General Public License v3.0
