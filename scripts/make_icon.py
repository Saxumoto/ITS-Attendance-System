from PIL import Image
# Convert logo.png to logo.ico
img = Image.open("logo.png")
img.save("logo.ico", format='ICO', sizes=[(256, 256)])
print("Icon created!")