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
        #this section which actually interacts with api is ai generated
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=[
                    types.Part.from_bytes(data=image_data, mime_type="image/jpeg"),
                    #detailed prompt made by me for accuracy. Also returns previous mistake if one made
                    "Step 1: Count number of questions in this image (look for numbered problems (use ex:1, 2, 3, 1a, 1b, 1c etc when counting)). Step 2: Then estimate number of minutes taken per question. Guidline Time/Q (approximate, DO NOT STRICTLY FOLLOW): simple math problem: 0.5-0.75 mins, moderate math problem: 2-3 mins, hard math problem: 4-5 mins. 1 page of history notes ~10 mins. Use your judgement for difficulty. Step 3: return total time taken as an integer. Fix error from previous response if there is one. IMPORTANT: Respond with ONLY a whole number. NO UNITS, WORDS, SYMBOLS. " + errors
                ]   ,
            #makes it so that only an integer can be sent back
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={"type": "INTEGER"}
            )
        )

        #double check to make sure gemini returned an integer
        if response.text.isdigit():
            minutes = int(response.text)
            break
        else:
            #errors is given to gemini so it can see what was wrong with a previous response
            errors = "Prev response couldn't be converted to integer. Prev response which is invalid: " + response.text
            print(response.text)

    return minutes

def picture():
    global hunger
    minutes = gemini_check()
    hunger += minutes
    if hunger > 30:
        hunger = 30


pygame.init()
screen = pygame.display.set_mode((400,500))
clock = pygame.time.Clock()
running = True

#all the buttons and the coordinates are in a list so code is more compact (x, y, width, height, (color))
buttons = {
    "picture": (15, 410, 177.5, 75, (200,200,200)),
    "stop": (207.5, 410, 177.5, 75, (200,200,200)),
    "pause": (15, 320, 177.5, 75, (200,200,200)),
    "button4": (207.5, 320, 177.5, 75, (200,200,200)),
    "image_loc": (15, 55, 370, 250, (200,200,200)),
    "hunger_bar": (25, 65, 350, 40, (255,255,255))
}
#rects used later in mousebuttondown for click detection
rects = {}
#draws rectangles
def update_ui():
    for key, data in buttons.items():
        x, y, width, height, color = data
        coords = (x, y, width, height)
        rect = pygame.Rect(coords)
        rects[key] = rect
    for key, rectangle in rects.items():
        x, y, w, h, color = buttons[key]
        pygame.draw.rect(screen, color, rectangle)

hunger = 30

while running:
    #required for window to not freeze
    update_ui()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            click_location = event.pos
            action = None
            for key, rectangle in rects.items():
                if rectangle.collidepoint(click_location):
                    action = key
                    break
            #skip rest of code if empty space was clicked
            if action == None: continue
            print("button "+key+" clicked!")


    #actually displays pictures and updated stuff
    pygame.display.flip()
    clock.tick(15)
