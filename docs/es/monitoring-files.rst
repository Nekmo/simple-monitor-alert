

Archivos de monitorización
##########################

Pueden encontrarse en el lenguaje de programación que uno desee, el que sea, la única condición es que devuelvan
los valores deseados para la monitorización siguiendo la estructura mostrada, y optativamente unas cabeceras, que
ofrecen más información y opciones al archivo de monitorización.


Ejemplo simple sin argumentos
=============================

El siguiente ejemplo comprueba que un archivo exista en el sistema:

.. code-block:: bash

    #!/usr/bin/env bash
    echo "file_exists.expected = yes"
    if [ -f "/path/to/file" ]; then value="yes"; else value="no"; fi
    echo "file_exists.value = $value"


El resultado de este ejemplo al ser ejecutado será el siguiente, si no existe el archivo::

    file_exists.expected = yes
    file_exists.value = no

Ejemplo de un mismo item repetido
=================================
En ocasiones, podemos querer poder utilizar un mismo comando con múltiples entidades, como por ejemplo, discos
duros. Para usar un mismo item de un mismo tipo y diferenciarlos, se usa tras el nombre del item paréntesis, y el
nombre de este grupo repetido en cuestión::

    <item_name>(<item section>)

Un ejemplo podría ser::

    pcnt_usage(sda).value = 1

Así, un ejemplo completo sería:

.. code-block:: bash

    #!/usr/bin/env bash

    IFS=$'\n'
    for part_data in `df -h`; do
        device=$(basename $(echo $part_data | awk '{ print $1 }'));
        if [[ `grep "$device" /proc/partitions` == "" ]]; then
            # Ignore dev, run, tmpfs...
            continue
        fi
        echo "pcnt_use($device).name = 'Percentage of space usted in $device ("`echo $part_data | awk '{ print $6 }'`")'";
        echo "pcnt_use($device).expected = <= 80"
        echo "pcnt_use($device).value = "`echo $part_data | awk '{ print substr($5, 1, length($5)-1) }'`;
        echo -n "pcnt_use($device).extra_info = 'Space: "`echo $part_data | awk '{ print $4 }'`"/";
        echo `echo $part_data | awk '{ print $3 }'`"'"
    done

Que tendría como un posible resultado::

    pcnt_use(sdc1).name = 'Percentage of space usted in sdc1 (/)'
    pcnt_use(sdc1).expected = <= 80
    pcnt_use(sdc1).value = 97
    pcnt_use(sdc1).extra_info = 'Space: 788M/23G'
    pcnt_use(sda1).name = 'Percentage of space usted in sda1 (/media/datos)'
    pcnt_use(sda1).expected = <= 80
    pcnt_use(sda1).value = 91
    pcnt_use(sda1).extra_info = 'Space: 91G/818G'
    pcnt_use(sdc2).name = 'Percentage of space usted in sdc2 (/home)'
    pcnt_use(sdc2).expected = <= 80
    pcnt_use(sdc2).value = 63
    pcnt_use(sdc2).extra_info = 'Space: 25G/42G'
    pcnt_use(sdc3).name = 'Percentage of space usted in sdc3 (/boot/efi)'
    pcnt_use(sdc3).expected = <= 80
    pcnt_use(sdc3).value = 67
    pcnt_use(sdc3).extra_info = 'Space: 22M/42M'
    pcnt_use(md0).name = 'Percentage of space usted in md0 (/media/nekraid01)'
    pcnt_use(md0).expected = <= 80
    pcnt_use(md0).value = 100
    pcnt_use(md0).extra_info = 'Space: 52G/5,4T'


Posibles parámetros
===================
El siguiente es un listado de los posibles parámetros que puede tener un item:

* **name** (opcional): Nombre que se mostrará para representar al comando en los informes.
* **expected** (opcional): Valor esperado para considerarse que no sea un error. Por defecto, yes, true o 0. Puede
tener modificadores como ">", ">=", etc., pero por defecto se asume "==".
* **level** (opcional): Por defecto, warning. Puede ser "info", "warning", "average", "high" o "disaster". Puede
ser sobrescrito por el usuario como cualquier otro parámetro en el archivo se settings principal.
* **value**: El valor que devuelve el item. Es lo que determina si se está dando un error o no.
