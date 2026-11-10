"""Turn a recorded frame folder into a 1280x880 clip with a caption bar on top.
usage: python render.py <recdir> <out.mp4> [phone]"""
import json, subprocess, sys
rec, out = sys.argv[1], sys.argv[2]
phone = len(sys.argv) > 3
FONT = "/usr/share/fonts/liberation/LiberationSans-Bold.ttf"
marks = json.load(open(f"{rec}/marks.json"))["marks"]
dur = sum(float(l.split()[1]) for l in open(f"{rec}/list.txt") if l.startswith("duration"))
filters = ["fps=30"]  # duplicate frames first, so captions switch on time
if phone:
    # phone frames are 780x1688 (2x); show at 370 wide, centred on the 1280x800 stage
    filters.append("scale=370:-2,pad=1280:800:(ow-iw)/2:(oh-ih)/2:color=0x2a2f34")
else:
    filters.append("scale=1280:800")
filters.append("pad=1280:880:0:80:color=0x14171a")
for i, (t, cap) in enumerate(marks):
    end = marks[i + 1][0] if i + 1 < len(marks) else dur + 1
    cap = cap.replace(":", r"\:").replace("'", "’").replace(",", r"\,")
    filters.append(f"drawtext=fontfile={FONT}:text='{cap}':fontcolor=white:fontsize=30:x=32:y=24:enable='between(t,{t:.2f},{end:.2f})'")
filters.append("drawbox=x=0:y=0:w=10:h=80:color=0xf2b400:t=fill")
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{rec}/list.txt",
                "-vf", ",".join(filters) + ",format=yuv420p", "-c:v", "libx264", "-crf", "22",
                "-preset", "medium", out], check=True)
