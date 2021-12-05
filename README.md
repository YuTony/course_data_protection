# Install requirements
```shell
pip install -r requirements.txt
```
# Create exe run
```shell
python -O -m PyInstaller --exclude-module _bootlocale --windowed --onefile <file>
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