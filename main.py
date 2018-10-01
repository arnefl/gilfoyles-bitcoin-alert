import urllib3
import tempfile
import json
import time
import youtube_dl
import subprocess
import sys

from os import system, name
from os.path import join, isfile

# Check OS requirements
if name == 'nt':
    import winsound
elif name == 'posix':
    import pyaudio
    import wave as wv
else:
    sys.exit('Error: Alerts is not implemented for your operating system.\nExiting.')

class sysutil2():
    # import sys
    # from os import system, name
    def __init__(self):
        self.operating_system = name

    def flush_output(self):
        if self.operating_system == 'nt':
            system('cls')
        elif self.operating_system == 'posix':
            system('clear')
        else:
            sys.Error('flush_output is not implemented for this OS.')

# Script to fetch sound from youtube
def youtube_to_wav(url, destination):
    dest_file = destination + '.wav'

    if isfile(dest_file):
        pass
    else:
        mkv_temp = destination
        ydl_opts = {
            'outtmpl' : "{}".format(mkv_temp),
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Convert to wav
        command = "ffmpeg -i {} -ab 160k -ac 2 -ar 44100 -vn {}".format(mkv_temp + '.mkv', dest_file)
        subprocess.call(command, shell=True)

    return(dest_file)

def sv_ascii():
    x = '  ________.__.__  .__                      ____   ____      .__  .__                \n'
    x += ' /   _____|__|  | |__| ____  ____   ____   \   \ /   _____  |  | |  |   ____ ___.__.\n'
    x += ' \_____  \|  |  | |  _/ ___\/  _ \ /    \   \   Y   /\__  \ |  | |  | _/ __ <   |  |\n'
    x += ' /        |  |  |_|  \  \__(  <_> |   |  \   \     /  / __ \|  |_|  |_\  ___/\___  |\n'
    x += '/_______  |__|____|__|\___  \____/|___|  /    \___/  (____  |____|____/\___  / ____|\n'
    x += '        \/                \/           \/                 \/               \/\/     \n'
    return(x)

# Alerter
class alerts():
    def __init__(self, os):
        self.user_os = os

        self.ding_sound_url = 'http://www.youtube.com/watch?v=ybGOT4d2Hs8'
        self.ding_local_path = join(tempfile.gettempdir(), 'gilfoyles_ding')
        self.ding_local_path = youtube_to_wav(self.ding_sound_url,
                                self.ding_local_path)

    def alert(self):
        if self.user_os == 'nt':
            winsound.PlaySound(self.ding_local_path, winsound.SND_FILENAME)
        elif self.user_os == 'posix':
            #define stream chunk
            chunk = 1024

            #open a wav format music
            f = wv.open(self.ding_local_path,'rb')
            #instantiate PyAudio
            p = pyaudio.PyAudio()
            #open stream
            stream = p.open(format = p.get_format_from_width(f.getsampwidth()),
                            channels = f.getnchannels(),
                            rate = f.getframerate(),
                            output = True)
            #read data
            data = f.readframes(chunk)

            #play stream
            while data:
                stream.write(data)
                data = f.readframes(chunk)

            #stop stream
            stream.stop_stream()
            stream.close()

            #close PyAudio
            p.terminate()


# Bitcoin price
class bitcoin():
    def __init__(self):
        self.json_url = 'https://www.bitstamp.net/api/ticker/'
        self.bitstamp_http = urllib3.PoolManager()

    def get_price(self):
        try:
            bitstamp_request = self.bitstamp_http.request('GET', self.json_url, timeout=4.0)
            bitstamp_response = bitstamp_request.data.decode('utf8')
            json_dump = json.loads(bitstamp_response)
            bitstamp_request.release_conn()
            return(float(json_dump['last']))
        except:
            return(float(-9999))

def price_watcher(bitcoin_obj, alert_obj, price_limit, su2):
    price_above = True

    # Build interface
    su2.flush_output()
    print(sv_ascii())
    print('Selected threshold: {}'.format(user_input_price_limit))
    print('(Exit: Ctrl + C)\n')

    try:
        while True:
            price = bitcoin_obj.get_price()
            print('Current price: {}'.format(price), end='\r')

            # Check fist for request timeout
            if price == -9999:
                pass
            elif price_above and price < price_limit:
                alert_obj.alert()
                price_above = False
            elif not price_above and price >= price_limit:
                alert_obj.alert()
                price_above = True

            time.sleep(1)

    except KeyboardInterrupt:
        su2.flush_output()
        print('Bye.')

if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Get os of user
    operating_system = name

    # Some tools
    su2 = sysutil2()

    # Start an instance of the alerter. The alter checks if user has the alert
    # sound, and if not downloads it.
    a = alerts(operating_system)

    # Start an instance of a bitcoin price fetcher.
    m = bitcoin()

    # Print current price and get user's desired price threshold
    su2.flush_output()
    print(sv_ascii())
    print('Price of bitcoin: {}'.format(m.get_price()))
    user_input_price_limit = float(input('Enter price threshold: '))
    price_watcher(m, a, user_input_price_limit, su2)
