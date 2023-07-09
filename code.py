
import time
import board
import displayio
import terminalio
import adafruit_imageload
import openweather_graphics 
import json

from digitalio import DigitalInOut, Direction, Pull
from adafruit_display_text.label import Label
from adafruit_display_text.scrolling_label import ScrollingLabel
from adafruit_bitmap_font import bitmap_font
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix

BLINK = False
DEBUG = False

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# --- Display setup ---
matrix = Matrix()
display = matrix.display

network = Network(status_neopixel=board.NEOPIXEL, debug=False)

# ----------------------------------------------------------------------------------------------------------------------------
# Button Inputs
# ----------------------------------------------------------------------------------------------------------------------------

button_down = DigitalInOut(board.BUTTON_DOWN)
button_down.switch_to_input(pull=Pull.UP)

button_up = DigitalInOut(board.BUTTON_UP)
button_up.switch_to_input(pull=Pull.UP)


menu_option = 0

    
# ----------------------------------------------------------------------------------------------------------------------------
# Clock
# ----------------------------------------------------------------------------------------------------------------------------

group_clock = displayio.Group()  # Create a Group

# Create a TileGrid using the Bitmap and Palette
# tile_grid = displayio.TileGrid(bitmap, pixel_shader=color)
# group_clock.append(tile_grid)  # Add the TileGrid to the Group
display.show(group_clock)

font = bitmap_font.load_font("/fonts/IBMPlexMono-Medium-24_jep.bdf")

clock_label = Label(font)

last_check = None
group_clock.append(clock_label)  # add the clock label to the group


def update_time(*, hours=None, minutes=None, show_colon=True, am_color, pm_color):
    now = time.localtime()  # Get the time values we need
    if hours is None:
        hours = now[3]
    if hours < 12:  
        clock_label.color = am_color
    else:
        clock_label.color = pm_color
    if hours > 12:  # Handle times later than 12:59
        hours -= 12
    elif not hours:  # Handle times between 0:00 and 0:59
        hours = 12

    if minutes is None:
        minutes = now[4]

    if BLINK:
        colon = ":" if show_colon or now[5] % 2 else " "
    else:
        colon = ":"

    clock_label.text = "{hours}{colon}{minutes:02d}".format(
        hours=hours, minutes=minutes, colon=colon
    )
    bbx, bby, bbwidth, bbh = clock_label.bounding_box
    # Center the label
    clock_label.x = round(display.width / 2 - bbwidth / 2)
    clock_label.y = display.height // 2

    if DEBUG:
        print("Label bounding box: {},{},{},{}".format(bbx, bby, bbwidth, bbh))
        print("Label x: {} y: {}".format(clock_label.x, clock_label.y))


# ----------------------------------------------------------------------------------------------------------------------------
# Loading
# ----------------------------------------------------------------------------------------------------------------------------

# Create a Group to hold the TileGrid
group_loading = displayio.Group()

loading = Label(terminalio.FONT)
loading.x = int((64 - 6 * len("Loading")) / 2)
loading.y = 15
loading.color = 0x999999
loading.text = "Loading"

# Add the TileGrid to the Group
group_loading.append(loading)


# ----------------------------------------------------------------------------------------------------------------------------
# Error
# ----------------------------------------------------------------------------------------------------------------------------

# Create a Group to hold the TileGrid
group_error = displayio.Group()

error_line1 = Label(terminalio.FONT)
error_line1.x = 5
error_line1.y = 5
error_line1.color = 0xaaaa00
error_line1.text = 'Something'
error_line2 = Label(terminalio.FONT)
error_line2.x = 5
error_line2.y = 15
error_line2.color = 0xaaaa00
error_line2.text = 'is wrong!'
error_line3 = Label(terminalio.FONT)
error_line3.x = 5
error_line3.y = 25
error_line3.color = 0xaaaa00
error_line3.text = 'Text Tiny'
# Add the TileGrid to the Group
group_error.append(error_line1)
group_error.append(error_line2)
group_error.append(error_line3)

# ----------------------------------------------------------------------------------------------------------------------------
# Happy Birthday
# ----------------------------------------------------------------------------------------------------------------------------

bearBmp, palette = adafruit_imageload.load("/images/bear.bmp",
                                          bitmap=displayio.Bitmap,
                                          palette=displayio.Palette)

# Create a TileGrid to hold the bitmap
tile_grid_hb = displayio.TileGrid(bearBmp, pixel_shader=palette)

# Create a Group to hold the TileGrid
group_hb = displayio.Group()


hb_line1 = Label(terminalio.FONT)
hb_line1.x = 33
hb_line1.y = 5
hb_line1.color = 0xFF0000
hb_line1.text = 'Happy'
hb_line2 = Label(terminalio.FONT)
hb_line2.x = 33
hb_line2.y = 16
hb_line2.color = 0x00FF00
hb_line2.text = 'Bear'
hb_line22 = Label(terminalio.FONT)
hb_line22.x = 53
hb_line22.y = 16
hb_line22.color = 0x00FF00
hb_line22.text = 'th'
hb_line3 = Label(terminalio.FONT)
hb_line3.x = 33
hb_line3.y = 25
hb_line3.color = 0x0000FF
hb_line3.text = 'Day:)'


# Add the TileGrid to the Group
group_hb.append(tile_grid_hb)
group_hb.append(hb_line1)
group_hb.append(hb_line2)
group_hb.append(hb_line22)
group_hb.append(hb_line3)

display.show(group_hb)


# ----------------------------------------------------------------------------------------------------------------------------
# Weather App
# ----------------------------------------------------------------------------------------------------------------------------

localtime_refresh = None
weather_refresh = None
weather_unit = 'metric'

