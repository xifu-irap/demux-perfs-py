import numpy as np
from numpy.fft import rfft
import os
import matplotlib.pyplot as plt
import get_data, general_tools


# -----------------------------------------------------------------------------
def analyse_dump(sig, nb, config):

    print("------------------------------------")
    f_carriers = np.array([])  
    io_str=""
    if abs(sig).max()==0:
        print("Data stream is empty!")
    else:
        sigfdb, f_carriers, _, io_str = makeanalysis(sig, nb, config)
    return(sigfdb, f_carriers, io_str)
     
 # -----------------------------------------------------------------------------
def readfile_dump_dds(dumpfilename, quiet=True):
    r"""
        This function reads data from a DRE dump file, and returns 2 arrays
        (format <h).
        The file header (first 32-bit) word is removed from the data

        Parameters
        ----------
        dumpfilename : string
        The name of the dump file (with the path and the extension)

        quiet : boolean
        Defines if text info shall be written by the routine

        Returns
        -------
        data : array type
        contains the values of the file (format int16).
            
        dumptype : number 'uint16'
        Identifier for the type of dump.
        
        """
    
    fdat=open(dumpfilename, 'rb')
    data=np.fromfile(fdat, dtype='<i4')
    fdat.close()
    return(data[1:])

# -----------------------------------------------------------------------------
def process_dump_dds(fulldirname, config, max_duration=0.2):
    r"""
        This function reads and process the data of DRE-DEMUX data dumps.
        
        Parameters
        ----------
        fulldirname : string
        The name of the dump file (with the path)

        config : dictionnary
        Contains path and constants definitions

        Max_duration : number, optional
        Maximum duration in seconds to be considered for analysis (default is 1)

        Returns
        -------
        Nothing

        """

    fs = float(config["fs"])
    datadirname = os.path.join(fulldirname, config['dir_data'])
    plotdirname = os.path.join(fulldirname, config['dir_plots'])
    general_tools.checkdir(plotdirname)
    nba, name_a = 19, "DDS" 
    nbb, name_b = 27, "DDSxAMP"
    nbc, name_c = 16, "DDSxAMP_TRUNCATED" 
    nbd, name_d = 21, "ADDER_IN" 
    nbe, name_e = 27, "ADDER_OUT"
    plotfilename_a = os.path.join(plotdirname, "PLOT_DUMP_" + name_a + ".png")
    plotfilename_b = os.path.join(plotdirname, "PLOT_DUMP_" + name_b + ".png")
    plotfilename_c = os.path.join(plotdirname, "PLOT_DUMP_" + name_c + ".png")
    plotfilename_d = os.path.join(plotdirname, "PLOT_DUMP_" + name_d + ".png")
    plotfilename_e = os.path.join(plotdirname, "PLOT_DUMP_" + name_e + ".png")

    dumpfilenames1 = [f for f in os.listdir(datadirname) \
                if os.path.isfile(os.path.join(datadirname, f)) \
                and f[-11:]=="DDSout1.dat"]
    dumpfilenames2 = [f for f in os.listdir(datadirname) \
                if os.path.isfile(os.path.join(datadirname, f)) \
                and f[-11:]=="DDSout2.dat"]
    dumpfilenames3 = [f for f in os.listdir(datadirname) \
                if os.path.isfile(os.path.join(datadirname, f)) \
                and f[-11:]=="DDSout3.dat"]
    dumpfilenames4 = [f for f in os.listdir(datadirname) \
                if os.path.isfile(os.path.join(datadirname, f)) \
                and f[-11:]=="DDSout4.dat"]

    if len(dumpfilenames1)>0 and len(dumpfilenames2)>0 and len(dumpfilenames3)>0 and len(dumpfilenames4)>0:
        dumpfilename1 = os.path.join(datadirname, dumpfilenames1[0])
        dumpfilename2 = os.path.join(datadirname, dumpfilenames2[0])
        dumpfilename3 = os.path.join(datadirname, dumpfilenames3[0])
        dumpfilename4 = os.path.join(datadirname, dumpfilenames4[0])

        # Getting the data from dump file
        print("Reading data from file "+dumpfilenames1[0])
        a = readfile_dump_dds(dumpfilename1).astype('float')
        print("Reading data from file "+dumpfilenames2[0])
        b = readfile_dump_dds(dumpfilename2).astype('float')
        print("Reading data from file "+dumpfilenames3[0])
        d = readfile_dump_dds(dumpfilename3).astype('float')
        print("Reading data from file "+dumpfilenames4[0])
        e = readfile_dump_dds(dumpfilename4).astype('float')

        nval=len(a)
        duration = (nval/fs)

        # Reduction of the number of samples (if needed)
        duration = min(duration, max_duration)
        nval = int(duration * fs)

        # reduction of the number of values to a power of 2 (for a faster FFT)
        power2 = int(np.log(nval)/np.log(2))
        nval = int(2**power2)   

        a = a[:nval]
        b = b[:nval]
        d = d[:nval]
        e = e[:nval]

        # Impact of truncation on 16 bits
        margin=32 # margin wrt FSR / PeakPeak1
        c = np.round((b*(2**(nbc-1))/b.max())/margin)

        f_res = fs / nval

        print("Processing datastream of DDS signal...")
        nba_real=np.log10(a.max()-a.min())/np.log10(2)
        print("This signal uses {0:3.2f} bits".format(nba_real))
        plot_str = ', Nb samples-> {0:8d},  Dump duration-> {1:6.2f} s,  RBW-> {2:8.2f} Hz,  nbits-> {3:3.2f}\n' \
        .format(nval, nval / fs, fs / nval, nba_real)
        afdb, f_carriers, _ = analyse_dump(a, nba, config)
        plot_dump(a, nba, afdb, f_carriers[0], config, "Signal "+name_a+plot_str, plotfilename_a)

        print("Processing datastream of DDSxAMP signal...")
        nbb_real=np.log10(b.max()-b.min())/np.log10(2)
        print("This signal uses {0:3.2f} bits".format(nbb_real))
        plot_str = ', Nb samples-> {0:8d},  Dump duration-> {1:6.2f} s,  RBW-> {2:8.2f} Hz,  nbits-> {3:3.2f}\n' \
        .format(nval, nval / fs, fs / nval, nbb_real)
        bfdb, _, _ = analyse_dump(b, nbb, config)
        plot_dump(b, nbb, bfdb, f_carriers[0], config, "Signal "+name_b+plot_str, plotfilename_b)

        print("Processing datastream of DDSxAMP signal truncated over 16 bits...")
        nbc_real=np.log10(c.max()-c.min())/np.log10(2)
        print("This signal uses {0:3.2f} bits".format(nbc_real))
        plot_str = ', Nb samples-> {0:8d},  Dump duration-> {1:6.2f} s,  RBW-> {2:8.2f} Hz,  nbits-> {3:3.2f}\n' \
        .format(nval, nval / fs, fs / nval, nbc_real)
        cfdb, _, _ = analyse_dump(c, nbc, config)
        plot_dump(c, nbc, cfdb, f_carriers[0], config, "Signal "+name_c+plot_str, plotfilename_c)

        print("Processing datastream of ADDER INPUT signal...")
        nbd_real=np.log10(d.max()-d.min())/np.log10(2)
        print("This signal uses {0:3.2f} bits".format(nbd_real))
        plot_str = ', Nb samples-> {0:8d},  Dump duration-> {1:6.2f} s,  RBW-> {2:8.2f} Hz,  nbits-> {3:3.2f}\n' \
        .format(nval, nval / fs, fs / nval, nbd_real)
        dfdb, _, _ = analyse_dump(d, nbd, config)
        plot_dump(d, nbd, dfdb, f_carriers[0], config, "Signal "+name_d+plot_str, plotfilename_d)

        print("Processing datastream of ADDER INPUT signal...")
        nbe_real=np.log10(e.max()-e.min())/np.log10(2)
        print("This signal uses {0:3.2f} bits".format(nbe_real))
        plot_str = ', Nb samples-> {0:8d},  Dump duration-> {1:6.2f} s,  RBW-> {2:8.2f} Hz,  nbits-> {3:3.2f}\n' \
        .format(nval, nval / fs, fs / nval, nbe_real)
        efdb, _, _ = analyse_dump(e, nbe, config)
        plot_dump(e, nbe, efdb, f_carriers[0], config, "Signal "+name_e+plot_str, plotfilename_e)

    print("Done!")
    print("------------------------------------")

