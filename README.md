# Miaou-Board

Petit projet de dashboard sur une Raspberry PI Zero WH avec les modules Inky pHAT et Button SHIM de [Pimoroni](https://shop.pimoroni.com/).

Ce projet utilise les éléments suivant :
* Station Météo Netatmo ([API](https://dev.netatmo.com/) | [Boutique](https://shop.netatmo.com))
* OpenWeather API ([Documentation](https://openweathermap.org/api))
* MeteoCalc ([Documentation](meteocalc))


# Installation

### Module Inky pHat

* [Boutique Pimoroni](https://shop.pimoroni.com/products/inky-phat?variant=12549254217811)
* [Guide et tutoriaux](https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-inky-phat)

```
curl https://get.pimoroni.com/inky | bash
```

### Module Button SHIM

* [Boutique Pimoroni](https://shop.pimoroni.com/products/button-shim)
* [Documentation](http://docs.pimoroni.com/buttonshim/)

```
curl https://get.pimoroni.com/buttonshim | bash
```

### Dépendances python

```
pip install pyyaml lnetatmo meteocalc geopy inkyphat buttonshim datetime 
```
