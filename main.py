#if u dont got these libraries, download em
from google import genai
from google.genai import types
import tkinter
import pygame
from tkinter import filedialog
import random
from PIL import Image

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
    if hunger > maxHunger:
        hunger = maxHunger

def stop():
    '''    
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
    '''
    global running
    font_large = pygame.font.SysFont(None, 36)
    confirming = True

    while confirming:
        screen.fill((50, 50, 50))

        # Draw prompt text
        text = font_large.render("Quit the app?", True, (255, 255, 255))
        screen.blit(text, (400//2 - text.get_width()//2, 200))

        # YES button
        yes_rect = pygame.Rect(60, 270, 110, 50)
        pygame.draw.rect(screen, (220, 80, 80), yes_rect)
        yes_text = font_large.render("YES", True, (255, 255, 255))
        screen.blit(yes_text, (yes_rect.x + (yes_rect.width - yes_text.get_width())//2, yes_rect.y + 12))

        # NO button
        no_rect = pygame.Rect(230, 270, 110, 50)
        pygame.draw.rect(screen, (100, 180, 100), no_rect)
        no_text = font_large.render("NO", True, (255, 255, 255))
        screen.blit(no_text, (no_rect.x + (no_rect.width - no_text.get_width())//2, no_rect.y + 12))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                confirming = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if yes_rect.collidepoint(event.pos):
                    running = False
                    confirming = False
                elif no_rect.collidepoint(event.pos):
                    confirming = False  # go back to game

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
font = pygame.font.SysFont(None, 32)
running = True
hunger = 180
maxHunger = 180
#very fast for testing purposes, default should be 10,000
hungerRate = 10000
targetTime = pygame.time.get_ticks() + hungerRate
currentImage = None

#all the buttons and the coordinates are in a list so code is more compact 
#format: (x, y, width, height, (color))
buttons = {
    "picture":          (15,    410, 177.5, 75, (100, 180, 100)),  # green  - submit homework
    "stop":             (207.5, 410, 177.5, 75, (220, 80,  80)),   # red    - quit
    "pause":            (15,    320, 177.5, 75, (100, 140, 220)),   # blue   - pause
    "button4":          (207.5, 320, 177.5, 75, (200, 200, 200)),   # grey   - unknown
    #"image_loc":       (15,    55,  370,   250, (230, 230, 230)),  # light grey - dog display area
    "hunger_background":(25,    65,  350,   40,  (47, 54, 153)),  # dark blue
    "hunger_bar":       (30,    70,  340*(hunger/maxHunger), 30, (0, 183, 239)) # light blue hunger bar
}
#rects used later in mousebuttondown for click detection (with keys so no need for if statement)
rects = {}
file_names = {
    "Full": {
        "hungerRange": [120, 180],
        "FileNames": [
            "happy.jpg", "happy2.jpg", 
            "sleeping.png", "sleeping2.png", "sleeping3.png"
        ]
    },
    "Neutral": {
        "hungerRange": [60, 120],
        "FileNames": [
            "neutral.png", "neutral2.png", 
            "sleeping4.png", "sleeping6.png"
        ]
    },
    "Hungry": {
        "hungerRange": [0, 60],
        "FileNames": [
            "hungry.jpg", "hungry2.png", "hungry3.png", 
            "hungry4.png", "hungry5.png", "leaving.png"
        ]
    },
    "Dead": {
        "FileNames": ["sleeping5.png"]
    },
    "Eating": {
        "FileNames": [
            "eating.jpg", "eating2.png", "eating3.png", "icky.png"
        ]
    },
    "UISprites":{
        #width, height for scaling
        "FileNames": {
            "pause.png":(), 
            "stop.png": (),
            "picture.png": (), 
            "background.png": (),
            "hungerbar.png": ()
        }
    }
}
#preload all images so no lag later
images = {
    "Full":[],
    "Neutral":[],
    "Hungry":[],
    "Dead": [],
    "Eating":[],
    "UISprites": []
}
for key, data in file_names.items():
    for fileName in data["FileNames"]:
        #ai generated pillow -> pygame
        pil_img = Image.open("Images/"+fileName)
        mode = pil_img.mode
        size = pil_img.size
        data_str = pil_img.tobytes()
        pygame_surface = pygame.image.fromstring(data_str, size, mode)
        #later figure something out so that images don't get warped
        if key == "UISprites":
            pygame_surface = pygame.transform.scale(pygame_surface, (177.5, 75))
        else:
            pygame_surface = pygame.transform.scale(pygame_surface, (370, 250))

        images[key].append(pygame_surface)

def change_dog_state():
    global currentImage
    for state in file_names:
        if state == "Eating" or state == "Dead": continue
        min, max = file_names[state]["hungerRange"]
        if min > hunger or max < hunger: continue
        break

    if state == "Eating": state = "Dead"
    relevantImages = images[state]

    selectedImage = random.choice(relevantImages)
    return selectedImage

def update_ui():
    screen.fill((0,183,239))
    buttons["hunger_bar"] = (30, 70, 340 * (hunger / maxHunger), 30, (0, 183, 239))
    selectedImage = change_dog_state()
    screen.blit(selectedImage, (15,55))

    for key, data in buttons.items():
        x, y, width, height, color = data
        rect = pygame.Rect((x, y, width, height))
        rects[key] = rect

    for key, rectangle in rects.items():
        x, y, width, height, color = buttons[key]
        pygame.draw.rect(screen, color, rectangle)

    # Button labels
    labels = {
        "picture": ("Submit HW", (0, 0, 0)),
        "stop":    ("Quit",      (180, 0, 0)),
        "pause":   ("Pause",     (0, 0, 0)),
        "button4": ("?",         (0, 0, 0)),
    }

    for key, (label, color) in labels.items():
        if key not in rects: continue
        rect = rects[key]
        text_surface = font.render(label, True, color)
        # Center the text inside the button
        text_x = rect.x + (rect.width - text_surface.get_width()) // 2
        text_y = rect.y + (rect.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))

    # "Hunger" label above the bar
    hunger_label = font.render("Hunger", True, (0, 0, 0))
    screen.blit(hunger_label, (25, 40))


while running:

    currentTime = pygame.time.get_ticks()
    if currentTime > targetTime:
        hunger -= 1
        targetTime = currentTime + hungerRate

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
            if action not in functions: continue
            functions[action]()


    #actually displays pictures and updated stuff
    pygame.display.flip()
    clock.tick(60)


'''
TO DO:
    Issues:
        1. the stop() function freezes pygame window (easy bypass of timer)
    Features:
        1. A way to lose (dead dog)
        2. Proper ui (placeholders is fine, but make placeholders such that they are
           stored in and accessed from the UISprites folder).
        3. Have the different images of the dog show up (from DogSprites) based on hunger
        4. Something that happens for button4 (idk what) and rename button4 based on new function
        5. functionality for the pause button
    And last but not least acc testing
'''