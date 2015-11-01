from PIL import Image, ImageDraw, ImageFont
import qrcode


def makeQR(string):
	"""
	Makes a QRcode image from <string>
	"""
	qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=4, border=1,)
	qr.add_data(string)
	qr.make(fit=True)
	qrim = qr.make_image()
	return qrim.convert('RGBA')

def makePaper(publickey, privatekey, background='paperwallet.png', fontsize=10, font='/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf'):
	# Open the paperwallet background
	r = Image.open(background).convert('RGBA')
	# Make and Paste QrCodes
	r.paste(makeQR(publickey),(20,20))
	r.paste(makeQR(privatekey),(560,135))
	# Rotate base -90 degrees
	base = r.rotate(-90)
	# Make blank transparent image for text
	txt = Image.new('RGBA', base.size, (160,160,160,0))
	# Set the Font of text
	fnt = ImageFont.truetype(font, fontsize)
	# Draw the addresses on the new image
	d = ImageDraw.Draw(txt)
	d.text((15,172), publickey, font=fnt, fill=(0,0,0,250))
	d.text((15,537), privatekey, font=fnt, fill=(0,0,0,250))
	
	# Merge the 2 layers and rotate 90 degrees
	out = Image.alpha_composite(base, txt)
	out.rotate(90).show()

if __name__ == "__main__":
	import sys
	if not len(sys.argv) > 2:
		print("At least 2 Arguments are required: <publickey> <privatekey> [image] [fontsize] [font]")
		sys.exit()
	pubkey=sys.argv[1]
	privkey=sys.argv[2]
	if not len(sys.argv) > 3: makePaper(pubkey, privkey)
	if not len(sys.argv) > 4: makePaper(pubkey, privkey, sys.argv[3])
	if not len(sys.argv) > 5: makePaper(pubkey, privkey, sys.argv[3], int(sys.argv[4]))
	else:makePaper(pubkey, privkey, sys.argv[3], int(sys.argv[4]), sys.argv[5])
