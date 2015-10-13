__author__ = 'reiners'

import serial
import time
import math
import os
import sys
import argparse
from PIL import Image, ImageFont, ImageDraw

effects = { "fix" : 4, "left" : 0, "right" : 1, "up" : 2, "down" : 3, "animation" : 5, "snow" : 6, "blink" : 7 }

class Message(object):

    def __init__(self):
        self._width = 0
        self._image = []
        self.effect = effects["fix"]
        self.speed = 1
        self.blink = False
        self.marquee = False


    def cropEmpty(self, image, left=False, right=True, top=False, bottom=False):
        s = image.size

        # Black pixels bounding box (l,r,t,b)
        box = [10000,-10000,10000,-10000]

        pixels = image.load()

        for x in xrange(0, s[0]):
            for y in xrange(0, s[1]):
                if pixels[x,y] != 0:
                    box[0] = min(box[0], x)
                    box[1] = max(box[1], x)
                    box[2] = min(box[2], y)
                    box[3] = max(box[3], y)

        cb = box
        if not left:
            cb[0] = 0
        if not right:
            cb[1] = s[0] - 1
        if not top:
            cb[2] = 0
        if not bottom:
            cb[3] = s[1] - 1

        crop = image.crop((cb[0],cb[2],cb[1] + 1,cb[3] + 1))
        crop.load()

        return crop


    def adjustAlign(self, im, halign, valign, full=True):
        s = im.size
        
        xoff = 0
        yoff = 0
        
        halign = halign.lower()
        valign = valign.lower()
       
        # Adjust horizontally?
        if halign != "left" and s[0] < clargs.width:
            if halign == "right":
                xoff = clargs.width - s[0]
            else:
                xoff = (clargs.width - s[0]) / 2
                
                if (clargs.width - s[0]) % 2 == 1:
                    if halign == "center-right":
                        xoff += 1
         
        # Adjust vertically?
        if valign != "top" and s[1] < clargs.width:
            if valign == "bottom":
                yoff = clargs.height - s[1]
            else:
                yoff = (clargs.height - s[1]) / 2
                
                if (clargs.height - s[1]) % 2 == 1:
                    if valign == "middle-down":
                        yoff += 1

        if xoff != 0 or yoff != 0:
            if full == True:
                outimage = Image.new(im.mode , (max(s[0], clargs.width), max(s[1], clargs.height)), "black")
            else:
                outimage = Image.new(im.mode , (s[0] + xoff, s[1] + yoff), "black")

            outimage.paste(im, (xoff, yoff))
            im = outimage

        return im


    def setImage(self, image, halign="center-left", valign="middle-down", invert=False):

        if isinstance(image, basestring):
            im = Image.open(image)
        else:
            im = image
        
        im = self.adjustAlign(im, halign, valign)
        
        s = im.size
        ih = min(clargs.height, s[1])
        
        self._image = [b""] * clargs.height
        col = [0] * clargs.height

        bwim = im.convert("L")
        pixels = bwim.load()

        mask = 0x80
        inv = 0x00
        col = [0] * clargs.height

        for x in xrange(s[0]):
            for y in xrange(ih):
                if pixels[x,y] >= 128:
                    col[y] |= mask

            inv |= mask
            mask = mask / 2

            if mask == 0:
                for y in xrange(clargs.height):
                    c = col[y]
                    if invert:
                        c = c ^ inv
                    self._image[y] += chr(c)
                    col[y] = 0
                mask = 0x80
                inv = 0x00

        # copy leftover pixels
        if mask != 0x80:
            for y in xrange(clargs.height):
                c = col[y]
                if invert:
                    c = c ^ inv
                self._image[y] += chr(c)

        self._width = (s[0] + 7) / 8

        if len(self._image[0]) != self._width:
            print "Something's wrong: %d != %d!" % (len(self._image[0]), self._width)
            sys.exit(1)



    def setText(self, text, font="pilfonts/helv10R.pil", halign="center-left", valign="middle-down", wrap="none", invert=False):

        ifont = ImageFont.load( font )
        (w, h) = ifont.getsize(text)

        tximage = Image.new( 'L' , (w, h), "black")
        idraw = ImageDraw.Draw( tximage )

        idraw.text((0,0), text, font=ifont, fill="white")

        crop = self.cropEmpty(tximage, left=True, right=True, top=True, bottom=True)

        if crop.size[1] > clargs.height:
            print "Warning: text %s with font %s has height %d > image height %d, ignoring extra rows!" % (text, font, crop.size[1], clargs.height)

        # Arg cleanup
        wrap = wrap.lower()
        
        # Do we need to split and wrap?
        if wrap != "none" and crop.size[0] > clargs.width:
            if wrap == "char":
                pieces = text
            elif wrap == "word":
                pieces = text.split(' ')
            else:
                print "Unknown wrap mode %s, aborting!"  % wrap
                sys.exit(1)

            outs = []
            outw = 0
            cur = ''

            for p in pieces:
                lastcur = cur

                if cur != "" and wrap == "word":
                    cur += ' '
                cur += p

                (w, h) = ifont.getsize(cur)

                if w > clargs.width:
                    (w, h) = ifont.getsize(lastcur)
                    outimage = Image.new('L' , (w, h), "black")
                    idraw = ImageDraw.Draw(outimage)
                    idraw.text((0,0), lastcur, font=ifont, fill="white")

                    outimage = self.cropEmpty(outimage, left=True, right=True, top=True, bottom=True)
                    outimage = self.adjustAlign(outimage, halign, valign, full=True)

                    outs.append(outimage)
                    outw += outimage.size[0]
                    cur = p

            if cur != '':
                (w, h) = ifont.getsize(cur)
                outimage = Image.new('L' , (w, h), "black")
                idraw = ImageDraw.Draw(outimage)
                idraw.text((0,0), cur, font=ifont, fill="white")

                outimage = self.cropEmpty(outimage, left=True, right=True, top=True, bottom=True)
                outimage = self.adjustAlign(outimage, halign, valign, full=True)

                outs.append(outimage)
                outw += outimage.size[0]

            outimage = Image.new('L' , (outw, clargs.height), "black")
            x = 0
            for o in outs:
                outimage.paste(o, (x,0))
                x += o.size[0]

            self.setImage(outimage, halign="left", valign="top", invert=invert)

        else:
            self.setImage(crop, halign=halign, valign=valign, invert=invert)



