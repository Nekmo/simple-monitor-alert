

Respuestas a preguntas frecuentes
#################################

¿Recibiré una alerta por cada ejecución de SMA si se mantiene el error?
=======================================================================
No. Las alertas sólo se envían la primera vez. No se reenvían en la siguiente ejecución si el estado de la alerta
no ha cambiado.

Esto es gracias al archivo de resultados, donde se muestra qué alertas se han enviado, entre otras cosas::

    {
        "monitors": {
            "example-1": {
                "file_exists": {
                    "alerted": [
                        "telegram"
                    ],
                    "executions": 10,
                    "fail": true,
                    "since": "2016-04-29T03:48:57.023764+02:00",
                    "updated_at": "2016-04-29T04:15:18.318204+02:00"
                }
            }
        }
    }

¿Qué pasa si el envío de una alerta falla?
==========================================
En tal caso la alerta no pasará a "alerted", y en la siguiente ejecución de SMA, si el error sigue sucediendo, se
volverá a intentar enviar la alerta.

Se ha pensado en hacer alertas que envíen alertas cuando otras alertas fallen, pero... ¿dónde se encontraría el
límite?

SMA no tiene X feature de Nagios, Zabbix...
===========================================
Usa Nagios/Zabbix.

La parte de "simple" de Simple-Monitor-Alert no es de pega. SMA es simple. Sencillo pero versátil. Si hay una
característica que de verdad sea útil y no lo haga más complejo, se implementará. Si no, no.

