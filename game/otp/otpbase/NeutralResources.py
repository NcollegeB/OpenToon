"""Build Open Town's local presentation overlay from the resource snapshot.

The upstream resource archive is intentionally a separate, ignored checkout.
This module keeps Open Town's authored presentation changes reproducible
without committing or modifying that archive.  Generated files mirror their
original resource paths under ``game/open_town_assets``; Configrc places that
directory ahead of ``game/resources`` on Panda3D's model path.
"""

from __future__ import print_function

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys

from panda3d.core import (
    Filename,
    LColor,
    Loader,
    LoaderOptions,
    NodePath,
    PNMBrush,
    PNMImage,
    PNMPainter,
    PNMTextMaker,
    get_model_path,
)


GAME_ROOT = Path(__file__).resolve().parents[2]
RESOURCE_ROOT = GAME_ROOT / 'resources'
OVERLAY_ROOT = GAME_ROOT / 'open_town_assets'
MARKER_PATH = OVERLAY_ROOT / '.neutral-resources.json'
GENERATOR_VERSION = 4
PINNED_RESOURCE_REVISION = (
    'd8c73a9978633979ddf2ef8813f0152037a0d978'
)

FONT_PATH = Path('phase_3/models/fonts/ImpressBT.ttf')

GAG_SIGN_PATHS = (
    Path('phase_3.5/maps/GS_sign.png'),
    Path('phase_8/maps/GS_signBIG_BR.png'),
)

DESTINATION_SIGNS = {
    'central': {
        'path': Path('phase_3.5/maps/sign_toontown_central.png'),
        'alias': Path('phase_4/maps/sign_central_commons.png'),
        'lines': ('CENTRAL', 'COMMONS'),
        'colors': ((0.95, 0.54, 0.12, 1), (0.18, 0.48, 0.20, 1)),
        'icon': 'star',
    },
    'dock': {
        'path': Path('phase_4/maps/sign_donaldSdock.png'),
        'lines': ('ANCHOR', 'BAY'),
        'colors': ((0.08, 0.45, 0.70, 1), (0.02, 0.18, 0.35, 1)),
        'icon': 'anchor',
    },
    'garden': {
        'path': Path('phase_4/maps/sign_daisysGarden.png'),
        'lines': ('BLOOM', 'GARDENS'),
        'colors': ((0.72, 0.22, 0.58, 1), (0.18, 0.48, 0.20, 1)),
        'icon': 'flower',
    },
    'melody': {
        'path': Path('phase_4/maps/sign_minnies_melodyland.png'),
        'lines': ('MELODY', 'MEADOWS'),
        'colors': ((0.55, 0.22, 0.72, 1), (0.20, 0.10, 0.35, 1)),
        'icon': 'music',
    },
    'dream': {
        'path': Path('phase_4/maps/sign_dreamland.png'),
        'alias': Path('phase_4/maps/sign_moonlight_meadows.png'),
        'lines': ('MOONLIGHT', 'MEADOWS'),
        'colors': ((0.18, 0.25, 0.62, 1), (0.05, 0.08, 0.28, 1)),
        'icon': 'moon',
    },
}

# Each map uses the original 128x128 destination art at a 64x64 endpoint.
# Coordinates are populated from the pinned d8c73a9 resource snapshot.
MAP_SIGN_PLACEMENTS = {
    'daisys_garden_5100': (
        ('garden', 8, 259, 42),
        ('central', 455, 214, 41),
    ),
    'daisys_garden_5200': (
        ('garden', 18, 233, 42),
        ('dock', 454, 200, 42),
    ),
    'daisys_garden_5300': (
        ('garden', 226, 377, 52),
    ),
    'donalds_dock_1100': (
        ('dock', 80, 136, 47),
        ('central', 278, 114, 58),
    ),
    'donalds_dock_1200': (
        ('dock', 276, 23, 65),
        ('garden', 157, 363, 66),
    ),
    'donalds_dock_1300': (
        ('dock', 17, 191, 52),
    ),
    'donalds_dreamland_9100': (
        ('dream', 301, 4, 51),
        ('melody', 201, 428, 69),
    ),
    'donalds_dreamland_9200': (
        ('dream', 226, 6, 59),
    ),
    'minnies_melody_land_4100': (
        ('central', 139, 103, 45),
        ('melody', 446, 269, 53),
    ),
    'minnies_melody_land_4200': (
        ('melody', 282, 422, 53),
    ),
    'minnies_melody_land_4300': (
        ('dream', 19, 261, 53),
        ('melody', 434, 103, 67),
    ),
    'the_burrrgh_3100': (
        ('dock', 398, 37, 50),
    ),
    'the_burrrgh_3200': (
        ('melody', 149, 168, 59),
    ),
    'toontown_central_2100': (
        ('central', 322, 9, 46),
        ('garden', 96, 260, 43),
    ),
    'toontown_central_2200': (
        ('melody', 21, 272, 46),
        ('central', 457, 154, 45),
    ),
    'toontown_central_2300': (
        ('central', 14, 245, 46),
        ('dock', 458, 214, 46),
    ),
}

