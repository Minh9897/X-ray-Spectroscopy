# X-ray Spectroscopy

A minimalistic logging wrapper for Python.

## Usage

Every project should utilize logging, but for simple use cases, this requires a bit too much boilerplate. Instead of including all of this in your modules:

```python
import logging

log = logging.getLogger(__name__)

def greet(name):
    log.info("Hello, %s!", name)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(name)s: %(message)s",
    )
```

with this package you can simply:

```python
import log

def greet(name):
    log.info("Hello, %s!", name)

if __name__ == "__main__":
    log.init()
```

It will produce the exact same standard library `logging` records behind the scenes.

## Installation

Install this library directly into an activated virtual environment:

```text
$ pip install -r requirements.txt
```