gfx = openweather_graphics.OpenWeather_Graphics(
    display, am_pm=True, units=weather_unit
)


while True:
    data = None
    messages = []
    clock_am_color = 0xaaaa00
    clock_pm_color = 0x00aaaa
    weather_unit = "metric"
    weather_location = "New York, US"

    try:
        data = network.fetch_data(secrets["data_location"], json_path=([],))
        data = json.loads(data)
        print (data)
        messages = data["custom_messages"] if "custom_messages" in data else []
    except:
        print ("Something is wrong with data.json file. Cannot load 'custom_messages'")

    try:
        clock_am_color = int(data["clock"]["am_color"])
        clock_pm_color = int(data["clock"]["pm_color"])
    except:
        print ("Cannot load 'clock'")

    try:
        weather_unit = data["weather"]["unit"]
        weather_location = data["weather"]["location"]
    except:
        print ("Cannot load 'weather'")



    # ----------------------------------------------------------------------------------------------------------------------------
    # Overwrite Custom Message
    # ----------------------------------------------------------------------------------------------------------------------------
    if messages is not None and len(messages) > 0:
        try:
            group_custom_message = displayio.Group()
            scrolling_labels = []
            for message in messages:
                print (message)
                if message["type"] == "label":
                    custom_message_line = Label(terminalio.FONT)
                    custom_message_line.x = int((64 - 6 * len(message["text"])) / 2) if "x" not in message else message["x"]
                    custom_message_line.y = message["y"]
                    custom_message_line.color = int(message["color"], 16)
                    custom_message_line.text = message["text"]
                    group_custom_message.append(custom_message_line)
                elif message["type"] == "scrolling_label":
                    animate_time = 0.3 if "animate_time" not in message else message["animate_time"]
                    custom_message_line = ScrollingLabel(terminalio.FONT, text=message["text"], max_characters=10, animate_time=animate_time)
                    custom_message_line.x = 3 if "x" not in message else message["x"]
                    custom_message_line.y = message["y"]
                    custom_message_line.color = int(message["color"], 16)
                    group_custom_message.append(custom_message_line)
                    scrolling_labels.append(custom_message_line)
                elif message["type"] == "bmp":
                    bmp, palette = adafruit_imageload.load(message["text"],
                                              bitmap=displayio.Bitmap,
                                              palette=displayio.Palette)
                    tile_grid_bmp = displayio.TileGrid(bmp, pixel_shader=palette)
                    tile_grid_bmp.x = message["x"]
                    tile_grid_bmp.y = message["y"]
                    group_custom_message.append(tile_grid_bmp)
                

            display.show(group_custom_message)
            if len(scrolling_labels) == 0:
                time.sleep(60) 
            else:
                last_check = time.monotonic()
                while time.monotonic() < last_check + 60:
                    for scrolling_label in scrolling_labels:
                        scrolling_label.update()

            weather_refresh = None
        except:
            print("Something is wrong with data.json file.")
            display.show(group_error)
            time.sleep(60)
            messages = []


    # ----------------------------------------------------------------------------------------------------------------------------
    # Clock
    # ----------------------------------------------------------------------------------------------------------------------------
    elif menu_option == 0:
        if last_check is None or time.monotonic() > last_check + 3600:
            try:
                update_time(am_color=clock_am_color,pm_color=clock_pm_color)  
                network.get_local_time()  # Synchronize Board's clock to Internet
                last_check = time.monotonic()
                
            except RuntimeError as e:
                print("Some error occured, retrying! -", e)
                display.show(group_error)
                time.sleep(5)

        display.show(group_clock)
        update_time(am_color=clock_am_color,pm_color=clock_pm_color)
        time.sleep(5)

        # localtime_refresh = None
        weather_refresh = None
      

    # ----------------------------------------------------------------------------------------------------------------------------
    # Weather App
    # ----------------------------------------------------------------------------------------------------------------------------
    elif menu_option == 1:
        # Use cityname, country code where countrycode is ISO3166 format.
        # E.g. "New York, US" or "London, GB"
        print("Getting weather for {}".format(weather_location))
        # Set up from where we'll be fetching data
        DATA_SOURCE = "http://api.openweathermap.org/data/2.5/weather?q=" + weather_location + "&units=" + weather_unit
        DATA_SOURCE += "&appid=" + secrets["openweather_token"]
        # You'll need to get a token from openweather.org, looks like 'b6907d289e10d714a6e88b30761fae22'
        # it goes in your secrets.py file on a line such as:
        # 'openweather_token' : 'your_big_humongous_gigantor_token',
        DATA_LOCATION = []
        SCROLL_HOLD_TIME = 0  # set this to hold each line before finishing scroll

        gfx.set_units(weather_unit)

        if (not localtime_refresh) or (time.monotonic() - localtime_refresh) > 3600:
            try:
                network.get_local_time()
                localtime_refresh = time.monotonic()
            except RuntimeError as e:
                print("Some error occured, retrying! -", e)
                display.show(group_error)
                time.sleep(5)

        # only query the weather every 10 minutes (and on first run)
        if (not weather_refresh) or (time.monotonic() - weather_refresh) > 600:
            try:
                value = network.fetch_data(DATA_SOURCE, json_path=(DATA_LOCATION,))
                print("Response is", value)
                gfx.display_weather(value)
                weather_refresh = time.monotonic()
            except RuntimeError as e:
                print("Some error occured, retrying! -", e)
                display.show(group_error)


        gfx.scroll_next_label()
        # Pause between labels
        time.sleep(SCROLL_HOLD_TIME)


    if not button_down.value:
        display.show(group_loading)
        menu_option = abs(menu_option - 1) % 2
    elif not button_up.value:
        display.show(group_loading)
        menu_option = abs(menu_option + 1) % 2

