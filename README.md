# LED Name Badge Programmer

## Word of warning

If you come here through google and are looking for a nive graphical system to program your badge, sorry, this is not th esoftware you're looking for. It only has a command-line interface and was primarily developed for Linux. It should still work on Windows, but only with the right USB-serial driver installed. 

## Intro

Scrolling LED name badges are still rare enough to be cool, but are common enough to have become pretty affordable. But a side effect of the affordability is that manufacturers are not spending a lot of money on making them very usable and easy to program. They often come with (sometimes very) outdated drivers and design programs with previews that look nothing like what actually ends up on the badge. Not to talk about the fact that all of that is almost always exclusively available for Windows, so Linux or MacOS users are left to dig an old machine out of the closet to use the shiny new toy they bought.

This project provides a very basic, simple way to program a specific kind of badge, the B1248W family, specifically [this one](http://www.amazon.com/gp/product/B00T9FEILE). It is the cheapest we could find that still allows programming through the USB connection (and not through endless click orgies on one of a few buttons in the back). Note that there are many other badges that will look pretty much the same, but there are many different protocols and interfaces, so even if you have one that looks the same, this program might not work for you. See the Other Links section below for other, similar projects that might work for you if this one doesn't.

## Basic Hardware Setup

This kind of badge connects to the computer through a USB connection. On the badge end is uses a USB to serial converter to drive the actual chip that does the display, thus to program it the computer it's connected to needs to have drivers for the USB to serial converter on the badge. The chip is manufactured by prolific (2303), which also provides a [Windows driver](http://www.prolific.com.tw/US/ShowProduct.aspx?p_id=225&pcid=41), but depending on the specific chip version if may not work under Windows 7/8/10. It worked find under Linux (FC20), the chip was immediately recognized. The vendor and product IDs for the ones we have are 067b and 2303, if you want to see whether you have support for it.

One caveat is that by default Linux will not create the serial device with permissions thta llow everybody to access it. You can either change them by hand (`sudo chmod 666 /dev/ttyUSB0`) or you can add the user to the group that the device has, usually `dialout`.

## Basic Software Setup

This program is written in Python (2.x) and uses the PIL Imaging library (or Pillow) for image manipulation and the PySerial package for serial communcations. PIL or Pillow are part of almost any Linux distro and are available for other systems, too. PySerial can be installed through (pip)[https://pypi.python.org/pypi/pip].

## Usage

The first thing to do is to figure out what version of the badge you have. They are all called B1248W, but in fact some of them (mostly the red ones) only have 11x44 LEDs. This package comes with two simple test images that help identifying them. Try to run

    python ledbadge.py test_12x48.png

If you get the `Can't write to serial port /dev/ttyUSB0, aborting!` message your permissions for the serial port need to be adjusted (see above).

If it works you should see an image with the letters '12x48' in the center. If you don't see any corners on the right side and there is only one pixel at the bottom you have an 11x48 display. Try the following:

    python ledbadge.py --width 44 --height 11 test_11x44.png

and you should see the image with correct corners.






## Program Options



## Protocol



## Other Links

http://www.daveakerman.com/?p=1440
https://bitbucket.org/bartj/led
http://zunkworks.com/projects/programmablelednamebadges/

## Copyrights

The pilfonts folder contains a subset of the [pilfonts](http://effbot.org/downloads#pilfonts) collection from EFFBot. Copyright for those fonts was not quite clear, but the following should be close:

Copyright © 1995-2014 by Fredrik Lundh

By obtaining, using, and/or copying this software and/or its associated documentation, you agree that you have read, understood, and will comply with the following terms and conditions:

Permission to use, copy, modify, and distribute this software and its associated documentation for any purpose and without fee is hereby granted, provided that the above copyright notice appears in all copies, and that both that copyright notice and this permission notice appear in supporting documentation, and that the name of Secret Labs AB or the author not be used in advertising or publicity pertaining to distribution of the software without specific, written prior permission.

SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
