def clean_tags(tag_string):
    return [tag.strip() for tag in tag_string.split(',') if tag.strip()]