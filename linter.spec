a = Analysis(['main.py'],
             pathex=['/path/to/your/project'],
             binaries=[],
             datas=[('ailinter/config.yaml', 'ailinter')])  # Add this line