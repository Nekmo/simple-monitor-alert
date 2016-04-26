Posibles parámetros
###################
El siguiente es un listado de los posibles parámetros que puede tener un item:

* **value**: El valor que devuelve el item. Es lo que determina si se está dando un error o no.
* **name** (opcional): Nombre que se mostrará para representar al comando en los informes. Es recomendable que
  este nombre sea estable, y no vaya cambiando a lo largo del tiempo que sucede una alerta. Para información
  varible, use `extra_info`.
* **expected** (opcional): Valor esperado para considerarse que no sea un error. Por defecto, yes, true o 0. Puede
  tener modificadores como ">", ">=", etc., pero por defecto se asume "==".
* **level** (opcional): Por defecto, warning. Puede ser "info", "warning", "average", "high" o "disaster". Puede
  ser sobrescrito por el usuario como cualquier otro parámetro en el archivo se settings principal.
* **extra_info** (opcional): En ocasiones, puede quererse mostrar más información en la alerta sin necesidad de
  modificar el nombre de la misma. Dicha información puede ubicarse aquí.
* **enabled** (opcional): Por defecto, "yes". Puede cambiarse a "no".
* **seconds** (opcional): Tiempo durante el cual debe estar en ejecución el fallo para mandarse la alerta.