#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Inkyphat functions - Create a mask
def create_mask(source, mask=(inky_display.BLACK, inky_display.WHITE, inky_display.RED)):
    mask_image = Image.new("1", source.size)
    w, h = source.size
    for x in range(w):
        for y in range(h):
            p = source.getpixel((x, y))
            if p in mask:
                mask_image.putpixel((x, y), 255)

    return mask_image
  
  
  # Multiline text functions (from : http://vnoted.com/articles/putting-text-on-images-with-python-pil/)
def text_wrap(text, font, max_width):
    lines = []
    if font.getsize(text)[0] <= max_width:
        lines.append(text) 
    else:
        words = text.split(' ')  
        i = 0
        while i < len(words):
            line = ''         
            while i < len(words) and font.getsize(line + words[i])[0] <= max_width:                
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            lines.append(line)    
    return lines
  
