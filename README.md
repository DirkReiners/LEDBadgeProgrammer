# LED Name Badge Programmer

## Word of warning!

There are several versions of LED badges that look almost identical, but have incompatible programming models, and sometimes the same Amazon seller changes the model without changing the Amazon page... The program here was developed for badges that use a mini-USB connection and have two buttons in the back. As of right now I can't find these on Amazon any more. :( If I find time I'll try to update the program to support newer badges, but I have no prediction when that will happen. Sorry!

## Word of warning (2)

If you come here through google and are looking for a nice graphical system to program your badge, sorry, this is not the software you are looking for. It only has a command-line interface and was primarily developed for Linux. It should still work on Windows, but only with the right USB-serial driver installed (see [Windows](#windows) for details). 

## Intro

Scrolling LED name badges are still rare enough to be cool, but are common enough to have become pretty affordable. But a side effect of the affordability is that manufacturers are not spending a lot of money on making them very usable and easy to program. They often come with (sometimes very) outdated drivers and design programs with previews that look nothing like what actually ends up on the badge. Not to talk about the fact that all of that is almost always exclusively available for Windows, so Linux or MacOS users are left to dig an old machine out of the closet to use the shiny new toy they bought.

This project provides a very basic, simple way to program a specific kind of badge, the B1248W family, specifically [this one](http://www.amazon.com/gp/product/B00T9FEILE). It is the cheapest we could find that still allows programming through the USB connection (and not through endless click orgies on one of a few buttons in the back). Note that there are many other badges that will look pretty much the same, but there are many different protocols and interfaces, so even if you have one that looks the same, this program might not work for you. See the [Other Links](#other-links) section below for other, similar projects that might work for you if this one doesn't.

## Basic Hardware Setup

This kind of badge connects to the computer through a USB connection. On the badge end is uses a USB to serial converter to drive the actual chip that does the display, thus to program it the computer it's connected to needs to have drivers for the USB to serial converter on the badge. The chip is manufactured by Prolific (2303), which also provides a [Windows driver](http://www.prolific.com.tw/US/ShowProduct.aspx?p_id=225&pcid=41), but depending on the specific chip version if may not work under Windows 7/8/10. It worked find under Linux (FC20), the chip was immediately recognized. The vendor and product IDs for the ones we have are 067b and 2303, if you want to see whether you have support for it.

One caveat is that by default Linux will not create the serial device with permissions that allow everybody to access it. You can either change them by hand (`sudo chmod 666 /dev/ttyUSB0`) after you plug in the badge, or you can add the user to the group that the device has, usually `dialout`, or you can run this program as root, but that should be used as a last resort.

## Basic Software Setup

This program is written in Python (2.x) and uses the [PIL Imaging library](http://www.pythonware.com/products/pil/) (or [Pillow](https://python-pillow.github.io/)) for image manipulation and the [PySerial](https://pypi.python.org/pypi/pyserial) package for serial communcations. PIL or Pillow are part of almost any Linux distro and are available as installers for other systems, too. PySerial can be installed through [pip](https://pypi.python.org/pypi/pip).

## Usage

The first thing to do is to figure out what version of the badge you have. They are all called B1248W, but in fact some of them (mostly some of the red ones) only have 11x44 LEDs. This package comes with two simple test images that help identifying them. Try to run

    python ledbadge.py test_12x48.png

If you get the `Can't write to serial port /dev/ttyUSB0, aborting!` message your permissions for the serial port need to be adjusted ([see above](#basic-hardware-setup)).

If it works you should see an image with the letters '12x48' in the center. If you don't see any corners on the right side and there is only one pixel at the bottom you have an 11x44 display. Try the following:

    python ledbadge.py --width 44 --height 11 test_11x44.png

and you should see the image with correct corners.

And that already shows the basic use of the program. Just add all the things that you want displayed on the command line and they will be displayed one after the other. You can provide images (white on black prefered) or text:

    python ledbadge.py "If you can see the corners this is working:" test_12x48.png "Did you see them?"
    
To make it more interesting you can set the transition effect:

    python ledbadge.py effect=left "If you can see the corners this is working:" test_12x48.png "Did you see them?"
    
or a little faster, leaving the image standing still

    python ledbadge.py effect=left speed=6 "If you can see the corners this is working:" effect=fix speed=3 test_12x48.png effect=left speed=6 "Did you see them?"
    
That covers the basics, see below for more options. Enjoy!

## Program Options

The program understands a few standard command line options.`--width` and `--height` specify the size of the badge. The only options that we've seen were 44x11 or 48x12, the default is 48x12. The only other option is `-p` (or `--port`) to specify the dev to use for the device (default `/dev/ttyUSB0`).

All other controlling options are passed as `<key>=<value>` pairs interspersed with the items to display.

The items to display can be images or text. Images that are too high will be cut be off, images that are not high enough will be padded. Images should be white on black. They can be inverted by using the `invert=on` option, if needed.

    python ledbadge.py speed=6 test_12x48.png invert=on test_12x48.png

Text is just interpreted as text. There are different fonts in the `pilfonts` folder to choose from by using the `font=` option, the default is `helvR08`.

    python ledbadge.py speed=5 effect=left font=pilfonts/luRS08.pil "This is luRS08." font=pilfonts/ncenBI08.pil "This is ncenBI08."

An interesting question is what happens with text that is longer than the display, especially for up or down effects. By default the text is just cut at the end of the display, which can lead to partial letters being displayed:

    python ledbadge.py speed=5 effect=up "No wrap makes this a bad text."

The alternative is to wrap the text at the letter level, to avoid partial letters:

    python ledbadge.py speed=5 effect=up wrap=char "No wrap makes this a bad text."

Or to wrap it at the word level, to avoid partial words:

    python ledbadge.py speed=5 effect=up wrap=word "No wrap makes this a bad text."

Other examples:


    python ledbadge.py speed=5 effect=up wrap=word halign=center "No wrap makes this a bad text."

    python ledbadge.py speed=5 effect=left blink=on "You can blink." blink=off "But why would you want to?" 

    python ledbadge.py speed=5 marquee=on halign=center "Fireworks"

    python ledbadge.py speed=5 effect=left "White on black" invert=on "Black on white"


Other options that need documentation:

* blink=on|off
* marquee=on|off
* invert=on|off
* halign=left|center|center-right|right
* valign=top|middle|middle-down|bottom


## Windows

You can run this program on Windows just like on Linux, but you also need to run it from the command line. Install [Python](http://www.python.org) and use [PIP](https://pip.pypa.io/en/stable/installing/) to install PySerial and PIP or Pillow. In addition to those you also need to install the USB-Serial driver that makes the badge accessible as a COM port. You can get it from the [manufacturer's website](http://www.prolific.com.tw/US/ShowProduct.aspx?p_id=225&pcid=41). Don't forget to reboot after installation or it might not work.

You will need to specify the correct COM port using the -p options to make it write to the badge, but other than that you should be fine.


## Other Links

* [http://www.daveakerman.com/?p=1440]
* [https://bitbucket.org/bartj/led]
* [http://zunkworks.com/projects/programmablelednamebadges/]


## Acknowledgements

* Thanks to Raphael for the Windows input and testing!


## Copyrights

The pilfonts folder contains a subset of the [pilfonts](http://effbot.org/downloads#pilfonts) collection from EFFBot, which in turn are based on X11 fonts. Please see the [pilfonts/README](https://github.com/DirkReiners/LEDBadgeProgrammer/blob/master/pilfonts/README) file for copyright details.

The software itself is licensed under the Simplified BSD License:

Copyright (c) 2015, Dirk Reiners
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of the FreeBSD Project.

