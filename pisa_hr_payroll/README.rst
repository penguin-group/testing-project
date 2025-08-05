====================
PISA HR Payroll
====================

Módulo de Nómina para Paraguay
===============================

Este módulo proporciona funcionalidades específicas para el procesamiento de nóminas en Paraguay, cumpliendo con las regulaciones locales.

Características Principales
============================

**Cálculos Salariales**

* Salario proporcional basado en días trabajados
* Horas extras diurnas (50% adicional)
* Horas extras nocturnas (100% adicional + 30% recargo nocturno)
* Recargos nocturnos (30% adicional)
* Trabajo en feriados (200% diurno, 230% nocturno)
* Licencias médicas (50% reembolso empresa para 2-3 días)
* Vacaciones proporcionales

**Asignaciones y Beneficios**

* Bonificación familiar (hijos menores de 17 años)
* Subsidio de guardería (hijos menores de 3 años)
* Otros ingresos esporádicos
* Bonos adicionales

**Descuentos y Deducciones**

* IPS Empleado (9% de la base imponible)
* Anticipos de salario
* Embargo judicial (máximo 25%)
* Seguro médico
* Contribuciones solidarias
* Descuentos varios (capacitación, estacionamiento, inglés, préstamos)

**Características del Sistema**

* Integración con localización contable paraguaya (l10n_py)
* Reportes de recibos de salario con formato paraguayo
* Parámetros configurables por fecha
* Múltiples estructuras salariales
* Validaciones automáticas de límites legales

Configuración
=============

**Instalación**

1. Asegúrese de tener instalados los módulos base:
   - hr_payroll (Enterprise)
   - hr_work_entry_contract
   - l10n_py

2. Instale el módulo pisa_hr_payroll

**Configuración Inicial**

1. **Empleados**: Configure la información específica de Paraguay en la ficha del empleado:
   - Número de IPS
   - Información de hijos (para asignaciones familiares)
   - Cuenta bancaria y método de pago

2. **Contratos**: Configure los parámetros específicos en los contratos:
   - Días de vacaciones por año
   - Contribución seguro médico
   - Porcentajes de embargo judicial
   - Asignaciones adicionales

3. **Parámetros**: Revise y ajuste los parámetros del sistema:
   - Salario mínimo
   - Tasas de IPS
   - Montos de asignaciones familiares
   - Tasas de horas extras y recargos

Uso
===

**Procesamiento de Nómina**

1. Vaya a Nómina > Recibos de Salario
2. Cree un nuevo recibo o use "Generar Recibos"
3. Seleccione la estructura "Liquidación Mensual Paraguay"
4. Configure las entradas adicionales según sea necesario:
   - Horas extras
   - Días de vacaciones
   - Licencias médicas
   - Bonos y otros ingresos
   - Descuentos varios

5. Compute el recibo para generar las líneas automáticamente
6. Revise y confirme el recibo
7. Genere el reporte en formato paraguayo

**Reportes**

El módulo incluye un reporte de recibo de salario que replica el formato estándar paraguayo con:
- Información del empleado y empresa
- Desglose detallado de ingresos y descuentos
- Cálculos de IPS y totales
- Observaciones y consideraciones legales

Soporte
=======

Para soporte técnico, contacte:

* **Penguin Infrastructure S.A.**
* Website: https://penguin.digital
* Versión: 18.0.1.0.0
* Licencia: OPL-1

Autor
=====

Desarrollado por Penguin Infrastructure S.A. para el procesamiento de nóminas en Paraguay siguiendo las regulaciones laborales locales.