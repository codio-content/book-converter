import logging

from subprocess import Popen, PIPE
from PIL import Image
from pathlib import Path


def run_command(command):
    command_process = Popen(
        command,
        stdin=open('/dev/null', 'w'),
        stdout=PIPE,
        stderr=PIPE
    )
    command_process.wait()
    command_output = command_process.communicate()
    rc = command_process.returncode
    logging.debug(f"{command}, {command_output}, {rc}")


def recursive_images_search(directory, glob, func, width):
    for filename in Path(directory).glob(glob):
        func(str(filename.absolute()), width)


def resize_images(image_path, options):
    image = Image.open(image_path)
    width, height = image.size
    image_width, image_height = options
    if width > image_width or height > image_height:
        logging.debug(f"thumbnail image {image_path}")
        image.thumbnail((image_width, image_height), Image.ANTIALIAS)
        image.save(image_path)


def optimize_jpg(image_path, options):
    logging.debug(f"optimize jpg {image_path}")
    run_command(['jpegoptim', image_path])


def optimize_png(image_path, options):
    logging.debug(f"optimize png {image_path}")
    run_command(['optipng', image_path])


def run_resize_images(config, directory):
    width = config.get('imageWidth', 0)
    height = config.get('imageHeight', 0)
    if width > 0 and height > 0:
        recursive_images_search(directory, '**/*.jpg', resize_images, (width, height))
        recursive_images_search(directory, '*.jpg', resize_images, (width, height))

        recursive_images_search(directory, '**/*.png', resize_images, (width, height))
        recursive_images_search(directory, '*.png', resize_images, (width, height))

    optimize_images = config.get('optimizeImages', False)
    if optimize_images:
        recursive_images_search(directory, '**/*.jpg', optimize_jpg, None)
        recursive_images_search(directory, '*.jpg', optimize_jpg, None)

        recursive_images_search(directory, '**/*.png', optimize_png, None)
        recursive_images_search(directory, '*.png', optimize_png, None)


def optimize(config, directory):
    optimization_config = config.get('optimization', {})
    if optimization_config:
        run_resize_images(optimization_config, directory)

