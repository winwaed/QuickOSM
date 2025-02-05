# QuickOSM

![Logo of QuickOSM](resources/icons/QuickOSM.svg)

## Versions

* QuickOSM is maintained only for a maintained QGIS version (LTR, stable release and dev).
* Current test status master on QGIS Master and LTR : [![Build Status](https://api.travis-ci.org/3liz/QuickOSM.svg?branch=master)](https://travis-ci.org/3liz/QuickOSM)

| QuickOSM  | QGIS Min | QGIS Max | Branch       |
|-----------|----------|----------|--------------|
| 1.0 → 1.4 | 2.0      | 2.18     | [master_qgis2](https://github.com/3liz/QuickOSM/tree/master_qgis2) |
| 1.5 → 1.7 | 3.0      | 3.2      |              |
| 1.8 →     | 3.4      |          | [master](https://github.com/3liz/QuickOSM/tree/master)       |

#### Watch the [Video tutorial](https://vimeo.com/108737868)

**Install the QuickOSM plugin**
* QGIS `Plugins` menu → `Manage and Install Plugins…`
* Search for `QuickOSM` and select it
* `Install Plugin`

**Try a quick query**
* `Vector` menu → `QuickOSM` -> `QuickOSM`
* In the `key` field enter `amenity`
* In the `value` field enter `toilets`
* Set the name of the town/village to `London`
* `Run Query`

The Overpass API takes a few seconds to respond, and after that you should get new 
point and polygon layers for the toilets of London! (nodes and ways in OpenStreetMap 
with the `amenity`=`toilet` tag on them) 


## Generalities

QuickOSM allows you to work quickly with OSM data in QGIS thanks to [Overpass API][Overpass].
* Write some queries for you by providing a key/value
* Choose to run the query on an area or an extent
* Configure the query : which layers, which columns…
* Open a local OSM (.osm or .pbf) with a specific osmconf in QGIS
* Build some models with QGIS Processing

There are some useful tips, like automatic colours on lines (if the tag is present)
 or some actions (right-click in the attribute table) for each entities (edit in JOSM for instance).

[Overpass]: https://wiki.openstreetmap.org/wiki/Overpass_API

## Using QuickOSM in a Processing model or in a Python script

Since QGIS 3.4, QuickOSM is available in the Processing modeler.
Here some useful algorithms in an appropriate order:
* **QuickOSM** → **Advanced**, one of the **Build query** algorithms.
* **File Tools** → **Download file**.
* **Modeler Tools** → **String concatenation**. 
Useful to concatenate the downloaded filepath with
  * `|layername=points`
  * `|layername=lines`
  * `|layername=multilinestrings`
  * `|layername=multipolygons`
* **QuickOSM** → **Open OSM file**. Instead of the step above with the string concatenation.
 
Check a more detailed answer on [stackexchange](https://gis.stackexchange.com/a/313360/24505).
* **Vector Table** → **Explode HStore field** (QGIS ≥ 3.6)
* **Vector Table** → **Feature filter**

Since QGIS 3.6, you can export your Processing model as a Python script.

## Translation

* The web-based translating platform [Transifex](https://www.transifex.com/quickosm/gui/dashboard/) is used.

![statistics](https://chart.googleapis.com/chart?chxt=y%2Cr&chd=e%3A....63yjyjx6xRJmEeEeD1DMAA&chco=B7E1FF%2C73E6D2%2CF4F6FB&chbh=9&chs=350x183&cht=bhs&chxl=0%3A%7CPortuguese%7CRussian%7CGerman%7CItalian%7CFinnish%7CSpanish%7CPortuguese+%28Brazil%29%7CIndonesian%7CDutch%7CChinese+%28Taiwan%29%7CPolish%7CEnglish%7CFrench%7C1%3A%7C0%25%7C5%25%7C6%25%7C7%25%7C7%25%7C15%25%7C77%25%7C78%25%7C79%25%7C79%25%7C92%25%7C100%25%7C100%25%7C)

## Development

* QuickOSM uses a [Git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules).
  * For a new clone, including the submodule, do `git clone --recursive https://github.com/3liz/QuickOSM.git`.
  * For an existing clone, do `git submodule init` and `git submodule update`.
  * These command will populate the `qgis_plugin_tools`.
* For panels, you can find a quick diagram in the `doc` folder.
* For tests, it's using the `unittest` framework.
  * They are launched on GitHub using Travis, you can check the [Travis status](https://travis-ci.org/3liz/QuickOSM) on each commits and pull requests.
  * You can launch them locally using the QGIS docker image:
     * `make docker_test` using the current LTR following the [QGIS release schedule](https://www.qgis.org/en/site/getinvolved/development/roadmap.html#release-schedule).
     * `qgis_plugin_tools/docker_test.sh QuickOSM release-3_4` for QGIS 3.4
     * `qgis_plugin_tools/docker_test.sh QuickOSM latest` for QGIS Master or any other tags available on [Docker Hub](https://hub.docker.com/r/qgis/qgis/tags).
     * If you are using docker, do not forget to update your image from time to time `docker pull qgis/qgis:latest`.
     * Setting up your IDE to launch them by adding paths to your QGIS installation. I personally use PyCharm on Ubuntu.
     * Launching tests from QGIS Desktop app, in the Python console.

```python
from qgis.utils import plugins
plugins['QuickOSM'].run_tests()
```

## Authors

Etienne Trimaille : https://twitter.com/etrimaille