
# Cut out clips from a video given a text file with times (durations to remove).
#
# An input example:
#
# 0.0-12.20
# 14.28-15.58
# 53.25-53.31
# 54.47-99.9

# Normalize audio beforehand with:
#   ffmpeg-normalize a.mp4 -o a.mp4 -c:a mp3 -f
#   https://github.com/slhck/ffmpeg-normalize
#   (see normalize_audio.bat)

import sys, re, os
import datetime

sys.path.append( r'c:\prj\python\\' )
from text_color import *

# one file at the time
base = "video_file"

##############

# expected input
fin = base + ".mp4"
fname = base + ".remove.txt"

def main():
    with open(fname) as f: 
        lines = f.readlines()
    #print(lines)

    print("Durations to remove:")
    times = ["00:00:00.000"]
    bAppend_last = 1
    #for line in sys.stdin:
    for line in lines:
        line = line.rstrip()
        if len(line) == 0:
            continue
            
        reg = re.compile('(\d+)\.(\d+)-(\d+)\.(\d+)')
        m = reg.match(line)
        if not m:
            print("Couldn't find pattern:", line)
            return

        m0, s0, m1, s1 = [int(m.group(i+1)) for i in range(4)]
        if ( m1 > 70 ):
            bAppend_last = 0
        t0 = "%02d:%02d:%02d.000" % (m0 / 60, m0 % 60, s0 % 60)
        t1 = "%02d:%02d:%02d.000" % (m1 / 60, m1 % 60, s1 % 60)
        print(t0, "...", t1)
        times.extend([t0, t1])
    # append last
    if bAppend_last:
        times.append("10:00:00.000")
    
    print( "times:\n", times )
    #return
    
    print(">> \nDurations:")
    fclip = open("clip_list.txt", "w")
    for i in range( len(times)//2 ):
        t0 = times[2*i]
        t1 = times[2*i+1]
        fout = "clip%02d.mp4" % i
        dur = datetime.datetime.strptime(t1[:8], "%H:%M:%S") - datetime.datetime.strptime(t0[:8], "%H:%M:%S")
        dur = dur.total_seconds()
        emphasize("\n>>", fout, t0, "...", t1, "%dsec" % dur)
        if dur < 2:
            print( 'skipped' )
            continue
        fclip.write( "file " + fout + "\n" )
        
        # copy is cleaner but may have precision issues with keyframes
        cmd = "ffmpeg -y -ss %s -i %s -t %d %s" % (t0, fin, dur, fout)
        #cmd = "ffmpeg -y -ss %s -i %s -t %d -c copy %s" % (t0, fin, dur, fout)
        
        emphasize(">>", cmd, '\n')
        os.system( cmd )
    fclip.close()

    print("\n>> Concatenate:")
    os.makedirs( 'out', exist_ok=True )
    cmd = f"ffmpeg -y -f concat -i clip_list.txt -c copy out/{base}.mp4"
    print(">>", cmd)
    os.system( cmd )
        
if __name__ == "__main__":
    main()
