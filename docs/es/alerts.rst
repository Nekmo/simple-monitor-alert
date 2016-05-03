

Alertas
#######
Las alertas permiten comunicar cuando ocurre un error con un observable por un medio de comunicación en función
a unas condiciones. Por defecto, cuando sucede un error, se envía a todas las configuraciones de alerta. Un
ejemplo puede ser el siguiente::

    [mail]
    to = alerts@company.com

El nombre de la sección, "mail", corresponde al nombre del script de alerta. No obstante, es posible definir dicho
nombre de forma manual::

    [company-alert]
    alert = mail
    to = alerts@company.com

Todo el contexto de la sección se le pasará al script que se ejecute con la alerta. Así pues, algunas configuraciones
podrán requerir opciones, o podrán darse optativamente::

    [company-alert]
    alert = mail
    host = smtp.company.com
    port = 25
    username = noreply
    password = secret
    from = noreply@company.com
    to = alerts@company.com


Utilizando una alerta base
==========================
Es posible reutilizar la configuración de una alerta existente para sobrescribirla y crear una nueva alerta.
Por ejemplo::

    [mail-smtp2]
    base = company-alert
    host = smtp2.company.com

No obstante, con lo anterior estamos haciendo que la alerta se envíe 2 veces: una por el medio de de la alerta base,
y de nuevo por esta. Esto puede tener sentido si queremos asegurarnos de recibir la alerta al instante, peor lo más
habitual es querer poner condiciones.

Es necesario remarcar, que el nombre de base es el de la sección (entre corchetes) y no necesariamente el nombre
del script ejecutado. También que, extender una alerta base no es obligatorio para crear una nueva alerta de un
mismo script, pero sí recomendado si queremos reutilizar configuraciones.

Enviar tras X tiempo
====================
Esto es sobre todo útil si queremos asegurarnos de recibir la alerta bien porque el medio de envío principal no
está funcionando bien, o no lo hemos leído. Esta alerta se envía sólo si el error se sigue produciendo tras el tiempo
marcado::

    [mail-smtp2]
    base = mail
    host = smtp2.company.com
    since = 12h

Delimitar por monitores y observables
=====================================
Hay ciertas que sólo queremos que reciban ciertas personas. Para ello filtraremos monitor o/y observable::

    [mail-webmaster]
    base = mail
    filter = http_monitor,services_monitor:running(nginx)
    to = webmaster@company.com

En el primer caso del filtro, estaremos filtrando todo lo de un monitor. En el segundo, sólo el observable de un
monitor determinado.

Extender de una base desactivada
================================
Este caso es un poco más complejo. Podríamos querer delimitar por monitores y observables todas nuestras alertas,
pero no queremos que nadie reciba todas las alertas, reutilizando la configuración de base. Para ello, desactivaremos
la alerta de base y de ella extenderemos las demás, pero activadas::

    [mail]
    host = smtp.company.com
    port = 25
    username = noreply
    password = secret
    from = noreply@company.com
    enabled = false

    [mail-webmaster]
    base = mail
    filter = http_monitor,services_monitor:running(nginx)
    to = webmaster@company.com
    enabled = true

    [mail-sysadmin]
    base = mail
    filter = cpu,memory,hdd,services_monitor
    to = sysadmin@company.com
    enabled = true

    [mail-junior]
    base = mail
    filter = coffee_pot
    to = junior@company.com
    enabled = true

O, podemos usar el enabled para activar y desactivar una alerta sin necesidad de borrar su configuración.


Alerta cuando un problema se soluciona
======================================
Por defecto, todas las alertas se envían únicamente cuando fallan. No obstante, es posible crear alertas que
se envíen cuando un problema se soluciona::

    [mail-resolved]
    base = mail
    resolved = true

Eso sí, es necesario avisar, y esto es muy importante, que la configuración se alerta sólo es aplicable cuando
el problema se ha solucionado. Esto significa, que si queremos una alerta avisando de del error y otra diciendo
que se ha solucionado, deberemos crear 2 alertas distintas.