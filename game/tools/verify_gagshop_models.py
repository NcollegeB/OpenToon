"""Load every active Gag Shop exterior and verify its neutral sign binding."""

from pathlib import Path

from panda3d.core import Filename, loadPrcFileData


RESOURCE_PATH = Filename.fromOsSpecific(
    str(Path(__file__).resolve().parents[1] / 'resources')
).getFullpath()
loadPrcFileData(
    '',
    'window-type none\nmodel-path {}'.format(RESOURCE_PATH),
)

from direct.showbase.ShowBase import ShowBase


MODELS = (
    ('phase_4/models/modules/gagShop_TT.bam', 'GS_sign.png'),
    ('phase_6/models/modules/gagShop_DD.bam', 'GS_sign.png'),
    ('phase_6/models/modules/gagShop_MM.bam', 'GS_sign.png'),
    ('phase_8/models/modules/gagShop_DG.bam', 'GS_sign.png'),
    ('phase_8/models/modules/gagShop_DL.bam', 'GS_sign.png'),
    ('phase_8/models/modules/gagShop_BR.bam', 'GS_signBIG_BR.png'),
)


def main():
    base = ShowBase(windowType='none')
    try:
        for model_path, expected_texture in MODELS:
            model = base.loader.loadModel(model_path)
            assert not model.isEmpty(), 'Could not load {}'.format(model_path)

            textures = model.findAllTextures()
            names = [
                textures.getTexture(index).getFilename().getBasename()
                for index in range(textures.getNumTextures())
            ]
            sign_names = [name for name in names if 'GS_sign' in name]
            assert expected_texture in sign_names, (
                model_path,
                expected_texture,
                sign_names,
            )
            print('PASS {} -> {}'.format(model_path, expected_texture))
    finally:
        base.destroy()


if __name__ == '__main__':
    main()
