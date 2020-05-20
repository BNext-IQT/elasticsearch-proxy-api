"""
Utils functions to handle elasticsearch properties/data
"""
import re

from app.config import RUN_CONFIG

PROPERTY_REGEX = re.compile('[0-9A-Za-z_]*')
PROPERTY_NAME_IDS = {}
CAPS_REGEX = re.compile('[A-Z]')
VOWELS_REGEX = re.compile('[aeiouy]', flags=re.IGNORECASE)
SPACE_REGEX = re.compile(r'\s')
REPEATED_CHARACTERS_REGEX = re.compile(r'(.)\1+')

def get_resource_name(index_name):
    """
    :param index_name: index name for which to get the resource name
    :return: the resouce name based on the index name
    """
    es_index_prefix = RUN_CONFIG.get('es_index_prefix')
    resource_name = re.sub(fr'{es_index_prefix}(\d*_)?', '', index_name)

    return resource_name

def get_labels_from_property_name(index_name, prop_id):
    """
    :param index_name: index name for which to get the resource name
    :param prop_id: id of the property for which to get the label
    :return: a generated label for the property
    """
    entity_name = get_resource_name(index_name)

    prop_parts = prop_id.split('.')
    label = ''
    if len(prop_parts) > 1:
        if not prop_parts[-2] in ['_metadata', 'drug_data']:
            if not prop_parts[-2] in ['molecule_properties', 'drug']:
                label += standardize_label(prop_parts[-2], entity_name) + ' '
    label += standardize_label(prop_parts[-1], entity_name)
    if len(label) == 0:
        label = standardize_label(prop_parts[-1])
    label = remove_duplicate_words(label)
    label = label.strip()
    label_mini = abbreviate_label(label)
    return label, label_mini

def standardize_label(prop_part, entity_name=None):
    """
    :param prop_part: part of the name of the property, after splitting by .
    :param entity_name: name of the entity to which the property belongs
    :return: a standad label for the property part given as parameter
    """
    std_label = re.sub('_+', ' ', prop_part).strip()
    std_label = std_label.title()
    std_label = re.sub(r'\batc\b', 'ATC', std_label, flags=re.IGNORECASE)
    std_label = re.sub(r'\bbao\b', 'BAO', std_label, flags=re.IGNORECASE)
    std_label = re.sub(r'\bchembl\b', 'ChEMBL', std_label, flags=re.IGNORECASE)
    std_label = re.sub(r'\bid\b', 'ID', std_label, flags=re.IGNORECASE)
    std_label = re.sub(r'\busan\b', 'USAN', std_label, flags=re.IGNORECASE)
    std_label = re.sub(r'\bbei\b', 'BEI', std_label, flags=re.IGNORECASE)
    std_label = re.sub(r'\ble\b', 'LE', std_label, flags=re.IGNORECASE)
    std_label = re.sub(r'\blle\b', 'LLE', std_label, flags=re.IGNORECASE)
    std_label = re.sub(r'\bsei\b', 'SEI', std_label, flags=re.IGNORECASE)
    std_label = re.sub(r'\befo\b', 'EFO', std_label, flags=re.IGNORECASE)
    std_label = re.sub(r'\buberon\b', 'UBERON', std_label, flags=re.IGNORECASE)
    std_label = re.sub(r'\bmesh\b', 'MESH', std_label, flags=re.IGNORECASE)
    std_label = re.sub(r'\bnum\b', '#', std_label, flags=re.IGNORECASE)
    if entity_name is not None:
        std_label = re.sub(r'\bgenerated\b', '', std_label, flags=re.IGNORECASE)
        std_label = re.sub(r'\b' + entity_name + r'\b', '', std_label, flags=re.IGNORECASE)
        if entity_name == 'molecule':
            std_label = re.sub(r'\bcompound\b', '', std_label, flags=re.IGNORECASE)
        if entity_name == 'cell_line':
            std_label = re.sub(r'\bcell\b', '', std_label, flags=re.IGNORECASE)
            std_label = re.sub(r'\bline\b', '', std_label, flags=re.IGNORECASE)

    return std_label.strip()

def remove_duplicate_words(sentence):
    """
    :param sentence: sentence for which remove the duplicate words
    :return: a sentence without the duplicate words
    """
    words = SPACE_REGEX.split(sentence)
    words_set = set()
    clean_sentence = ''
    for word in words:
        if word.lower() == 'pref':
            continue
        if word not in words_set:
            clean_sentence += word + ' '
            if word.endswith('s'):
                words_set.add(word[:-1])
            elif word.endswith('es'):
                words_set.add(word[:-2])
            elif word.endswith('ies'):
                words_set.add(word[:-3])
            else:
                words_set.add(word)
    return clean_sentence

def abbreviate_label(std_label):
    """
    :param std_label:
    :return: a
    """

    words = SPACE_REGEX.split(std_label)
    max_word_length = 10
    if 15 < len(std_label) <= 20:
        max_word_length = 6
    elif len(std_label) > 20:
        max_word_length = 4

    abbreviated_words = []
    for word in words:
        abbreviated_words.append(abbreviate_word(word, max_word_length))
    return ' '.join(abbreviated_words)

def abbreviate_word(word, max_word_length):
    if len(word) <= max_word_length:
        return word
    total_caps = len(CAPS_REGEX.findall(word))
    if total_caps > round(len(word) / 2):
        return word
    inner_word = word[1:]
    next_vowel_match = VOWELS_REGEX.search(inner_word)
    if next_vowel_match is not None:
        next_vowel_idx = next_vowel_match.pos
        after_vowel = inner_word[next_vowel_idx + 1:]
        pre_vowel = inner_word[:next_vowel_idx + 1]

        inner_word = pre_vowel + VOWELS_REGEX.sub('', after_vowel)
        if REPEATED_CHARACTERS_REGEX.search(inner_word):
            inner_word = REPEATED_CHARACTERS_REGEX.sub(r'\1', inner_word)
    return word[0] + inner_word[:max_word_length - 1] + '.'