# CHANGELOG

<!-- version list -->

## v1.0.0 (2026-07-23)

### Bug Fixes

- Add explicit permissions to code_quality workflow
  ([`595ea93`](https://github.com/micxer/kradio/commit/595ea9303f246bb303a0765c5d9c45639eeabf14))

- Add gpiod as explicit pip dependency
  ([`64ae479`](https://github.com/micxer/kradio/commit/64ae47979115eeddd644819ad3e17cf359743d0b))

- Add i2c group to SupplementaryGroups in system unit
  ([`b36e7e0`](https://github.com/micxer/kradio/commit/b36e7e03fea0cdd069c14a31369dd590822f8635))

- Add type annotation for _last_event_time to satisfy mypy
  ([`01321d8`](https://github.com/micxer/kradio/commit/01321d878194a201ebf12a028aeab113d08d3bad))

- Backup mpd.conf before overwrite and document boot config manual step
  ([`cf2f3d6`](https://github.com/micxer/kradio/commit/cf2f3d6cc22eacb53a980267648572e273f3778b))

- Correct umlaut mapping for Python 3 Unicode strings
  ([`f7c3a06`](https://github.com/micxer/kradio/commit/f7c3a0635e7ac3cc9bd1a98e927a2d7760686c7d))

- Decouple scroll speed from loop cadence
  ([`ef85a72`](https://github.com/micxer/kradio/commit/ef85a7289925ac403ee0ec36bb3a1a473501157e))

- Disable WLAN adapter shutdown to improve performance
  ([`bfa7339`](https://github.com/micxer/kradio/commit/bfa733993ea9b64c048820f0dd88d8c55271592f))

- Guard get_stations() against malformed #EXTINF lines; tighten tests
  ([`353ba6a`](https://github.com/micxer/kradio/commit/353ba6a90eb5ed671c80b023afcc4b21f32c6e29))

- Install gpiod system packages for RPi.GPIO2
  ([`6a24130`](https://github.com/micxer/kradio/commit/6a241306b89e0d0f754461269588e0715b3c4937))

- Install zizmor on CI runner before running audit
  ([`1d07382`](https://github.com/micxer/kradio/commit/1d073826f15b8237a0657fe6b4f509e41df633c8))

- Make gpiod Linux-only dep, suppress mypy import errors on macOS
  ([`67e7cd8`](https://github.com/micxer/kradio/commit/67e7cd8151b3f09ca8a6a9f81bdb4e45dbf18d9f))

- Migrate playlist to EXTM3U format for MPD compatibility
  ([`33bddaa`](https://github.com/micxer/kradio/commit/33bddaa83b6445e9f5be2f093a7bf488ab4870d9))

- Pin gpiod to v1.x for rpi-gpio2 compatibility
  ([`7cf9fe9`](https://github.com/micxer/kradio/commit/7cf9fe9a9fb4e459d7a0f9e25c36c47b1535321b))

- Pin Python to 3.11 in renovate, target system constraint
  ([`f9b4624`](https://github.com/micxer/kradio/commit/f9b462408b980e959dbba221d3e3dc0e09007007))

- Quicker shutdown
  ([`b7cdc60`](https://github.com/micxer/kradio/commit/b7cdc60d389ef534df14299aa8bb7e2582a4fa8d))

- Remove dash overwrite before standby backlight off
  ([`9297c7e`](https://github.com/micxer/kradio/commit/9297c7e1939d6cc2a4de42d7826e877d48fa23b5))

- Remove kernel debounce delay, use software debounce instead
  ([`454ae43`](https://github.com/micxer/kradio/commit/454ae431130f46dcfdc8f239812627df4517089d))

- Replace rpi-gpio2 with direct gpiod v2 API
  ([`f4b7761`](https://github.com/micxer/kradio/commit/f4b77617c0d366b617f2de2e42a42b166ddb1c5e))

- Replace x.com URLs with stream.example.com in test fixtures
  ([`35a0fe0`](https://github.com/micxer/kradio/commit/35a0fe020e443beff32d6423284406f65237bfde))

- Resolve wheel glob before passing to fpm
  ([`fd9733e`](https://github.com/micxer/kradio/commit/fd9733e0f4de8c9e951657c030228e1cf775ae5f))

- Scope app token to contents write and suppress artipacked false positive
  ([`6d103d2`](https://github.com/micxer/kradio/commit/6d103d2e6e303ba7cc7fa100b95623a6d6b206a9))

- Shorten startup, show version for longer time
  ([`1b91249`](https://github.com/micxer/kradio/commit/1b912491f95f9e19cd9a655557b701664cb62e6d))

- Standby display and timeout
  ([`70c8c02`](https://github.com/micxer/kradio/commit/70c8c0229f2f777aca76cfcb1b1894a9c11c50bc))

- Use GitHub App token for semantic-release push
  ([`7292ec2`](https://github.com/micxer/kradio/commit/7292ec26c5159b5f60ca19cb2a2bb7ae7d261e90))

- Use monotonic() baseline for scroll timer instead of 0.0
  ([`675554e`](https://github.com/micxer/kradio/commit/675554ea17f684f5a0589752ae20f1f43b9daa24))

- Use sudo for gem install fpm on ubuntu-latest runner
  ([`4c11204`](https://github.com/micxer/kradio/commit/4c11204710278fc08934668ef4024fcb79654bdb))

- Use venv Python in systemd service
  ([`8226fbf`](https://github.com/micxer/kradio/commit/8226fbf728ef8df41c2b135d67f68e886ef233e0))

### Chores

- **deps**: Bump gitpython from 3.1.51 to 3.1.52
  ([`f34f819`](https://github.com/micxer/kradio/commit/f34f8194f282d4f944956621095cb680c964e90d))

- **deps**: Update dependency smbus2 to ~=0.6.1
  ([`e86fd33`](https://github.com/micxer/kradio/commit/e86fd33b7244d78e97e5aa6d342e3024451c7900))

### Documentation

- Add build provenance verification instructions to README
  ([`8ee1d97`](https://github.com/micxer/kradio/commit/8ee1d975d61039c9ce7c67d1e127af69b93ceb31))

### Features

- Add semantic-release workflow and dynamic version from package metadata
  ([`556b6b6`](https://github.com/micxer/kradio/commit/556b6b6d018bd67a7aeba3c227974744b2d93cda))

- Add SLSA build provenance attestation for release artifacts
  ([`fef305f`](https://github.com/micxer/kradio/commit/fef305fe4f5f10f910197a02065267d2fcd4abd0))

- Build and ship .deb package via fpm
  ([`b4188b5`](https://github.com/micxer/kradio/commit/b4188b5dc8a022699784b6a981076d7a4e1a8b2d))

- Move scrolling into DisplayManager
  ([`912ba08`](https://github.com/micxer/kradio/commit/912ba08caa00c4b3fd577914f31b3ac5a8516120))

- Pause at scroll start position for 3x interval
  ([`aacd466`](https://github.com/micxer/kradio/commit/aacd466335111c434c3745acd1c7c3a869b48c8b))

- Restructure as installable package with full test coverage
  ([`400f482`](https://github.com/micxer/kradio/commit/400f482d7dddc8650b36aff7b25d00ca634771ba))

- Show post-install notice for manual /boot/config.txt step
  ([`a3256e5`](https://github.com/micxer/kradio/commit/a3256e5f0a7dce168de5c19e542b5a9d726a91bb))

### Refactoring

- Add DisplayManager with background thread, rename to English
  ([`7096558`](https://github.com/micxer/kradio/commit/7096558d0e2c0c0d495f0da7dbb18d7641d639cf))

- Remove display.py, move scroll tests to DisplayManager
  ([`c3bcc9b`](https://github.com/micxer/kradio/commit/c3bcc9b85ddedb9a418b2b076af999fb0b6080f7))

- Replace magic mode numbers with named constants
  ([`b68a12c`](https://github.com/micxer/kradio/commit/b68a12c3c5895293d55658d1eeea10831662632d))

- Replace sys_config/ tree with flat packaging/ directory
  ([`745bf19`](https://github.com/micxer/kradio/commit/745bf19e0c186a58b75f4e64901a57e8ae717623))


## v0.1.0 (2024-07-28)

- Initial Release