# -----------------------------------------------------------------------------

def makeanalysis(sig, nb, config):
    r"""
        This function does the analysis of a signal. In time domain (measurment
        of the power) but mostly in frequency domain (fft, normalisation, ...).

        Parameters
        ----------
        sig : array_like
        The (time domain) signal to be analysed.

        nb : number
        Number of bits used to code the digital signal (16 for the DAC).

        config : dictionnary
        Contains path and constants definitions

        Returns
        -------
        sigfdb : array_like
        The signal in frequency domain and expressed in dB FSR.

        carriers : array_like
        Frequency of detected peaks according to the input array

        Noise_Power : number
        The maximum power measured in the science band around the carriers.

        io_str : string
        The log message.

    """

    nval=len(sig)
    df = float(config["fs"])/nval    # spectral resolution

    #######################################################################
    # Computation of fft
    sigf = abs(rfft(sig))
     
    #######################################################################
    # Get the peak-to-peak amplitude of the time signal.
    peakpeak = 2.*max(abs(sig))

    # FSR power level (constant signal equal to DAC at full scale)
    e_fsr_db = 10*np.log10(nval*(2.**nb)**2)

    # Power of the signal measured in time domain
    e_time_db = 10*np.log10(np.sum(sig.astype(float)**2))
    # Power obtained in frequency domain (to be corrected for)
    e_freq_db = 10*np.log10(np.sum(sigf.astype(float)**2))

    sigfdb = -300.*np.ones(len(sigf))
    inotzero = np.where(sigf != 0)[0]
    sigfdb[inotzero] = 20*np.log10(sigf[inotzero]) - e_freq_db + e_time_db - e_fsr_db

    io_str = '\
Peak Peak amplitude--------------> {0:9.2f} \n\
Measured crest factor------------> {1:9.2f} \n\
Max of spectrum------------------> {2:9.2f} dB\n'\
    .format(peakpeak, crestfactor(sig), sigfdb.max())

    ##### Noise power measurement around each carriers
    fcarriers=np.array([])
    noise_power = 0
    if nb > 12: # bias or feedback
        print("Peak detection...")
        icarriers = peakdetect(sigfdb)
        fcarriers = icarriers*df
        ncar=len(fcarriers)
        print(" => {0:3d} carriers detected. \nCarrier frequencies (Hz):".format(ncar))
        freq_str, power_str =  " > ",  " > "
        if ncar > 0 and ncar < 80:
            noise_power = noiseandspurpower(sigf, icarriers, df, config) - e_freq_db + e_time_db - e_fsr_db
            for carrier in range(ncar):
                freq_str += '{0:12.2f}'.format(fcarriers[carrier])
                power_str += '{0:12.2f}'.format(noise_power[carrier])
                if (carrier+1) % 8 == 0:
                    freq_str += "\n > "
                    power_str += "\n > "
            print(freq_str)
            print("\nNoise power calculation... \nMeasured power (dBFS / 2 x Binfo)")
            print(power_str)

        io_str += 'Number of carriers detected------> {0:9d} : \n'\
        .format(ncar)
        io_str += freq_str + '\n\
Noise power around carriers-> (dBFS / 2 x Binfo)\n\
=============================================================================\n'\
        + power_str

    else:
        print("Calculation of mean noise power... (dBFS / 2 x Binfo)")
        noise_power = 10*np.log10(np.sum(sig**2)) - 10*np.log10(df*nval/2) - e_fsr_db 
        print(noise_power)
 
    return(sigfdb, fcarriers, noise_power, io_str)


