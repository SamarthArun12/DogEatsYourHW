from google import genai
from google.genai import types
import pygame
import time
import tkinter
from tkinter import filedialog

key = "AIzaSyA6B-G3ycGcn_GeJJMSi8nV2M7fAY1Gw1I"
client = genai.Client(api_key=key)

#for image selecting
def select_image():
    #creates a temp screen(req for filedialog)
    temp = tkinter.Tk()
    temp.withdraw()
    image = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
    temp.destroy()
    return image

#for checking the time it took for person to do their hw
def gemini_check():
    image = select_image()

    with open(image, "rb") as file:
        image_data = file.read()

    errors = "None"

    #keeps on asking gemini until returned a valid response
    while True:
        #next 7 lines of code ai generated (prompt made by me however)
        response = client.models.generate_content(
    model="gemini-3.1-flash-lite-preview",
    contents=[
            types.Part.from_bytes(data=image_data, mime_type="image/jpeg"),
            #cool detailed prompt for increased consistency and accuracy, also gives gemini previous response which errored.
            "Step 1: Count number of questions in this image (look for numbered problems (use ex:1, 2, 3, 1a, 1b, 1c etc when counting)). Step 2: Then estimate number of minutes taken per question. Guidline Time/Q (approximate, DO NOT STRICTLY FOLLOW): simple math problem: 0.5-0.75 mins, moderate math problem: 2-3 mins, hard math problem: 4-5 mins. 1 page of history notes ~10 mins. Use your judgement for difficulty. Step 3: return total time taken as an integer. Fix error from previous response if there is one. IMPORTANT: Respond with ONLY a whole number. NO UNITS, WORDS, SYMBOLS. " + errors
        ]   ,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema={"type": "INTEGER"}
    )
)

        #if gemini's response isn't an integer, try again
        if response.text.isdigit():
            minutes = int(response.text)
            break
        else:
            #errors is given to gemini so it can see what was wrong with a previous response
            errors = "Prev response couldn't be converted to integer. Prev response which is invalid: " + response.text
            print(response.text)
    return minutes



pygame.init()
screen = pygame.display.set_mode((400,500))
clock = pygame.time.Clock()
running = True

hunger = 100

#just placeholder names btw
picture_button = pygame.Rect(15, 410, 177.5, 75)
pygame.draw.rect(screen, (200, 200, 200), picture_button)

#bottom right
button2 = pygame.Rect(207.5, 410, 177.5, 75)
pygame.draw.rect(screen, (200, 200, 200), button2)

#top left
button3 = pygame.Rect(15, 320, 177.5, 75)
pygame.draw.rect(screen, (200, 200, 200), button3)

#top right
button4 = pygame.Rect(207.5, 320, 177.5, 75)
pygame.draw.rect(screen, (200, 200, 200), button4)

#where the image shud be
image_loc = pygame.Rect(15, 55, 370, 250)
pygame.draw.rect(screen, (200, 200, 200), image_loc)

while running:
    #required for window to not freeze
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #no acc functionality as of yet js displays the rects
    pygame.display.flip()
    clock.tick(15)
