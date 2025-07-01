========================
Penguin Analytic Account
========================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-penguin%2Fpisa--addons-lightgray.png?logo=github
    :target: https://github.com/penguin-group/pisa-addons/tree/master/penguin_analytic_account
    :alt: penguin-group/pisa-addons

|badge1| |badge2| |badge3|

En este módulo se agruparan todas las operaciones respecto a cuentas analíticas.

**Tabla de contenidos**

.. contents::
   :local:

Características
===============

* **Gestión Avanzada de Cuentas Analíticas**: Funcionalidades extendidas para el manejo de cuentas analíticas
* **Integración con Activos**: Conexión con el módulo de activos contables
* **Integración con Ventas**: Funcionalidad analítica en el proceso de ventas
* **Integración con Solicitudes de Compra**: Análisis de costos en solicitudes de compra
* **Vistas Personalizadas**: Interfaces mejoradas para la gestión analítica
* **Reportes Analíticos**: Informes especializados para análisis de costos y rentabilidad

Descripción
===========

Este módulo centraliza y mejora todas las operaciones relacionadas con cuentas analíticas en Odoo. 
Proporciona una gestión integral que permite a las organizaciones realizar un seguimiento detallado 
de costos, ingresos y rentabilidad por proyecto, departamento, producto o cualquier otra dimensión analítica.

Funcionalidades Principales
===========================

**Gestión de Cuentas Analíticas**

* Configuración avanzada de estructuras analíticas
* Jerarquías de cuentas analíticas
* Distribución automática de costos
* Seguimiento de presupuestos analíticos

**Integración con Módulos**

* **Activos Contables**: Distribución analítica de depreciaciones
* **Ventas**: Análisis de rentabilidad por venta
* **Compras**: Seguimiento de costos por proyecto
* **Solicitudes de Compra**: Control presupuestario analítico

**Vistas Mejoradas**

* Formularios de movimientos contables con información analítica mejorada
* Vistas de árbol de activos con dimensiones analíticas
* Formularios de productos con configuración analítica
* Interfaces optimizadas para análisis de datos

Modelos Extendidos
==================

**Account Move (account.move)**

Funcionalidades analíticas mejoradas:

* Distribución automática por líneas
* Validaciones de cuentas analíticas
* Reportes integrados por dimensión

**Product Template (product.template)**

Configuración analítica por producto:

* Cuentas analíticas por defecto
* Reglas de distribución automática
* Seguimiento de costos por producto

**Account Asset (account.asset)**

Integración analítica en activos:

* Distribución de depreciaciones
* Seguimiento por centro de costo
* Reportes de activos por proyecto

Instalación
===========

Para instalar este módulo:

#. Asegúrese de que las dependencias estén instaladas: ``base``, ``account_asset``, ``analytic``, ``sale``, ``purchase_request``
#. Clone el repositorio
#. Agregue el módulo a su ruta de addons
#. Actualice la lista de módulos
#. Instale el módulo desde el menú de Aplicaciones

Dependencias
============

Este módulo depende de:

* ``base``: Funcionalidad core de Odoo
* ``account_asset``: Gestión de activos contables
* ``analytic``: Funcionalidad analítica base
* ``sale``: Módulo de ventas
* ``purchase_request``: Solicitudes de compra

Configuración
=============

Después de la instalación:

#. Vaya a Contabilidad > Configuración > Contabilidad Analítica
#. Configure la estructura de cuentas analíticas
#. Defina las reglas de distribución automática
#. Configure los centros de costo y proyectos
#. Establezca las validaciones y controles necesarios

**Configuración de Cuentas Analíticas**

#. Acceda a Contabilidad > Configuración > Contabilidad Analítica > Cuentas Analíticas
#. Cree la estructura jerárquica de cuentas
#. Configure los códigos y descripciones
#. Establezca los responsables de cada cuenta

**Configuración de Productos**

#. Vaya a Inventario > Configuración > Productos
#. Configure las cuentas analíticas por defecto
#. Establezca reglas de distribución automática
#. Configure los parámetros de seguimiento

Uso
===

**Análisis de Movimientos Contables**

#. Cree movimientos contables normalmente
#. El sistema aplicará automáticamente las reglas analíticas
#. Revise la distribución analítica en las líneas
#. Genere reportes analíticos según necesidad

**Gestión de Activos**

#. Registre activos con dimensiones analíticas
#. El sistema distribuirá automáticamente las depreciaciones
#. Realice seguimiento por centro de costo
#. Genere reportes de activos por proyecto

**Análisis de Ventas**

#. Las ventas se analizan automáticamente por dimensión
#. Seguimiento de rentabilidad por proyecto
#. Reportes de márgenes por cuenta analítica
#. Análisis de performance por vendedor/proyecto

Reportes
========

* **Reporte de Costos por Proyecto**: Análisis detallado de costos
* **Reporte de Rentabilidad**: Análisis de márgenes por dimensión
* **Reporte de Presupuesto vs Real**: Comparación presupuestaria
* **Reporte de Activos Analíticos**: Distribución de activos por proyecto

Rastreador de Errores
=====================

Los errores se rastrean en `GitHub Issues <https://github.com/penguin-group/pisa-addons/issues>`_.
En caso de problemas, verifique si el error ya ha sido reportado.

Créditos
========

Autores
~~~~~~~

* Penguin Infrastructure

Mantenedores
~~~~~~~~~~~~

Este módulo es mantenido por Penguin Infrastructure.

.. image:: https://penguin.digital/logo.png
   :alt: Penguin Infrastructure
   :target: https://penguin.digital

Penguin Infrastructure es una empresa de desarrollo de software especializada en implementaciones de Odoo. 