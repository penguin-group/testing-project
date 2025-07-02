=======================================
Excepción para bloqueo de periodos PISA y PASA
=======================================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-penguin%2Fpisa--addons-lightgray.png?logo=github
    :target: https://github.com/penguin-group/pisa-addons/tree/master/period_block_exception
    :alt: penguin-group/pisa-addons

|badge1| |badge2| |badge3|

Excepción de bloqueo de fechas contabilidad para las empresas de PISA y PASA para el periodo de 2022-2023.

**Tabla de contenidos**

.. contents::
   :local:

Características
===============

* **Excepción de Bloqueo de Períodos**: Permite excepciones específicas al bloqueo de períodos contables
* **Configuración Específica**: Diseñado específicamente para las empresas PISA y PASA
* **Período 2022-2023**: Configurado para el período contable específico 2022-2023
* **Integración con Contabilidad**: Se integra seamlessly with the Odoo accounting module

Descripción
===========

Este módulo proporciona una excepción específica al sistema de bloqueo de períodos contables de Odoo, 
diseñado especialmente para las necesidades de las empresas PISA y PASA durante el período 2022-2023.

El bloqueo de períodos es una característica importante en contabilidad que previene la modificación 
de registros contables después de ciertas fechas. Sin embargo, en algunos casos específicos, 
se requieren excepciones para permitir ajustes necesarios.

Funcionalidad
=============

* **Gestión de Excepciones**: Permite configurar excepciones específicas al bloqueo de períodos
* **Control por Empresa**: Las excepciones se aplican específicamente a PISA y PASA
* **Período Específico**: Configurado para el período contable 2022-2023
* **Seguridad Integrada**: Mantiene la seguridad contable mientras permite excepciones necesarias

Instalación
===========

Para instalar este módulo:

#. Asegúrese de que las dependencias estén instaladas: ``base``, ``account``, ``account_accountant``
#. Clone el repositorio
#. Agregue el módulo a su ruta de addons
#. Actualice la lista de módulos
#. Instale el módulo desde el menú de Aplicaciones

Dependencias
============

Este módulo depende de:

* ``base``: Funcionalidad core de Odoo
* ``account``: Módulo de contabilidad
* ``account_accountant``: Funcionalidades avanzadas de contabilidad

Configuración
=============

Después de la instalación:

#. El módulo se configura automáticamente para las empresas PISA y PASA
#. Las excepciones se aplican al período 2022-2023
#. No se requiere configuración adicional manual

Uso
===

**Aplicación de Excepciones**

#. Las excepciones se aplican automáticamente cuando se cumplen las condiciones:
   - La empresa es PISA o PASA
   - El período afectado es 2022-2023
   - Se intenta realizar operaciones en períodos bloqueados

**Verificación de Estado**

#. Vaya a Contabilidad > Configuración
#. Verifique la configuración de bloqueo de períodos
#. Las excepciones aparecerán aplicadas según la configuración del módulo

Consideraciones Técnicas
========================

**Alcance Limitado**

Este módulo está específicamente diseñado para:

* Empresas: PISA y PASA únicamente
* Período: 2022-2023 únicamente
* Propósito: Excepción temporal para ajustes necesarios

**Seguridad**

* Mantiene la integridad contable
* Aplica excepciones solo cuando es necesario
* Controla el acceso según los permisos existentes

Rastreador de Errores
=====================

Los errores se rastrean en `GitHub Issues <https://github.com/penguin-group/pisa-addons/issues>`_.
En caso de problemas, verifique si el error ya ha sido reportado.

Créditos
========

Autores
~~~~~~~

* Penguin Infrastructure

Contribuidores
~~~~~~~~~~~~~~

* Giuliano Díaz <giuliano@penguin.digital>
* David Páez <david@penguin.digital>

Mantenedores
~~~~~~~~~~~~

Este módulo es mantenido por Penguin Infrastructure.

.. image:: https://penguin.digital/logo.png
   :alt: Penguin Infrastructure
   :target: https://penguin.digital

Penguin Infrastructure es una empresa de desarrollo de software especializada en implementaciones de Odoo. 