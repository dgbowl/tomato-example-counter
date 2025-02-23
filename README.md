# tomato-example-counter
An example driver for `tomato`, used for testing purposes.

This driver is developed by the [ConCat lab at TU Berlin](https://tu.berlin/en/concat).

## Supported functions

### Capabilities
- `count`: for counting up every second
- `random`: for returning a random number between `min` and `max` every query

### Attributes
- `max`: the upper limit to `random`, `float`
- `min`: the lower limit to `random`, `float`
- `param`: test attribute for validation, `param > pint.Quantity("0.1 seconds")`

## Contributors
- Peter Kraus