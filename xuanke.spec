# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['xuanke.py','login.py','xkqk.py','clear.py'],
    pathex=['C:\\Users\\Administrator\\Desktop\\project'],
    binaries=[],
    datas=[('./onnxruntime_providers_shared.dll','onnxruntime_providers_shared.dll'),('C:\\Users\\Administrator\\Desktop\\project\\venv\\Lib\\site-packages\\ddddocr\\common_old.onnx','ddddocr'),('C:\\Users\\Administrator\\Desktop\\project\\venv\\Lib\\site-packages\\ddddocr\\common.onnx','ddddocr')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    icon='C:\\Users\\Administrator\\Desktop\\project\\favicon.ico',
    name='xuanke',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='xuanke',
)
