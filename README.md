# plataforma-checker
Pequeña web para checar las ultimas notificaciones de la plafatorma de tareas

- El proposito de esta pagina es revisar cada 20 minutos la pagina [UNIO](https://edi-unoi-mx.stn-neds.com/notificacion/notifications/received) y verificar si hay una nueva notificacion.
- Si se muestra una pagina en blanco, se debe proceder a https://edi-unoi-mx.stn-neds.com/ts/view/access para el login
- Si se muestra una pagina con informacion, verificar la fecha de la ultima notificacion y en caso de ser una nueva notificacion, mandar un email o whatsapp (a configurar) y guardar la nueva fecha para comparar despues.
- El proceso se debe repetir cada 20 minutos (configurable)