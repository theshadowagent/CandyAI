import numpy as np
from utils import hex_to_3d, hex_embedding_similarity
from clarifai.rest import Image as ClImage
from clarifai.rest import ClarifaiApp
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("my_logger")
logger.setLevel(logging.INFO)


def predict_color(app, url, num_top=2):
    if app is None:
        app = ClarifaiApp(api_key='9a2117f4967a4f2d92e84adb221c5cc1')

    model = app.models.get("color")

    # predict with the model
    if isinstance(url, str):
        prediction = model.predict_by_url(url=url)
    else:
        image = ClImage(file_obj=url)
        prediction = model.predict([image])

    colors = prediction['outputs'][0]['data']['colors']

    #example : [{'raw_hex': '#d4ced6', 'w3c': {'hex': '#d3d3d3', 'name': 'LightGray'}, 'value': 0.59625}, {'raw_hex': '#e42123', 'w3c': {'hex': '#dc143c', 'name': 'Crimson'}, 'value': 0.09675}, {'raw_hex': '#24242a', 'w3c': {'hex': '#000000', 'name': 'Black'}, 'value': 0.10125}, {'raw_hex': '#928f76', 'w3c': {'hex': '#808080', 'name': 'Gray'}, 'value': 0.16375}, {'raw_hex': '#f08b85', 'w3c': {'hex': '#f08080', 'name': 'LightCoral'}, 'value': 0.042}]

    colors = list(map(lambda c: {"embedding": c['w3c']['hex'],
                                 "prob": c['value']
                                 },
                      colors)
                  )

    colors.sort(key=lambda x: -x['prob'])

    colors = colors[:min(num_top, len(colors))]

    logger.info("predict_color. colors are: {}".format(colors))
    return colors


COLOR_PATTERNS = {
    "Yellow": {
        "message": "Yo, yellow guy!",
        "embedding": hex_to_3d("00ffff")
    },
    "Yellow Green Red": {
        "message": "Wassap, color guy!",
        "embedding": hex_to_3d("0ff44f")
    },
    "Black": {
        "message": "Hi, Nigger!",
        "embedding": hex_to_3d("000000")
    },
    "Orange Mint Magenta": {
        "message": "How r u, unicorn?",
        "embedding": hex_to_3d("aa98a9")
    },
}


def match_embedding_with_patterns(embedding, patterns):
    similarities = {}
    for key, item in patterns.items():
        similarities[key] = hex_embedding_similarity(item["embedding"], embedding)
    return similarities


def detect_close_patter(app, url):
    colors = predict_color(app, url)

    embeddings = np.array([hex_to_3d(item["embedding"]) for item in colors]).T
    probs = np.array([item["prob"] for item in colors])

    probs = probs / np.sum(np.abs(probs))

    logger.info("embeddings: {}".format(embeddings))
    logger.info(("probs: {}").format(probs))

    mean_embedding = np.sum(embeddings * probs, axis=1)

    logger.info("mean embedding: {}".format(mean_embedding))
    logger.info("patterns: {}".format(COLOR_PATTERNS))
    return match_embedding_with_patterns(mean_embedding, COLOR_PATTERNS)

def get_message_for_user(params):
    detected_color = params["detected_candy_type"]
    output = COLOR_PATTERNS[detected_color]['message']
    return output

def get_message_by_picture(app, url):
    closest_patterns = detect_close_patter(app, url)
    sorted_by_score = sorted(closest_patterns.items(), key=lambda x: x[1])

    logger.info("similarities: {}".format(sorted_by_score))
    top1key = sorted_by_score[0][0]

    payload = {
        "detected_candy_type": top1key
    }

    return get_message_for_user(payload)
