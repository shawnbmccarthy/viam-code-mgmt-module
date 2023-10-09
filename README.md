# Viam Code Deploy Demo

simple code management module to show how we can deploy a simple application
as well as provide basic management which can be reported by the get readings
interface.

## Overview

Viam's module registry, the question is can we deploy a simple web-app to
my robot which hosts a very simple page right now using the module registry.

The core requirements: 
1. the web-app must not live in the same github repository as the module
2. the web-app must provide an installation script called install.sh
2. this web module must not have any hard-coded artifacts about the repo
3. this web module should have a basic sensor which can validate the web-app is up

## github action
The github action is responsible for deploying the viam module, while the sensor 
is `reconfigure` method is responsible for managing the code deploy.

## Code Management Sensor
During the code management sensor configuration/reconfiguration the sensor will
ensure the package is:
1. installed, if not an installation will be kicked off
2. validate the release version, if the version is different from what is deployed an installation will occur

## Configuration

Below is an example of the component, using the web demo release

Currently, we support a web action which executes a simple `requests.get` and 
a simple make execution.

```json
{
  "model": "shawns-modules:code-mgmt:sensor",
  "namespace": "rdk",
  "type": "sensor",
  "attributes": {
    "health_check": {
      "type": "web",
      "web_urls": [
        "http://localhost:9090/version"
      ]
    },
    "package_info": {
      "org": "shawnbmccarthy",
      "repo": "viam-web-demo",
      "release": "0.0.60",
      "make_opts": {
        "INSTALL_DIR": "/opt/viam-web-demo",
        "VERSION": "0.0.60",
        "TARGET": "install_web"
      }
    }
  },
  "depends_on": [],
  "name": "demo"
}
```
## TODO
1. documentation
2. validate generalization of code
3. testing

## Reference
1. [viam-web-demo](https://github.com/shawnbmccarthy/viam-web-demo/)

# Support

Contributions are welcome in the form of issues and pull request, any support needs
please email me at:
[shawn@viam.com](mailto:shawn@viam.com)