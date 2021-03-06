#!/usr/bin/env python
from moviepy.editor import *
from PIL import Image,ImageDraw,ImageFont
from modules.configHandler import *
import random

class Slide:
    def __init__(self,text="Test",
                size=(1920,1080),
                bgColor=(0,0,0),
                txtColor=(255,255,255),
                file_name=f"slide{random.randrange(1000)}",
                font_name="font",
                fontSize=100,
                customBg=False,
                bgName=None):
        self.text=text                  # Text Displayed in the Slide
        self.size=size                  # Size of the Slide as as a tuple (width,height)  
        self.bgColor=bgColor            # Color of the background  as a tuple (R,G,B)
        self.txtColor=txtColor          # Color of the text as a tuple (R,G,B) 
        self.file_name=file_name        # File name of the Slide file , without extension
        self.font_name = font_name      # Name of the Font file used for the text without the extension,
                                        #   must be in the /res folder and be a ttf file
        self.fontSize = fontSize        # Font size of the text in the Slide
        self.customBg=customBg          # {True|False} Use Custom Background
        self.bgName=bgName              # Name of the image file used as background with the extension, must be in /res folder
        


def getMaxDimension(file_path):
    # Return the max dimension among the video file 
    # in the file_path folder as a tuplet (width,height)
    import cv2
    heights = []
    widths = []
    for name in os.listdir(file_path):
        try:
            vid = cv2.VideoCapture(file_path+"/"+name)
            heights.append(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
            widths.append(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        except:
            continue
    return (int(max(widths)),int(max(heights)))

def getDimension(file_name):
    # Return Width of a video file named file_name contained in the ./Clips folder
    import cv2
    vid = cv2.VideoCapture("./Clips/"+file_name)
    return vid.get(cv2.CAP_PROP_FRAME_WIDTH)

def getMaxFps(file_path):
    # Return the highest fps among the video file contained in the file_path folder
    import cv2
    fps = []
    for name in os.listdir(file_path):
        try:
            vid = cv2.VideoCapture(file_path+"/"+name)
            fps.append(vid.get(cv2.CAP_PROP_FPS))
        except:
            continue
    return int(max(fps))
    
def createTextSlide(slide):
    # Create and save a text slide based on the Slide object that is passed
    assert type(slide) == Slide
    fontSize=int((slide.fontSize/1920)*slide.size[0])
    fnt = ImageFont.truetype(f'./res/{slide.font_name}.ttf', slide.fontSize)
    if slide.customBg:
        tr = Image.open(f"./res/{slide.bgName}")
        if tr.size != slide.size:
            tr = tr.resize(slide.size)
    else:
        tr = Image.new("RGB",slide.size,color=slide.bgColor)
    d = ImageDraw.Draw(tr)
    w,h = d.textsize(slide.text,font=fnt)
    h+= int(h*0.21)
    d.text(((slide.size[0]-w)/2, (slide.size[1]-h)/2),text=slide.text,fill=slide.txtColor,font=fnt)
    tr.save(f"./Clips/{slide.file_name}.png")
    
def createIntro(size,video_fps,numberOfClips,channel,time):
    # Return an intro slide as an ImageSequenceClip  object
    if time == "24h":
        time_period="the day"
    if time == "7d":
        time_period="the week"
    if time=="30d":
        time_period="the month"
    if time == "all":
        time_period="all time"
    createTextSlide(Slide(text=f"Top {numberOfClips} best {channel}'s clips of {time_period}",
                        size=size,
                        file_name=f"intro",
                        font_name=getIntroFontName(),
                        fontSize=getIntroFontSize(),
                        customBg=getIntroCustomBg(),
                        bgName=getIntroBgName()))
    imgList = []
    for s in range(video_fps*getIntroTime()):
        imgList.append('./Clips/intro.png')
    return ImageSequenceClip(imgList,fps=video_fps)

def createTransition(size,video_fps,number):
    # Return an in-clip-transition as an ImageSequenceClip object
    createTextSlide(Slide(text=f"Clip #{number}",
                        size=size,
                        file_name=f"transition{number}",
                        font_name=getRankingFontName(),
                        fontSize=getRankingFontSize(),
                        customBg=getRankingCustomBg(),
                        bgName=getRankingBgName()))
    imgList = []
    for s in range(video_fps*getRankingTime()):
        imgList.append(f'./Clips/transition{number}.png')
    return ImageSequenceClip(imgList,fps=video_fps)

def createOutro(size,video_fps):
    # Return an outro as an ImageSequenceClip object
    createTextSlide(Slide(text=getOutroText(),
                        size=size,
                        file_name="outro",
                        font_name=getOutroFontName(),
                        fontSize=getOutroFontSize(),
                        customBg=getOutroCustomBg(),
                        bgName=getOutroBgName()))
    imgList = []
    for s in range(video_fps*getOutroTime()):
        imgList.append('./Clips/outro.png')
    return ImageSequenceClip(imgList,fps=video_fps)
    

def createVideo(save_path=".",channel=None,time="7d"):

    # Create and save the final video 

    file_name = getOutputTitle()
    numberOfClips = sum([len(files) for r, d, files in os.walk("./Clips")])
    video_size = getMaxDimension("./Clips")
    video_fps = getMaxFps("./Clips")
    clipList =[]
    #---INTRO---
    if getIntro():
        clipList.append(createIntro(video_size,video_fps,numberOfClips,channel,time))

    #---Clips and transitions---
    for i in range(numberOfClips,0,-1):
        if getRankingSlide():
            clipList.append(createTransition(video_size,video_fps,i))
        vid = VideoFileClip(f"./Clips/clip{i}.mp4")
        if getDimension(f"clip{i}.mp4") != video_size[0]:
                vid = vid.resize(width=video_size[0])
        clipList.append(vid)
    
    #---Outro---
    if getOutro():
        clipList.append(createOutro(video_size,video_fps))
    #   Concatenate clips
    final_clip = concatenate_videoclips(clipList)
    final_clip.write_videofile(f"{save_path}/{file_name}.mp4",fps=video_fps)