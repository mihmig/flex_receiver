ymaps.ready(init);
last_event = {}
function init() {
    // Создаем карту.
    var myMap = new ymaps.Map("map", {
            center: [57.62, 39.89],
            zoom: 11,
            controls: ['zoomControl']
        }, {
            searchControlProvider: 'yandex#search'
        });

    // Создаем круг.
    myCircle = new ymaps.Circle([
            // Координаты центра круга.
            [57.62, 39.89],
            // Радиус круга в метрах.
            10000
        ], {}, {
            // Задаем опции круга.
            // Цвет заливки.
            fillColor: "#DB709377",
            // Цвет обводки.
            strokeColor: "#990066",
            // Прозрачность обводки.
            strokeOpacity: 0.8,
            // Ширина обводки в пикселях.
            strokeWidth: 5
        });
    myCircle.events.add(['geometrychange', 'pixelgeometrychange', 'propertieschange', 'dragend' ],
        function (e) {
            last_event = e;
            console.log(last_event.originalEvent.target.geometry._coordinates, last_event.originalEvent.target.geometry._radius);
            //console.log(e);
        }
    );
    // Добавляем круг на карту.
    myMap.geoObjects.add(myCircle);

    // Включаем редактирование круга.
    myCircle.editor.startEditing();
}