class LEDBadge(object):

    def __init__(self, port):

        if not os.access(port, os.W_OK):
            print "Can't write to serial port %s, aborting!" % port
            sys.exit(1)

        self._port = port
        self._messages = []


    def addMessage(self, m):

        self._messages.append(m)


    def send(self):

        if not len(self._messages):
            print "No message, not sending."
            return

        print "Sending message(s):",
        sys.stdout.flush()

        # Assemble necessary data
        # configuration part of header. Starts with 0x00
        confheader = b"\x00"
        # Image part of the header
        imgheader = b""
        # Image data part (12 lines of binary image)
        image = [b""] * clargs.height

        iw = 0
        lastw = 0

        # Assemble headers and image data
        for m in self._messages:
            # configuration header: 1 byte per message, 8 total. bits: msssbeee
            h = m.effect + m.speed * 16
            if m.blink:
                h |= 0x08
            if m.marquee:
                h |= 0x80
            confheader += chr(h)

            # image header: 4 bytes: length of last message,0x8,offset in line of this message,0x0
            imgheader += chr(lastw) + "\x08" + chr(iw) + "\x00"
            lastw = m._width
            iw += m._width

            # Image data: all messages concatenated for each line, e.g. make a wide image with all messages
            for i in xrange(len(m._image)):
                image[i] += m._image[i]

        # Add dummy lines until 12 lines reached, if needed
        while len(image) < 12:
            image.append(b"\x00" * iw)

        # Fill up header to cover 8 messages
        for i in xrange(8 - len(self._messages)):
            confheader += chr(h)
            imgheader += chr(lastw) + "\x08" + chr(iw) + "\x00"
            lastw = 0

        # Image header stop byte
        imgheader += "\x00"

        # Message ready, let's send it...
        # Open serial port
        ser = serial.Serial(self._port, 4800)

        # Intro
        ser.write(b"Hello")
        time.sleep(.050)

        # Config
        ser.write(confheader + imgheader)
        print "Header sent...",
        sys.stdout.flush()
        time.sleep(.500)

        print "Image lines",
        sys.stdout.flush()

        # Image data, line by line
        # After 256 bytes it needs a ~500 ms break or things go very wrong
        sent = 0
        for i in image:
            if sent + len(i) < 256:
                ser.write(i)
                ser.flush()
                sent += len(i)
            else:
                ser.write(i[:256-sent])
                print ".",
                sys.stdout.flush()
                time.sleep(.500)
                ser.write(i[256-sent:])
                sent = len(i) - (256-sent)
            print "=",
            sys.stdout.flush()
            time.sleep(.090)

        # All done
        ser.close()

        print ""
        print "All done!"

        # Unfortunately we don't get any error messages, so let's hope it worked...
        # If not, just run it again. ;)


if __name__ == "__main__":

    global clargs
    
    parser = argparse.ArgumentParser(description='LED Badge Programmer')

    parser.add_argument('--width', help='width of badge', type=int, default=48)
    parser.add_argument('--height', help='height of badge', type=int, default=12)
    parser.add_argument('-p', '--port', help='serial port to use', default="/dev/ttyUSB0")
    parser.add_argument('coms', nargs='+', help='options/message images')

    clargs = parser.parse_args()


    speed=1
    effect="Fix"
    blink=False
    marquee=False
    invert=False
    font="pilfonts/helvR08.pil"
    halign="left"
    valign="middle-down"
    wrap="none"

    b = LEDBadge(clargs.port)

    for c in clargs.coms:

        if c.startswith("speed="):
            speed = int(c[6:])
        elif c.startswith("effect="):
            effect = c[7:]
        elif c.startswith("blink="):
            if c.endswith("on"):
                blink = True
            else:
                blink = False
        elif c.startswith("marquee="):
            if c.endswith("on"):
                marquee = True
            else:
                marquee = False
        elif c.startswith("invert="):
            if c.endswith("on"):
                invert = True
            else:
                invert = False
        elif c.startswith("font="):
            font = c[5:]
        elif c.startswith("halign="):
            halign = c[7:]
        elif c.startswith("valign="):
            valign = c[7:]
        elif c.startswith("wrap="):
            wrap = c[5:]
        else:

            m = Message()
            m.effect = effects[effect.lower()]
            m.speed = speed
            m.blink = blink
            m.marquee = marquee

            if os.path.isfile(c):
                m.setImage(c, halign=halign, valign=valign, invert=invert)
            else:
                m.setText(c, font, halign=halign, valign=valign, wrap=wrap, invert=invert)

            b.addMessage(m)

    b.send()


