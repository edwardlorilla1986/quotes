import os
import re
import subprocess
from random import randint
import requests
from requests import get
from json import loads
from PIL import Image, ImageDraw, ImageFont
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

print(os.environ['TO_EMAIL'], "os.environ['TO_EMAIL']")
def ensure_model_available(model_name="llama3"):
    """Ensure the model[
        "Researchers", "Data Scientists", "Common People", "Students", "Entrepreneurs",
        "Marketers", "Tech Enthusiasts", "Environmentalists", "Educators", "Healthcare Professionals",
        "Investors", "Content Creators", "Policy Makers", "Journalists", "Travel Enthusiasts",
        "Parents", "Artists", "Fitness Enthusiasts", "Engineers", "Historians",
        "Teachers", "Developers", "Startup Founders", "Writers", "Bloggers",
        "Gamers", "Environmental Activists", "Social Workers", "Consultants", "Small Business Owners",
        "Public Speakers", "Podcasters", "Psychologists", "Sociologists", "Economists",
        "Architects", "Designers", "Photographers", "Lawyers", "Accountants",
        "Athletes", "Personal Trainers", "Chefs", "Food Critics", "Fashion Designers",
        "Musicians", "Film Makers", "Storytellers", "Book Lovers", "Minimalists",
        "Philosophers", "Technologists", "AI Enthusiasts", "Robotics Experts", "Urban Planners",
        "Astronomers", "Mathematicians", "Physicists", "Chemists", "Biologists",
        "Medical Researchers", "Veterinarians", "Farmers", "Futurists", "Cryptocurrency Enthusiasts",
        "HR Professionals", "Recruiters", "Sales Experts", "E-commerce Entrepreneurs", "Digital Nomads",
        "Remote Workers", "Mental Health Advocates", "Mindfulness Coaches", "Public Relations Experts", "Event Planners",
        "Adventure Seekers", "Wildlife Conservationists", "Marine Biologists", "Astronauts", "Space Enthusiasts",
        "DIY Hobbyists", "Car Enthusiasts", "Pet Owners", "Nature Photographers", "Gardeners",
        "Home Decorators", "Interior Designers", "Outdoor Enthusiasts", "Sports Fans", "Social Media Influencers",
        "YouTubers", "Film Critics", "Comedians", "Lifestyle Bloggers", "Relationship Coaches",
        "Spiritual Guides", "Religious Leaders", "Ethicists", "Activists", "Human Rights Advocates",
        "Policy Analysts", "Data Analysts", "Startup Mentors", "Cultural Historians", "Linguists"
    ] is available locally or pull it if missing."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if model_name not in result.stdout:
            print(f"Model {model_name} not found locally. Attempting to pull...")
            pull_result = subprocess.run(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if pull_result.returncode != 0:
                raise Exception(f"Error pulling model: {pull_result.stderr.strip()}")
            print(f"Model {model_name} pulled successfully.")
        else:
            print(f"Model {model_name} is already available locally.")
    except Exception as e:
        raise Exception(f"Error ensuring model availability: {e}")

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


def explain_quote_with_ollama(quote, model_name="llama3"):
    ensure_model_available()
    prompt = (
        f"You are a professional writer creating a blog post about inspirational quotes. "
        f"Write a detailed blog post analyzing the following quote:\n\n"
        f"\"{quote}\"\n\n"
        f"Your blog post should include the following sections:\n"
        f"1. **Introduction**: Provide context about the quote and its relevance in today's world.\n"
        f"2. **Detailed Analysis**: Break down the meaning of the quote and explain its key components.\n"
        f"3. **Real-Life Application**: Discuss how this quote can be applied in everyday life or specific scenarios.\n"
        f"4. **Conclusion**: Summarize the importance of the quote and leave the reader with a thought-provoking takeaway.\n\n"
        f"Write in an engaging and motivational tone suitable for a broad audience."
    )
    result = subprocess.run(
        ["ollama", "run", model_name, prompt],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    if result.returncode != 0:
        raise Exception(f"Error running model: {result.stderr.strip()}")
    return result.stdout.strip()
quote_explanation = explain_quote_with_ollama(quote_text)

# Combine quote and explanation
full_message = f"{quote_text}\n\n- {quote_author}\n\n**Explanation:**\n{quote_explanation}"

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

# Email configuration
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

# Email details
to_email = os.environ['TO_EMAIL']
from_email = os.environ['FROM_EMAIL']
smtp_server = os.environ['SMTP_SERVER']
smtp_port = int(os.environ['SMTP_PORT'])
login = os.environ['EMAIL_LOGIN']
password = os.environ['EMAIL_PASSWORD']

# Send the email with the quote and explanation
send_email(quote_text, full_message, to_email, from_email, smtp_server, smtp_port, login, password, output_path)
