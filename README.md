# Install requirements
```shell
pip install -r requirements.txt
```

# Run
```shell
python src/main.py
```

# Create exe
```shell
python -O -m PyInstaller --windowed --onefile .\src\main.py
```

# Create cert
```shell
openssl req -newkey rsa:4096 \
            -x509 \
            -sha256 \
            -days 3650 \
            -nodes \
            -out example1.crt \
            -keyout example1.key
```