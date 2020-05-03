from xml.etree import ElementTree
from constants import SENTIMENT_RAW_DATA_DIR
from os.path import splitext
from utils import init_logger
from tqdm import tqdm
from datasets.utils import TOKEN_SEPARATOR, WORD_POS_SEPARATOR, clean_review
from Timer import timer
import spacy
import numpy as np

LOGGER = init_logger(__name__)


@timer
def main():
    tagger = spacy.load("en_core_web_lg")
    for domain in ("books", "dvd", "electronics", "kitchen"):
        LOGGER.info(f"{domain.title()} Dataset")
        dataset_dir = f"{SENTIMENT_RAW_DATA_DIR}/{domain}"
        for file in (f"{domain}UN.txt", "negative.parsed", "positive.parsed"):
            tag_xml_dataset(f"{dataset_dir}/{file}", tagger)


def tag_xml_dataset(dataset_file, tagger):
    LOGGER.info(f"Tagging {dataset_file}")
    data_tree = ElementTree.parse(dataset_file)
    tagged_dataset = []
    untagged_dataset = []
    num_adj = 0
    num_adv = 0
    num_words = 0
    review_lengths = []
    for review in tqdm(data_tree.iter("review")):
        review_text = clean_review(review.text)
        untagged_dataset.append(review_text)
        tagged_review_text = []
        for token in tagger(review_text):
            tagged_review_text.append(f"{token.text}{WORD_POS_SEPARATOR}{token.pos_}")
            num_words += 1
            if token.pos_ == "ADJ":
                num_adj += 1
            if token.pos_ == "ADV":
                num_adv += 1
        review_lengths.append(len(tagged_review_text))
        tagged_dataset.append(TOKEN_SEPARATOR.join(tagged_review_text))
    LOGGER.info(f"Number of reviews: {len(tagged_dataset)}")
    LOGGER.info(f"Number of words: {num_words}")
    LOGGER.info(f"Maximum number of words per review: {np.max(review_lengths)}")
    LOGGER.info(f"Minimum number of words per review: {np.min(review_lengths)}")
    LOGGER.info(f"Average number of words per review: {np.mean(review_lengths)}")
    LOGGER.info(f"Median number of words per review: {np.median(review_lengths)}")
    LOGGER.info(f"Number of adjectives: {num_adj}")
    LOGGER.info(f"Total Adjectives ratio: {float(num_adj)/num_words}")
    LOGGER.info(f"Number of adverbs: {num_adv}")
    LOGGER.info(f"Total Adverbs ratio: {float(num_adv)/num_words}")
    LOGGER.info(f"Total Adverbs + Adjectives ratio: {float(num_adv + num_adj)/num_words}\n")
    _, file_ext = splitext(dataset_file)
    untagged_dataset_file = f"{dataset_file.replace(file_ext, f'_clean{file_ext}')}"
    with open(untagged_dataset_file, "w") as tagged_file:
        tagged_file.write("\n".join(untagged_dataset))
    tagged_dataset_file = f"{dataset_file.replace(file_ext, f'_tagged{file_ext}')}"
    with open(tagged_dataset_file, "w") as tagged_file:
        tagged_file.write("\n".join(tagged_dataset))


if __name__ == "__main__":
    main()
