from geminiClient import GeminiClient
from textToSpeech import TextToSpeech
from videoGenerator import VideoProcessor
from youtubeUploader import YouTubeUploader
from dotenv import load_dotenv
from datetime import datetime

import os
import time
import random

audioOutputFileName = "output.mp3"
finalOutputFileName = "finalOutput.mp4"
redditTemplateVideos = ["minecraft.mp4", "gta.mp4", "surfers.mp4"]
subreddits = ["unsolved mysteries", "true crime", "scary stories", "reddit stories", "karma stories", "today I fucked up", "am I the asshole"]
tags = {
    "unsolved mysteries": ["mystery", "unsolved mysteries", "creepy", "paranormal", "true crime", "conspiracy", "unexplained", "spooky", "intrigue", "cold case"],
    "true crime": ["true crime", "crime", "murder", "investigation", "serial killer", "mystery", "forensic", "crime documentary", "justice", "criminal"],
    "scary stories": ["scary stories", "horror", "creepy", "ghost stories", "paranormal", "spooky", "terrifying", "haunted", "supernatural", "chilling"],
    "reddit stories": ["reddit stories", "reddit", "storytime", "tales", "rslash", "askreddit", "funny stories", "drama", "anecdotes", "social media"],
    "karma stories": ["karma stories", "karma", "wholesome", "feel good", "justice served", "payback", "revenge stories", "uplifting", "satisfying", "life lessons"],
    "today I fucked up": ["TIFU", "funny fails", "oops", "embarrassing", "funny stories", "reddit TIFU", "mistakes", "hilarious", "cringe", "comedy"],
    "am I the asshole": ["AITA", "am I the asshole", "relationships", "judgment", "reddit AITA", "drama", "morality", "ethics", "social dilemmas", "conflict"]
}
descriptions = {
    "unsolved mysteries": "Explore the unknown and the eerie with gripping tales of unsolved cases and bizarre events that defy explanation. From mysterious disappearances to paranormal encounters, dive into the world of the unexplained. #mystery #unsolvedmysteries #creepy #paranormal #truecrime #conspiracy #unexplained #spooky #intrigue #coldcase",
    "true crime": "Delve into real-life criminal cases that shock and captivate. From infamous murders to chilling investigations, uncover the dark details behind the headlines. #truecrime #crime #murder #investigation #serialkiller #mystery #forensic #crimedocumentary #justice #criminal",
    "scary stories": "Get ready for spine-chilling tales that will keep you up at night. From ghostly encounters to supernatural horrors, these stories are guaranteed to send shivers down your spine. #scarystories #horror #creepy #ghoststories #paranormal #spooky #terrifying #haunted #supernatural #chilling",
    "reddit stories": "Discover intriguing stories from Reddit that range from hilarious to heartwarming to downright bizarre. Join us as we dive into the best tales from the internet’s most vibrant communities. #redditstories #reddit #storytime #tales #rslash #askreddit #funnystories #drama #anecdotes #socialmedia",
    "karma stories": "Enjoy uplifting tales of justice where good deeds are rewarded and wrongdoers get their comeuppance. These satisfying stories of karma will leave you feeling inspired. #karmastories #karma #wholesome #feelgood #justiceserved #payback #revengestories #uplifting #satisfying #lifelessons",
    "today I fucked up": "Laugh at relatable fails and oops moments that make you glad it wasn’t you. From embarrassing blunders to hilarious mishaps, these stories are pure comedy gold. #TIFU #funnyfails #oops #embarrassing #funnystories #redditTIFU #mistakes #hilarious #cringe #comedy",
    "am I the asshole": "Engage in moral dilemmas and judgments with stories that spark debate. Are they in the wrong, or is it someone else? Dive into the drama and decide for yourself. #AITA #amItheasshole #relationships #judgment #redditAITA #drama #morality #ethics #socialdilemmas #conflict"
}
playlistIds = {
    "unsolved mysteries": "PLgcw4jDW3kqNlxGZ9wlqRegZMgPTiol8j",
    "true crime": "PLgcw4jDW3kqOCYVw9kD-iOVZxBZOCYcTX",
    "scary stories": "PLgcw4jDW3kqPDQ6bXWb1u5yaw390jXjqe",
    "reddit stories": "PLgcw4jDW3kqP8Od8Kw6ZyO9aXpZWSpvG-",
    "karma stories": "PLgcw4jDW3kqPfssSGnSvxFkjQJJsnPZO9",
    "today I fucked up": "PLgcw4jDW3kqMKGKi7bMIZFBXYmvmOX7dL",
    "am I the asshole": "PLgcw4jDW3kqOJB9q5jedDhDFi3DmFcv4k"
}


def main():
    startTime = time.time()
    load_dotenv()
    API_KEY = os.getenv("GEMINI_API_KEY")
    gemini = GeminiClient(API_KEY)

    question = os.getenv("GEMINI_QUESTION_PROMPT")
    subreddit = random.choice(subreddits)
    question = question.replace("{subreddit}", subreddit)
    answer = gemini.query(question)

    redditQuestion = answer.split("~")[1].strip()
    story = answer.split("~")[2].strip()
    print("redditQuestion: ", redditQuestion)
    print("story: ", story)

    textToSpeech = TextToSpeech(
        voice_sample="voiceSample2.wav",
        exaggeration=0.6,
        cfg_weight=0.3
    )
    textToSpeech.synthesize(story, audioOutputFileName, speed = 1)

    redditTemplateVideo = random.choice(redditTemplateVideos)
    processor = VideoProcessor(redditTemplateVideo, audioOutputFileName, finalOutputFileName, redditQuestion)
    processor.process_video(random_start=True)
    
    uploader = YouTubeUploader(env_file = ".env", video_file = finalOutputFileName)
    uploader.authenticate()
    response = uploader.upload_video(
        title = redditQuestion + " #" + str(random.randint(0, 999)),
        description = descriptions[subreddit],
        tags = tags[subreddit],
        category_id = "22",
        privacy_status = "public",
        playlist_id = playlistIds[subreddit]
    )
    if response:
        print(f"Video uploaded with ID: {response.get('id')}")

    endTime = time.time()
    print(f"Execution time: {endTime - startTime} seconds")
    now = datetime.now()
    formatted = now.strftime("%Y-%m-%d %H:%M:%S")
    with open("lastExecuted.txt", "a", encoding="utf-8") as f:
        print(f"Last Executed to Completion: {formatted}, Execution Time: {endTime - startTime} seconds", file=f)
    exit()

if __name__ == "__main__":
    main()