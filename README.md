# Niquhiko
A light-weight blog site.

## Get Started
Run `run_debug.py` to start the debug server (with a random port number).

## Configuration
Niquhiko includes many customization options, including changing user permissions. These settings can be changed through `configuration.toml`.

### Permission Types
- `CAN_LOGIN`: Allows logins.
- `CAN_LOGOUT`: Allows logouts.
- `CAN_REGISTER`: Allows registration of accounts.
- `CAN_WRITE_POSTS`: Allows writing posts.
- `CAN_LIKE`: Allows liking posts.

## Static Generator
Niquhiko includes a static site generator `run_staticify.py` to convert the site into static files. Converted files can be found in the `export` folder.

## Attribution
Look at `ATTRIBUTION.txt`.
