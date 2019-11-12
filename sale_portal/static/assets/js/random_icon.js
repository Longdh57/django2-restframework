var iconArray = new Array(
    "icon-music text-pink-300",
    "icon-chess-queen",
    "icon-hat text-pink",
    "icon-crown",
    "icon-medal-first text-orange-300",
    "icon-trophy2 text-orange-300",
    "icon-trophy3 text-warning",
    "icon-mustache",
    "icon-rocket text-primary",
    "icon-gift text-danger",
    "icon-reddit",
    "icon-tux",
    "icon-sun3 text-warning",
    "icon-weather-windy text-primary",
    "icon-heart5 text-danger",
    "icon-satellite-dish2 text-indigo-600",
    "icon-theater text-violet-400",
);

var randIcon = Math.floor(Math.random() * (iconArray.length));
$('#sp-icon').append("<i class='" + iconArray[randIcon] + " mr-1'></i>");
