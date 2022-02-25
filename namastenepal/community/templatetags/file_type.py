from django import template
import os

register = template.Library()

images = ['.png', '.jpg', '.jpeg', '.gif', '.PNG', '.JPG', '.JPEG']
videos = ['.mp4', '.mov', '.MP4', '.MOV']


@register.simple_tag
def check_type(file):
    filename, ext = os.path.splitext(file)
    if ext in images:
        return 'images'
    elif ext in videos:
        return 'videos'
    else:
        return 'Error'
