# -*- mode: python -*-

block_cipher = None


a = Analysis(['main_app.py'],
             pathex=['/Users/Jevin/Desktop/MSU_ROLL/source'],
             binaries=[],
             datas=[],
             hiddenimports=['splinter', 'html.parser'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='MSUroll',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , icon='sushi.icns')
app = BUNDLE(exe,
             name='MSUroll.app',
             icon='sushi.icns',
             bundle_identifier=None,
             info_plist={'NSHighResolutionCapable': 'True'}
             )
