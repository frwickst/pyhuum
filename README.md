# huum - A python library for controlling [Huum](https://huum.eu/) saunas

This library was created primarily to be used together with Home Assistant, but
can be used as a stand-alone library as well. The API used by this library is sanctioned
by Huum to be used by third parties. At least to the extent that they happily provided
documentation for the API when asked about it.

This library has been tested against a [Huum Drop](https://huum.eu/products/drop-electric-sauna-heater/) sauna
using the [UKU Wi-Fi](https://huum.eu/products/uku-wi-fi-sauna-controller/) control unit.

No guarantees are given when using this library. You are using it at your own risk.
Saunas can be dangerous if used without care or without the right security measures.

## Installation

### PIP
`pip install huum`

### Poetry
`poetry add huum`

## Quick guide
```python
from huum import Huum

# Usage with env vars
huum = Huum()

# Setting auth variables explicitly
huum = Huum(username="foo", password="bar")

# If you don't have an existing aiohttp session
# then run `open_session()` after initilizing
huum.open_session()

# Turn on the sauna
huum.turn_on(80)

# Turn off the sauna
huum.turn_off(80)
```

## Usage

The `huum` package is fully asynchronous.

Supported Python versions:

| Python | Supported |
|--------|-----------|
| <= 3.8 | ❌         |
| 3.9    | ✅         |
| 3.10   | ✅         |
| 3.11   | ✅         |
| 3.12   | Untested  |


### Authentication
Authentication uses username + password. The same credentials that you use for logging into the Huum application.

**Passing credentials to constructor**

```python
huum = Huum(username=<username>, password=<password>)
```

### Sessions
You can use the library either with an already existing session or create one yourself. This design decision
was created mainly to support Home Assistants (HA) existing sessions and complying with their guidelines. In
most cases you will want to create your own session if you are using this outside of HA.

If you already have an existing session you can pass it to the constructor using the `session` argument.

```python
huum = Huum(session=<session>)
```

If you want the library to create a new session, run `open_session()` after creating a `Huum` instance.
You must do this before running any commands. You can close the session using `close_session()`.

```
huum = Huum()
huum.open_session()
...
huum.close_session()
```

### Controlling the sauna

#### Getting sauna status

The Huum API exposes a status endpoint for getting the current status of the sauna. This will
return the basic information about the sauna. It will however not return all of the info that
the sauna _could_ give you _when the sauna is not heating_. You will however get this info
if you try turning off the sauna again after it is already off. For that reason, this library
exposes two methods of getting the status of the sauna, `status()` and `status_from_status_or_stop()`.
The latter will first call the status endpoint, and if the sauna is off, then call the off endpoint
to get the full status response.

The main difference, and the main reason to use the latter endpoint, is that `status()` will not
give you the previously set temperature of the sauna is off, while `status_from_status_or_stop()` will.

```python
huum.status()
```

```python
huum.status_from_status_or_stop()
```

#### Turning on and setting temperature

The Huum API does not have a specific endpoint for turning on a setting the temperature.
The same endpoint does both. This library has two functions for turning on and settings the
temperature, mainly for exposing a nicer interface to the developer.

```python
# Turns on the sauna and sets its temperature to 80
huum.turn_on(temperature=80)

# Identical the the above
huum.set_temperature(temperature=80)
```

##### Security concerns

Huums API does not check if the sauna door is open or not when turning it on. It will happily
turn on the sauna while the door is open. The sauna itself will most likely still not heat as
it has a security guard in the sauna, but it will turn it on and will start heating if the door
is closed. The Huum mobile application however checks if the sauna door is open or closed before
turning on the sauna.

To mimic the security guards of the mobile application the library, by default, checks the status
of the sauna before it turns it on. If you do not want to have this check, then you can pass the
argument `safety_override=True` to either `turn_on()` or `set_temperature`.

```python
huum.set_temperature(temperature=80, safety_override=True)
```

#### Turning off the sauna
The sauna can be turned off by calling `turn_off()`.

```python
huum.turn_off()
```

## Response objects

This library uses Pydantic schemas for all method responses.
I recommend checking the /huum/schemas.py for checking responses.

## Handling exceptions

All exceptions that are raised from making an HTTP request are coming directly from `aiohttp`.
More of the time these will be `aiohtto.ClientResponseError` as all requests are done with `raise_for_status` set
to `True` for requests that goes through `aiohttp`.

If the door is open and the sauna is turned on, and the client is not told to explicitly bypass security
measures (see "Security concerns" above), then `huum.exceptions.SafetyException` will be raised.

