# Std dependencies
import argparse, queue, sys

# External dependencies
import sounddevice as sd
import numpy as np
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt

############################################################################
############################################################################
#######               BEGIN COMMAND-LINE PARSING BLOCK               #######
#######             (taken from sounddevice API samples)             #######
############################################################################
############################################################################

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

parser = argparse.ArgumentParser(add_help=False)

parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-w', '--window', type=float, default=200, metavar='DURATION',
    help='visible time slot (default: %(default)s ms)')
parser.add_argument(
    '-i', '--interval', type=float, default=30,
    help='minimum time between plot updates (default: %(default)s ms)')
parser.add_argument(
    '-b', '--blocksize', type=int, help='block size (in samples)')
parser.add_argument(
    '-r', '--samplerate', type=float, help='sampling rate of audio device')
parser.add_argument(
    '-n', '--downsample', type=int, default=10, metavar='N',
    help='display every Nth sample (default: %(default)s)')
args = parser.parse_args(remaining)
args.columns = 1
args.gain = .5

############################################################################
############################################################################
#######               END COMMAND-LINE PARSING BLOCK                 #######
############################################################################
############################################################################

def update_plot(frame):
    """This is called by matplotlib for each plot update.

    Typically, audio callbacks happen more frequently than plot updates,
    therefore the queue tends to contain multiple blocks of audio data.

    """
    global plotdata
    #while True:
    try:
       data = q.get_nowait()
    except queue.Empty:
        return
        """
        shift = len(data)
        plotdata = np.roll(plotdata, -shift, axis=0)
        plotdata[-shift:, :] = data
         
        transform = abs(np.fft.rfft(data))
        plotdata = transform"""

    transform = abs(np.fft.rfft(data))
    ax.clear()
    ax.stem(freqs, transform)

    #for column, line in enumerate(lines):
    #    line.set_ydata(transform)
    return

q = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        print(str(status))
        
    q.put(indata)

try:
    samplerate = 48000
    T = samplerate / 2
    N = 1024
    bins = 512
    bandwidth = int(T / N)

    freqs = np.fft.fftfreq(bins * 2) * samplerate
    freqs = freqs[0:int(len(freqs)/2)]

    plotdata = np.zeros(bins)
    
    fig, ax = plt.subplots()
    lines = ax.stem(plotdata, freqs)

    #ax.axis((0, len(plotdata), -1, 1))
    ax.set_yticks([0])
    ax.yaxis.grid(True)
    ax.tick_params(bottom=False, top=False, labelbottom=False,
                   right=False, left=False, labelleft=False)
    fig.tight_layout(pad=0)
    ax.set_xlim(0, samplerate / 2)

    ani = FuncAnimation(fig, update_plot, repeat=False, interval=args.interval, blit=False)
    
    stream = sd.InputStream(device=args.device, samplerate=48000, callback=audio_callback)

    with stream:
        plt.show()
   
    
    

except KeyboardInterrupt:
    parser.exit('Interrupted by user')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
  
    
        