PORTRAIT_MODEL_PATHS = (
    Path('phase_3.5/models/props/mickeySZ.bam'),
    Path('phase_4/models/props/minnieSZ.bam'),
    Path('phase_4/models/props/donaldSZ.bam'),
    Path('phase_4/models/props/donald_DL_SZ.bam'),
    Path('phase_4/models/props/daisySZ.bam'),
    Path('phase_4/models/props/goofySZ.bam'),
    Path('phase_4/models/props/plutoSZ.bam'),
)

LANDMARK_MODEL_PATHS = (
    Path('phase_4/models/props/mickey_on_horse.bam'),
    Path('phase_4/models/props/goofy_statue.bam'),
)

ACORN_MODELS = {
    Path('phase_6/models/golf/chip_dale_enterance.bam'):
        Path('phase_6/models/golf/chip_dale_enterance.bam'),
    Path('phase_6/models/golf/chip_dale_NoSign_enterance.bam'):
        Path('phase_6/models/golf/chip_dale_NoSign_enterance.bam'),
}

QUEST_SCRIPTS_PATH = Path('phase_3/etc/QuestScripts.txt')

PINNED_SOURCE_PATHS = (
    FONT_PATH,
    QUEST_SCRIPTS_PATH,
    Path('phase_3.5/models/gui/name_star.bam'),
    Path('phase_3.5/models/props/big_planter.bam'),
) + tuple(
    Path('phase_4/maps/%s_english.png' % name)
    for name in sorted(MAP_SIGN_PLACEMENTS)
) + (
    Path('phase_6/models/golf/chip_dale_NoSign_enterance.bam'),
    Path('phase_6/models/golf/chip_dale_enterance.bam'),
)
PINNED_SOURCE_FINGERPRINT = (
    'bffe8ccbe77f8ea4227af5e6455ea56017b3a09be90b9b1025aa4d056cfe1c93'
)

# Longer expressions run before individual words.  These substitutions apply
# only to displayed DNA titles and sign baselines, never to internal codes,
# model names, filenames, group names, or distributed-class identifiers.
DISPLAY_REPLACEMENTS = (
    (r"Chip\s+(?:'n|n')\s+Dale's\s+Acorn\s+Acres", 'Acorn Acres'),
    (r"Chip\s+(?:'n|n')\s+Dale's\s+MiniGolf", 'Acorn MiniGolf'),
    (r"Donald's\s+Dreamland", 'Moonlight Meadows'),
    (r"Donald's\s+Dock", 'Anchor Bay'),
    (r"Minnie's\s+Melodyland", 'Melody Meadows'),
    (r'Daisy\s+Gardens', 'Bloom Gardens'),
    (r'Goofy\s+Speedway', 'Turbo Speedway'),
    (r'Toontown\s+Central', 'Central Commons'),
    (r"Goofy's\s+Gag\s+Shops?", 'Gag Shop'),
    (r"Chip\s+(?:'n|n')\s+Dale's", 'Acorn Acres'),
    (r'Mickey\s+Mouse', 'Milo Mouse'),
    (r'Minnie\s+Mouse', 'Millie Mouse'),
    (r'Donald\s+Duck', 'Duncan Duck'),
    (r'Daisy\s+Duck', 'Dahlia Duck'),
    (r'Mickey', 'Milo'),
    (r'Minnie', 'Millie'),
    (r'Donald', 'Duncan'),
    (r'Daisy', 'Dahlia'),
    (r'Goofy', 'Gus'),
    (r'Pluto', 'Pogo'),
    (r'Chip', 'Pip'),
    (r'Dale', 'Pebble'),
    (r'Toontown', 'Open Town'),
    (r'Disney', 'Legacy'),
)

COMPILED_DISPLAY_REPLACEMENTS = tuple(
    (re.compile(r'(?<![A-Za-z])(?:%s)(?![A-Za-z])' % pattern, re.I),
     replacement)
    for pattern, replacement in DISPLAY_REPLACEMENTS
)

TITLE_PATTERN = re.compile(
    r'(\btitle\s*\[\s*")((?:[^"\\]|\\.)*)("\s*\])',
    re.I,
)
LETTERS_PATTERN = re.compile(
    r'\bletters\s*\[\s*"((?:[^"\\]|\\.)*)"\s*\]',
    re.I,
)


class NeutralResourceError(RuntimeError):
    """Raised when the local neutral overlay cannot be built safely."""


