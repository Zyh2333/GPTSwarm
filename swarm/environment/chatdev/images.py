import os
import re

import openai
import requests
import shutil

proposed_images = {}
incorporated_images = {}


def generate_images_from_codes(directory, code):
    def download(img_url, file_name):
        r = requests.get(img_url)
        filepath = os.path.join(directory, file_name)
        if os.path.exists(filepath):
            os.remove(filepath)
        with open(filepath, "wb") as f:
            f.write(r.content)
            print("{} Downloaded".format(filepath))

    regex = r"(\w+.png)"
    joined_codes = code.get_codes()
    matches = re.finditer(regex, joined_codes, re.DOTALL)
    # matched_images = {}
    for match in matches:
        filename = match.group(1).strip()
        if filename in proposed_images.keys():
            incorporated_images[filename] = proposed_images[filename]
        else:
            incorporated_images[filename] = filename.replace("_", " ")

    for filename in incorporated_images.keys():
        if not os.path.exists(os.path.join(directory, filename)):
            desc = incorporated_images[filename]
            if desc.endswith(".png"):
                desc = desc.replace(".png", "")
            print("{}: {}".format(filename, desc))
            openai_new_api = True
            # if openai_new_api:
            #     response = openai.images.generate(
            #         prompt=desc,
            #         n=1,
            #         size="256x256"
            #     )
            #     image_url = response.data[0].url
            # else:
            #     response = openai.Image.create(
            #         prompt=desc,
            #         n=1,
            #         size="256x256"
            #     )
            #     image_url = response['data'][0]['url']
            # download(image_url, filename)
            filepath = os.path.join(directory, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            shutil.copy('/Users/zhuyuhan/Downloads/img.png', filepath)


def get_proposed_images_from_message(messages, results):
    def download(img_url, file_name):
        r = requests.get(img_url)
        filepath = os.path.join(results['directory'], file_name)
        if os.path.exists(filepath):
            os.remove(filepath)
        with open(filepath, "wb") as f:
            f.write(r.content)
            print("{} Downloaded".format(filepath))

    regex = r"(\w+.png):(.*?)\n"
    matches = re.finditer(regex, messages, re.DOTALL)
    images = {}
    for match in matches:
        filename = match.group(1).strip()
        desc = match.group(2).strip()
        images[filename] = desc

    if len(images.keys()) == 0:
        regex = r"(\w+.png)"
        matches = re.finditer(regex, messages, re.DOTALL)
        images = {}
        for match in matches:
            filename = match.group(1).strip()
            desc = " ".join(filename.replace(".png", "").split("_"))
            images[filename] = desc
            print("{}: {}".format(filename, images[filename]))

    for filename in images.keys():
        if not os.path.exists(os.path.join(results['directory'], filename)):
            desc = images[filename]
            if desc.endswith(".png"):
                desc = desc.replace(".png", "")
            print("{}: {}".format(filename, desc))

            openai_new_api = True
            # if openai_new_api:
            #     response = openai.images.generate(
            #         prompt=desc,
            #         n=1,
            #         size="256x256"
            #     )
            #     image_url = response.data[0].url
            # else:
            #     response = openai.Image.create(
            #         prompt=desc,
            #         n=1,
            #         size="256x256"
            #     )
            #     image_url = response['data'][0]['url']

            # download(image_url, filename)
            filepath = os.path.join(results['directory'], filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            shutil.copy('/Users/zhuyuhan/Downloads/img.png', filepath)

    return images
