sma.ini
#######
Aquí es donde se encuentran las configuraciones de Simple-Monitor-Alert. Hay 2 cosas principales que podemos querer
tocar aquí:

* **Las alertas**: Quienes recibirán las notificaciones, por qué método, bajo qué circustancias...
* **Sobrescribir y configurar monitores:** Cambiar nivel de alerta, entregar parámetros, ejecutar scripts varias
  veces...

Monitores
=========
Todos los items entregados por los monitores son sobrescribibles en teoría. El caso más común, es cambiar las
condiciones de alerta. Por ejemplo, un monitor puede saltar al llenarse el disco al 80%, y nosotros queremos aumentar
o disminuir. También ciertos items pueden requerir un parámetro, o podemos hacer que se ejecute más de una vez un item.

Sobrescribir parámetros
-----------------------
En teoría, todos los items que son entregados por un monitor son sobrescribibles. Esto significa, que podemos cambiar
cualquier comportamiento. Por ejemplo, tenemos un monitor que devuelve el nivel de la CPU::

    $ ./monitors-enabled/cpu.sh
    cpu_pcnt.name = 'CPU percentage usage'
    cpu_pcnt.expected= <= 80
    cpu_pcnt.seconds = 600
    cpu_pcnt.value = 4.16875

Podríamos cambiar cosas como el nombre, el expected o los seconds en la configuración::

    [cpu]
    cpu_pcnt.name = 'CPU usage'
    cpu_pcnt.expected= <= 75
    cpu_pcnt.seconds = 300

El value por ejemplo no tendría sentido sobrescribirlo, porque el archivo de configuración es estático, y sería
siempre el mismo valor. Nótese que el nombre de la sección es el del archivo del monitor.

Puede darse el casi también, de que quiera sobrescribirse una configuración de un item con un grupo, por ejemplo::

    $ ./monitors-enabled/hdds.sh
    pcnt_use(sdc1).name = 'Percentage of space used in sdc1 (/)'
    pcnt_use(sdc1).expected = <= 80
    pcnt_use(sdc1).value = 97
    pcnt_use(sdc1).extra_info = 'Space: 755M/23G'
    pcnt_use(sda1).name = 'Percentage of space used in sda1 (/media/datos)'
    pcnt_use(sda1).expected = <= 80
    pcnt_use(sda1).value = 91
    pcnt_use(sda1).extra_info = 'Space: 91G/818G'

Sólo hay que hacer lo mismo que antes::

    [hdds]
    pcnt_use(sdc1).expected = <= 90
    pcnt_use(sda1).expected = <= 95

Véase que en este caso, tampoco tendría sentido sobrescribir `extra_info`, pues es algo dinámico.

Entregar parámetros
-------------------
Los items de algunos parámetros pueden requerir parámetros. Lea los comentarios al comienzo del script para ver
qué requiere. Igualmente, los items que requieran un parámetro, son señalizados de la siguiente forma:

.. code-block::

    #!/usr/bin/env bash
    ...
    echo "file_exists.require_param = yes"
    ...

Para entregar parámetros, utilice `param`. Por ejemplo:

    [script-name]
    file_exists.param = /etc/passwd

Ejecutar más de una vez
-----------------------
En el caso de un observable puede recibir un parámetro, podemos querer ejecutarlo más de una vez. Por ejemplo,
para ver si más de un archivo existe. Como no podemos duplicar entradas en la configuración, usaremos grupos::

    [script-name]
    file_exists(passwd).param = /etc/passwd
    file_exists(group).param = /etc/group

Gracias a esto, se sabrá que el script debe ejecutarse dos veces, una por cada grupo. No debe confundirse este
caso con el del segundo ejemplo (el de los hdds) de la sección "sobrescribir parámetros". si el script crea
los grupos como dicho caso, no puede recibir un parámetro. En este caso, el parámetro es obligatorio.

Esto es porque los parámetros tienen como objetivo definir qué se monitoriza. Si el script hace una iteración y
genera él mismo los grupos, se considera que no necesita parámetro. En este segundo caso, el parámetro es
obligatorio.
