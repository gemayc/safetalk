"""
Verifica el impacto del preprocesado en el dataset.

Antes de entrenar V2, comprueba que el preprocesado nuevo
NO rompe el dataset (palabras clave preservadas, no hay
textos vacíos, etc.).

Uso (desde la raíz del proyecto):
    python scripts/verify_preprocessing.py
"""

import sys
from pathlib import Path
import pandas as pd

# Permitir imports desde la raíz del repo
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.preprocessing import TextPreprocessor


# ========================================
# CONFIGURACIÓN
# ========================================

# Archivos a verificar
ARCHIVOS = [
    "data/processed/dataset_safetalk_final.csv",
]

# Palabras clave que deberían preservarse
PALABRAS_CLAVE = [
    "gilipollas",
    "idiota",
    "tonto",
    "imbécil",
    "puta",
    "cabrón",
    "maricón",
    "mierda",
    "estúpido",
]


def verificar_preprocesado(ruta_csv: str):
    """Analiza el impacto del preprocesado en un dataset"""
    
    print(f"\n{'='*80}")
    print(f"📂 VERIFICANDO: {ruta_csv}")
    print(f"{'='*80}")
    
    # Cargar
    df = pd.read_csv(ruta_csv)
    print(f"Total ejemplos: {len(df)}")
    
    # Mantener solo texto y label
    if "fuente" in df.columns:
        df = df[["texto", "label"]]
    
    # Aplicar preprocesado
    preprocessor = TextPreprocessor()
    df["texto_procesado"] = preprocessor.clean_batch(df["texto"].tolist())
    
    # =========================
    # 1. ESTADÍSTICAS GENERALES
    # =========================
    print(f"\n📊 ESTADÍSTICAS GENERALES")
    print("-" * 80)
    
    cambios = (df["texto"] != df["texto_procesado"]).sum()
    print(f"Textos modificados: {cambios} ({cambios/len(df)*100:.1f}%)")
    print(f"Textos sin cambios: {len(df)-cambios} ({(len(df)-cambios)/len(df)*100:.1f}%)")
    
    # =========================
    # 2. CAMBIOS DE LONGITUD
    # =========================
    print(f"\n📏 CAMBIOS DE LONGITUD")
    print("-" * 80)
    
    df["len_original"] = df["texto"].str.len()
    df["len_procesado"] = df["texto_procesado"].str.len()
    
    print(f"Longitud media ANTES:    {df['len_original'].mean():.1f} caracteres")
    print(f"Longitud media DESPUÉS:  {df['len_procesado'].mean():.1f} caracteres")
    print(f"Longitud mínima ANTES:   {df['len_original'].min()} caracteres")
    print(f"Longitud mínima DESPUÉS: {df['len_procesado'].min()} caracteres")
    
    # =========================
    # 3. TEXTOS VACÍOS (CRÍTICO)
    # =========================
    print(f"\n⚠️  TEXTOS VACÍOS TRAS PREPROCESADO")
    print("-" * 80)
    
    vacios = (df["texto_procesado"].str.strip() == "").sum()
    
    if vacios > 0:
        print(f"❌ ATENCIÓN: {vacios} textos quedaron vacíos ({vacios/len(df)*100:.1f}%)")
        print(f"\nPrimeros 3 ejemplos problemáticos:")
        
        ejemplos = df[df["texto_procesado"].str.strip() == ""].head(3)
        for _, row in ejemplos.iterrows():
            print(f"\n  Label: {row['label']}")
            print(f"  Original: '{row['texto']}'")
            print(f"  Procesado: '{row['texto_procesado']}'")
    else:
        print(f"✅ Ningún texto quedó vacío. Excelente.")
    
    # =========================
    # 4. PALABRAS CLAVE
    # =========================
    print(f"\n🔍 PRESERVACIÓN DE PALABRAS CLAVE")
    print("-" * 80)
    print(f"{'Palabra':<15} {'Antes':>10} {'Después':>10} {'Preservadas':>15}")
    print("-" * 80)
    
    alguna_pierde = False
    
    for palabra in PALABRAS_CLAVE:
        antes = df["texto"].str.lower().str.contains(palabra, na=False).sum()
        despues = df["texto_procesado"].str.contains(palabra, na=False).sum()
        
        if antes > 0:
            pct = (despues / antes) * 100
            status = "✅" if pct >= 95 else ("⚠️" if pct >= 80 else "❌")
            
            if pct < 95:
                alguna_pierde = True
            
            print(f"{status} {palabra:<13} {antes:>10} {despues:>10} {pct:>14.1f}%")
        else:
            print(f"   {palabra:<13} {'N/A':>10} {'N/A':>10} {'(no aparece)':>15}")
    
    # =========================
    # 5. EJEMPLOS DE CAMBIOS
    # =========================
    print(f"\n📝 EJEMPLOS DE CAMBIOS (5 ejemplos aleatorios)")
    print("-" * 80)
    
    cambiados = df[df["texto"] != df["texto_procesado"]]
    
    if len(cambiados) > 0:
        ejemplos = cambiados.sample(min(5, len(cambiados)), random_state=42)
        
        for i, (_, row) in enumerate(ejemplos.iterrows(), 1):
            print(f"\nEjemplo {i} [label={row['label']}]:")
            print(f"  ANTES:   {row['texto'][:100]}{'...' if len(row['texto']) > 100 else ''}")
            print(f"  DESPUÉS: {row['texto_procesado'][:100]}{'...' if len(row['texto_procesado']) > 100 else ''}")
    
    # =========================
    # 6. VEREDICTO FINAL
    # =========================
    print(f"\n{'='*80}")
    print(f"🎯 VEREDICTO")
    print(f"{'='*80}")
    
    problemas = []
    if vacios > len(df) * 0.05:  # Más del 5% vacíos
        problemas.append(f"❌ {vacios} textos vacíos ({vacios/len(df)*100:.1f}%)")
    if alguna_pierde:
        problemas.append("⚠️  Algunas palabras clave se pierden (<95%)")
    
    if not problemas:
        print("✅ TODO CORRECTO - Procede a entrenar V2")
        print("   - Sin textos vacíos significativos")
        print("   - Palabras clave preservadas")
        print("   - Cambios razonables")
    else:
        print("⚠️  PROBLEMAS DETECTADOS:")
        for p in problemas:
            print(f"   {p}")
        print("\n   Revisa el preprocesado antes de entrenar V2")


def main():
    print("="*80)
    print("VERIFICACIÓN DE IMPACTO DEL PREPROCESADO")
    print("="*80)
    print("\nEste script verifica que el preprocesado nuevo NO rompa el dataset")
    print("antes de gastar tiempo entrenando V2.\n")
    
    for archivo in ARCHIVOS:
        if Path(archivo).exists():
            verificar_preprocesado(archivo)
        else:
            print(f"\n❌ No encontrado: {archivo}")
    
    print(f"\n{'='*80}")
    print("✅ VERIFICACIÓN COMPLETADA")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
    