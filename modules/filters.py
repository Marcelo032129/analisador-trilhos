import streamlit as st

def criar_lista_filtro(coluna, df, texto_todas="Todas"):
    """Cria lista segura para filtros"""
    try:
        if coluna not in df.columns:
            return [texto_todas]
        
        valores = df[coluna].dropna().astype(str).str.strip().unique()
        valores_validos = [v for v in valores if v not in ['', 'nan', 'NaN', 'None', 'null', 'NÃO INFORMADO']]
        
        if not valores_validos:
            return [texto_todas]
        
        try:
            valores_ordenados = sorted(valores_validos)
        except:
            valores_ordenados = list(valores_validos)
        
        return [texto_todas] + valores_ordenados
    except:
        return [texto_todas]

def criar_filtros(df):
    """Cria os filtros na sidebar"""
    st.sidebar.markdown("## 🔍 Filtros de Análise")
    
    # Filtro por Gerência
    gerencias = criar_lista_filtro('Gerência', df, "Todas")
    gerencia_selecionada = st.sidebar.selectbox('Gerência', gerencias)
    
    # Filtro por Nível Crítico
    niveis = criar_lista_filtro('Nível Crítico', df, "Todos")
    nivel_selecionado = st.sidebar.selectbox('Nível Crítico', niveis)
    
    # Filtro por Classe
    classes = criar_lista_filtro('Classe', df, "Todas")
    classe_selecionada = st.sidebar.selectbox('Classe', classes)
    
    # Filtro por Ano
    if 'Ano Prospecção' in df.columns:
        try:
            anos_validos = df['Ano Prospecção'].dropna().unique()
            anos_numericos = [a for a in anos_validos if isinstance(a, (int, float))]
            if anos_numericos:
                anos_ordenados = sorted(anos_numericos)
                anos = ['Todos'] + [str(int(a)) for a in anos_ordenados]
            else:
                anos = ['Todos']
        except:
            anos = ['Todos']
    else:
        anos = ['Todos']
    
    ano_selecionado = st.sidebar.selectbox('Ano de Prospecção', anos)
    
    return {
        'gerencia': gerencia_selecionada,
        'nivel': nivel_selecionado,
        'classe': classe_selecionada,
        'ano': ano_selecionado
    }

def aplicar_filtros(df, filtros):
    """Aplica os filtros selecionados ao DataFrame"""
    df_filtrado = df.copy()
    
    if filtros['gerencia'] != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Gerência'].astype(str).str.strip() == filtros['gerencia']]
    
    if filtros['nivel'] != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Nível Crítico'].astype(str).str.strip() == filtros['nivel']]
    
    if filtros['classe'] != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Classe'].astype(str).str.strip() == filtros['classe']]
    
    if filtros['ano'] != 'Todos' and 'Ano Prospecção' in df_filtrado.columns:
        try:
            ano_num = int(filtros['ano'])
            df_filtrado = df_filtrado[df_filtrado['Ano Prospecção'] == ano_num]
        except:
            pass
    
    return df_filtrado