# -----------------------------------------------------------------------------
def plot_dump(sig, nb, sigfdb, f_car, config, io_str, plotfilename):
    r"""
        This function plots a signal in time and frequency domain.

        Parameters
        ----------
        sig : array_like
        The data in time domain.

        nb : number
        The number of bits used to code the signal.

        sigfdb : array_like
        The data in frequency domain (expressed in dbFSR)

        f_car : number
        Frequency of the carrier we wabt to focus on.

        config : dictionnary
        Contains path and constants definitions

        io_str : string
        text to be displayed on the plot

        plotfilename : string
        name of the plotfile.

        Returns
        -------
        Nothing

    """

    fs = config["fs"]
    f_res = (fs/2)/len(sigfdb) # frequency resolution
    i_car = int(f_car / f_res) # position of the carrier in the frequency vector

    cf = crestfactor(sig-sig.mean())
    moyenne = sig.mean()
    moyenne_dbfs = 20*np.log10(2**nb/np.abs(moyenne))
    peakpeak = 2.*abs(sig).max()
    fsr_over_peakpeak = 2**nb/peakpeak
    io_str2 = '\n Crest factor = {0:5.2f}    FSR_DAC/PeakPeak = {1:6.2f}\n Mean = {2:5.2f} = {3:5.2f} dBFS'\
        .format(cf, fsr_over_peakpeak, moyenne, moyenne_dbfs)

    f = np.linspace(0, fs/2, len(sigfdb))
    L1 = 1024         # length of time plot (long)
    fig = plt.figure(figsize=(11, 12))
    fig.text(0.05, 0.98, io_str, family='monospace')
    ytimetitle = "amplitude"
    yfreqtitle = "amplitude (dB FSR)"

    # some reference levels
    all_sines_rms_level = -20.*np.log10(2*np.sqrt(2.)*4.5*np.sqrt(40))
    # some reference levels
    noise_req = -156

    # setting of the plot-ranges
    fxmin = (f_car - config['ScBandMax']) / 1e6
    fxmax = (f_car + config['ScBandMax']) / 1e6
    fxmin2 = 0.7
    fxmax2 = 5.2
    fymin = -180
    fymax = 0

    #####################################################################
    # Plotting data in time domain

    t = np.arange(len(sig))/fs
    ax1 = fig.add_subplot(3, 2, 1)
    ax1.plot(1000*t[0:L1], sig[0:L1], 'b')
    ax1.text(0, 2**(nb-1)*0.75, io_str2, color='k')
    ax1.set_ylabel(ytimetitle)
    ax1.set_xlabel('Time (ms)')
    ax1.grid(color='k', linestyle=':', linewidth=0.5)
    ax1.axis([0, 1000*L1/fs, -1*2**(nb-1), 2**(nb-1)])

    #####################################################################
    # Plotting data in frequency domain

    ax2 = fig.add_subplot(3, 2, 2)
    ax2.plot(f/1e6, sigfdb, 'b', linewidth=1)
    if nb==16:
        ax2.plot([0, f[-1]], [all_sines_rms_level, all_sines_rms_level], '--g', linewidth=1.5)
        ax2.plot([0, f[-1]], [noise_req, noise_req], '--k', linewidth=1.5)
    ax2.set_ylabel(yfreqtitle)
    ax2.set_xlabel('Frequency (MHz)')
    ax2.grid(color='k', linestyle=':', linewidth=0.5)
    ax2.axis([0, fs/2 / 1e6, fymin, fymax])

    ax3 = fig.add_subplot(3, 2, 3)
    ax3.plot(f / 1e6, sigfdb, 'b', linewidth=1)
    if nb==16:
        ax3.plot([0, f[-1]], [all_sines_rms_level, all_sines_rms_level], '--g', linewidth=1.5)
        ax3.plot([0, f[-1]], [noise_req, noise_req], '--k', linewidth=1.5)
    ax3.set_ylabel(yfreqtitle)
    ax3.set_xlabel('Frequency (MHz)')
    ax3.grid(color='k', linestyle=':', linewidth=0.5)
    ax3.axis([fxmin2, fxmax2, fymin, fymax])

    ax4 = fig.add_subplot(3, 2, 4)
    ax4.plot(f / 1e6, sigfdb, 'b', linewidth=1)
    ax4.plot(f / 1e6, sigfdb, '.r')
    if nb==16:
        ax4.plot([0, f[-1]], [all_sines_rms_level, all_sines_rms_level], '--g', linewidth=1.5)
        ax4.plot([0, f[-1]], [noise_req, noise_req], '--k', linewidth=1.5)
    ax4.set_ylabel(yfreqtitle)
    ax4.set_xlabel('Frequency (MHz)')
    ax4.grid(color='k', linestyle=':', linewidth=0.5)
    ax4.axis([fxmin, fxmax, fymin, fymax])

    ax5 = fig.add_subplot(3, 1, 3)
    npts = 50000
    f_shift = np.linspace(0, fs/2, len(sigfdb)) - f_car # frequency vector shifted around f_car
    delta = 0.1
    f_shift[i_car]+=delta # slight shift to allow xlog plot
    ax5.semilogx(f_shift[i_car:i_car+npts], sigfdb[i_car:i_car+npts], 'b', linewidth=1)
    ax5.set_ylabel("amplitude (dB FSR)")
    ax5.set_xlabel('Offset wrt carrier frequency (Hz)')
    ax5.grid(color='k', linestyle=':', linewidth=0.5)
    ax5.set_xlim(delta, f_shift[i_car+npts])
    ax5.set_ylim(-200, 0)
    ax5.text(delta*2, -10, 'Carrier frequency: {0:5.0f}MHz'.format(f_car))

    # Plotting spuriouses for the BIAS signal
    i_spurs = spurdetect(sigfdb[i_car:i_car+npts])
    n_spurs = len(i_spurs)
    spurs_mean = (sigfdb[i_car+i_spurs]-sigfdb[i_car]).mean()
    i_spur_max = np.where(sigfdb[i_car+i_spurs] == sigfdb[i_car+i_spurs].max())
    f_spur_max = f_shift[i_car+i_spurs[i_spur_max]]
    spur_max = sigfdb[i_car+i_spurs[i_spur_max]]
    spur_max_text = '{0:5.1f}dBc'.format((spur_max-sigfdb[i_car])[0])
    general_spur_text = '{0:2d} spurious detected in the plot range,\n'.format(n_spurs) \
        +'Stronger spurious measured at {0:5d}Hz from the carrier with an amplitude of {1:5.1f}dBc\n' \
            .format(int(f_spur_max[0]), (spur_max-sigfdb[i_car])[0]) \
        +'Mean spurious value: {0:5.1f}dBc (mean of dB values)'.format(spurs_mean)            
    ax5.semilogx(f_shift[i_car+i_spurs], sigfdb[i_car+i_spurs],'o', color='orange')
    ax5.semilogx(f_spur_max, spur_max, '*', color='red')
    ax5.text(f_spur_max, spur_max+5, spur_max_text, horizontalalignment='center', color='red')
    ax5.text(3, -75, general_spur_text)

    fig.tight_layout()
    #plt.show()
    plt.savefig(plotfilename, bbox_inches='tight')
    print('Plots done')

