# C2B: DEMAND non-speech clips

C2B contains 100 five-second clips of environmental noise, 20 from each of five DEMAND scenes. The audio is not redistributed here. `drpf/build_c2b.py` rebuilds it from the original archives using the offsets in `data/manifests/c2b_demand.csv`.

- **Source**: DEMAND (Diverse Environments Multichannel Acoustic Noise Database), Zenodo record [1227121](https://zenodo.org/records/1227121)
- **License**: CC BY-SA 3.0
- **Channel**: `ch01`, 16 kHz mono
- **Clips**: 5 s each, non-overlapping, 20 per scene

## Scenes

The scenes stand in for care settings. None of them were recorded in a hospital.

| Venue ID | DEMAND scene | Stands in for |
| --- | --- | --- |
| `waiting_proxy` | `PCAFETER` | Waiting area (cafeteria) |
| `corridor_proxy` | `OHALLWAY` | Corridor or nursing station (office hallway) |
| `clinic_proxy` | `OOFFICE` | Consultation or admin room (office) |
| `restaurant_proxy` | `PRESTO` | Public dining area (university restaurant) |
| `indoor_care_proxy` | `DLIVING` | Home care setting (living room) |

## Archive checksums (SHA-256)

| Archive | SHA-256 |
| --- | --- |
| `DLIVING_16k.zip` | `2b1726fe06e41551ce2397f2aaf3e4fb692c912d81914b04708df0bbb5252338` |
| `OHALLWAY_16k.zip` | `4d5ef858a05954f03340048131f60a2004b7b28afc65f7bd2301636a7002d6cb` |
| `OOFFICE_16k.zip` | `7570c952f621990d0d71b8398107d9a78066254f883a5569abec9c233ffda358` |
| `PCAFETER_16k.zip` | `89be7194b83cd583c4b12f4bf7c19e9cf0e612b95312e9f4aedc968cd811bcd5` |
| `PRESTO_16k.zip` | `cfd2e13998fac36aa5628070e08261deb7993dada302dc00a76aaf4e02ee4166` |

## Citation

Joachim Thiemann, Nobutaka Ito, and Emmanuel Vincent. 2013. DEMAND: a collection of multi-channel recordings of acoustic noise in diverse environments. Zenodo. https://doi.org/10.5281/zenodo.1227121
