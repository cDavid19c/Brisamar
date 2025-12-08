#!/bin/bash
# Script para verificar que los cambios se aplicaron correctamente

echo "======================================================================"
echo "  🔍 VERIFICACIÓN DE CAMBIOS - SISTEMA DE GENERACIÓN DE FACTURAS"
echo "======================================================================"
echo ""

echo "1️⃣  Verificando FuncionesEspecialesGestionRest.py..."
if grep -q "DEBUG emitir_factura_interna" "servicios/rest/gestion/FuncionesEspecialesGestionRest.py"; then
    echo "   ✅ Logging de emitir_factura_interna añadido"
else
    echo "   ❌ Logging no encontrado"
fi

echo ""
echo "2️⃣  Verificando views.py..."
if grep -q "Pago actualizado automáticamente por el SP" "webapp/views.py"; then
    echo "   ✅ Lógica de generar_factura simplificada"
else
    echo "   ❌ Cambio no encontrado"
fi

echo ""
echo "3️⃣  Verificando pagos/index.html..."
if grep -q "btnConfirmarFactura.textContent = 'Generar Factura'" "webapp/templates/webapp/pagos/index.html"; then
    echo "   ✅ JavaScript de pagos corregido"
else
    echo "   ❌ JavaScript no actualizado"
fi

echo ""
echo "======================================================================"
echo "  ✨ PRÓXIMOS PASOS"
echo "======================================================================"
echo ""
echo "1. Reinicia el servidor Django:"
echo "   python manage.py runserver"
echo ""
echo "2. Navega a: http://localhost:8000/usuario/pagos/?uid=9"
echo ""
echo "3. Haz click en 'Generar Factura'"
echo ""
echo "4. Revisa los logs en la consola para verificar que todo funciona"
echo ""
echo "======================================================================"
