import datetime
import os
import subprocess
import nltk
from nltk.corpus import wordnet
from tqdm import tqdm
import json

# Constants

DATE_RANGES = [
    # 2003 until 2020
    (
        "2003-09-01|2004-09-01",
        "xxxxxxx|xxxxxxx",
    )(
        "2004-09-01|2005-09-01",
        "xxxxxxx|xxxxxxx",
    )(
        "2005-09-01|2006-09-01",
        "xxxxxxx|xxxxxxx",
    )(
        "2006-09-01|2007-09-01",
        "xxxxxxx|xxxxxxx",
    )(
        "2007-09-01|2008-09-01",
        "xxxxxxx|xxxxxxx",
    )(
        "2008-09-01|2009-09-01",
        "xxxxxxx|xxxxxxx",
    )(
        "2009-09-01|2010-09-01",
        "xxxxxxx|xxxxxxx",
    )(
        "2010-09-01|2011-09-01",
        "xxxxxxx|xxxxxxx",
    )(
        "2011-09-01|2012-09-01",
        "xxxxxxx|xxxxxxx",
    )(
        "2012-09-01|2013-09-01",
        "xxxxxxx|xxxxxxx",
    )(
        "2013-09-01|2014-09-01",
        "xxxxxxx|xxxxxxx",
    )(
        "2014-09-01|2015-09-01",
        "xxxxxxx|xxxxxxx",
    )(
        "2015-09-01|2016-09-01",
        "xxxxxxx|xxxxxxx",
    )(
        "2016-09-01|2017-09-01",
        "xxxxxxx|xxxxxxx",
    )(
        "2017-09-01|2018-09-01",
        "xxxxxxx|xxxxxxx",
    )(
        "2018-09-01|2019-09-01",
        "xxxxxxx|xxxxxxx",
    )(
        "2019-09-01|2020-09-01",
        "xxxxxxx|xxxxxxx",
    )
]


def readFromJSON():
    # Read JSON data from a file
    with open("hashes/hashes.json", "r") as file:
        data = json.load(file)

    return data


def generate_dates(start_date, end_date):
    # Generate dates between the given dates
    dates = []
    delta = end_date - start_date
    for i in range(delta.days + 1):
        date = start_date + datetime.timedelta(days=i)
        dates.append(date.strftime("%m/%d/%y"))
    return dates


def get_words():
    nltk.download("wordnet")

    words = list(wordnet.words())
    final_words = [word.title() for word in words if word.isalpha()]
    return final_words


def dictGen(start_date, end_date):
    if not os.path.exists("wordlists"):
        os.mkdir("wordlists")

    if not os.path.isfile("wordlists/all.txt"):
        with open("wordlists/all.txt", "w") as file:
            words = get_words()
            for word in tqdm(words, total=len(words)):
                file.write(word + "\n")

    if not os.path.isfile("wordlists/4and5.txt"):
        with open("wordlists/4and5.txt", "w") as file:
            words = open("wordlists/all.txt").read().splitlines()
            final_words = [word for word in words if (len(word) == 4 or len(word) == 5)]
            for word in tqdm(final_words, total=len(final_words)):
                file.write(word + "\n")

    if not os.path.isfile("wordlists/num4and5.txt"):
        with open("wordlists/num4and5.txt", "w") as file:
            words = open("wordlists/4and5.txt").read().splitlines()
            for num in range(100):
                for word in words:
                    file.write(f"{word}{num:02}\n")

    # If file does not exist or date range does not match
    if not os.path.isfile("wordlists/dates.txt"):
        with open("wordlists/dates.txt", "w") as file:
            dates = generate_dates(start_date, end_date)
            for date in tqdm(dates, total=len(dates)):
                file.write(date + "\n")
    else:
        with open("wordlists/dates.txt", "r") as file:
            dates = file.read().splitlines()
        if len(dates) == 0 or not (
            dates[0] == start_date.strftime("%m/%d/%y")
            and dates[-1] == end_date.strftime("%m/%d/%y")
        ):
            with open("wordlists/dates.txt", "w") as file:
                dates = generate_dates(start_date, end_date)
                for date in tqdm(dates, total=len(dates)):
                    file.write(date + "\n")
    if not os.path.isfile("wordlists/combined4and5.txt"):
        with open("wordlists/combined4and5.txt", "w") as file:
            words = open("wordlists/4and5.txt").read().splitlines()
            dates = open("wordlists/dates.txt").read().splitlines()
            for word in words:
                for date in dates:
                    file.write(f"{word}{date}\n")

    print("Wordlists generated successfully.")


