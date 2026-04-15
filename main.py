from google import genai
from google.genai import types
import tkinter
import pygame
import time
from tkinter import filedialog
#crashes b/c pygame and tkinter at same time, threading lets them work together

key = "AIzaSyA6B-G3ycGcn_GeJJMSi8nV2M7fAY1Gw1I"
client = genai.Client(api_key=key)

#tkinter is used for filedialog, which allows us to have a user select image from finder/explorer etc
#create a screen to be used and instantly withdraw (hide without quitting)
#dont change order so that this happens later (throws a weird error)
tkinterScreen = tkinter.Tk()
tkinterScreen.withdraw()
def select_image():
    image = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
    return image

#for checking the time it took for person to do their hw
def gemini_check():
    image = select_image()
    if not image: return 0

    #opens the image data to be sent to gemini
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

        #double check to make sure gemini returned an integer, break out of retry loop if returned an int
        if response.text.isdigit():
            minutes = int(response.text)
            break
        else:
            #errors is given to gemini so it can see what was wrong with a previous response
            errors = "Prev response couldn't be converted to integer. Prev response which is invalid: " + response.text
            print(response.text)

    return minutes

def picture():
    print("picture func")
    global hunger
    minutes = gemini_check()
    hunger += minutes
    if hunger > 30:
        hunger = 30

def stop():
    invalid = True
    while invalid:
        close = input("Do you want to close the app y/n: ").lower()
        #if possible make a popup or something so that user doesn't need to type in terminal
        if close == "y":
            invalid = False
            pygame.quit()
        elif close == "n":
            invalid = False
            pass

def pause():
    print("paused")

#store the functions in a dictionary where so that they can be called directly
#from user input as a key rather than if statement (shorter code yay)
functions = {
    "picture": picture,
    "stop": stop,
    "pause": pause
}

pygame.init()
screen = pygame.display.set_mode((400,500))
clock = pygame.time.Clock()
running = True
hunger = 20

#all the buttons and the coordinates are in a list so code is more compact 
#format: (x, y, width, height, (color))
buttons = {
    "picture": (15, 410, 177.5, 75, (200,200,200)),
    "stop": (207.5, 410, 177.5, 75, (200,200,200)),
    "pause": (15, 320, 177.5, 75, (200,200,200)),
    "button4": (207.5, 320, 177.5, 75, (200,200,200)),
    "image_loc": (15, 55, 370, 250, (200,200,200)),
    "hunger_background": (25, 65, 350, 40, (255,255,255)),
    "hunger_bar": (30, 70, 340*(hunger/30), 30, (0,0,0))
}
#rects used later in mousebuttondown for click detection (with keys so no need for if statement)
rects = {}

#refreshes the ui
def update_ui():
    for key, data in buttons.items():
        #unpack data from buttons and create rectangle (not yet drawn)
        x, y, width, height, color = data
        coords = (x, y, width, height)
        rect = pygame.Rect(coords)
        rects[key] = rect
    #draws the rectangles on the screen
    for key, rectangle in rects.items():
        x, y, width, height, color = buttons[key]
        pygame.draw.rect(screen, color, rectangle)

while running:
    #required for window to not freeze
    update_ui()
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            click_location = event.pos
            action = None

            #find which rectangle was clicked (if one was clicked)
            for key, rectangle in rects.items():
                if rectangle.collidepoint(click_location):
                    action = key
                    break

            #skip rest of code if empty space was clicked
            if action == None: continue
            print("button "+key+" clicked!")
            
            #calls necessary function based on key from mouse button input
            if not functions[key]: continue
            functions[key]()

    #actually displays pictures and updated stuff
    pygame.display.flip()
    clock.tick(15)


'''
TO DO:
    Issues:
        1. Hunger bar isn't actively updated, its predefined in buttons 
            Add a section to update_ui so that the width is redefined
        2. the stop() function freezes pygame window (easy bypass of timer)
    Features:
        1. Hunger acc changing, and an actual timer, and a way to lose (dead dog)
        2. Proper ui (placeholders is fine, but make placeholders such that they are
           stored in and accessed from the UISprites folder). Make sure buttons labeled
        3. Have the different images of the dog show up (from DogSprites) based on hunger
        4. Something that happens for button4 (idk what) and rename button4 based on new function
        5. functionality for the pause button
    And last but not least acc testing
'''