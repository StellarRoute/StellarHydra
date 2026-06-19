# StellarRoute response parsing

`StellarRouteClient` normalizes heterogeneous API JSON before building `RoutingSignal` objects.

## Envelope unwrapping

Responses wrapped as `{ "data": { ... } }` are unwrapped via `_unwrap_envelope()` so callers can handle both bare and enveloped payloads.

## Path step aliases

`_parse_path()` accepts step objects with either naming style:

- `selling_asset` / `buying_asset` / `venue`
- `sell` / `buy` / `venue_type`

Missing fields default to empty strings.

## Orderbook depth

`_sum_levels()` aggregates bid or ask levels whether each level is a dict (`price`, `amount`) or a two-tuple `[price, amount]`.

## Numeric coercion

`_to_float` and `_to_int` swallow parse errors and return `None` or `0` so a single bad field does not fail the whole signal.

See `src/stellarhydra/integrations/stellarroute_client.py` and `tests/test_stellarroute_client.py`.