def _resource(relative_path):
    path = RESOURCE_ROOT / relative_path
    if not path.is_file():
        raise NeutralResourceError(
            'Required resource is missing: %s. Run Setup OpenToon first.'
            % path
        )
    return path


def _git_resource_revision():
    git_metadata = RESOURCE_ROOT / '.git'
    if git_metadata.is_file():
        try:
            first_line = git_metadata.read_text(encoding='utf-8').strip()
        except OSError:
            return None
        if first_line.lower().startswith('gitdir:'):
            git_metadata = (
                RESOURCE_ROOT / first_line.split(':', 1)[1].strip()
            ).resolve()
    head_path = git_metadata / 'HEAD'
    try:
        head = head_path.read_text(encoding='ascii').strip()
    except OSError:
        return None
    if head.startswith('ref:'):
        reference_path = git_metadata / head.split(':', 1)[1].strip()
        try:
            head = reference_path.read_text(encoding='ascii').strip()
        except OSError:
            return None
    if re.fullmatch(r'[0-9a-fA-F]{40}', head):
        return head.lower()
    return None


def _pinned_source_fingerprint():
    digest = hashlib.sha256()
    for relative_path in PINNED_SOURCE_PATHS:
        digest.update(relative_path.as_posix().encode('utf-8'))
        digest.update(b'\0')
        with _resource(relative_path).open('rb') as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b''):
                digest.update(chunk)
        digest.update(b'\0')
    return digest.hexdigest()


def _resource_revision():
    revision = _git_resource_revision()
    if revision is not None:
        return revision
    try:
        fingerprint = _pinned_source_fingerprint()
    except (NeutralResourceError, OSError):
        return None
    if fingerprint == PINNED_SOURCE_FINGERPRINT:
        return PINNED_RESOURCE_REVISION
    return None


def _validate_resource_revision():
    revision = _resource_revision()
    if revision is None:
        raise NeutralResourceError(
            'The resource snapshot could not be matched to the supported '
            'revision %s. Move the incompatible game/resources directory '
            'aside, then run Setup OpenToon again.'
            % PINNED_RESOURCE_REVISION
        )
    if revision != PINNED_RESOURCE_REVISION:
        raise NeutralResourceError(
            'The neutral overlay targets resource revision %s, but the local '
            'snapshot is %s. Run Setup OpenToon with the pinned snapshot.'
            % (PINNED_RESOURCE_REVISION, revision)
        )
    return revision


def _output(relative_path):
    path = OVERLAY_ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _filename(path):
    return Filename.from_os_specific(str(path))


def _ensure_resource_model_path():
    resource_directory = _filename(RESOURCE_ROOT)
    if resource_directory not in get_model_path().get_directories():
        # Keep this lookup behind the normal search entries. QuickStart loads
        # Configrc after a first-run build, where open_town_assets must still
        # take precedence over resources.
        get_model_path().append_directory(resource_directory)


def _color(values):
    return LColor(*values)


def _new_rgba(width, height):
    image = PNMImage(width, height, 4)
    image.fill(0, 0, 0)
    image.alpha_fill(0)
    return image


def _paint_rectangle(image, bounds, color):
    painter = PNMPainter(image)
    brush = PNMBrush.make_pixel(_color(color), PNMBrush.BE_set)
    painter.set_pen(brush)
    painter.set_fill(brush)
    painter.draw_rectangle(*bounds)


