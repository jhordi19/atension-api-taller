# Sustainability Guidelines

## Propósito

Este documento describe las prácticas sostenibles y eficientes implementadas en el proyecto **aTensión Backend API** para contribuir a un software verde, eficiente y responsable con los recursos.

---

## Prácticas implementadas

### 1. **Paginación en endpoints**

- Todos los endpoints que devuelven listas grandes (por ejemplo, historial de presiones) implementan paginación (`page` y `limit`).
- Esto evita transferencias innecesarias de datos y reduce el consumo de memoria y ancho de banda.

### 2. **Compresión GZip**

- El middleware GZip está habilitado en FastAPI (`minimum_size=500`).
- Las respuestas grandes se comprimen automáticamente, reduciendo el tráfico de red y acelerando la transferencia de datos.

### 3. **Logging eficiente y centralizado**

- Se utiliza el módulo estándar `logging` de Python, configurado en `app/core/log_config.py`.
- Los logs se registran solo en eventos importantes (creación, borrado, login, evaluaciones).
- Se mide y registra el tiempo de procesamiento en endpoints críticos para monitorear el rendimiento y detectar cuellos de botella.
- Se evita el uso de `print` y logs innecesarios para reducir la carga de CPU y el tamaño de archivos de log.

### 4. **Eliminación de código redundante**

- Se han refactorizado endpoints para evitar bucles y validaciones repetidas.
- Se utilizan funciones auxiliares para lógica compartida, mejorando la mantenibilidad y eficiencia.

### 5. **Formato y calidad de código**

- Se utiliza `black` y `flake8` para asegurar un formato consistente y buenas prácticas de codificación.
- El pre-commit está configurado para aplicar estos formateadores automáticamente antes de cada commit.

### 6. **Pruebas de carga y monitoreo**

- Se realizan pruebas de carga con Locust antes de cada despliegue.
- Los resultados se documentan y analizan para validar el rendimiento y la escalabilidad.

---

## Recomendaciones para desarrollo sostenible

- **Evitar transferencias de datos innecesarias:** Siempre usar paginación y filtros en endpoints que devuelvan listas.
- **Monitorear el rendimiento:** Registrar el tiempo de procesamiento en endpoints críticos y analizar los logs periódicamente.
- **Optimizar el uso de recursos:** Mantener la compresión activa y revisar el consumo de memoria y CPU.
- **Mantener el código limpio:** Refactorizar regularmente, eliminar redundancias y seguir las guías de estilo.
- **Actualizar dependencias:** Mantener las librerías y frameworks actualizados para aprovechar mejoras de eficiencia y seguridad.
- **Documentar cambios sostenibles:** Registrar en este archivo cualquier nueva práctica verde implementada.

---

## Futuras mejoras

- Integrar el sistema de logging con servicios en la nube (ejemplo: Google Cloud Logging) para monitoreo avanzado.
- Implementar cache selectivo en endpoints de solo lectura.
- Automatizar el análisis de consumo energético en el entorno de producción.

---

**Última actualización:** Noviembre 2025
