from PIL import Image, ImageOps
import csv
import sys
import os
import random
import json

dirname = os.path.dirname(__file__)


class NFTWeight:
    def __init__(self, type, name, rarity, location=None):
        self.type = type
        self.name = name
        self.rarity = rarity
        self.location = location


class NFT:
    def __init__(self, arms, eyes, front_plate, background, mouth, hat, slot_color):
        self.arms = arms
        self.eyes = eyes
        self.front_plate = front_plate
        self.background = background
        self.mouth = mouth
        self.hat = hat
        self.slot_color = slot_color


def load_csv(csv_path):
    reader = csv.DictReader(open(csv_path))

    result = {}
    for row in reader:
        for column, value in row.items():
            result.setdefault(column, []).append(value)

    return result


def gen_weight_list(csv_dict):
    type_list = csv_dict["type"]
    name = csv_dict["name"]
    rarity = csv_dict["rarity"]

    weight_list = []

    for index, value in enumerate(rarity):
        rarity_percent = round(float(value) * 100, 2)
        weight = NFTWeight(type_list[index], name[index], rarity_percent)
        weight_list.append(weight)

    return weight_list


def gen_weight_list_category(weight_list, type):
    weights = {}
    for weight in weight_list:
        if weight.type == type:
            weights[weight.name] = weight.rarity

    return weights


def gen_attrib(weight_list_category):
    return random.choices(list(weight_list_category.keys()), list(weight_list_category.values()))[0]


def gen_nft_traits(weight_list, traits):
    trait = {"arm": gen_attrib(gen_weight_list_category(weight_list, "arm")),
             "eyes": gen_attrib(gen_weight_list_category(weight_list, "eyes")),
             "front_plate": gen_attrib(gen_weight_list_category(weight_list, "front_plate")),
             "background": gen_attrib(gen_weight_list_category(weight_list, "backgrounds")),
             "mouth": gen_attrib(gen_weight_list_category(weight_list, "mouth")),
             "hat": gen_attrib(gen_weight_list_category(weight_list, "hats")),
             "slot_color": gen_attrib(gen_weight_list_category(weight_list, "slot_colors"))}

    if trait in traits:
        gen_nft_traits(weight_list, traits)

    return trait


def open_valid_image(image_path):
    return Image.open(image_path).convert("RGBA").resize((1198, 1498))


def main():
    # check to make sure the right arguments have been parsed
    script_name = os.path.basename(__file__)
    if len(sys.argv) != 3:
        print("Error! Usage: python " + script_name + " [csv path] [amount to generate]")
        sys.exit(-1)

    # grab the information from the arguments
    csv_path = sys.argv[1]
    gen_count = int(sys.argv[2])

    # load the csv_dict into memory as a dictionary
    csv_dict = load_csv(csv_path)

    weight_list = gen_weight_list(csv_dict)

    for weight in weight_list:
        # generate filepath and check if it can be found
        filepath = os.path.join(dirname, "Attr\\" + weight.type + "\\" + weight.name + ".png")
        if not os.path.isfile(filepath):
            print("Error! Can't find " + filepath)

        weight.location = filepath

        print(weight.type + " | " + weight.name + " | " + str(weight.rarity) + " | " + weight.location)


    # generate as many traits as the user specifies and append to a list
    nfts = []
    for x in range(gen_count):
        nft = gen_nft_traits(weight_list, nfts)
        print(nft)
        nfts.append(nft)

    nft_dict = {}
    # give each of the nfts a token_id
    i = 0
    for item in nfts:
        item["token_id"] = i
        nft_dict[str(i)] = item
        i += 1

    # generate tokens
    with open(os.path.join(dirname, "output\\traits.json"), "w") as outfile:
        json.dump(nft_dict, outfile, indent=4)

    for item in nfts:
        arm_path = ""
        eyes_path = ""
        front_plate_path = ""
        background_path = ""
        mouth_path = ""
        hat_path = ""
        slot_color_path = ""

        for weight in weight_list:
            if weight.name == item["arm"] and weight.type == "arm":
                arm_path = weight.location
            if weight.name == item["eyes"] and weight.type == "eyes":
                eyes_path = weight.location
            if weight.name == item["front_plate"] and weight.type == "front_plate":
                front_plate_path = weight.location
            if weight.name == item["mouth"] and weight.type == "mouth":
                mouth_path = weight.location
            if weight.name == item["hat"] and weight.type == "hats":
                hat_path = weight.location
            if weight.name == item["slot_color"] and weight.type == "slot_colors":
                slot_color_path = weight.location
            if weight.name == item["background"] and weight.type == "backgrounds":
                background_path = weight.location

        background_image = open_valid_image(background_path)
        slot_color_image = open_valid_image(slot_color_path)
        eyes_image = open_valid_image(eyes_path)
        mouth_image = open_valid_image(mouth_path)
        hat_image = open_valid_image(hat_path)
        arm1_image = open_valid_image(arm_path)
        arm2_image = ImageOps.mirror(open_valid_image(arm_path))


        composite = Image.alpha_composite(background_image, slot_color_image)
        composite = Image.alpha_composite(composite, eyes_image)
        composite = Image.alpha_composite(composite, mouth_image)
        composite = Image.alpha_composite(composite, hat_image)
        composite = Image.alpha_composite(composite, arm1_image)
        composite = Image.alpha_composite(composite, arm2_image)

        file_path = os.path.join(dirname, "output\\" + str(item["token_id"]) + ".png")
        composite.save(file_path)
        print(str(item["token_id"]) + " done!")


if __name__ == "__main__":
    main()
