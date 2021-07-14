import argparse
import os

# get the audio from a given YouTube URL, uses song name to name the file
def get_audio(url, song_name):
    command1 = f'youtube-dl -f 140 --output {song_name}-raw.m4a \"{url}\"'
    os.system(command1)
    command2 = f'ffmpeg -i {song_name}-raw.m4a -vn -c:a copy {song_name}.m4a'
    os.system(command2)
    os.system(f'rm {song_name}-raw.m4a')

# merge a video file with the audio for a song (song name acts as unique identifier), assumes get_audio() was called
def merge(video_file, song_name, output_file):
    command3 = f'ffmpeg -i {video_file} -i {song_name}.m4a -c:v copy -c:a aac {output_file} -shortest'
    os.system(command3)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, help='url of video on youtube')
    parser.add_argument('--song_name', type=str, help='name of song')
    parser.add_argument('--video_file', type=str, help='name of video file')
    parser.add_argument('--output_file', type=str, help='final output filename (audio and video)')
    args = parser.parse_args()

    get_audio(args.url, args.song_name)
    merge(args.video_file, args.song_name, args.output_file)

