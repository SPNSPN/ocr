#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from functools import reduce
import argparse
from PIL import Image
import cv2
import pyocr


def video_stream (video_path):
    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), "cannot open video capture.: {0}".format(video_path)

    ok, first = cap.read()
    assert ok, "cannot read video."
    yield first

    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break
        yield frame

    cap.release()

def parse_cmd_args ():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help = "path to image or video.")
    return parser.parse_args()

def main (args):
    tools = pyocr.get_available_tools()
    assert len(tools) > 0, "No ocr tool found."

    tool = tools[0]
    print("found ocr tool: {0}".format(tool.get_name()))

    txt = ""
    ext = os.path.splitext(args.path)[-1]
    if ext in [".png", ".jpg"]:
        txt = tool.image_to_string(Image.open(args.path), lang = "eng"\
                , builder = pyocr.builders.TextBuilder(tesseract_layout = 6))
    elif ext in [".mp4"]:
        fps = cv2.VideoCapture(args.path).get(cv2.CAP_PROP_FPS)
        txts = map(lambda frame: tool.image_to_string(Image.fromarray(frame), lang = "eng"\
                , builder = pyocr.builders.TextBuilder(tesseract_layout = 6))\
                , video_stream(args.path))
        txt = reduce(lambda s, p: "{0}{1}, {2}\n".format(s, p[0] / fps, p[1]), enumerate(txts), "")
    else:
        txt = "cannot process '{0}'".format(ext)

    print(txt)

if __name__ == "__main__":
    main(parse_cmd_args())