# -----------------------------------------------------------------------------
def spurdetect(sig, margin=6):

    delta1 = sig - np.concatenate((sig[1:], [sig[-1]]))
    delta2 = sig - np.concatenate(([sig[0]], sig[:-1]))
    return(np.intersect1d(np.where(delta1 > margin)[0], np.where(delta2 > margin)[0]))


# -----------------------------------------------------------------------------
def peakdetect(sig, margin=6):
    r"""
        This function detects all peaks in a 1D signal. A threshold is used
        to define the lower limit (wrt the maximum of the signal) for the search.

        Parameters
        ----------
        sig : array_like
        The signal in which peaks will be detected

        margin : number
        The range where to look for maxima wrt to the absolute maximum 
        (default is 6).

        Returns
        -------
        detected_peaks_indexes : array_like
        Indexes of detected peaks according to the input array

        Example
        -------
        >>> a = peakdetect(vector,margin)
        >>> a
        array([ 5,  9,  23, ...,  102,  143,  340])

        """
    # First look for maximum areas
    ithreshold = np.where(sig > sig.max() - margin)[0]

    # Then look for local maxima in each area
    derivative1 = sig[1:] - sig[:-1]
    i_zero = np.where(derivative1 == 0)[0]       # To avoid division
    derivative1[i_zero] = 1                      # by 0 at the next step.
    derivative2 = derivative1 / abs(derivative1) # keeps only +1 and -1
    pic = derivative2[:-1] - derivative2[1:]     # equals 2 at local maxima
    i = np.where(pic[ithreshold-1] == 2)[0]
    return(ithreshold[i])

# -----------------------------------------------------------------------------
def crestfactor(signal):
    r"""
        This function computes the crest factor (cf) of a signal.

        The cf is defined as the ratio between the peak value of a signal and
        its rms value.

        Parameters
        ----------
        signal : array_like
        an array

        Returns
        -------
        cf : number
        The crest factor computed using cf = Peak / rms

        Example
        -------
        >>> crestfactor(array([3., 7., 1., 5., 4., 6., 3.5]))
        0.651887905613

        """
    peak = abs(signal).max()
    return(peak / signal.std())

# -----------------------------------------------------------------------------
def noiseandspurpower(sigf, indexes, df, config):
    r"""
        This function measures the power of the signal in a band around
        specific frequency indexes.

        Parameters
        ----------
        sig : array_like
        The signal in which the power is measured.

        indexes : array_like
        An array containing the indexes of the carriers.

        df : number
        The frequency resolution.

        config : dictionnary
        Contains path and constants definitions

        Returns
        -------
        The values of the power measured around each carrier.

    """

    powers = np.zeros(len(indexes))
    for k, index in enumerate(indexes):
        l_side_1 = index - int(np.ceil(config['ScBandMax']/df))
        l_side_2 = index - int(np.ceil(config['ScBandMin']/df))
        r_side_1 = index + int(np.ceil(config['ScBandMin']/df))
        r_side_2 = index + int(np.ceil(config['ScBandMax']/df))
        powers[k] = np.sum(sigf.astype(float)[l_side_1:l_side_2]**2) \
                    + np.sum(sigf.astype(float)[r_side_1:r_side_2]**2)

    powers_db=-1*np.inf*np.ones(len(powers))
    inotzero=np.where(powers != 0)[0]
    powers_db[inotzero] = 10*np.log10(powers[inotzero])
    return(powers_db)

