# tomato-example-counter
An example driver for `tomato`, used for testing purposes.

This driver is developed by the [ConCat lab at TU Berlin](https://tu.berlin/en/concat).

## Supported functions

### Capabilities
- `count`: for counting up every second
- `random`: for returning a random number every query

### Attributes
- `val`: the returned value, `RO`, `float`
- `max`: the upper limit to `random`, `RW`, `float`
- `min`: the lower limit to `random`, `RW`, `float`

## Contributors
- Peter Kraus