import moviepy.editor as mp

def main():
    pass

def compileMov(name, clipsInfo):
    # vidName='/Users/swoolf/GitHub/SoccerHighlights/cv/Videos/180517_v2.MP4'
    clips=[]
    for clipI in clipsInfo:
        vidName=clipI[0]
        dur = int(mp.VideoFileClip(vidName).duration)
        Tstart = clipI[1] - 5 if clipI[1]>=5 else 0
        Tend = clipI[1] + 3 if dur >=clipI[1]+3 else dur
        clips.append(mp.VideoFileClip(vidName).subclip( Tstart , Tend ) )
    concat_clip = mp.concatenate_videoclips(clips, method="compose")
    concat_clip.write_videofile(name)

if __name__ == '__main__':
    main()