def generate_numbers():
    """Generate a list of possible numbers in the format."""
    nums = (str(i) for i in range(0, 100))

    # Append a 0 to the front of each number if it is less than 10
    return [f"0{num}" if len(num) == 1 else num for num in nums]


def crack(start_date, end_date):

    # parse dates
    start_date = datetime.date.fromisoformat(start_date)
    end_date = datetime.date.fromisoformat(end_date)

    # Generate wordlist
    dictGen(start_date, end_date)

    subprocess.run(
        [
            "hashcat",
            "-m0",  # TODO
            "-O",
            "-o",
            "hashes/cracked.txt",
            "hashes/toCrack.txt",
            "-a1",
            "wordlists/dates.txt",
            "wordlists/num4and5.txt",
            "-D",
            "1,2",
            "-w3",
        ]
    )


def log(string):
    with open("logs.log", "a") as f:
        f.write(string + "\n")


def main():
    if not os.path.exists("logs.log"):
        os.system("touch logs.log")

    if not os.path.exists("hashes"):
        os.mkdir("hashes")

    os.system("echo '' > hashes/toCrack.txt")

    log("Starting program..." + str(datetime.datetime.now()))

    # Read JSON data
    hashes = readFromJSON()

    for date_range in DATE_RANGES:
        log(f"Cracking hashes for {date_range[0]}" + str(datetime.datetime.now()))
        start_date, end_date = date_range[0].split("|")
        start_id, end_id = date_range[1].split("|")

        with open("hashes/toCrack.txt", "w") as file:
            for hash in hashes:
                if hash["id"] >= start_id and hash["id"] <= end_id:
                    file.write(f"{hash['hash']}\n")

        crack(start_date, end_date)

    log("Crack by year complete." + str(datetime.datetime.now()))

    with open("hashes/toCrack.txt", "w") as file:
        for hash in hashes:
            file.write(f"{hash['hash']}\n")

    crack("2003-09-01", "2020-09-01")

    log("Crack all complete." + str(datetime.datetime.now()))

    # Go through all ids and check if they have been cracked, making a new json file of those that haven't
    # Connect cracked hashes to their respective ids, and write to a new json file
    cracked_hashes = []
    with open("hashes/cracked.txt", "r") as file:

        for cracked_hash in file.read().splitlines():
            if cracked_hash.count(":") == 1:
                hash, password = cracked_hash.split(":")
                cracked_hash = {"hash": hash, "password": password}
            if cracked_hash.count(":") == 2:
                hash, salt, password = cracked_hash.split(":")
                cracked_hash = {"hash": hash, "salt": salt, "password": password}
            cracked_hashes.append(cracked_hash)

    uncracked_hashes = []

    # TODO: make sure the parsing catches everything
    for hash in hashes:
        if hash["hash"] not in cracked_hashes:
            uncracked_hashes.append(hash)
        else:
            # Search cracked_hashes for matching password
            for cracked in cracked_hashes:
                if cracked["hash"] == hash["hash"]:
                    hash["password"] = cracked["password"]
                    break

    with open("hashes/hashes.json") as f:
        json.dump(hashes, f)

    with open("hashes/uncracked.json", "w") as file:
        json.dump(uncracked_hashes, file)


if __name__ == "__main__":
    main()