# -----------------------------------------------------------------------
def process_dump_pulses(fulldirname, config):
    r"""
        This function reads and process the data of DRE-DEMUX data dumps.
        INPUT signal while pulses.
        
        Parameters
        ----------
        fulldirname : string
        The name of the dump file (with the path)

        config : dictionnary
        Contains path and constants definitions

        Returns
        -------
        Nothing

        """

    datadirname = os.path.join(fulldirname, config['dir_data'])
    plotdirname = os.path.join(fulldirname, config['dir_plots'])
    general_tools.checkdir(plotdirname)

    fs = config["fs"]
    nb = 12 # INPUT signal over 12 bits

    f_type_deb, f_type_fin = 21, 33
    dumpfilenames = [f for f in os.listdir(datadirname) \
                if os.path.isfile(os.path.join(datadirname, f)) \
                and f[-4:]=='.dat'\
                and f[f_type_deb:f_type_fin]=="IN-BIA_PULSE"]

    if len(dumpfilenames)>0:
        dumpfilename = os.path.join(datadirname, dumpfilenames[0])
        plotfilename = os.path.join(plotdirname, "PLOT_INPUT_WITH_PULSES.png")

        # Getting the data from dump file
        data, _ = get_data.readfile(dumpfilename)

        channel=int(data[0, 1]/2**12)
        a=data[1:,0]
        pp=a.max()-a.min()
    
        nval=len(a)
        duration = (nval/fs)
    
        t = np.linspace(0, duration, nval)

        pulse_length = 1024*128
        center = a[pulse_length:-pulse_length] # Only consider the center of the dumb to have a full pulse
        imax = np.where(center==np.max(center))[0][0]+pulse_length
        ideb = imax - 128*100
        ifin = imax + pulse_length
        i3 = ifin - 128*30
        i2 = ifin - 128*100
        i1 = ifin - 128*170

        # Making plot
        fig = plt.figure(figsize=(8, 6))
        io_str="File: "+dumpfilenames[0]+", Channel {0:1d}, FSR(ADC)/PeakPeak = {1:5.2f}".format(channel, 2.**12/pp)
        fig.text(0.1, 0.982, io_str, family='monospace')

        #---------------------------
        # Assumptions:
        # - The FSR of the ADC corresponds to the FSR output of the SQUID (i.e. 0.5Phi0pp)
        # - 12keV corresponds to 0.3Phi0 at SQUID input
        # - The "SQUID flux" versus "ADC input level" is a non linear function for high signals (sine function)
        # - ADC level for 12keV = FSR * sin(pi/2 * 0.3/0.5) / sin(pi/2)
        # - ADC level for 7keV = FSR * sin(pi/2 * 0.3*(7/12)/0.5) / sin(pi/2)
        fsr_peak = 2**(nb-1) # FSR peak
        fsr_flux = 0.5
        twelve_kev_flux = 0.3
        seven_kev_flux = 0.3*7./12.
        twelve_kev_peak = fsr_peak * np.sin((np.pi/2)*twelve_kev_flux/fsr_flux) / np.sin(np.pi/2)
        seven_kev_peak = fsr_peak * np.sin((np.pi/2)*seven_kev_flux/fsr_flux) / np.sin(np.pi/2)
        deltatext = 128*30
        ytext = -0.1 * fsr_peak

        ax = fig.add_subplot(1, 1, 1)
        ax.plot(t[ideb:ifin]*1e3, a[ideb:ifin])
        ax.plot([t[ideb]*1e3,t[ifin]*1e3], [twelve_kev_peak, twelve_kev_peak], '--g', linewidth=0.5)
        ax.plot([t[ideb]*1e3,t[ifin]*1e3], [-twelve_kev_peak, -twelve_kev_peak], '--g', linewidth=0.5)
        plt.annotate(s='',xytext=(t[i1]*1e3, 0), xycoords='data',
            xy=(t[i1]*1e3, fsr_peak), textcoords='data',
            arrowprops=dict(width=0.8, headwidth=4, headlength=12))
        plt.annotate(s='',xytext=(t[i1]*1e3, 0), xycoords='data',
            xy=(t[i1]*1e3, -fsr_peak), textcoords='data',
            arrowprops=dict(width=0.5, headwidth=4, headlength=12))
        plt.text(t[i1-deltatext]*1e3, ytext, r'0.50 $\phi_0$', rotation=90)

        plt.annotate(s='',xytext=(t[i2]*1e3, 0), xycoords='data',
            xy=(t[i2]*1e3, twelve_kev_peak), textcoords='data',
            arrowprops=dict(width=0.8, headwidth=4, headlength=12))
        plt.annotate(s='',xytext=(t[i2]*1e3, 0), xycoords='data',
            xy=(t[i2]*1e3, -twelve_kev_peak), textcoords='data',
            arrowprops=dict(width=0.5, headwidth=4, headlength=12))
        plt.text(t[i2-deltatext]*1e3, ytext, r'0.30 $\phi_0$ (12 keV)', rotation=90)

        ax.plot([t[ideb]*1e3,t[ifin]*1e3], [seven_kev_peak, seven_kev_peak], '--g', linewidth=0.5)
        ax.plot([t[ideb]*1e3,t[ifin]*1e3], [-1*seven_kev_peak, -1*seven_kev_peak], '--g', linewidth=0.5)
        plt.annotate(s='',xytext=(t[i3]*1e3, 0), xycoords='data',
            xy=(t[i3]*1e3, seven_kev_peak), textcoords='data',
            arrowprops=dict(width=0.8, headwidth=4, headlength=12))
        plt.annotate(s='',xytext=(t[i3]*1e3, 0), xycoords='data',
            xy=(t[i3]*1e3, -seven_kev_peak), textcoords='data',
            arrowprops=dict(width=0.5, headwidth=4, headlength=12))
        plt.text(t[i3-deltatext]*1e3, ytext, r'{0:3.2f} $\phi_0$ (7 keV)'.format(seven_kev_flux), rotation=90)

        ax.set_ylabel("ADC unit (FSR range)")
        ax.set_xlabel("Time (ms)")
        ax.set_ylim([-2**(nb-1), 2**(nb-1)])

        fig.tight_layout()
        #plt.show()
        plt.savefig(plotfilename, bbox_inches='tight')

def mosaic_labels(ax, box, n_cols, n_lines, x_lab, y_lab):
    r"""
        This function defines the xlabel and ylabel for a plot in a plot mosaic.
        The xlabel is displayed only for the plots at the bottom of the mosaic.
        The ylabel is displayed only for the plots at the left of the mosaic.

        Parameters
        ----------
        ax : matplotlib axis

        box : number
        the number of the plot in the mosaic

        n_cols, n_lines : numbers
        the number of columns and lines in the mosaic

        x_lab, y_lab : string
        the x and y labels

        Returns
        -------
        Nothing

        """
    if box//n_cols == n_lines-1:
        ax.set_xlabel(x_lab)
    else:
        plt.xticks(visible=False)
    if box%n_cols == 0:
        ax.set_ylabel(y_lab)
    else:
        plt.yticks(visible=False)