def _paint_line(image, start, end, color, width=1):
    painter = PNMPainter(image)
    painter.set_pen(PNMBrush.make_pixel(
        _color(color),
        PNMBrush.BE_blend,
    ))
    x1, y1 = start
    x2, y2 = end
    radius = max(0, int(width) // 2)
    for offset in range(-radius, radius + 1):
        painter.draw_line(x1 + offset, y1, x2 + offset, y2)
        if offset:
            painter.draw_line(x1, y1 + offset, x2, y2 + offset)


def _paint_spot(image, center, radius, color):
    diameter = max(2, int(radius * 2))
    spot = _new_rgba(diameter, diameter)
    spot.render_spot(
        _color(color),
        LColor(0, 0, 0, 0),
        0.88,
        1.0,
    )
    x = int(center[0] - diameter / 2)
    y = int(center[1] - diameter / 2)
    image.blend_sub_image(spot, x, y, 0, 0, diameter, diameter, 1.0)


def _text_maker(pixel_size, color, align=PNMTextMaker.A_center):
    maker = PNMTextMaker(_filename(_resource(FONT_PATH)), 0)
    if not maker.is_valid():
        raise NeutralResourceError('Could not load sign font: %s' % FONT_PATH)
    maker.set_pixel_size(pixel_size)
    maker.set_align(align)
    maker.set_fg(_color(color))
    return maker


def _draw_centered_text(image, text, y, max_width, pixel_size,
                        color=(1, 1, 1, 1), shadow=True):
    size = int(pixel_size)
    while size > 7:
        maker = _text_maker(size, color)
        if maker.calc_width(text) <= max_width:
            break
        size -= 1
    if shadow:
        shadow_maker = _text_maker(size, (0, 0, 0, 0.85))
        shadow_maker.generate_into(text, image, image.get_x_size() // 2 + 2,
                                   int(y) + 2)
    maker.generate_into(text, image, image.get_x_size() // 2, int(y))


def _draw_destination_icon(image, icon):
    light = (1.0, 0.92, 0.35, 1)
    dark = (0.03, 0.08, 0.14, 1)
    if icon == 'star':
        points = (
            ((64, 18), (64, 55)),
            ((45, 37), (83, 37)),
            ((50, 23), (78, 51)),
            ((78, 23), (50, 51)),
        )
        for start, end in points:
            _paint_line(image, start, end, dark, 7)
            _paint_line(image, start, end, light, 4)
    elif icon == 'anchor':
        _paint_spot(image, (64, 22), 8, light)
        _paint_spot(image, (64, 22), 4, dark)
        _paint_line(image, (64, 29), (64, 56), dark, 7)
        _paint_line(image, (64, 29), (64, 56), light, 4)
        _paint_line(image, (43, 43), (50, 55), light, 4)
        _paint_line(image, (85, 43), (78, 55), light, 4)
        _paint_line(image, (48, 54), (80, 54), light, 4)
    elif icon == 'flower':
        for center in ((64, 20), (48, 32), (80, 32), (53, 49), (75, 49)):
            _paint_spot(image, center, 12, light)
        _paint_spot(image, (64, 36), 11, (0.95, 0.48, 0.12, 1))
    elif icon == 'music':
        _paint_line(image, (57, 21), (57, 49), dark, 8)
        _paint_line(image, (78, 16), (78, 43), dark, 8)
        _paint_line(image, (57, 21), (78, 16), dark, 8)
        _paint_line(image, (57, 21), (57, 49), light, 4)
        _paint_line(image, (78, 16), (78, 43), light, 4)
        _paint_line(image, (57, 21), (78, 16), light, 4)
        _paint_spot(image, (50, 50), 9, light)
        _paint_spot(image, (71, 44), 9, light)
    elif icon == 'moon':
        _paint_spot(image, (62, 35), 23, light)
        _paint_spot(image, (72, 27), 20, (0.05, 0.08, 0.28, 1))
        _paint_spot(image, (91, 22), 4, (1, 1, 0.75, 1))


def _build_destination_sign(specification):
    outer, inner = specification['colors']
    image = _new_rgba(128, 128)
    _paint_rectangle(image, (3, 5, 124, 124), (0.02, 0.03, 0.06, 0.75))
    _paint_rectangle(image, (1, 1, 126, 120), (1.0, 0.86, 0.25, 1))
    _paint_rectangle(image, (5, 5, 122, 116), outer)
    _paint_rectangle(image, (10, 10, 117, 112), inner)
    _draw_destination_icon(image, specification['icon'])
    first, second = specification['lines']
    _draw_centered_text(image, first, 82, 104, 19)
    _draw_centered_text(image, second, 104, 104, 19)
    return image


def _build_gag_sign(width, height, cold_palette=False):
    image = _new_rgba(width, height)
    if cold_palette:
        outer = (0.18, 0.72, 0.52, 1)
        inner = (0.03, 0.28, 0.24, 1)
    else:
        outer = (0.96, 0.60, 0.08, 1)
        inner = (0.52, 0.08, 0.14, 1)
    margin = max(6, width // 32)
    _paint_rectangle(
        image,
        (margin, margin * 2, width - margin - 1, height - margin - 1),
        (0.02, 0.03, 0.06, 0.78),
    )
    _paint_rectangle(
        image,
        (margin // 2, margin // 2, width - margin, height - margin * 2),
        (1.0, 0.88, 0.22, 1),
    )
    _paint_rectangle(
        image,
        (margin, margin, width - margin * 2, height - margin * 2 - 1),
        outer,
    )
    _paint_rectangle(
        image,
        (margin * 2, margin * 2, width - margin * 3,
         height - margin * 3),
        inner,
    )
    _paint_spot(image, (width * 0.21, height * 0.26),
                width * 0.065, (0.98, 0.38, 0.45, 1))
    _paint_spot(image, (width * 0.79, height * 0.26),
                width * 0.065, (0.30, 0.72, 1.0, 1))
    _draw_centered_text(
        image,
        'GAG SHOP',
        height * 0.62,
        width * 0.78,
        width * 0.20,
    )
    return image


def _write_image(image, relative_path):
    destination = _output(relative_path)
    if not image.write(_filename(destination)):
        raise NeutralResourceError('Could not write image: %s' % destination)
    return relative_path


def _build_signs():
    outputs = []
    generated = {}
    for key, specification in DESTINATION_SIGNS.items():
        image = _build_destination_sign(specification)
        generated[key] = image
        outputs.append(_write_image(image, specification['path']))
        alias = specification.get('alias')
        if alias:
            outputs.append(_write_image(image, alias))

    for index, relative_path in enumerate(GAG_SIGN_PATHS):
        source = PNMImage()
        if not source.read(_filename(_resource(relative_path))):
            raise NeutralResourceError('Could not read %s' % relative_path)
        image = _build_gag_sign(
            source.get_x_size(),
            source.get_y_size(),
            cold_palette=(index == 1),
        )
        outputs.append(_write_image(image, relative_path))
    return generated, outputs


def _build_street_maps(generated_signs):
    outputs = []
    for map_name, placements in MAP_SIGN_PLACEMENTS.items():
        relative_path = Path('phase_4/maps/%s_english.png' % map_name)
        image = PNMImage()
        if not image.read(_filename(_resource(relative_path))):
            raise NeutralResourceError('Could not read %s' % relative_path)
        for sign_key, x, y, size in placements:
            replacement = PNMImage(int(size), int(size), 4)
            replacement.quick_filter_from(generated_signs[sign_key])
            image.blend_sub_image(
                replacement,
                int(x),
                int(y),
                0,
                0,
                int(size),
                int(size),
                1.0,
            )
        outputs.append(_write_image(image, relative_path))
    return outputs


def _copy_model(source_relative_path, output_relative_path):
    source = _resource(source_relative_path)
    destination = _output(output_relative_path)
    shutil.copy2(str(source), str(destination))
    return output_relative_path


def _collision_solid_count(node_path):
    total = 0
    for collision in node_path.find_all_matches('**/+CollisionNode'):
        total += collision.node().get_num_solids()
    return total


def _build_acorn_model(source_relative_path, output_relative_path):
    source = _resource(source_relative_path)
    options = LoaderOptions(LoaderOptions.LF_no_cache)
    node = Loader.get_global_ptr().load_sync(_filename(source), options)
    if node is None:
        raise NeutralResourceError('Could not load model: %s' % source)
    model = NodePath(node)
    original_collision_count = _collision_solid_count(model)
    character = model.find('**/chip_dale')
    if character.is_empty():
        raise NeutralResourceError(
            'Expected character subtree was not found in %s' % source
        )
    character.remove_node()
    if _collision_solid_count(model) != original_collision_count:
        raise NeutralResourceError(
            'Collision geometry changed while neutralizing %s' % source
        )
    destination = _output(output_relative_path)
    if not model.write_bam_file(_filename(destination)):
        raise NeutralResourceError('Could not write model: %s' % destination)
    return output_relative_path


def _build_renamed_model(source_relative_path, output_relative_path,
                         source_node_name, output_node_name):
    source = _resource(source_relative_path)
    options = LoaderOptions(LoaderOptions.LF_no_cache)
    node = Loader.get_global_ptr().load_sync(_filename(source), options)
    if node is None:
        raise NeutralResourceError('Could not load model: %s' % source)
    model = NodePath(node)
    source_node = model.find('**/%s' % source_node_name)
    if source_node.is_empty():
        raise NeutralResourceError(
            'Expected node %s was not found in %s.'
            % (source_node_name, source)
        )
    source_node.set_name(output_node_name)
    destination = _output(output_relative_path)
    if not model.write_bam_file(_filename(destination)):
        raise NeutralResourceError('Could not write model: %s' % destination)
    return output_relative_path


def _build_models():
    outputs = []
    _ensure_resource_model_path()

    neutral_portrait = Path('phase_3.5/models/gui/name_star.bam')
    for output_path in PORTRAIT_MODEL_PATHS:
        outputs.append(_build_renamed_model(
            neutral_portrait,
            output_path,
            'name_star',
            output_path.stem,
        ))

    neutral_landmark = Path('phase_3.5/models/props/big_planter.bam')
    for output_path in LANDMARK_MODEL_PATHS:
        outputs.append(_copy_model(neutral_landmark, output_path))

    for source_path, output_path in ACORN_MODELS.items():
        outputs.append(_build_acorn_model(source_path, output_path))
    return outputs


def _match_case(source, replacement):
    if source.isupper():
        return replacement.upper()
    if source.islower():
        return replacement.lower()
    return replacement


def _neutralize_display_text(value):
    result = value
    protected = []
    for index, phrase in enumerate(('Daisy Lamp', 'Pink Daisy')):
        token = '\x00open-town-%d\x00' % index
        if phrase in result:
            result = result.replace(phrase, token)
            protected.append((token, phrase))
    for pattern, replacement in COMPILED_DISPLAY_REPLACEMENTS:
        result = pattern.sub(
            lambda match: _match_case(match.group(0), replacement),
            result,
        )
    for token, phrase in protected:
        result = result.replace(token, phrase)
    return result


def _find_keyword_blocks(text, keyword):
    pattern = re.compile(r'\b%s\s*\[' % re.escape(keyword), re.I)
    position = 0
    while True:
        match = pattern.search(text, position)
        if match is None:
            return
        opening = text.find('[', match.start(), match.end())
        depth = 0
        quoted = False
        escaped = False
        for index in range(opening, len(text)):
            character = text[index]
            if quoted:
                if escaped:
                    escaped = False
                elif character == '\\':
                    escaped = True
                elif character == '"':
                    quoted = False
            elif character == '"':
                quoted = True
            elif character == '[':
                depth += 1
            elif character == ']':
                depth -= 1
                if depth == 0:
                    yield match.start(), index + 1
                    position = index + 1
                    break
        else:
            raise NeutralResourceError(
                'Unbalanced %s block in DNA text.' % keyword
            )


def _decode_dna_string(value):
    return value.replace(r'\"', '"').replace(r'\\', '\\')


def _encode_dna_string(value):
    return value.replace('\\', r'\\').replace('"', r'\"')


def _rewrite_baseline(block):
    text_blocks = list(_find_keyword_blocks(block, 'text'))
    if not text_blocks:
        return block
    pieces = []
    for start, end in text_blocks:
        matches = LETTERS_PATTERN.findall(block[start:end])
        pieces.extend(_decode_dna_string(value) for value in matches)
    original = ''.join(pieces)
    replacement = _neutralize_display_text(original)
    if replacement == original:
        return block

    first_start = text_blocks[0][0]
    last_end = text_blocks[-1][1]
    between = block[first_start:last_end]
    stripped = LETTERS_PATTERN.sub('', between)
    stripped = re.sub(r'\btext\s*\[|\]', '', stripped, flags=re.I)
    if stripped.strip():
        raise NeutralResourceError(
            'A displayed DNA baseline contains unsupported text metadata.'
        )

    line_start = block.rfind('\n', 0, first_start) + 1
    indent = block[line_start:first_start]
    child_indent = indent + ' '
    rebuilt = []
    for character in replacement:
        rebuilt.append(
            '%stext [\n%s letters [ "%s" ]\n%s]'
            % (
                indent,
                child_indent,
                _encode_dna_string(character),
                indent,
            )
        )
    return block[:first_start] + '\n'.join(rebuilt) + block[last_end:]


def _rewrite_dna(source_text):
    def replace_title(match):
        original = _decode_dna_string(match.group(2))
        replacement = _neutralize_display_text(original)
        return (
            match.group(1)
            + _encode_dna_string(replacement)
            + match.group(3)
        )

    rewritten = TITLE_PATTERN.sub(replace_title, source_text)
    blocks = list(_find_keyword_blocks(rewritten, 'baseline'))
    for start, end in reversed(blocks):
        replacement = _rewrite_baseline(rewritten[start:end])
        rewritten = rewritten[:start] + replacement + rewritten[end:]
    return rewritten


def _build_dna():
    outputs = []
    for source in sorted(RESOURCE_ROOT.glob('phase_*/dna/*.dna')):
        relative_path = source.relative_to(RESOURCE_ROOT)
        source_text = source.read_text(encoding='utf-8')
        rewritten = _rewrite_dna(source_text)
        if rewritten == source_text:
            continue
        destination = _output(relative_path)
        destination.write_text(rewritten, encoding='utf-8')
        outputs.append(relative_path)
    return outputs


def _build_quest_scripts():
    source = _resource(QUEST_SCRIPTS_PATH)
    text = source.read_text(encoding='utf-8')
    block_match = re.search(
        r'(?ms)^ID tutorial_mickey\s*$.*?(?=^ID\s+|\Z)',
        text,
    )
    if block_match is None:
        raise NeutralResourceError(
            'The tutorial_mickey quest script block was not found.'
        )
    guide_lines = []
    for line in block_match.group(0).rstrip().splitlines():
        stripped = line.strip()
        if (
            stripped.startswith('LOAD_CC_DIALOGUE ')
            or stripped.startswith('LOAD_DIALOGUE mickeyTutorialDialogue_')
        ):
            continue
        if stripped == 'ID tutorial_mickey':
            line = 'ID tutorial_guide'
        elif stripped == 'LOAD_CLASSIC_CHAR classicChar':
            line = 'LOAD_TOON_GUIDE tutorialGuide'
        else:
            line = re.sub(r'\bclassicChar\b', 'tutorialGuide', line)

        stripped = line.strip()
        if (
            stripped.startswith('CC_CHAT_CONFIRM tutorialGuide ')
            and 'QuestScriptTutorial%s_1' in stripped
        ):
            line = (
                'LOCAL_CHAT_CONFIRM tutorialGuide '
                'QuestScriptTutorialGuide_1'
            )
        elif stripped.startswith(
                'CC_CHAT_TO_CONFIRM npc tutorialGuide '):
            line = (
                'LOCAL_CHAT_CONFIRM npc QuestScriptTutorialGuide_2 '
                '"CFReversed"'
            )
        elif (
            stripped.startswith('CC_CHAT_CONFIRM tutorialGuide ')
            and 'QuestScriptTutorial%s_3' in stripped
        ):
            line = (
                'LOCAL_CHAT_CONFIRM tutorialGuide '
                'QuestScriptTutorialGuide_3'
            )
        elif stripped.startswith(
                'LOCAL_CHAT_PERSIST npc QuestScriptTutorialMickey_4'):
            line = (
                'LOCAL_CHAT_PERSIST npc QuestScriptTutorialGuide_4'
            )
        guide_lines.append(line)

    guide_block = '\n'.join(guide_lines).rstrip() + '\n\n'
    compatibility_lines = list(guide_lines)
    compatibility_lines[0] = 'ID tutorial_mickey'
    compatibility_block = (
        '\n'.join(compatibility_lines).rstrip() + '\n\n'
    )
    existing_guide = re.search(
        r'(?ms)^ID tutorial_guide\s*$.*?(?=^ID\s+|\Z)',
        text,
    )
    if existing_guide is not None:
        text = (
            text[:existing_guide.start()]
            + text[existing_guide.end():]
        )
        block_match = re.search(
            r'(?ms)^ID tutorial_mickey\s*$.*?(?=^ID\s+|\Z)',
            text,
        )
    rewritten = (
        text[:block_match.start()]
        + compatibility_block
        + guide_block
        + text[block_match.end():]
    )
    destination = _output(QUEST_SCRIPTS_PATH)
    destination.write_text(rewritten, encoding='utf-8')
    return QUEST_SCRIPTS_PATH


def _sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _write_marker(outputs):
    relative_outputs = sorted(str(path).replace(os.sep, '/') for path in outputs)
    payload = {
        'generator_version': GENERATOR_VERSION,
        'resource_revision': _resource_revision(),
        'outputs': relative_outputs,
    }
    OVERLAY_ROOT.mkdir(parents=True, exist_ok=True)
    temporary = MARKER_PATH.with_suffix('.tmp')
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + '\n',
        encoding='utf-8',
    )
    os.replace(str(temporary), str(MARKER_PATH))


def _read_current_marker():
    try:
        payload = json.loads(MARKER_PATH.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
    if payload.get('generator_version') != GENERATOR_VERSION:
        return None
    current_revision = _resource_revision()
    marker_revision = payload.get('resource_revision')
    if current_revision is not None and marker_revision != current_revision:
        return None
    outputs = payload.get('outputs')
    if not isinstance(outputs, list) or not outputs:
        return None
    if any(not (OVERLAY_ROOT / path).is_file() for path in outputs):
        return None
    return payload


def build_neutral_resources(force=False):
    """Build the overlay and return its marker payload."""
    if not RESOURCE_ROOT.is_dir():
        raise NeutralResourceError(
            'The resource snapshot is missing: %s. Run Setup OpenToon first.'
            % RESOURCE_ROOT
        )
    _validate_resource_revision()
    if not force:
        current = _read_current_marker()
        if current is not None:
            return current

    print('Building Open Town neutral presentation assets...')
    try:
        MARKER_PATH.unlink()
    except FileNotFoundError:
        pass
    generated_signs, outputs = _build_signs()
    outputs.extend(_build_street_maps(generated_signs))
    outputs.extend(_build_models())
    outputs.extend(_build_dna())
    outputs.append(_build_quest_scripts())
    _write_marker(outputs)
    print(
        'Built %d neutral overlay files in %s.'
        % (len(outputs), OVERLAY_ROOT)
    )
    return _read_current_marker()


def ensure_neutral_resources():
    """Create the overlay when setup has not already produced it."""
    return build_neutral_resources(force=False)


def verify_neutral_resources():
    _validate_resource_revision()
    marker = _read_current_marker()
    if marker is None:
        raise NeutralResourceError(
            'The neutral overlay is missing or incomplete. Rebuild it first.'
        )
    _ensure_resource_model_path()
    options = LoaderOptions(LoaderOptions.LF_no_cache)

    for relative_path in GAG_SIGN_PATHS:
        if _sha256(_resource(relative_path)) == _sha256(
                OVERLAY_ROOT / relative_path):
            raise NeutralResourceError(
                'Gag Shop sign was not replaced: %s' % relative_path
            )

    for sign in DESTINATION_SIGNS.values():
        relative_path = sign['path']
        if _sha256(_resource(relative_path)) == _sha256(
                OVERLAY_ROOT / relative_path):
            raise NeutralResourceError(
                'Destination sign was not replaced: %s' % relative_path
            )
        alias = sign.get('alias')
        if alias is not None and _sha256(
                OVERLAY_ROOT / relative_path) != _sha256(
                    OVERLAY_ROOT / alias):
            raise NeutralResourceError(
                'Destination sign alias differs from %s' % relative_path
            )

    for map_name in MAP_SIGN_PLACEMENTS:
        relative_path = Path('phase_4/maps/%s_english.png' % map_name)
        if _sha256(_resource(relative_path)) == _sha256(
                OVERLAY_ROOT / relative_path):
            raise NeutralResourceError(
                'Street map was not replaced: %s' % relative_path
            )

    for relative_path in PORTRAIT_MODEL_PATHS:
        node = Loader.get_global_ptr().load_sync(
            _filename(OVERLAY_ROOT / relative_path),
            options,
        )
        if node is None:
            raise NeutralResourceError(
                'Could not verify model: %s' % relative_path
            )
        model = NodePath(node)
        if model.find('**/%s' % relative_path.stem).is_empty():
            raise NeutralResourceError(
                'Expected portrait node is missing from %s' % relative_path
            )
        if _sha256(_resource(relative_path)) == _sha256(
                OVERLAY_ROOT / relative_path):
            raise NeutralResourceError(
                'Character portrait was not replaced: %s' % relative_path
            )

    for relative_path in LANDMARK_MODEL_PATHS:
        node = Loader.get_global_ptr().load_sync(
            _filename(OVERLAY_ROOT / relative_path),
            options,
        )
        if node is None or NodePath(node).is_empty():
            raise NeutralResourceError(
                'Could not verify model: %s' % relative_path
            )
        if _sha256(_resource(relative_path)) == _sha256(
                OVERLAY_ROOT / relative_path):
            raise NeutralResourceError(
                'Character landmark was not replaced: %s' % relative_path
            )

    for relative_path in ACORN_MODELS.values():
        node = Loader.get_global_ptr().load_sync(
            _filename(OVERLAY_ROOT / relative_path),
            options,
        )
        if node is None:
            raise NeutralResourceError(
                'Could not verify model: %s' % relative_path
            )
        model = NodePath(node)
        if not model.find('**/chip_dale').is_empty():
            raise NeutralResourceError(
                'Character subtree remains in %s' % relative_path
            )
        source_node = Loader.get_global_ptr().load_sync(
            _filename(_resource(relative_path)),
            options,
        )
        if source_node is None or (
            _collision_solid_count(model)
            != _collision_solid_count(NodePath(source_node))
        ):
            raise NeutralResourceError(
                'Collision verification failed for %s' % relative_path
            )

    for relative_path_string in marker['outputs']:
        relative_path = Path(relative_path_string)
        if relative_path.suffix.lower() != '.dna':
            continue
        text = (OVERLAY_ROOT / relative_path).read_text(encoding='utf-8')
        if _rewrite_dna(text) != text:
            raise NeutralResourceError(
                'Targeted display text remains in %s' % relative_path
            )

    quest_scripts = (OVERLAY_ROOT / QUEST_SCRIPTS_PATH).read_text(
        encoding='utf-8'
    )
    for script_id in ('tutorial_mickey', 'tutorial_guide'):
        script_match = re.search(
            r'(?ms)^ID %s\s*$.*?(?=^ID\s+|\Z)'
            % re.escape(script_id),
            quest_scripts,
        )
        if script_match is None:
            raise NeutralResourceError(
                'The neutral %s script is missing.' % script_id
            )
        script_block = script_match.group(0)
        commands = [
            line for line in script_block.splitlines()[1:]
            if line.strip() and not line.lstrip().startswith('#')
        ]
        if len(commands) != 48 or 'LOAD_CLASSIC_CHAR' in script_block:
            raise NeutralResourceError(
                'The neutral %s script failed structural verification.'
                % script_id
            )

    print(
        'Neutral resource overlay verified: %d files.'
        % len(marker['outputs'])
    )
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Build Open Town neutral resources over the base snapshot.'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='regenerate files even when the current marker is complete',
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='verify the generated overlay after building it',
    )
    args = parser.parse_args(argv)
    try:
        build_neutral_resources(force=args.force)
        if args.verify:
            verify_neutral_resources()
    except NeutralResourceError as error:
        print('Neutral resource setup failed: %s' % error, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
