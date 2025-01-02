import os
import re
from random import randint
import requests
from requests import get
from json import loads
from PIL import Image, ImageDraw, ImageFont
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def clean_response_text(text):
    text = re.sub(r'\\', '', text)
    return text

# Function to wrap text
def wrap_text(draw, text, font, max_width):
    lines = []
    words = text.split()
    while words:
        line = ''
        while words and draw.textbbox((0, 0), line + words[0], font=font)[2] <= max_width:
            line = line + (words.pop(0) + ' ')
        lines.append(line)
    return lines

# Fetch a random quote from the Forismatic API
quote_data = {}
while True:
    try:
        response = get('http://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en')
        clean_text = clean_response_text(response.text)
        quote_data = loads(clean_text)
        if 'quoteText' in quote_data and 'quoteAuthor' in quote_data:
            break
    except Exception as e:
        print(f"Error fetching quote: {e}")

quote_text = quote_data['quoteText']
quote_author = quote_data['quoteAuthor']
text = f"{quote_text} - {quote_author}"

# Select and blend two random background images
x1 = randint(1, 9)
bg_path1 = os.path.join(os.getcwd(), "BG", f"{x1}.png")
x2 = randint(1, 9)
bg_path2 = os.path.join(os.getcwd(), "BG", f"{x2}.png")
im1 = Image.open(bg_path1).convert("RGBA")
im2 = Image.open(bg_path2).convert("RGBA")
alpha = randint(0, 10) / 10
post = Image.blend(im1, im2, alpha)
post = post.convert("RGBA")

draw = ImageDraw.Draw(post)

# List of fonts to choose from
fontlist = [
    "Montserrat-Black.ttf", "Montserrat-BlackItalic.ttf", "Montserrat-Bold.ttf", "Montserrat-BoldItalic.ttf",
    "Montserrat-ExtraBold.ttf", "Montserrat-ExtraBoldItalic.ttf", "Montserrat-ExtraLight.ttf",
    "Montserrat-ExtraLightItalic.ttf", "Montserrat-Italic.ttf", "Montserrat-Light.ttf", "Montserrat-LightItalic.ttf",
    "Montserrat-Medium.ttf", "Montserrat-MediumItalic.ttf", "Montserrat-Regular.ttf", "Montserrat-SemiBold.ttf",
    "Montserrat-SemiBoldItalic.ttf", "Montserrat-Thin.ttf", "Montserrat-ThinItalic.ttf"
]

# Draw the signing name at the bottom
fontnumber = randint(0, 17)
fontname = fontlist[fontnumber]
font = ImageFont.truetype(os.path.join(os.getcwd(), "Font", fontname), 30)
signing_name = "QuoteEnlighten"  # Replace with the actual signing name
draw.text((760, 1000), signing_name, (50, 50, 50), font=font)

# Draw the quote text in the center
fontnumber2 = randint(0, 17)
fontname2 = fontlist[fontnumber2]
font = ImageFont.truetype(os.path.join(os.getcwd(), "Font", fontname2), 70)
max_width = 1000  # Set a max width for the text

wrapped_text = wrap_text(draw, text, font, max_width)
line_height = draw.textbbox((0, 0), 'hg', font=font)[3] - draw.textbbox((0, 0), 'hg', font=font)[1]
total_height = line_height * len(wrapped_text)

# Calculate position
W, H = post.size
y = (H - total_height) // 2

for line in wrapped_text:
    bbox = draw.textbbox((0, 0), line, font=font)
    w = bbox[2] - bbox[0]
    x = (W - w) // 2
    draw.text((x, y), line, (30, 30, 30), font=font)
    y += line_height

# Save the final image
output_path = os.path.join(os.getcwd(), "Post", "post.png")
post.save(output_path)


access_token = "EAAWuCPnPZAZA4BO8zpeMi0xZAMMEqXPHpmbmDC9oEqXuI1SW6AC9zlo5pANW1SoGzcQCq9u6JhCu3OW81L3WCWlRXjhGm5oQZCpVQZAeszdcdZBuKlZBtd2IWke95TPoZC8F63qNYxp08vuRU9ZAqQSZABbXbBMmqbNZCt6ie6nEulZAO3QHH5rVqnwZBx67tHfEMtIowkWuqthVo1dYHdmvvZCbZAs6ZBEmwzA6WF6tvAZDZD"  # Replace with your actual access token
page_id = "332087273320790"  # Replace with your actual page ID

# Post the image to Facebook
def post_to_facebook(image_path, message, access_token, page_id):
    url = f"https://graph.facebook.com/{page_id}/photos"
    payload = {
        "message": message,
        "access_token": access_token
    }
    files = {
        "source": open(image_path, "rb")
    }
    response = requests.post(url, data=payload, files=files)
    return response.json()

message = f"{quote_text}\n\n- {quote_author}"

response = post_to_facebook(output_path, message, access_token, page_id)
print(response)

def send_email(subject, body, to_email, from_email, smtp_server, smtp_port, login, password, image_path):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    text = MIMEText(body)
    msg.attach(text)

    with open(image_path, 'rb') as f:
        img = MIMEImage(f.read())
        img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path))
        msg.attach(img)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(login, password)
        server.sendmail(from_email, to_email, msg.as_string())

# Email configuration
subject = quote_text
body = quote_text
to_email = os.environ['TO_EMAIL']
from_email = os.environ['FROM_EMAIL']
smtp_server = os.environ['SMTP_SERVER']
smtp_port = int(os.environ['SMTP_PORT'])
login = os.environ['EMAIL_LOGIN']
password = os.environ['EMAIL_PASSWORD']

# Send the email
send_email(subject, body, to_email, from_email, smtp_server, smtp_port, login, password, output_path)