# -----------------------------------------------------------------------
def plot_spectra(sptdb, config, pltfilename, cf, fsr_over_peakpeak, suffixe, bw_correction_factor_db, pix_zoom=40):
    r"""
        This function plots spectra of IQ data wrt the carriers.
                
        Parameters
        ----------
        sptdb : arrays
        Spectra.
        
        config: dictionnary
        contains usefull parameters
        
        pltfilename, suffixe: strings
        Used to specify the plot file names.

        Cf : number.
        Crest factor of the signal (used for the conversion dBc / dBFS)

        FSR_over_PeakPeak : number.
        Ratio between signal peak to peak value and DAC FSR (used for the conversion dBc / dBFS)

        suffixe : string.
        Extension to be added to the plot file name.

        bw_correction_factor_db : number.
        BW correction factor that has been applied to obtain the spectra in dB.Hz. This value needs to be 
        indicated on the plot so that it can be taken into account when measuring spuriouses.

        pix_zoom: number
        The id of a pixel to be zoomed in.
        (default value is 40 = test pixel)

        Returns
        -------
        Nothing           
        """

    npts = len(sptdb[0,:])
    ncar = len(sptdb[:,0])
    fs=float(config["fs"])/2**float(config["power_to_fs2"])
    f=np.arange(npts)*fs/(2*npts)
    impact_2_dacs = 3    # Because the test set-up involves two DACs (bias and feedback)
    impact_non_stationarity = 20*np.log10(1.4) # Because our test set-up does not reproduce the TES non-stationarity 
    impact_bbfb = 3  # BBFB adds 3 dB noise (TBC)
    snr_pix_min = config['SNR_pix'] + impact_2_dacs + impact_non_stationarity
    snr_pix_max = snr_pix_min + impact_bbfb
    sc_band_min = config['ScBandMin'] 
    sc_band_max = config['ScBandMax'] 
    bw_res_warn = r'A BW res. correction factor of {0:4.2f}dB has been applied on the spectra. It shall be corrected for spurious measurements.'.format(bw_correction_factor_db)

    # Plot for zoom pixel only
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(1, 1, 1)
    ax.semilogx(f[1:], sptdb[pix_zoom,1:])
    i_spurs = spurdetect(sptdb[pix_zoom,:])
    ax.semilogx(f[i_spurs], sptdb[pix_zoom,i_spurs],'o',color='orange')
    ax.semilogx([sc_band_min, sc_band_max], [snr_pix_min, snr_pix_min], ':r', linewidth=3)
    ax.semilogx([sc_band_min, sc_band_max], [snr_pix_max, snr_pix_max], ':r', linewidth=3)
    ax.semilogx([sc_band_min, sc_band_min], [snr_pix_min, 0], ':r', linewidth=3)
    ax.semilogx([sc_band_max, sc_band_max], [snr_pix_min, 0], ':r', linewidth=3)
    ax.text(40, -17, r'band of interest', fontsize=11)
    ax.text(sc_band_min, snr_pix_min-5, r'DRD requirement level', fontsize=11)
    ax.text(1.5, -159, bw_res_warn, fontsize=11)
    L1, L2=100, 2.5
    ax.arrow(sc_band_min, -20, sc_band_max-L1, 0, head_width=3, head_length=L1, fc='k', ec='k')
    ax.arrow(sc_band_max, -20, -sc_band_max+sc_band_min+L2, 0, head_width=3, head_length=L2, fc='k', ec='k')
    ax.axis([1, f[-1], -160, 0])
    ax.set_xlabel(r'Frequency (Hz)')
    ax.set_ylabel(r'DRD (dBc.Hz)')
    ax.set_title(r'Pixel {0:2d}'.format(pix_zoom))
    # Major ticks every 20, minor ticks every 10
    major_ticks = np.arange(-160, 1, 20)
    minor_ticks = np.arange(-160, 1, 10)
    ax.set_yticks(major_ticks)
    ax.set_yticks(minor_ticks, minor=True)
    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
        item.set_weight('bold')
        item.set_fontsize(17)
    for item in (ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(15)
    if cf!=0:
        carrier_vs_fullscale_db=20*np.log10(fsr_over_peakpeak*2*cf*np.sqrt(ncar))
        ax2 = plt.gca().twinx()
        ax2.axis([f[1], f[-1], -160-carrier_vs_fullscale_db, 0-carrier_vs_fullscale_db])
        ax2.set_ylabel(r'DRD (dBFS.Hz)')
        ax2.yaxis.label.set_weight('bold')
        ax2.yaxis.label.set_fontsize(17)
        for item in (ax2.get_yticklabels()):
            item.set_fontsize(15)
    fig.tight_layout()
    plt.savefig(pltfilename+suffixe+'_zoom'+str(pix_zoom)+'.png', bbox_inches='tight')

    # Plot for all other pixels (but the test pixels)
    n_boxes=40 
    n_lines=5
    n_cols =8

    # Checking which pixel is on
    pix_on = np.ones((n_boxes), dtype=bool)
    for pix in range(n_boxes):
        if sptdb[pix,1:].max()==sptdb[pix,1:].min():
            pix_on[pix]=False
            print("\n------------------> Pixel {0:2d} is off.".format(pix))

    fig = plt.figure(figsize=(18, 12))
    for box in range(n_boxes):
        if pix_on[box]:
            ax = fig.add_subplot(n_lines, n_cols, box+1)
            ax.semilogx(f[1:], sptdb[box,1:])
            ax.semilogx([sc_band_min, sc_band_max], [snr_pix_min, snr_pix_min], ':r')
            ax.semilogx([sc_band_min, sc_band_max], [snr_pix_max, snr_pix_max], ':r')
            ax.semilogx([sc_band_min, sc_band_min], [snr_pix_min, 0], ':r')
            ax.semilogx([sc_band_max, sc_band_max], [snr_pix_min, 0], ':r')
            ax.axis([f[1], f[-1], -160, 0])
            ax.grid(color='k', linestyle=':', linewidth=0.5)
            ax.set_title(r'Pixel {0:2d}'.format(box))
            mosaic_labels(ax, box, n_cols, n_lines, r'Frequency (Hz)', r'DRD (dBc.Hz)')
            for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
                item.set_fontsize(15)
            for item in (ax.get_xticklabels() + ax.get_yticklabels()):
                item.set_fontsize(13)
    fig.tight_layout()
    plt.savefig(pltfilename+suffixe+'_40pix.png', bbox_inches='tight')

# -----------------------------------------------------------------------
def get_cf_and_fsroverpeakpeak_from_file(fulldirname, quiet=True):
    r"""   
        This function gets data from a ADC - Feedback dump file, it 
        computes the crest factor and the FSR_over_peakpeak ratio.

        Parameters
        ----------
        fulldirname : string
        Name of the directory
        """

    f_type_deb, f_type_fin = 21, 27
    dumpfilenames = [f for f in os.listdir(fulldirname) \
            if os.path.isfile(os.path.join(fulldirname, f)) \
            and f[-4:]=='.dat'\
            and f[f_type_deb:f_type_fin]=="IN-BIA"]

    if len(dumpfilenames)>0:
        filename = os.path.join(fulldirname, dumpfilenames[0])

        data, _ = get_data.readfile(filename)
        feedback = data[1:,1].astype(float)
        cf = crestfactor(feedback)
        peakpeak = 2.*max(abs(feedback))
        fsr_over_peakpeak = 2.**16/peakpeak
        
        # Searching the carriers
        feedback_f = abs(rfft(feedback[:2**16]))
        feedback_f_db = -300.*np.ones(2**16)
        inotzero = np.where(feedback_f != 0)[0]
        feedback_f_db[inotzero] = 20*np.log10(feedback_f[inotzero])
        ncar = len(peakdetect(feedback_f_db))
        #print("============>>>>>>>>>>>> ", ncar)

        if not quiet:
            print("Feedback crest factor: {0:5.2f}".format(cf))
            print("Feedback peak value:   {0:5.2f}".format(peakpeak))
            print("Number of carriers:    {0:5d}".format(ncar))
            print("DAC peak value:        {0:5d}".format(2**16-1))
            print("FSR / Peak:            {0:5.2f}".format(fsr_over_peakpeak))
    else:
        cf = fsr_over_peakpeak = ncar = 0

    return(cf, fsr_over_peakpeak, ncar)

# -----------------------------------------------------------------------
def win(window, npts):
    if window:
        win = np.blackman(npts)
    else:
        win = 1
    return(win)

# -----------------------------------------------------------------------
def process_iq_multi(fulldirname, config, pix_zoom=40, window=False, bw_correction=True):
    r"""
        This function reads data from several DRE IQ data files.
        It computes the accumulated spectra and makes the plots.
        
        Parameters
        ----------
        fulldirname : string
        The name of the directory containing the data files
        
        config: dictionnary
        contains usefull parameters

        pix_zoom: number
        The id of a pixel to be zoomed in.
        (default value is 40 = test pixel)

        window: boolean
        Specifies if a windowing shall be done before the FFT.
        If True a Blackman Harris window is applied. (Default is False)

        bw_correction: boolean
        Specifies if a correction factor has to be applied to take into account the resolution BW (Default is True).
        If this factor is applied the measurment will be wrong for spuriouses (Default is True).

        Returns
        ------- 
        spt0dB : Array containing the accumulated pixels spectra
           
        """

    # computing sampling frequency at BBFB output
    fs = config["fs"]/2**7

    npix=41
    npts_max=2**17
    nb_short_files=0

    datadirname = os.path.join(fulldirname, config['dir_data'])
    plotdirname = os.path.join(fulldirname, config['dir_plots'])
    general_tools.checkdir(plotdirname)

    pltfilename = os.path.join(plotdirname, "PLOT_carrier_spt")

    i_test_deb, i_test_fin = 21, 40
    test = "IQ-ALL_Science-Data"
    fichlist = [f for f in os.listdir(datadirname) \
                if os.path.isfile(os.path.join(datadirname, f)) \
                and f[-4:]=='.dat' and f[i_test_deb:i_test_fin]==test]

    if len(fichlist)>0:
        print('Measurment of signal crest factor from feedback dump files if they exist')
        cf0, fsr_over_peakpeak0, _ = get_cf_and_fsroverpeakpeak_from_file(datadirname)

        # definning file length
        chan0_i, _, _, _, FLAG_ERROR = get_data.read_iq(os.path.join(datadirname, fichlist[0]))
        npts = len(chan0_i[:,0])
        print('Npts:', npts)
        npts=min(npts_max, 2**np.int(np.log(npts)/np.log(2)))
        duration=npts/fs
        # Factor to correct the resolution BW effect on noise
        bw_correction_factor_db=10*np.log10(duration)
        print("Scan duration is about: {0:6.4f}".format(duration))
        print("WARNING, a bandwidth correction factor of {0:6.4f}dB is applied on the spectra.".format(bw_correction_factor_db))
        print("This offset needs to be taken into account when considering spurious values.")

        spt0db=-300*np.ones((npix, npts//2+1))
        total_spt0=np.zeros((npix, npts//2+1))
        spt = np.zeros((npix, npts//2+1))
    
        nfiles = len(fichlist)
        print("{0:3d} files to process...".format(nfiles))
        file=0
        errors_counter = 0
        CHAN0_EMPTY=True
        for fich in fichlist:
            file+=1
            print('Processing file {0:3d}/{1:3d} '.format(file, nfiles), end='')
            print(fich)
            chan0_i, chan0_q, _, _, FLAG_ERROR = get_data.read_iq(os.path.join(datadirname, fich))
            npts_current = len(chan0_i[:,0])
            if FLAG_ERROR:
                errors_counter += 1

            if npts_current >= npts:

                chan0_modulus = \
                    np.sqrt(chan0_i[0:npts,:].astype('float')**2 + chan0_q[0:npts,:].astype('float')**2)
                            
                if chan0_modulus.max() > 0: # data exists
                    CHAN0_EMPTY=False
                    for pix in range(npix):
                        spt[pix,:] = abs(rfft((chan0_modulus[:,pix])*win(window, npts)))
                    total_spt0 += spt**2
                                
            else:
                print("File is too short!")
                nb_short_files += 1 

        print("Data processing is done.")
        print("{0:4d} corrupted files found.".format(errors_counter))
        print("{0:4d} files were too short for processing.".format(nb_short_files))
        print("Doing the plots...", end='')
    
        if not CHAN0_EMPTY:
            # Normalisation wrt each carrier
            for pix in range(npix): 
                i_good = np.where(total_spt0[pix,:] > 0)[0]
                spt0db[pix,i_good] = 10*np.log10(total_spt0[pix,i_good])
                spt0db[pix,:] = spt0db[pix,:] - spt0db[pix,:].max()
            # 3 dB correction to compensate the impact of the rfft on DC bin
            spt0db[:,1:] += 3
            # Normalisation to a RBW of 1Hz
            if bw_correction:
                spt0db[:,1:] += bw_correction_factor_db
            plot_spectra(spt0db, config, pltfilename, cf0, fsr_over_peakpeak0, '', bw_correction_factor_db, pix_zoom)
    else:
        spt0db=0
        
    return(spt0db)

# -----------------------------------------------------------------------
def process_iq_tst_multi(fulldirname, config, window=False, bw_correction=True):
    r"""
        This function reads data from several DRE IQ-TST data files.
        It computes the accumulated spectra and makes the plots.
        
        Parameters
        ----------
        fulldirname : string
        The name of the directory containing the data files
        
        config: dictionnary
        contains usefull parameters
        
        window: boolean
        Specifies if a windowing shall be done before the FFT.
        If True a Blackman Harris window is applied. (Default is False)

        bw_correction: boolean
        Specifies if a correction factor has to be applied to take into account the resolution BW (Default is True).
        If this factor is applied the measurment will be wrong for spuriouses (Default is True).
        
        Returns
        ------- 
        spt0dB : Array containing the accumulated pixels spectra
           
        """

    npts_max=2**26
    nb_short_files=0

    fs = float(config["fs"])

    datadirname = os.path.join(fulldirname, config['dir_data'])
    plotdirname = os.path.join(fulldirname, config['dir_plots'])
    if not os.path.isdir(plotdirname):
        os.mkdir(plotdirname)

    pltfilename = os.path.join(plotdirname, "PLOT_carrier-TST_spt")

    i_test_deb, i_test_fin = 21, 40
    test = "IQ-TST_Science-Data"
    fichlist = [f for f in os.listdir(datadirname) \
                if os.path.isfile(os.path.join(datadirname, f)) \
                and f[-4:]=='.dat' \
                and f[i_test_deb:i_test_fin]==test]

    if len(fichlist)>0:
        print('Measurment of signal crest factor from feedback dump files if they exist')
        cf, fsr_over_peakpeak, ncar = get_cf_and_fsroverpeakpeak_from_file(datadirname)

        # definning file length
        data, dumptype = get_data.readfile(os.path.join(datadirname, fichlist[0]))
        if dumptype != 9:
            raise ValueError('Wrong dumptype')

        # decommutation des donnees        
        npts = len(data[1:,0])   
        print('Npts:', npts)
        npts=min(npts_max, 2**np.int(np.log(npts)/np.log(2)))
        duration=npts/fs
        # Factor to correct the resolution BW effect on noise
        bw_correction_factor_db=10*np.log10(duration)
        print("Scan duration is about: {0:6.4f}".format(duration))
        print("WARNING, a bandwidth correction factor of {0:6.4f}dB is applied on the spectra.".format(bw_correction_factor_db))
        print("This offset needs to be taken into account when considering spurious values.")

        sptdb=np.zeros((npts//2+1))
        total_spt=np.zeros((npts//2+1))
    
        nfiles = len(fichlist)
        print("{0:3d} files to process...".format(nfiles))
        file=0
        errors_counter = 0
        EMPTY=True
        for fich in fichlist:
            file+=1
            print('Processing file {0:3d}/{1:3d} '.format(file, nfiles), end='')
            print(fich)

            data, dumptype = get_data.readfile(os.path.join(datadirname, fich))
            if dumptype != 9:
                raise ValueError('Wrong dumptype')

            # decommutation des donnees        
            npts_current = len(data[1:,0])

            if npts_current >= npts:

                modulus = np.sqrt(data[1:npts+1,0].astype('float')**2 + data[1:npts+1,1].astype('float')**2)
                            
                if modulus.max() > 0: # data exists
                    EMPTY=False
                    total_spt += abs(rfft(modulus*win(window, npts)))**2
                                
            else:
                print("File is too short!")
                nb_short_files += 1 

        print("Data processing is done.")
        print("{0:4d} corrupted files found.".format(errors_counter))
        print("{0:4d} files were too short for processing.".format(nb_short_files))
        print("Doing the plots...", end='')
    
        if not EMPTY:            
            sptdb = 10*np.log10(total_spt)
            # Normalisation wrt carrier
            sptdb -= sptdb.max()
            # 3 dB correction to compensate the impact of the rfft on DC bin
            sptdb[1:] += 3
            # Normalisation to a RBW of 1Hz
            if bw_correction:
                sptdb[1:] += bw_correction_factor_db

            npts = len(sptdb)
            f=np.arange(npts)*fs/(2*npts)
            impact_2_dacs = 3    # Because the test set-up involves two DACs (bias and feedback)
            impact_non_stationarity = 20*np.log10(1.4) # Because our test set-up does not reproduce the TES non-stationarity 
            impact_bbfb = 3  # BBFB adds 3 dB noise (TBC)
            snr_pix_min = config['SNR_pix'] + impact_2_dacs + impact_non_stationarity
            snr_pix_max = snr_pix_min + impact_bbfb
            sc_band_min = config['ScBandMin'] 
            sc_band_max = config['ScBandMax'] 
            bw_res_warn = r'A BW res. correction factor of {0:4.2f}dB has been applied on the spectra. It shall be corrected for spurious measurements.'.format(bw_correction_factor_db)

            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(1, 1, 1)
            ax.semilogx(f[1:], sptdb[1:])
            ax.semilogx([sc_band_min, sc_band_max], [snr_pix_min, snr_pix_min], ':r', linewidth=3)
            ax.semilogx([sc_band_min, sc_band_max], [snr_pix_max, snr_pix_max], ':r', linewidth=3)
            ax.semilogx([sc_band_min, sc_band_min], [snr_pix_min, 0], ':r', linewidth=3)
            ax.semilogx([sc_band_max, sc_band_max], [snr_pix_min, 0], ':r', linewidth=3)
            ax.text(40, -17, r'band of interest', fontsize=11)
            ax.text(sc_band_min, snr_pix_min-5, r'DRD requirement level', fontsize=11)
            ax.text(1.5, -179, bw_res_warn, fontsize=11)
            L1, L2=100, 2.5
            ax.arrow(sc_band_min, -20, sc_band_max-L1, 0, head_width=3, head_length=L1, fc='k', ec='k')
            ax.arrow(sc_band_max, -20, -sc_band_max+sc_band_min+L2, 0, head_width=3, head_length=L2, fc='k', ec='k')
            #ax.axis([1, f[-1], -180, 0])
            ax.set_ylim(-180, 0)
            ax.set_xlim(1, f[-1])
            ax.set_xlabel(r'Frequency (Hz)')
            ax.set_ylabel(r'DRD (dBc.Hz)')
            ax.set_title(r'Test pixel')
            # Major ticks every 20, minor ticks every 10
            major_ticks = np.arange(-160, 1, 20)
            minor_ticks = np.arange(-160, 1, 10)
            ax.set_yticks(major_ticks)
            ax.set_yticks(minor_ticks, minor=True)
            ax.grid(which='minor', alpha=0.2)
            ax.grid(which='major', alpha=0.5)
            for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
                item.set_weight('bold')
            for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
                item.set_fontsize(17)
            for item in (ax.get_xticklabels() + ax.get_yticklabels()):
                item.set_fontsize(15)
            if cf!=0:
                carrier_vs_full_scale_db=20*np.log10(fsr_over_peakpeak*2*cf*np.sqrt(ncar))
                ax2 = plt.gca().twinx()
                ax2.axis([f[1], f[-1], -160-carrier_vs_full_scale_db, 0-carrier_vs_full_scale_db])
                ax2.set_ylabel(r'DRD (dBFS.Hz)')
                ax2.yaxis.label.set_weight('bold')
                ax2.yaxis.label.set_fontsize(17)
                for item in (ax2.get_yticklabels()):
                    item.set_fontsize(15)

            fig.tight_layout()
            plt.savefig(pltfilename+'.png', bbox_inches='tight')

    else:
        sptdb=0
        
    return(sptdb)

# -----------------------------------------------------------------------
