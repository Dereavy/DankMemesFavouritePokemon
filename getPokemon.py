import praw
import json
import re
from itertools import groupby
from os.path import exists as file_exists
from collections import Counter

# Reddit API information
reddit = praw.Reddit(
    client_id="--reddit-api-client-id--",
    client_secret="--reddit-api-client-secret--",
    user_agent="getPokemon",
)

# Comment thread id of the sub with the pokemon
sub_id = 'zwu64n'

# File to save the raw comments 
save_to = "redditGrab_{}.json".format(sub_id)

# File to save the transformed comments
output_file = "redditGrab_{}_output.json".format(sub_id)


# Load comments from the json
def load_from_json(json_file):
    with open(json_file, "r") as f:
        content = json.load(f)
    f.close()
    return content

# Save comments to the json
def save_to_json(json_file, content):
	with open(json_file, "w") as f:
	    json.dump(content, f)
 
# Download comments from reddit submission.
def download_comments(comments_json):
	submission_list = []
	submission = reddit.submission(id=sub_id)
	submission.comments.replace_more(limit=None)
	for comment in submission.comments.list():
	    formatted = comment.body
	    submission_list.append(formatted)
	save_to_json(save_to, submission_list)

# Remove ascii characters and transform to lowercase
def clean_comments(comments):
    cleaned = []
    for comment in comments:
        clean_comment = comment.encode('ascii','ignore').decode().lower()
        cleaned.append(clean_comment)
    return cleaned

# Extract grid coordinates from strings:
def extract_tile_from_comment(comment):
    coords_rgx = re.compile("(?<![\w|\/])((?:[a-zA-Z][\s\-\,]?\d{1,2})|(?:\d{1,2}[\s\-\,]?[a-zA-Z]))(?![#|\w|\/])")
    tiles = coords_rgx.search(comment)
    if tiles == None : return None
    return list(tiles.groups())

# Flatten a nested array (utility)
def flatten(nested_list):
    return [item for sublist in nested_list for item in sublist]

# Extract and flatten tiles into an array
def extract_tiles(comments):
    tiles = []
    for comment in comments:
        tile = extract_tile_from_comment(comment)
        if(tile is not None):
            tiles.append(tile)
    flattened_tiles = flatten(tiles)
    return flattened_tiles

# Normalise the tile names ("23,N", "D-22", .. => "n23", "d22", ..) 
def clean_tiles(tiles):
    cleaned = []
    digits_rgx = re.compile(r"\d{1,2}")
    character_rgx = re.compile(r"\w")
    for tile in tiles:
        number = digits_rgx.search(tile).group(0)
        letter = character_rgx.search(tile).group(0)
        clean_tile = "{}{}".format(letter,number)
        cleaned.append(clean_tile)
    return cleaned

# Count the occurance of each tile and order them from most common first.
def get_common_tiles(tiles):
    sorted_tiles = {value: len(list(freq)) for value, freq in groupby(sorted(tiles))}
    counted_tiles = Counter(sorted_tiles)
    return counted_tiles.most_common()

# EXECUTION    
# Open and save raw comments if file does not exist.
# if not (file_exists(save_to)):
download_comments(save_to)

comments = load_from_json(save_to)
comments = clean_comments(comments)
tiles = extract_tiles(comments)
tiles = clean_tiles(tiles)
common_tiles = get_common_tiles(tiles)

save_to_json(output_file,common_tiles)


