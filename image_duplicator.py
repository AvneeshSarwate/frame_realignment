import json
import os
import math
import shutil


FRAMERATE = 24
HOVER_TIME = math.floor(FRAMERATE * 0.5) #number of frames to hover on a key frame

TEST = False

def testGetFiles(DATA_DIR):
    file_names = open(DATA_DIR + "filenames_example.txt").read().split()
    file_names = [fn for fn in file_names if len(fn.strip()) != 0]
    return file_names

def getFiles(DATA_DIR):
    if TEST:
        return testGetFiles()
    else:
        return os.listdir(DATA_DIR)

#frames: list of images, outputNoutput_numberumber - how many images to end up with after duplication/fitlering
def resampleImages(frames, output_number):

    input_number = len(frames)
    step_size = input_number/output_number

    new_frames = []
    for i in range(output_number):
        try:
            new_frames.append(frames[math.floor(step_size*i)])
        except:
            print(input_number, output_number, step_size, i)
            raise Exception("except")

    return new_frames

def make_ts_json(lyrics_json, DATA_DIR):
    jpg_files = [fn for fn in getFiles() if fn.endswith("fin.jpg")]
    with open(lyrics_json, 'r') as ly_j:
        lyrics = json.load(ly_j)
    lyrics.insert(0, {"seconds": 0, "lyrics": "START"})
    kf_dict_all = {}
    kf_dict_all['keyframes'] = []
    for lyric, jpg in zip(lyrics, jpg_files):
        #if lyric == 0:
        #    kf_dict = {'filename': jpg, 'timestamp': 0}
        #    kf_dict_all.append(kf_dict)
        #    continue
        kf_dict ={'filename': jpg, 'timestamp': lyric['seconds']}
        kf_dict_all['keyframes'].append(kf_dict)
    with open(os.path.join(DATA_DIR, 'keyframes.json'), 'w') as ts_json:
        json.dump(kf_dict_all, ts_json)


def runFrameRealignment(DATA_DIR):

    make_ts_json(DATA_DIR + 'lyrics.json', DATA_DIR)

    keyframe_json = json.load(open(DATA_DIR + "keyframes.json"))
    jpg_files = [fn for fn in getFiles() if fn.endswith(".jpg")]

    num_iterations = keyframe_json['number_of_iterations']

    keyframe_files = keyframe_json["keyframes"]

    num_keyframe_ranges = len(keyframe_files) - 1

    new_frames = []

    # duplicate starting key frame
    for i in range(HOVER_TIME):
        new_frames.append('keyframe_0_fin.jpg')

    for frame_num in range(1, num_keyframe_ranges+1):
        
        #duplicate or filter interpolation frames to the desired number for the lyric line duration 
        lyric_duration = keyframe_files[frame_num]["timestamp"] - keyframe_files[frame_num-1]["timestamp"]
        output_number = lyric_duration * FRAMERATE - HOVER_TIME

        #frame_str = str(frame_num).zfill(3) - zfilling to 3 digits
        interpolation_frames = [fn for fn in jpg_files if f"keyframe_{frame_num:03}" in fn and "fin" not in fn]
        
        interpolation_frames = sorted(interpolation_frames)

        resampled_frames = resampleImages(interpolation_frames, output_number)
        new_frames += resampled_frames
            
        # duplicate key frame
        for i in range(HOVER_TIME):
            new_frames.append(f'keyframe_{frame_num:03}_fin.jpg')


    if TEST:

        for i in range(len(new_frames)):
            print(i, new_frames[i])
    else :

        OUTPUT_SUBDIR = DATA_DIR + "output_frame_files"

        os.mkdir(OUTPUT_SUBDIR)

        for i in range(len(new_frames)):
            index_string = str(i).zfill( math.ceil(math.log(len(new_frames), 10) ))
            new_file_name = f"frame_{index_string}.jpg"
            shutil.copyfile(DATA_DIR + new_frames[i], OUTPUT_SUBDIR + "/" + new_file_name)    


    ## ffmpeg command to run on the output directory to generate the video
    #!ffmpeg -r {fps} -pattern_type glob -i "{out_folder + '/*.jpg'}"  -ss 0 -crf 15 -vcodec libx264 -pix_fmt yuv420p {save_path} -hide_banner -loglevel error
    ffmpeg_command = f'ffmpeg -r {FRAMERATE} -pattern_type glob -i "{OUTPUT_SUBDIR + "/*.jpg"}"  -ss 0 -crf 15 -vcodec libx264 -pix_fmt yuv420p {OUTPUT_SUBDIR}/generated_movie.mp4 -hide_banner -loglevel error'
    os.system(ffmpeg_command)