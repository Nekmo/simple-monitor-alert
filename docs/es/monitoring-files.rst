

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
        echo "pcnt_use($device).name = 'Percentage of space used in $device ("`echo $part_data | awk '{ print $6 }'`")'";
        echo "pcnt_use($device).expected = <= 80"
        echo "pcnt_use($device).value = "`echo $part_data | awk '{ print substr($5, 1, length($5)-1) }'`;
        echo -n "pcnt_use($device).extra_info = 'Space: "`echo $part_data | awk '{ print $4 }'`"/";
        echo `echo $part_data | awk '{ print $3 }'`"'"
    done

Que tendría como un posible resultado::

    pcnt_use(sdc1).name = 'Percentage of space used in sdc1 (/)'
    pcnt_use(sdc1).expected = <= 80
    pcnt_use(sdc1).value = 97
    pcnt_use(sdc1).extra_info = 'Space: 788M/23G'
    pcnt_use(sda1).name = 'Percentage of space used in sda1 (/media/datos)'
    pcnt_use(sda1).expected = <= 80
    pcnt_use(sda1).value = 91
    pcnt_use(sda1).extra_info = 'Space: 91G/818G'
    pcnt_use(sdc2).name = 'Percentage of space used in sdc2 (/home)'
    pcnt_use(sdc2).expected = <= 80
    pcnt_use(sdc2).value = 63
    pcnt_use(sdc2).extra_info = 'Space: 25G/42G'
    pcnt_use(sdc3).name = 'Percentage of space used in sdc3 (/boot/efi)'
    pcnt_use(sdc3).expected = <= 80
    pcnt_use(sdc3).value = 67
    pcnt_use(sdc3).extra_info = 'Space: 22M/42M'
    pcnt_use(md0).name = 'Percentage of space used in md0 (/media/nekraid01)'
    pcnt_use(md0).expected = <= 80
    pcnt_use(md0).value = 100
    pcnt_use(md0).extra_info = 'Space: 52G/5,4T'


Ejemplo pasando parámetros
==========================
Ahora vamos a complicarlo un poco más. Esto es sobre todo útil si queremos hacer monitores reutilizables, que
compartamos con nuestros amigos. En el primer ejemplo, monitorizábamos un archivo específico, pero sería mucho
mejor poder definir qué archivo queremos monitorizar. Para ello pasaremos una variable de entorno:


.. code-block:: bash

    #!/usr/bin/env bash
    echo "file_exists.expected = yes"
    echo "file_exists.require_param = yes"
    if [ -f "$file_exists" ]; then value="yes"; else value="no"; fi
    echo "file_exists.value = $value"

El nombre de la variable será el del item. Puedes probar su funcionamiento usando una variable de entorno en la
ejecución del mismo::

    file_exists=/etc/passwd ./example-3.sh

En el archivo de settings de simple-monitor-alert, es donde el usuario establecerá dicho parámetro::

    settings.ini
    ------------
    [example-3]
    file_exists.param = /etc/passwd

¿Y en qué consiste el `require_param`? Es lo que permite decirle al monitor que ese item requiere un parámetro, y si
al ejecutarse estuviese estuviese definido como `yes` y no se le hubiese pasado ninguno, que debe notificar al usuario
que hay un problema en su configuración.


Evitando los picos
==================
Cuando monitorizamos ciertas cosas que son susceptibles a estar en estado de alerta durante unos momentos, podemos
querer que dicha alerta se lance únicamente cuando se mantiene durante cierto tiempo. El caso más claro de este
ejemplo, es el porcentaje de CPU.

Para solucionar este problema, definiremos `seconds`. Cuando lo definamos, la alerta sólo se ejecutará cuando se
haya mantenido dicho estado un determinado tiempo.

.. code-block:: bash

    #!/usr/bin/env bash
    echo "cpu_pcnt.name = 'CPU percentage usage'"
    echo "cpu_pcnt.expected= <= 80"
    echo "cpu_pcnt.seconds = 600"
    echo "cpu_pcnt.value = "`grep 'cpu ' /proc/stat | awk '{ print ($2+$4)*100/($2+$4+$5)}'`

Cabeceras
=========
Los scripts pueden tener ciertas opciones que son globales a todos los items del mismo.

Las cabeceras deben establecerse al inicio y tener una estructura como la siguiente::

    X-Camel-Case-Header: <value>

Por ejemplo::

    X-Run-Every-Seconds: 600

Ejecutar cada X tiempo
----------------------
Establece cada cuánto tiempo queremos que se ejecute el archivo. Si **simple-monitor-alert** se ejecuta cada 5
segundos y sabemos que nuestro script es lento y es algo que varía poco, podemos establecer que tenga que pasar
un tiempo mínimo para volver a ejecutarlo:


.. code-block:: bash

    #!/usr/bin/env bash
    echo "X-Run-Every-Seconds: 600"
    echo "observable.name = 'My observable name'"
    ...


Cabecera de error
-----------------
Esta cabecera permite informar de un error en el script, normalmente por una mala configuración.

.. code-block:: bash

    #!/usr/bin/env bash
    echo "X-Error: 'You need to configure this plugin to use'"


