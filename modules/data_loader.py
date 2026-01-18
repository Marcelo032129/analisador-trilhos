import streamlit as st
import pandas as pd
import numpy as np

def limpar_valor(valor):
    """Limpa e converte valores do DataFrame"""
    if pd.isna(valor):
        return None
    if isinstance(valor, (int, float, np.integer, np.floating)):
        return valor
    if isinstance(valor, str):
        valor = valor.strip()
        try:
            if ',' in valor and '.' not in valor:
                valor = valor.replace(',', '.')
            return float(valor)
        except:
            return valor if valor not in ['', 'nan', 'NaN', 'None', 'null'] else None
    return valor

@st.cache_data
def load_data(uploaded_file=None):
    """Carrega dados - função principal com nome correto"""
    try:
        # Se arquivo foi enviado (modo deploy)
        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file, sheet_name='Export', engine='openpyxl')
            st.success(f"✅ Arquivo carregado: {uploaded_file.name}")
            return process_data(df)
        
        # Modo local: tenta carregar arquivo local
        caminho_local = r"C:\Users\cs261742\Notas\Python\Analista_V12\data\Dados_Simulador_Trilho.xlsx"
        
        try:
            df = pd.read_excel(caminho_local, sheet_name='Export', engine='openpyxl')
            st.success("✅ Arquivo local carregado")
            return process_data(df)
        except Exception as e:
            st.warning(f"⚠️ Não foi possível carregar arquivo local: {str(e)}")
            st.info("ℹ️ Usando dados de exemplo...")
            return create_sample_data()
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        return create_sample_data()

def process_data(df):
    """Processa os dados do DataFrame"""
    # Limpar nomes das colunas
    df.columns = [str(col).strip() for col in df.columns]
    
    # Aplicar limpeza
    for col in df.columns:
        df[col] = df[col].apply(limpar_valor)
    
    # Tratar strings importantes
    string_cols = ['Gerência', 'Coordenador', 'Classe', 'Backlog', 'Contribuinte',
                  'Restrição Via (Motivo)', 'Restrição Trilho (Motivo)']
    
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str)
            df[col] = df[col].replace(['None', 'nan', 'NaN', 'null', '<NA>'], 'NÃO INFORMADO')
            df[col] = df[col].str.strip()
    
    # Garantir que Gerência seja string limpa
    if 'Gerência' in df.columns:
        df['Gerência'] = df['Gerência'].astype(str)
        df['Gerência'] = df['Gerência'].replace(['None', 'nan', 'NaN', 'null', '<NA>', ''], 'NÃO INFORMADO')
        df['Gerência'] = df['Gerência'].str.strip().str.upper()
    
    # Datas
    if 'Data da Prospecção' in df.columns:
        try:
            df['Data da Prospecção'] = pd.to_datetime(df['Data da Prospecção'], errors='coerce')
            df['Ano Prospecção'] = df['Data da Prospecção'].dt.year
        except:
            df['Ano Prospecção'] = None
    
    # Colunas numéricas
    numeric_columns = ['DV Atual', 'DH Atual', 'DV A+1', 'DH A+1', 'Extensão']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Classificação de criticidade
    df['Nível Crítico'] = df.apply(classificar_criticidade, axis=1)
    
    # Score de prioridade
    df['Score Prioridade'] = df.apply(calcular_score, axis=1)
    
    return df

def classificar_criticidade(row):
    """Classifica o nível crítico do trecho"""
    try:
        classe = str(row.get('Classe', '')).upper() if pd.notna(row.get('Classe')) else ''
        dv = float(row.get('DV Atual', 0)) if pd.notna(row.get('DV Atual')) else 0
        
        if any(['A (P1)' in classe, 'B' in classe, 'E' in classe, dv > 100]):
            return 'Alta'
        elif any(['A (P2)' in classe and dv > 15, 'C' in classe, 'D' in classe, dv > 30]):
            return 'Média'
        else:
            return 'Baixa'
    except:
        return 'Baixa'

def calcular_score(row):
    """Calcula score de prioridade"""
    try:
        score = 0
        dv = float(row.get('DV Atual', 0)) if pd.notna(row.get('DV Atual')) else 0
        dh = float(row.get('DH Atual', 0)) if pd.notna(row.get('DH Atual')) else 0
        
        score += dv * 0.5
        score += dh * 0.3
        
        classe = str(row.get('Classe', '')) if pd.notna(row.get('Classe')) else ''
        if 'A (P1)' in classe or 'B' in classe or 'E' in classe:
            score += 50
        elif 'A (P2)' in classe:
            score += 20
        
        return round(score, 2)
    except:
        return 0

def create_sample_data():
    """Cria dados de exemplo para demonstração"""
    data = {
        'Equipamento': ['12/040448-040470tg', '29/064622-064870tg', '10/065400-065460cv'],
        'Gerência': ['UP SERRAS', 'UP RS', 'UP SERRAS'],
        'Classe': ['A (P2)', 'A (P2)', 'A (P2)'],
        'DV Atual': [203, 115, 44],
        'DH Atual': [2, 6, 16],
        'Nível Crítico': ['Alta', 'Média', 'Baixa'],
        'Score Prioridade': [152.1, 58.5, 22.0]
    }
    return pd.DataFrame(data)
